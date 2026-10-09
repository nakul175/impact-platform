"""VF-DIN-001 golden corpus and reconciliation harness.

Every vector in qualification/golden/calculation-corpus-v1.json is evaluated three ways and all three
must agree exactly (raw stored decimal string and displayed string, per total and per category):

1. `reference()` below: an independent exact-rational implementation (fractions.Fraction, explicit
   half-away-from-zero rounding) written from the FSD text. It shares no code with impact_api.
2. The domain path: impact_api.domain.calculate/disaggregate and measurement.coverage.
3. The live path: definition, independent approval, indicator, collection plan, activation,
   observations with independent approvals, then the calculate action through the HTTP API.

The reference is also checked against the hand-prepared expected values, so a vector that the platform
and the reference both get wrong still fails. Results are written to docs/evidence/golden-reconciliation.json.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads((ROOT / "qualification/golden/calculation-corpus-v1.json").read_text())
VECTORS = CORPUS["vectors"]
EVIDENCE = ROOT / "docs/evidence/golden-reconciliation.json"
OUTCOMES = {}
RESULT_KEYS = ["value_state", "value", "numerator", "denominator", "displayed_value", "reason_code"]


# ---------------------------------------------------------------- independent reference implementation


def exact(text):
    return Fraction(text)


def round_half_up(q, places):
    """Nearest multiple of 10**-places; exact halves move away from zero."""
    scale = 10**places
    magnitude = abs(q) * scale
    whole = magnitude.numerator // magnitude.denominator
    if magnitude - whole >= Fraction(1, 2):
        whole += 1
    return (-1 if q < 0 else 1) * whole, scale


def render(units, scale, places, trim):
    sign = "-" if units < 0 else ""
    units = abs(units)
    digits = str(units).rjust(places + 1, "0")
    text = digits[: len(digits) - places] + ("." + digits[len(digits) - places :] if places else "")
    if trim and "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if units == 0 and trim else (sign if units else "") + text


def stored_text(q):
    units, scale = round_half_up(q, 12)
    text = render(units, scale, 12, trim=True)
    if len(text.lstrip("-").split(".")[0]) > 26:
        raise OverflowError
    return text


def shown_text(q, places):
    units, scale = round_half_up(q, places)
    return render(units, scale, places, trim=False)


def when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def reference(vector):
    d = vector["definition"]
    period = CORPUS["period"]
    if any(when(o["event_at"]).tzinfo is None for o in vector["observations"]):
        # An instant without an offset has no period membership or order; it is invalid input.
        return {"error": "VALIDATION_FAILED", "reason_code": "TIMESTAMP_OFFSET_REQUIRED"}
    start, end = when(period["starts_at"]), when(period["ends_at"])
    rows = [o for o in vector["observations"] if start <= when(o["event_at"]) < end]
    places = d["display_decimals"]

    def evaluate(rows):
        used = [o for o in rows if o["approval"] == "APPROVED" and o["value_state"] == "PRESENT"]
        out = dict.fromkeys(RESULT_KEYS)
        out.update(value_state="UNDEFINED", displayed_value="Undefined", reason_code="NO_APPROVED_VALUES")
        if not used:
            return out
        pct = d["measurement_type"] == "PERCENTAGE"
        mult = 100 if pct else 1
        method = d["combination_rule"]

        def pair(o):
            n, den = exact(o["numerator"]), exact(o["denominator"])
            if n < 0 or den < 0 or (pct and n > den):
                raise ValueError("INCOMPATIBLE_MEASURE")
            return n, den

        if method == "POOLED_RATIO":
            pairs = [pair(o) for o in used]
            n, den = sum(p[0] for p in pairs), sum(p[1] for p in pairs)
            out.update(numerator=stored_text(n), denominator=stored_text(den))
            if den == 0:
                out["reason_code"] = "ZERO_DENOMINATOR"
                return out
            value = n / den * mult
        elif method == "LAST_VALID":
            latest = max(when(o["event_at"]) for o in used)
            ratio = d["measurement_type"] in {"RATIO", "PERCENTAGE"}
            key = (lambda o: pair(o)) if ratio else (lambda o: (exact(o["value"]),))
            last = {key(o) for o in used if when(o["event_at"]) == latest}
            if len(last) > 1:
                out["reason_code"] = "TIED_LATEST_VALUES"
                return out
            if d["time_semantic"] == "CUMULATIVE":
                series = [key(o) for o in sorted(used, key=lambda o: when(o["event_at"]))]
                for a, b in zip(series, series[1:]):
                    if any(y < x for x, y in zip(a, b)):
                        out["reason_code"] = "CUMULATIVE_DECLINE"
                        return out
            (chosen,) = last
            if ratio:
                out.update(numerator=stored_text(chosen[0]), denominator=stored_text(chosen[1]))
                if chosen[1] == 0:
                    out["reason_code"] = "ZERO_DENOMINATOR"
                    return out
                value = chosen[0] / chosen[1] * mult
            else:
                value = chosen[0]
        elif method == "MEAN" and d["measurement_type"] in {"RATIO", "PERCENTAGE"}:
            pairs = [pair(o) for o in used]
            if any(den == 0 for _, den in pairs):
                out["reason_code"] = "ZERO_DENOMINATOR"
                return out
            value = sum(n / den * mult for n, den in pairs) / len(pairs)
        else:
            xs = sorted(exact(o["value"]) for o in used)
            if method == "SUM":
                value = sum(xs)
            elif method == "COUNT":
                if any(x != 1 for x in xs):
                    raise ValueError("INCOMPATIBLE_MEASURE")
                value = Fraction(len(xs))
            elif method == "MEAN":
                value = sum(xs) / len(xs)
            elif method == "MEDIAN":
                k = len(xs) // 2
                value = xs[k] if len(xs) % 2 else (xs[k - 1] + xs[k]) / 2
            elif method == "MIN":
                value = xs[0]
            else:
                value = xs[-1]
        out.update(
            value_state="PRESENT",
            value=stored_text(value),
            # Displayed from the stored 12-place decimal, the value every artifact exports.
            displayed_value=shown_text(Fraction(stored_text(value)), places),
            reason_code="CALCULATED",
        )
        return out

    try:
        result = evaluate(rows)
    except OverflowError:
        return {"error": "VALIDATION_FAILED", "reason_code": "NUMERIC_OVERFLOW"}
    except ValueError as exc:
        return {"error": str(exc)}
    breakdown = []
    for dim in (d.get("disaggregation") or {}).get("dimensions", []):
        codes = [c["code"] for c in dim["categories"]] + ([] if dim["exhaustive"] else ["UNSPECIFIED"])
        additive = not dim["multiselect"] and d["combination_rule"] in {"SUM", "COUNT"}
        for code in codes:

            def member(o):
                raw = (o.get("dimension_values") or {}).get(dim["code"])
                return (code == "UNSPECIFIED" and not raw) or (bool(raw) and code in raw.split("|"))

            subset = [o for o in rows if member(o)]
            breakdown.append(
                {
                    "dimension": dim["code"],
                    "dimension_version": dim["version"],
                    "category": code,
                    "additivity": "ADDITIVE" if additive else "NONADDITIVE",
                    "contributor_count": sum(
                        o["approval"] == "APPROVED" and o["value_state"] == "PRESENT" for o in subset
                    ),
                    **evaluate(subset),
                }
            )
    if breakdown:
        result["disaggregation"] = breakdown
    return result


def comparable(result):
    if "error" in result:
        return {k: result[k] for k in ["error", "reason_code"] if k in result}
    out = {k: result.get(k) for k in RESULT_KEYS}
    if result.get("disaggregation"):
        out["disaggregation"] = [
            {
                k: e.get(k)
                for k in ["dimension", "dimension_version", "category", "additivity", "contributor_count"]
            }
            | {k: e.get(k) for k in RESULT_KEYS}
            for e in result["disaggregation"]
        ]
    return out


def expected(vector):
    return comparable(vector["expected"])


def record(vector, path, outcome):
    OUTCOMES.setdefault(vector["id"], {"fsd": vector["fsd"], "category": vector["category"]})[path] = outcome


@pytest.fixture(scope="module", autouse=True)
def evidence():
    started = time.monotonic()
    yield
    if not any("live" in outcome for outcome in OUTCOMES.values()):
        # A run without the live API (make unit) must not overwrite the tracked evidence with a partial one.
        return
    rows = [{"id": v["id"], **OUTCOMES.get(v["id"], {})} for v in VECTORS]
    summary = {
        path: {
            "passed": sum(r.get(path) == "PASS" for r in rows),
            "failed": sum(r.get(path) == "FAIL" for r in rows),
            "not_run": sum(r.get(path) is None for r in rows),
        }
        for path in ["reference", "domain", "live"]
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(
            {
                "corpus": CORPUS["corpus"],
                "corpus_version": CORPUS["corpus_version"],
                "vector_count": len(VECTORS),
                "live_vector_count": sum("live" in v["paths"] for v in VECTORS),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": round(time.monotonic() - started, 1),
                "summary": summary,
                "vectors": rows,
            },
            indent=2,
        )
        + "\n"
    )


IDS = [v["id"] for v in VECTORS]


@pytest.mark.parametrize("vector", VECTORS, ids=IDS)
def test_reference_matches_prepared_expectation(vector):
    ok = comparable(reference(vector)) == expected(vector)
    record(vector, "reference", "PASS" if ok else "FAIL")
    assert comparable(reference(vector)) == expected(vector)


# ------------------------------------------------------------------------------------------ domain path


def payloads(vector, keys=None):
    rows = []
    for i, o in enumerate(vector["observations"]):
        rows.append(
            {
                "source_namespace": "MANUAL",
                "source_key": (keys or {}).get(i, f"golden-{i}"),
                "event_at": o["event_at"],
                "value_state": o["value_state"],
                "value": o["value"],
                "numerator": o.get("numerator"),
                "denominator": o.get("denominator"),
                "dimension_values": o.get("dimension_values", {}),
                "approval_state": o["approval"],
            }
        )
    return rows


def definition_payload(vector):
    d = vector["definition"]
    ratio = d["measurement_type"] in {"RATIO", "PERCENTAGE"}
    return {
        "code": "G" + str(uuid.uuid4())[:8],
        "name": "Golden " + vector["id"],
        "unit": "percent" if d["measurement_type"] == "PERCENTAGE" else "units",
        "population": "Golden corpus population",
        "inclusion": "Every corpus contribution",
        "exclusion": "None",
        "method": "Golden corpus vector " + vector["id"],
        "source_mode": "MANUAL",
        **(
            {"numerator_meaning": "Eligible numerator", "denominator_meaning": "Eligible population"}
            if ratio
            else {}
        ),
        **d,
    }


def domain_result(vector):
    from impact_api.domain import DomainError, calculate, disaggregate

    d = definition_payload(vector)
    start, end = (when(CORPUS["period"][k]) for k in ["starts_at", "ends_at"])

    def inside(p):
        try:
            return start <= when(p["event_at"]) < end
        except TypeError:  # a naive instant is passed through so that the domain code must refuse it
            return True

    rows = [p for p in payloads(vector) if inside(p)]
    try:
        result = calculate(d, rows)
    except DomainError as exc:
        return {"error": exc.code, **({"reason_code": exc.reason} if exc.reason else {})}
    if d.get("disaggregation"):
        result["disaggregation"] = disaggregate(d, rows)
    return result


@pytest.mark.parametrize("vector", [v for v in VECTORS if "domain" in v["paths"]], ids=lambda v: v["id"])
def test_domain_reconciles_with_reference(vector):
    got, want = comparable(domain_result(vector)), comparable(reference(vector))
    record(vector, "domain", "PASS" if got == want else "FAIL")
    assert got == want


def test_domain_coverage_vector():
    from impact_api.measurement import coverage

    vector = next(v for v in VECTORS if "coverage" in v)
    d = definition_payload(vector)
    rows = [
        {"object_id": str(uuid.uuid4()), "head_revision": str(uuid.uuid4()), "payload": p}
        for p in payloads(vector)
    ]
    obligations = [
        {
            "label": f"P{i}",
            "source_namespace": "MANUAL",
            "source_key": f"golden-{i}",
            "due_at": "2026-09-01T00:00:00Z",
        }
        for i in range(len(rows) + vector["missing_obligations"])
    ]
    plan = {"head_revision": str(uuid.uuid4()), "payload": {"obligations": obligations}}
    measured, _ = coverage(plan, rows, d, datetime(2026, 9, 29, tzinfo=timezone.utc))
    assert {k: measured.get(k) for k in vector["coverage"]} == vector["coverage"]


# -------------------------------------------------------------------------------------------- live path


def live_result(live, vector):
    from test_measurement import action, approve, create, get, submit

    calendar = get(live, "reporting-calendars")["items"][0]
    geography = get(live, "geographies")["items"][0]
    programme = create(
        live,
        "programmes",
        {
            "code": "GLD",
            "title": "Golden " + vector["id"] + " " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2027-01-01T00:00:00Z",
            "reporting_calendar_id": calendar["object_id"],
            "geography_id": geography["object_id"],
        },
    )
    d = create(live, "indicator-definitions", definition_payload(vector))
    approve(live, submit(live, "indicator-definitions", d))
    d = get(live, "indicator-definitions", d["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": d["revision_id"],
            "local_applicability": "Golden corpus",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = get(live, "periods", live.records["period"]["object_id"])
    prefix = str(uuid.uuid4())
    keys = {
        i: f"{prefix}-{i}" for i in range(len(vector["observations"]) + vector.get("missing_obligations", 0))
    }
    plan = create(
        live,
        "collection-plans",
        {
            "title": "Golden collection",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": f"Contributor {i}",
                    "source_namespace": "MANUAL",
                    "source_key": k,
                    "due_at": "2026-09-01T00:00:00Z",
                }
                for i, k in keys.items()
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    indicator = get(live, "indicator-instances", indicator["object_id"])
    action(live, "programmes", programme, "ready")
    programme = get(live, "programmes", programme["object_id"])
    action(live, "programmes", programme, "activate")
    for payload in payloads(vector, keys):
        approval = payload.pop("approval_state")
        data = {k: v for k, v in payload.items() if v is not None or k == "value"} | {
            "indicator_id": indicator["object_id"],
            "captured_at": "2026-09-29T00:00:00Z",
            "capture_zone": "UTC",
            "source_version": "1",
        }
        row = create(live, "observations", data)
        if approval in {"SUBMITTED", "APPROVED"}:
            workflow = submit(live, "observations", row)
            if approval == "APPROVED":
                approve(live, workflow)
    response = live.request(
        live.path("indicator-instances", indicator["object_id"]) + "/actions/calculate",
        method="POST",
        body={
            "operation_id": str(uuid.uuid4()),
            "expected_revision": indicator["revision_id"],
            "data": {"period_id": period["object_id"]},
        },
    )
    if response.status_code != 200:
        body = response.json()
        return {
            "error": body["code"],
            **({"reason_code": body["reason_code"]} if body.get("reason_code") else {}),
        }, None
    return get(live, "calculated-results", response.json()["object_id"])["data"], d


@pytest.mark.parametrize("vector", [v for v in VECTORS if "live" in v["paths"]], ids=lambda v: v["id"])
def test_live_api_reconciles_with_reference(live, vector):
    result, _ = live_result(live, vector)
    got, want = comparable(result), comparable(reference(vector))
    extra = True
    if "coverage" in vector:
        extra = {k: result["coverage"].get(k) for k in vector["coverage"]} == vector["coverage"]
    if "limitation" in vector:
        extra = extra and vector["limitation"] in [x["code"] for x in result["limitations"]]
    record(vector, "live", "PASS" if got == want and extra else "FAIL")
    assert got == want and extra
