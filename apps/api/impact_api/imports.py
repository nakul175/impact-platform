"""Import and data quality (v0.21): bounded tabular import batches that are staged, checked and then
committed as observations through the existing observation review path.

An import batch (registry kind ImportJob) carries its own source file (CSV text or a base64 .xlsx,
first worksheet), a mapping that binds source columns by header name to indicator instances, a unit
column and one reporting period. Preview parses the file and validates every row before anything is
written: each row is ACCEPTED, QUARANTINED (with reason codes) or DUPLICATE, non-blocking quality
warnings (a robust outlier against prior approved values) are recorded beside it, and the staged
outcome is pinned by a hash. Commit recomputes the outcome under the tenant lock, refuses it when it
no longer matches the preview, and then writes one observation per accepted row and bound indicator
in the reserved IMPORT namespace and submits each into the independent observation review — all in
one transaction, so a batch is applied completely or not at all."""

import base64
import binascii
import csv
import hashlib
import io
import re
import zipfile
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, localcontext
from xml.etree import ElementTree
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .domain import NUMBER, RATIO_TYPES, DomainError, aware, ratio, stored, validate_dimensions
from .import_contracts import MAX_COLUMNS, MAX_OBSERVATIONS, MAX_ROWS
from .store import canonical, load, write

NAMESPACE = "IMPORT"
RULE_SET = "IMPORT_DQ_1"
SUPPORTED = {"COUNT", "DECIMAL", "RATIO", "PERCENTAGE"}
UNIT_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
# Robust outlier check (FR-DQ-007, warning only): modified z-score 0.6745·(x − median)/MAD over the
# indicator's most recent approved PRESENT values. It never changes a value or blocks a row; with fewer
# than the minimum history or no spread (MAD = 0) the check is not evaluated.
ANOMALY = {
    "method": "MODIFIED_Z_MAD",
    "version": "1",
    "threshold": "3.5",
    "minimum_history": 5,
    "history_limit": 200,
    "blocking": False,
}
SERVER_FIELDS = ["source_namespace", "content_sha256", "received_at", "preview", "committed", "cancel_reason"]
MAX_UNCOMPRESSED = 8 * 1024 * 1024
MAX_CELL = 1000
XML_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
XML_REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
XML_PACKAGE = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def fail(reason, status=422, code="VALIDATION_FAILED", fields=None):
    return DomainError(code, status, reason=reason, fields=fields)


# Parsing ----------------------------------------------------------------------------------------
class Sheet:
    """Cell text by row, plus the positions that held a formula and the positions that were numeric
    spreadsheet cells (a numeric date column is a spreadsheet serial day number)."""

    def __init__(self, rows, formulas=(), numeric=()):
        self.rows, self.formulas, self.numeric = rows, set(formulas), set(numeric)


def parse_csv(content):
    text = content[1:] if content.startswith("﻿") else content
    if "\x00" in text:
        raise fail("FILE_UNREADABLE")
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error:
        raise fail("FILE_UNREADABLE") from None
    return Sheet(rows)


def column_index(letters):
    index = 0
    for ch in letters:
        index = index * 26 + (ord(ch) - 64)
    return index - 1


def parse_xlsx(content):
    """The first worksheet of an .xlsx file, read with the standard library only. Safety checks come
    before parsing: base64 and zip structure, at most 8 MiB uncompressed and 500 entries, and no
    document type declarations (no entity expansion)."""
    try:
        raw = base64.b64decode(content, validate=True)
        archive = zipfile.ZipFile(io.BytesIO(raw))
        entries = archive.infolist()
    except (binascii.Error, ValueError, zipfile.BadZipFile):
        raise fail("FILE_UNREADABLE") from None
    if len(entries) > 500 or sum(e.file_size for e in entries) > MAX_UNCOMPRESSED:
        raise fail("FILE_TOO_LARGE")
    names = {e.filename for e in entries}

    def xml(name):
        if name not in names:
            raise fail("FILE_UNREADABLE")
        data = archive.read(name)
        if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
            raise fail("FILE_UNSAFE")
        try:
            return ElementTree.fromstring(data)
        except ElementTree.ParseError:
            raise fail("FILE_UNREADABLE") from None

    try:
        sheet = xml("xl/workbook.xml").find(XML_MAIN + "sheets/" + XML_MAIN + "sheet")
        if sheet is None:
            raise fail("FILE_UNREADABLE")
        rid = sheet.get(XML_REL + "id")
        target = next(
            (r.get("Target") for r in xml("xl/_rels/workbook.xml.rels") if r.get("Id") == rid), None
        )
        if not target:
            raise fail("FILE_UNREADABLE")
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        shared = []
        if "xl/sharedStrings.xml" in names:
            shared = [
                "".join(t.text or "" for t in si.iter(XML_MAIN + "t"))
                for si in xml("xl/sharedStrings.xml").findall(XML_MAIN + "si")
            ]
        cells, formulas, numeric = {}, set(), set()
        for cell in xml(path).iter(XML_MAIN + "c"):
            match = re.fullmatch(r"([A-Z]{1,3})([0-9]{1,7})", cell.get("r") or "")
            if not match:
                raise fail("FILE_UNREADABLE")
            r, col = int(match.group(2)) - 1, column_index(match.group(1))
            if col >= MAX_COLUMNS:
                raise fail("FILE_TOO_WIDE")
            if r > MAX_ROWS + 1000:
                raise fail("IMPORT_ROW_LIMIT", code="LIMIT_EXCEEDED")
            kind, value = cell.get("t", "n"), cell.find(XML_MAIN + "v")
            text = value.text if value is not None and value.text is not None else ""
            if kind == "s":
                text = shared[int(text)] if text else ""
            elif kind == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(XML_MAIN + "t"))
            elif kind == "b":
                text = "TRUE" if text == "1" else "FALSE"
            elif kind == "n" and text:
                numeric.add((r, col))
                if not NUMBER.fullmatch(text):
                    with localcontext() as ctx:
                        ctx.prec = 60
                        text = format(Decimal(text), "f")
                    if "." in text:
                        text = text.rstrip("0").rstrip(".")
            if cell.find(XML_MAIN + "f") is not None:
                formulas.add((r, col))
            cells[(r, col)] = text
    except (KeyError, IndexError, ValueError, InvalidOperation, zipfile.BadZipFile):
        raise fail("FILE_UNREADABLE") from None
    if not cells:
        return Sheet([])
    height = max(r for r, _ in cells) + 1
    width = max(c for _, c in cells) + 1
    rows = [[cells.get((r, c), "") for c in range(width)] for r in range(height)]
    return Sheet(rows, formulas, numeric)


def parse(payload):
    return parse_xlsx(payload["content"]) if payload["format"] == "XLSX" else parse_csv(payload["content"])


# Interpretation ---------------------------------------------------------------------------------
def interpret_date(text, pattern, zone, serial=False):
    """An event instant from one cell. ISO 8601 needs an explicit offset; a date pattern reads a
    calendar date at midnight in the period's reporting zone; a numeric spreadsheet cell is a serial
    day number (1900 date system). Ambiguous text is never guessed."""
    if serial and NUMBER.fullmatch(text):
        day = datetime(1899, 12, 30, tzinfo=zone) + timedelta(days=float(text))
        return day.astimezone(timezone.utc)
    if pattern in (None, "ISO_8601"):
        try:
            return aware(text).astimezone(timezone.utc)
        except DomainError:
            raise fail("EVENT_AT_INVALID") from None
    formats = {"YYYY-MM-DD": "%Y-%m-%d", "DD/MM/YYYY": "%d/%m/%Y", "MM/DD/YYYY": "%m/%d/%Y"}
    if not re.fullmatch(r"[0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4}", text):
        raise fail("DATE_PATTERN_MISMATCH")
    try:
        return datetime.strptime(text, formats[pattern]).replace(tzinfo=zone).astimezone(timezone.utc)
    except ValueError:
        raise fail("DATE_PATTERN_MISMATCH") from None


def cell_state(text, missing_codes):
    """('VALUE', text), or the explicit value state of a blank or declared token. A blank is MISSING,
    never zero."""
    stripped = text.strip()
    if stripped == "":
        return "MISSING", None
    if stripped in missing_codes:
        return missing_codes[stripped], None
    return "VALUE", stripped


def number(text, binding, integer=False):
    if not NUMBER.fullmatch(text):
        raise fail("VALUE_NOT_NUMERIC")
    value = Decimal(text)
    if integer and value != value.to_integral_value():
        raise fail("VALUE_TYPE_INVALID")
    low, high = binding.get("minimum"), binding.get("maximum")
    if (low is not None and value < Decimal(low)) or (high is not None and value > Decimal(high)):
        raise fail("VALUE_OUT_OF_RANGE")
    return value


def measure(definition, roles, cells, missing_codes):
    """The value state and value one indicator receives from one row, or a DomainError whose reason
    is the row's quarantine reason. Type and range follow the pinned definition: a COUNT is a
    non-negative integer, ratio components are non-negative, a percentage numerator never exceeds its
    denominator, and a zero denominator is UNDEFINED, never zero."""
    kind = definition["measurement_type"]
    states = {role: cell_state(cells[role], missing_codes) for role in roles}
    if any(s == "VALUE" for s, _ in states.values()) and not all(s == "VALUE" for s, _ in states.values()):
        # One component present and the other blank: nothing can be computed, and nothing is zero.
        for role, (s, text) in states.items():
            if s == "VALUE":
                number(text, roles[role])
        return {"value_state": "MISSING", "value": None}
    if not all(s == "VALUE" for s, _ in states.values()):
        found = {s for s, _ in states.values()}
        return {"value_state": found.pop() if len(found) == 1 else "MISSING", "value": None}
    if kind in RATIO_TYPES:
        n = number(states["NUMERATOR"][1], roles["NUMERATOR"])
        d = number(states["DENOMINATOR"][1], roles["DENOMINATOR"])
        if n < 0 or d < 0 or (kind == "PERCENTAGE" and n > d):
            raise fail("INVALID_COMPONENTS")
        with localcontext() as ctx:
            ctx.prec = 60
            value = ratio(definition, n, d)
        if value is None:
            return {"value_state": "UNDEFINED", "value": None}
        return {
            "value_state": "PRESENT",
            "value": stored(value),
            "numerator": states["NUMERATOR"][1],
            "denominator": states["DENOMINATOR"][1],
        }
    value = number(states["VALUE"][1], roles["VALUE"], integer=kind == "COUNT")
    if kind == "COUNT" and value < 0:
        raise fail("VALUE_OUT_OF_RANGE")
    return {"value_state": "PRESENT", "value": stored(value)}


def robust_outlier(value, history):
    """The anomaly finding for one value against prior approved values, or None."""
    if len(history) < ANOMALY["minimum_history"]:
        return None
    with localcontext() as ctx:
        ctx.prec = 60
        ordered = sorted(history)
        median = _median(ordered)
        mad = _median(sorted(abs(v - median) for v in ordered))
        if mad == 0:
            return None
        score = Decimal("0.6745") * (value - median) / mad
        if abs(score) <= Decimal(ANOMALY["threshold"]):
            return None
        return {
            "median": stored(median),
            "mad": stored(mad),
            "score": format(score.quantize(Decimal("0.01")), "f"),
        }


def _median(values):
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2


class Imports:
    def __init__(self, service):
        self.service = service

    # Draft --------------------------------------------------------------------------------------
    def save(self, c, ctx, previous, data):
        """Create or edit a batch draft. Server-owned fields are never taken from the body; an edit
        discards the staged preview (FR-DAT-002: a preview expires when the source or mapping
        changes) and returns the batch to Draft."""
        if previous and previous["lifecycle_state"] not in {"Draft", "Previewed"}:
            raise DomainError("INVALID_STATE", 409)
        base = {k: v for k, v in (previous["payload"] if previous else {}).items() if k not in SERVER_FIELDS}
        merged = {**base, **data}
        merged.setdefault("mode", "APPEND")
        merged.setdefault("date_pattern", "ISO_8601")
        content = merged.get("content")
        changed = not previous or content != previous["payload"].get("content")
        stamped = {
            **merged,
            "source_namespace": NAMESPACE,
            "content_sha256": hashlib.sha256(content.encode()).hexdigest() if content else None,
            "received_at": datetime.now(timezone.utc).isoformat()
            if changed
            else previous["payload"].get("received_at"),
            "preview": None,
            "committed": None,
            "cancel_reason": None,
        }
        if stamped["content_sha256"] is None:
            stamped.pop("content_sha256")
        if merged.get("programme_id"):
            load(c, ctx, merged["programme_id"], "Programme", "programmes.read")
        if merged.get("period_id"):
            load(c, ctx, merged["period_id"], "Period", "periods.read")
        if merged.get("mapping"):
            self.columns(merged["mapping"])
        return write(c, ctx, "ImportJob", stamped, "Draft", previous)

    @staticmethod
    def columns(mapping):
        names = (
            [mapping["unit_column"]]
            + ([mapping["event_at_column"]] if mapping.get("event_at_column") else [])
            + [b["column"] for b in mapping["columns"]]
            + [d["column"] for d in mapping.get("dimension_columns") or []]
        )
        if len(set(names)) != len(names):
            raise fail("MAPPING_COLUMN_DUPLICATE")
        codes = [d["dimension_code"] for d in mapping.get("dimension_columns") or []]
        if len(set(codes)) != len(codes):
            raise fail("MAPPING_DIMENSION_INVALID")
        return names

    # Staging ------------------------------------------------------------------------------------
    def bindings(self, c, ctx, payload):
        """Each mapped indicator with its pinned definition and value roles. The mapping is refused as
        a whole (nothing is staged) when an indicator is outside the batch's programme, not active,
        not a manual measure of a supported type, bound with the wrong roles, or stated in a unit
        other than its definition's."""
        from .service import revision

        bound = {}
        for binding in payload["mapping"]["columns"]:
            bound.setdefault(binding["indicator_id"], {})
            if binding["value_role"] in bound[binding["indicator_id"]]:
                raise fail("MAPPING_ROLE_INVALID")
            bound[binding["indicator_id"]][binding["value_role"]] = binding
        result = {}
        for indicator_id, roles in bound.items():
            instance = load(c, ctx, indicator_id, "IndicatorInstance", "indicator-instances.read")
            if instance["payload"].get("programme_id") != payload["programme_id"]:
                raise fail("MAPPING_INDICATOR_INVALID")
            if instance["lifecycle_state"] != "Active":
                raise DomainError("INVALID_STATE", 409, reason="ACTIVE_MEASUREMENT_REQUIRED")
            definition = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )["payload"]
            kind = definition.get("measurement_type")
            if definition.get("source_mode") != "MANUAL" or kind not in SUPPORTED:
                raise fail("MAPPING_INDICATOR_INVALID")
            expected = {"NUMERATOR", "DENOMINATOR"} if kind in RATIO_TYPES else {"VALUE"}
            if set(roles) != expected:
                raise fail("MAPPING_ROLE_INVALID")
            for binding in roles.values():
                if binding["unit"] != definition.get("unit"):
                    raise fail("MAPPING_UNIT_MISMATCH")
                low, high = binding.get("minimum"), binding.get("maximum")
                if low is not None and high is not None and Decimal(low) > Decimal(high):
                    raise fail("MAPPING_RANGE_INVALID")
            result[indicator_id] = (definition, roles)
        declared = {
            d["code"]
            for definition, _ in result.values()
            for d in (definition.get("disaggregation") or {}).get("dimensions", [])
        }
        for dim in payload["mapping"].get("dimension_columns") or []:
            if dim["dimension_code"] not in declared:
                raise fail("MAPPING_DIMENSION_INVALID")
        return result

    def history(self, c, ctx, indicator_id):
        """Recent approved PRESENT values of one indicator for the anomaly check; None when the caller
        cannot read every observation (the check is then not evaluated, never approximated)."""
        if not any(
            g["capability"] == "observations.read" and g["scope_type"] == "TENANT" and g["purpose"] is None
            for g in ctx.grants
        ):
            return None
        rows = c.execute(
            "SELECT o.value FROM impact.observation_current o JOIN impact.object_registry r ON r.tenant_id=o.tenant_id AND r.object_id=o.object_id "
            "WHERE o.tenant_id=%s AND o.indicator_id=%s AND o.value_state='PRESENT' AND o.approval_state='APPROVED' AND o.value IS NOT NULL AND r.classification<>'RESTRICTED' "
            "ORDER BY o.event_at DESC, o.object_id LIMIT %s",
            (ctx.tenant_id, indicator_id, ANOMALY["history_limit"]),
        ).fetchall()
        return [Decimal(r["value"]) for r in rows]

    def duplicate(self, c, ctx, indicator_id, period, unit):
        """Why this unit's value for this indicator and period already exists, or None: an earlier
        import registered it, or a form response for the same unit and indicator with an event in the
        period was recorded."""
        if c.execute(
            "SELECT 1 FROM impact.import_unit_register WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s AND unit_key=%s",
            (ctx.tenant_id, indicator_id, period["object_id"], unit),
        ).fetchone():
            return "DUPLICATE_UNIT_PERIOD"
        if c.execute(
            "SELECT 1 FROM impact.observation_current o JOIN impact.object_registry r ON r.tenant_id=o.tenant_id AND r.object_id=o.object_id "
            "WHERE o.tenant_id=%s AND o.source_namespace='FORM' AND o.source_key=%s AND o.event_at>=%s AND o.event_at<%s AND r.lifecycle_state<>'Rejected'",
            (
                ctx.tenant_id,
                unit + "/" + indicator_id,
                period["payload"]["starts_at"],
                period["payload"]["ends_at"],
            ),
        ).fetchone():
            return "DUPLICATE_SOURCE_KEY"
        return None

    def stage(self, c, ctx, payload):
        """The staged outcome of a batch: every data row classified, nothing written. Deterministic
        for the same source, mapping and database state, so commit can recompute and compare it."""
        if any(not payload.get(k) for k in ["format", "content", "programme_id", "period_id", "mapping"]):
            raise fail("IMPORT_INCOMPLETE")
        programme = load(c, ctx, payload["programme_id"], "Programme", "programmes.read")
        if programme["lifecycle_state"] != "Active":
            raise DomainError("INVALID_STATE", 409, reason="ACTIVE_MEASUREMENT_REQUIRED")
        period = load(c, ctx, payload["period_id"], "Period", "periods.read")
        state = self.service.periods.state(c, ctx, payload["programme_id"], payload["period_id"])
        if state["lifecycle_state"] != "Open":
            raise DomainError("INVALID_STATE", 409, reason="PERIOD_RESTATEMENT_REQUIRED")
        try:
            zone = ZoneInfo(period["payload"].get("reporting_zone") or "UTC")
        except (ZoneInfoNotFoundError, ValueError):
            zone = timezone.utc
        starts, ends = aware(period["payload"]["starts_at"]), aware(period["payload"]["ends_at"])
        mapping = payload["mapping"]
        self.columns(mapping)
        bound = self.bindings(c, ctx, payload)
        missing_codes = mapping.get("missing_codes") or {}
        sheet = parse(payload)
        rows = sheet.rows
        while rows and not any(cell.strip() for cell in rows[-1]):
            rows = rows[:-1]
        if not rows:
            raise fail("FILE_EMPTY")
        header = [h.strip() for h in rows[0]]
        if len(header) > MAX_COLUMNS:
            raise fail("FILE_TOO_WIDE")
        if any(not h for h in header) or len(set(header)) != len(header):
            raise fail("FILE_HEADER_INVALID")
        position = {h: i for i, h in enumerate(header)}
        mapped = self.columns(mapping)
        absent = [name for name in mapped if name not in position]
        if absent:
            # A renamed or missing column pauses the batch; values are never shifted (FR-DAT-002).
            raise fail(
                "MAPPING_COLUMN_MISSING",
                fields=[{"path": "mapping", "message": "Column not found: " + n[:100]} for n in absent[:20]],
            )
        data_rows = [(i + 1, r) for i, r in enumerate(rows[1:], start=1) if any(cell.strip() for cell in r)]
        if len(data_rows) > MAX_ROWS:
            raise fail("IMPORT_ROW_LIMIT", code="LIMIT_EXCEEDED")
        if len(data_rows) * len(bound) > MAX_OBSERVATIONS:
            raise fail("IMPORT_OBSERVATION_LIMIT", code="LIMIT_EXCEEDED")
        histories = {indicator: self.history(c, ctx, indicator) for indicator in bound}
        dims = {d["dimension_code"]: d["column"] for d in mapping.get("dimension_columns") or []}
        seen, staged = set(), []
        for number_, cells in data_rows:
            index = number_ - 1
            reasons, warnings, observations, anomalies = [], [], [], []
            if len(cells) != len(header):
                staged.append(
                    {
                        "row_number": number_,
                        "row_key": None,
                        "outcome": "QUARANTINED",
                        "reasons": ["ROW_SHAPE_INVALID"],
                        "warnings": [],
                    }
                )
                continue
            raw = {name: cells[position[name]] for name in mapped}
            if any(len(v) > MAX_CELL for v in raw.values()):
                reasons.append("CELL_TOO_LONG")
            if any((index, position[name]) in sheet.formulas for name in mapped):
                reasons.append("FORMULA_NOT_PERMITTED")
            unit = raw[mapping["unit_column"]].strip()
            if not unit:
                reasons.append("UNIT_KEY_MISSING")
            elif not UNIT_KEY.fullmatch(unit):
                reasons.append("UNIT_KEY_INVALID")
            event_at = starts
            if mapping.get("event_at_column"):
                column = mapping["event_at_column"]
                text = raw[column].strip()
                try:
                    if not text:
                        raise fail("EVENT_AT_MISSING")
                    event_at = interpret_date(
                        text,
                        payload.get("date_pattern"),
                        zone,
                        serial=(index, position[column]) in sheet.numeric,
                    )
                    if not starts <= event_at < ends:
                        reasons.append("EVENT_OUTSIDE_PERIOD")
                except DomainError as e:
                    reasons.append(e.reason)
                    event_at = None
            values = {code: raw[column].strip() for code, column in dims.items() if raw[column].strip()}
            for indicator, (definition, roles) in bound.items():
                try:
                    cells_ = {role: raw[b["column"]] for role, b in roles.items()}
                    measured = measure(definition, roles, cells_, missing_codes)
                except DomainError as e:
                    reasons.append(e.reason)
                    continue
                declared = {d["code"] for d in (definition.get("disaggregation") or {}).get("dimensions", [])}
                measured["dimension_values"] = {k: v for k, v in values.items() if k in declared}
                try:
                    validate_dimensions(definition, measured)
                except DomainError:
                    reasons.append("DIMENSION_INVALID")
                    continue
                observations.append({"indicator_id": indicator, **measured})
            outcome = "QUARANTINED" if reasons else "ACCEPTED"
            if not reasons:
                found = (
                    ["DUPLICATE_IN_BATCH"]
                    if unit in seen
                    else sorted(
                        {
                            r
                            for o in observations
                            if (r := self.duplicate(c, ctx, o["indicator_id"], period, unit))
                        }
                    )
                )
                if found:
                    outcome, reasons = "DUPLICATE", found
                else:
                    seen.add(unit)
                    for o in observations:
                        history = histories[o["indicator_id"]]
                        if o["value_state"] != "PRESENT" or history is None:
                            continue
                        finding = robust_outlier(Decimal(o["value"]), history)
                        if finding:
                            anomalies.append(
                                {"indicator_id": o["indicator_id"], "value": o["value"], **finding}
                            )
                    if anomalies:
                        warnings.append("ANOMALY_ROBUST_OUTLIER")
            staged.append(
                {
                    "row_number": number_,
                    "row_key": unit or None,
                    "outcome": outcome,
                    "reasons": sorted(set(reasons)),
                    "warnings": warnings,
                    "raw": raw,
                    "event_at": event_at.isoformat().replace("+00:00", "Z") if event_at else None,
                    "observations": observations if outcome == "ACCEPTED" else [],
                    "anomalies": anomalies,
                }
            )
        accepted = [r for r in staged if r["outcome"] == "ACCEPTED"]
        preview = {
            "rule_set": RULE_SET,
            "anomaly_method": {
                **ANOMALY,
                "evaluated_indicators": sorted(i for i, h in histories.items() if h is not None),
            },
            "header": header,
            "dropped_columns": [h for h in header if h not in mapped],
            "blank_rows": len(rows) - 1 - len(data_rows),
            "counts": {
                "rows": len(staged),
                "accepted": len(accepted),
                "quarantined": sum(r["outcome"] == "QUARANTINED" for r in staged),
                "duplicate": sum(r["outcome"] == "DUPLICATE" for r in staged),
                "warnings": sum(bool(r["warnings"]) for r in accepted),
                "observations": sum(len(r["observations"]) for r in accepted),
            },
            "rows": staged,
        }
        fingerprint = {
            "content_sha256": hashlib.sha256(payload["content"].encode()).hexdigest(),
            "mapping": mapping,
            "programme_id": payload["programme_id"],
            "period_id": payload["period_id"],
            "date_pattern": payload.get("date_pattern"),
            "atomic": payload.get("atomic", False),
            "preview": preview,
        }
        preview["preview_hash"] = hashlib.sha256(canonical(fingerprint)).hexdigest()
        return preview, period

    def preview(self, c, ctx, row):
        if row["lifecycle_state"] not in {"Draft", "Previewed"}:
            raise DomainError("INVALID_STATE", 409)
        staged, _ = self.stage(c, ctx, row["payload"])
        staged.update(previewed_at=datetime.now(timezone.utc).isoformat(), previewed_by=ctx.principal_id)
        return write(
            c, ctx, "ImportJob", {**row["payload"], "preview": staged}, "Previewed", row, track_author=False
        )

    def cancel(self, c, ctx, row, data):
        """Cancel a batch that was never committed. Nothing was written, so nothing is rolled back."""
        if row["lifecycle_state"] not in {"Draft", "Previewed"}:
            raise DomainError("INVALID_STATE", 409)
        payload = {**row["payload"], "cancel_reason": data["reason"]}
        return write(c, ctx, "ImportJob", payload, "Cancelled", row, track_author=False)

    # Commit -------------------------------------------------------------------------------------
    def commit(self, c, ctx, row, data, correlation=None):
        if row["lifecycle_state"] != "Previewed":
            raise DomainError("INVALID_STATE", 409)
        if not any(
            g["capability"] == "observation.submit" and g["scope_type"] == "TENANT" and g["purpose"] is None
            for g in ctx.grants
        ):
            # A commit creates observations and submits them for review, so the committer must hold
            # what a manual observation submit needs (declared in the policy row).
            raise DomainError("POLICY_DENIED", 403, reason="OBSERVATION_SUBMIT_REQUIRED")
        payload = row["payload"]
        if data["preview_hash"] != payload["preview"]["preview_hash"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="PREVIEW_HASH_MISMATCH")
        staged, period = self.stage(c, ctx, payload)
        if staged["preview_hash"] != payload["preview"]["preview_hash"]:
            # Something the outcome depends on changed since preview (for example another batch now
            # holds a unit): the batch must be previewed again before anything is written.
            raise DomainError("INVALID_STATE", 409, reason="PREVIEW_STALE")
        counts = staged["counts"]
        if payload.get("atomic") and counts["accepted"] != counts["rows"]:
            raise fail("IMPORT_ATOMIC_REJECTED")
        if counts["warnings"] and not data.get("accept_warnings"):
            raise fail("WARNINGS_NOT_ACCEPTED")
        if not counts["accepted"]:
            raise fail("IMPORT_NOTHING_TO_COMMIT")
        reporting_zone = period["payload"].get("reporting_zone") or "UTC"
        registered = []
        ids = []
        rows = []
        for staged_row in payload["preview"]["rows"]:
            if staged_row["outcome"] != "ACCEPTED":
                rows.append(staged_row)
                continue
            produced = []
            for o in staged_row["observations"]:
                observation = {
                    "source_namespace": NAMESPACE,
                    "source_key": str(row["object_id"])
                    + "/"
                    + staged_row["row_key"]
                    + "/"
                    + o["indicator_id"],
                    "indicator_id": o["indicator_id"],
                    "event_at": staged_row["event_at"],
                    "captured_at": payload["received_at"],
                    "capture_zone": reporting_zone,
                    "source_version": str(row["head_revision"]),
                    "value_state": o["value_state"],
                    "value": o.get("value"),
                    "dimension_values": o.get("dimension_values") or {},
                }
                if o.get("numerator") is not None:
                    observation.update(numerator=o["numerator"], denominator=o["denominator"])
                observation_id = self.service.forms.record(
                    c,
                    ctx,
                    observation,
                    data["workflow_version"],
                    correlation,
                    row["object_id"],
                    op="action_imports_commit",
                )
                ids.append(observation_id)
                produced.append({**o, "observation_id": observation_id})
                registered.append(
                    (o["indicator_id"], staged_row["row_key"], observation_id, staged_row["row_number"])
                )
            rows.append({**staged_row, "observations": produced})
        now = datetime.now(timezone.utc)
        receipt = write(
            c,
            ctx,
            "ImportJob",
            {
                **payload,
                "preview": {**payload["preview"], "rows": rows},
                "committed": {
                    "committed_at": now.isoformat(),
                    "committed_by": ctx.principal_id,
                    "preview_hash": staged["preview_hash"],
                    "observation_ids": ids,
                    "accepted_warnings": bool(counts["warnings"]),
                },
            },
            "Committed",
            row,
            track_author=False,
        )
        for indicator, unit, observation_id, number_ in registered:
            c.execute(
                "INSERT INTO impact.import_unit_register(tenant_id,indicator_id,period_id,unit_key,observation_id,import_id,import_revision,row_number,registered_by,registered_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    indicator,
                    payload["period_id"],
                    unit,
                    observation_id,
                    str(row["object_id"]),
                    receipt["revision_id"],
                    number_,
                    ctx.principal_id,
                    now,
                ),
            )
        return receipt
