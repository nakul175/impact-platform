"""Results framework, targets, baselines and milestones (v0.18).

A framework is one governed object per programme version: typed nodes with stable identities, an
intended result level, an owner and the indicator instances placed on them. Targets, baselines and
milestones are governed objects per indicator instance and programme period. Both follow the
definition lifecycle (Draft -> Submitted/InReview -> Approved | Returned | Rejected; Approved ->
Superseded) through the single independent review stage of `Service.submit`/`Service.review`.
Approval appends a row to an insert-only register (`framework_baseline`, `target_binding`) that
names the approved revision and the revision it supersedes; nothing approved is re-pointed.

All writes run inside `Service.command`'s tenant lock and receipt transaction.
"""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext

from .domain import DomainError, decimal_value, stored
from .store import authorize, context, envelope, load, scopes, write

LEVELS = {"IMPACT": 4, "OUTCOME": 3, "OUTPUT": 2, "ACTIVITY": 1}
RESULT_LEVELS = {"IMPACT", "OUTCOME", "OUTPUT"}
# Structural invalidity is refused on every save and can never be excepted (FR-PLN-001/010).
STRUCTURAL = {
    "DUPLICATE_NODE_ID",
    "ORPHAN_PARENT",
    "CONTAINMENT_CYCLE",
    "LEVEL_ORDER",
    "INDICATOR_PROGRAMME_MISMATCH",
    "INDICATOR_LINKED_TWICE",
    "NODE_REFERENCED",
    "DUPLICATE_EXCEPTION",
}
PLANNING_KINDS = {"Framework", "Target"}
OPEN_PROGRAMME = {"Draft", "Ready", "Active"}
MAX_INDICATORS = 200


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def display(value, places):
    return format(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP), f".{places}f")


def slot(data):
    if data.get("target_basis") == "BASELINE":
        return "BASELINE"
    if data.get("target_kind") == "MILESTONE":
        return "MILESTONE:" + (data.get("milestone_label") or "")
    return "TARGET"


def structure_issues(nodes):
    """Pure structural and completeness rules over a node list (no database): returns issues as
    (severity, rule, object_id, message)."""
    issues = []
    by_id = {}
    for node in nodes:
        if node["node_id"] in by_id:
            issues.append(
                ("ERROR", "DUPLICATE_NODE_ID", node["node_id"], "Each node needs its own identity.")
            )
        by_id[node["node_id"]] = node
    for node in nodes:
        parent = node.get("parent_node_id")
        if parent is None:
            continue
        if parent == node["node_id"]:
            issues.append(("ERROR", "CONTAINMENT_CYCLE", node["node_id"], "A node cannot contain itself."))
        elif parent not in by_id:
            issues.append(
                ("ERROR", "ORPHAN_PARENT", node["node_id"], "The parent node is not part of this framework.")
            )
        elif LEVELS[by_id[parent]["node_type"]] < LEVELS[node["node_type"]]:
            issues.append(
                (
                    "ERROR",
                    "LEVEL_ORDER",
                    node["node_id"],
                    "A node cannot sit under a lower result level than its own.",
                )
            )
    for node in nodes:
        seen, current = {node["node_id"]}, node
        while current.get("parent_node_id") in by_id and current["parent_node_id"] != current["node_id"]:
            current = by_id[current["parent_node_id"]]
            if current["node_id"] in seen:
                issues.append(
                    ("ERROR", "CONTAINMENT_CYCLE", node["node_id"], "Containment must not form a cycle.")
                )
                break
            seen.add(current["node_id"])
    linked = set()
    for node in nodes:
        for indicator in node.get("indicator_ids", []):
            if indicator in linked:
                issues.append(
                    (
                        "ERROR",
                        "INDICATOR_LINKED_TWICE",
                        node["node_id"],
                        "An indicator is placed on one node only.",
                    )
                )
            linked.add(indicator)
    top = max((LEVELS[n["node_type"]] for n in nodes), default=0)
    for node in nodes:
        if not node.get("owner_id"):
            issues.append(("ERROR", "NODE_INCOMPLETE", node["node_id"], "Assign an owner to this node."))
        if node.get("parent_node_id") is None and LEVELS[node["node_type"]] < top:
            issues.append(
                (
                    "WARNING",
                    "ORPHAN_NODE",
                    node["node_id"],
                    "This node is not placed under a higher-level result.",
                )
            )
        if node["node_type"] in RESULT_LEVELS and not node.get("indicator_ids"):
            issues.append(
                (
                    "WARNING",
                    "UNMEASURED_RESULT",
                    node["node_id"],
                    "No indicator measures this result.",
                )
            )
    return issues


def progress(actual, target, baseline, places):
    """Target attainment per the declared direction (LLD: uncapped higher attainment, signed lower
    deviation, inclusive range bounds); zero or negative higher targets and zero baselines are
    undefined, never divided. Arithmetic uses stored decimals, never displayed values."""
    result = {
        "status": "NO_ACTUAL",
        "attainment_percent": None,
        "deviation": None,
        "displayed_deviation": None,
        "change_from_baseline": None,
        "change_from_baseline_percent": None,
        "reason_code": None,
    }
    value = (
        decimal_value(actual["value"])
        if actual.get("value_state") == "PRESENT" and actual.get("value") is not None
        else None
    )
    with localcontext() as c:
        c.prec = 60
        if value is not None and baseline and baseline.get("value_state") == "PRESENT":
            base = decimal_value(baseline["value"])
            result["change_from_baseline"] = stored(value - base)
            result["change_from_baseline_percent"] = (
                "Undefined" if base == 0 else display((value - base) / abs(base) * 100, 2)
            )
        if value is None:
            result["reason_code"] = "NO_PRESENT_ACTUAL" if actual.get("mode") != "NONE" else "NO_RESULT"
            return result
        if target is None:
            return {**result, "status": "NO_TARGET", "reason_code": "NO_APPROVED_TARGET"}
        if target.get("value_state") != "PRESENT":
            return {**result, "status": "NO_TARGET", "reason_code": "TARGET_" + target["value_state"]}
        kind, direction = target["target_kind"], target["direction"]
        if kind == "MILESTONE":
            return {**result, "status": "ASSESSMENT_REQUIRED", "reason_code": "MILESTONE_ASSESSMENT"}
        if kind == "RANGE":
            low, high = decimal_value(target["low"]), decimal_value(target["high"])
            deviation = value - low if value < low else value - high if value > high else Decimal(0)
            status = "BELOW_RANGE" if value < low else "ABOVE_RANGE" if value > high else "WITHIN_RANGE"
        else:
            goal = decimal_value(target["value"])
            deviation = value - goal
            if direction == "HIGHER":
                status = "ACHIEVED" if value >= goal else "BELOW_TARGET"
                if goal > 0:
                    result["attainment_percent"] = display(value / goal * 100, 2)
                else:
                    result["attainment_percent"] = "Undefined"
                    result["reason_code"] = "ZERO_TARGET" if goal == 0 else "NON_POSITIVE_TARGET"
            else:
                status = "ACHIEVED" if value <= goal else "ABOVE_TARGET"
        result.update(
            status=status,
            deviation=stored(deviation),
            displayed_deviation=display(deviation, places),
        )
        return result


class Planning:
    def __init__(self, service):
        self.service = service

    # Registers ---------------------------------------------------------------------------------
    def baseline(self, c, ctx, programme_id, at=None):
        return c.execute(
            "SELECT * FROM impact.framework_baseline WHERE tenant_id=%s AND programme_id=%s"
            + (" AND approved_at<=%s" if at else "")
            + " ORDER BY baseline_version DESC LIMIT 1",
            (ctx.tenant_id, str(programme_id), *([at] if at else [])),
        ).fetchone()

    def binding(self, c, ctx, indicator_id, period_id, target_slot):
        return c.execute(
            "SELECT * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s AND slot=%s ORDER BY binding_version DESC LIMIT 1",
            (ctx.tenant_id, str(indicator_id), str(period_id), target_slot),
        ).fetchone()

    def programme(self, c, ctx, programme_id):
        programme = load(c, ctx, programme_id, "Programme", "programmes.read")
        if programme["lifecycle_state"] not in OPEN_PROGRAMME:
            raise DomainError("INVALID_STATE", 409, reason="PROGRAMME_CONFIGURATION_FROZEN")
        return programme

    # Frameworks ---------------------------------------------------------------------------------
    def framework_issues(self, c, ctx, data, owner_id=None):
        from .service import revision

        nodes = data.get("nodes", [])
        found = list(structure_issues(nodes))
        by_id = {n["node_id"]: n for n in nodes}
        programme_id = data.get("programme_id")
        for node in nodes:
            for indicator in node.get("indicator_ids", []):
                row = load(c, ctx, indicator, "IndicatorInstance", "indicator-instances.read")
                if programme_id and row["payload"].get("programme_id") != programme_id:
                    found.append(
                        (
                            "ERROR",
                            "INDICATOR_PROGRAMME_MISMATCH",
                            node["node_id"],
                            "Only indicators of this programme can be placed on its framework.",
                        )
                    )
            if node.get("owner_id") and not self.service.measurement.principal(c, ctx, node["owner_id"]):
                found.append(
                    ("ERROR", "OWNER_INELIGIBLE", node["node_id"], "The node owner must be an active member.")
                )
        base = None
        if data.get("supersedes_revision"):
            previous = revision(c, ctx, data["supersedes_revision"], "Framework", "frameworks.read")
            register = c.execute(
                "SELECT * FROM impact.framework_baseline WHERE tenant_id=%s AND framework_revision=%s",
                (ctx.tenant_id, data["supersedes_revision"]),
            ).fetchone()
            if not register or str(register["programme_id"]) != programme_id:
                raise DomainError("INVALID_STATE", 409, reason="FRAMEWORK_BASELINE_REQUIRED")
            base = {**register, "payload": previous["payload"]}
            for old in previous["payload"].get("nodes", []):
                if old.get("indicator_ids") and old["node_id"] not in by_id:
                    found.append(
                        (
                            "ERROR",
                            "NODE_REFERENCED",
                            old["node_id"],
                            "A node that places indicators in the approved baseline cannot be deleted.",
                        )
                    )
        if programme_id:
            placed = {i for n in nodes for i in n.get("indicator_ids", [])}
            rows = c.execute(
                "SELECT object_id FROM impact.indicator_instance_current WHERE tenant_id=%s AND programme_id=%s ORDER BY object_id LIMIT %s",
                (ctx.tenant_id, programme_id, MAX_INDICATORS + 1),
            ).fetchall()
            if len(rows) > MAX_INDICATORS:
                raise DomainError("LIMIT_EXCEEDED", 422)
            for row in rows:
                if str(row["object_id"]) not in placed and scopes(
                    c, ctx, "indicator-instances.read", row["object_id"]
                ):
                    found.append(
                        (
                            "WARNING",
                            "ORPHAN_INDICATOR",
                            str(row["object_id"]),
                            "This programme indicator is not placed on any framework node.",
                        )
                    )
        exceptions = {}
        for item in data.get("exceptions", []):
            key = (item["object_id"], item["rule"])
            if key in exceptions:
                found.append(
                    ("ERROR", "DUPLICATE_EXCEPTION", item["object_id"], "Record one exception per issue.")
                )
            exceptions[key] = item
        issues, used = [], set()
        for severity, rule, obj, message in found:
            key = (obj, rule)
            exception = exceptions.get(key) if severity == "WARNING" else None
            if exception:
                used.add(key)
            node = by_id.get(obj)
            issues.append(
                {
                    "severity": severity,
                    "rule": rule,
                    "object_id": obj,
                    "message": message,
                    "resolver_id": (node or {}).get("owner_id") or owner_id,
                    "exceptable": severity == "WARNING",
                    "excepted": bool(exception),
                    "exception": exception,
                }
            )
        for key, item in exceptions.items():
            if key not in used:
                issues.append(
                    {
                        "severity": "ERROR",
                        "rule": "EXCEPTION_NOT_APPLICABLE",
                        "object_id": item["object_id"],
                        "message": "This exception does not match a current warning.",
                        "resolver_id": owner_id,
                        "exceptable": False,
                        "excepted": False,
                        "exception": item,
                    }
                )
        empty = not nodes
        return issues, base, empty

    def validate_framework(self, c, ctx, data, complete=False, owner_id=None):
        if data.get("programme_id"):
            self.programme(c, ctx, data["programme_id"])
        issues, base, empty = self.framework_issues(c, ctx, data, owner_id)
        structural = [i for i in issues if i["rule"] in STRUCTURAL]
        if structural:
            raise DomainError(
                "VALIDATION_FAILED",
                reason=structural[0]["rule"],
                fields=[{"path": "nodes." + i["object_id"], "message": i["rule"]} for i in structural[:20]],
            )
        if data.get("programme_id"):
            current = self.baseline(c, ctx, data["programme_id"])
            if base is None and current:
                raise DomainError("INVALID_STATE", 409, reason="FRAMEWORK_BASELINE_EXISTS")
            if base is not None and str(current["framework_revision"]) != data["supersedes_revision"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="FRAMEWORK_BASELINE_CHANGED")
        if base is not None and data.get("effective_from"):
            if instant(data["effective_from"]) <= base["effective_from"]:
                raise DomainError("VALIDATION_FAILED", reason="EFFECTIVE_DATE_ORDER")
        if complete:
            if any(not data.get(k) for k in ["programme_id", "version_label", "effective_from"]) or empty:
                raise DomainError("VALIDATION_FAILED", reason="SUBMISSION_INCOMPLETE")
            blocking = [i for i in issues if i["severity"] == "ERROR" or not i["excepted"]]
            if blocking:
                raise DomainError(
                    "VALIDATION_FAILED",
                    reason="FRAMEWORK_INCOMPLETE",
                    fields=[{"path": "nodes." + i["object_id"], "message": i["rule"]} for i in blocking[:20]],
                )
        return issues, base

    def completeness(self, c, ctx, row):
        data = row["payload"]
        issues, base, empty = self.framework_issues(c, ctx, data, str(row["owner_id"]))
        if empty:
            issues.insert(
                0,
                {
                    "severity": "ERROR",
                    "rule": "EMPTY_FRAMEWORK",
                    "object_id": str(row["object_id"]),
                    "message": "Add at least one result node.",
                    "resolver_id": str(row["owner_id"]),
                    "exceptable": False,
                    "excepted": False,
                    "exception": None,
                },
            )
        comparison = None
        if base:
            old = {n["node_id"]: n for n in base["payload"].get("nodes", [])}
            new = {n["node_id"]: n for n in data.get("nodes", [])}
            changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
            affected = set()
            for key in set(old) ^ set(new) | set(changed):
                for side in (old, new):
                    affected.update(side.get(key, {}).get("indicator_ids", []))
            comparison = {
                "base_revision": str(base["framework_revision"]),
                "base_version": base["baseline_version"],
                "added": sorted(set(new) - set(old)),
                "removed": sorted(set(old) - set(new)),
                "changed": changed,
                "affected_indicator_ids": sorted(affected),
            }
        return {
            "framework_id": str(row["object_id"]),
            "revision_id": str(row["head_revision"]),
            "ready": not any(i["severity"] == "ERROR" or not i["excepted"] for i in issues),
            "issues": issues,
            "comparison": comparison,
        }

    # Targets ------------------------------------------------------------------------------------
    def validate_target(self, c, ctx, data, complete=False):
        from .service import revision

        indicator = (
            load(c, ctx, data["indicator_id"], "IndicatorInstance", "indicator-instances.read")
            if data.get("indicator_id")
            else None
        )
        programme = self.programme(c, ctx, indicator["payload"]["programme_id"]) if indicator else None
        period = load(c, ctx, data["period_id"], "Period", "periods.read") if data.get("period_id") else None
        if indicator and period:
            p = programme["payload"]
            calendar = c.execute(
                "SELECT object_id FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s AND object_type='ReportingCalendar' AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, period["payload"].get("calendar_version")),
            ).fetchone()
            if not calendar or str(calendar["object_id"]) != p.get("reporting_calendar_id"):
                raise DomainError("VALIDATION_FAILED", reason="PERIOD_NOT_IN_PROGRAMME_CALENDAR")
            if (
                not p.get("starts_at")
                or not p.get("ends_at")
                or instant(period["payload"]["starts_at"]) < instant(p["starts_at"])
                or instant(period["payload"]["ends_at"]) > instant(p["ends_at"])
            ):
                raise DomainError("VALIDATION_FAILED", reason="PERIOD_OUTSIDE_PROGRAMME")
            state = self.service.periods.state(c, ctx, str(programme["object_id"]), str(period["object_id"]))
            if state["lifecycle_state"] != "Open":
                # A new or revised target never changes a frozen period (FR-IND-004); restated
                # comparisons are not implemented.
                raise DomainError("INVALID_STATE", 409, reason="PERIOD_LOCKED")
        kind, direction, basis = data.get("target_kind"), data.get("direction"), data.get("target_basis")
        allowed = {"VALUE": {"HIGHER", "LOWER"}, "RANGE": {"RANGE"}, "MILESTONE": {"MILESTONE"}}
        if kind and direction and direction not in allowed[kind]:
            raise DomainError("VALIDATION_FAILED", reason="DIRECTION_KIND_MISMATCH")
        if basis == "BASELINE" and kind and kind != "VALUE":
            raise DomainError("VALIDATION_FAILED", reason="BASELINE_REQUIRES_VALUE")
        present = data.get("value_state") == "PRESENT"
        if kind == "RANGE":
            if data.get("value") is not None:
                raise DomainError("VALIDATION_FAILED", reason="RANGE_USES_BOUNDS")
            if present and (data.get("low") is None or data.get("high") is None) and complete:
                raise DomainError("VALIDATION_FAILED", reason="RANGE_BOUNDS_REQUIRED")
            if data.get("low") is not None and data.get("high") is not None:
                if decimal_value(data["low"]) > decimal_value(data["high"]):
                    raise DomainError("VALIDATION_FAILED", reason="RANGE_ORDER")
        elif kind:
            if data.get("low") is not None or data.get("high") is not None:
                raise DomainError("VALIDATION_FAILED", reason="BOUNDS_ONLY_FOR_RANGE")
            if present and data.get("value") is None:
                raise DomainError("VALIDATION_FAILED", reason="VALUE_REQUIRED")
        for field in ["value", "low", "high"]:
            if data.get(field) is not None:
                decimal_value(data[field])
        if kind == "MILESTONE":
            if complete and (not data.get("milestone_label") or not data.get("due_at")):
                raise DomainError("VALIDATION_FAILED", reason="MILESTONE_INCOMPLETE")
            if (
                period
                and data.get("due_at")
                and not (
                    instant(period["payload"]["starts_at"])
                    <= instant(data["due_at"])
                    < instant(period["payload"]["ends_at"])
                )
            ):
                raise DomainError("VALIDATION_FAILED", reason="MILESTONE_OUTSIDE_PERIOD")
        elif kind and (data.get("milestone_label") is not None or data.get("due_at") is not None):
            raise DomainError("VALIDATION_FAILED", reason="MILESTONE_FIELDS_NOT_ALLOWED")
        superseding = data.get("supersedes_revision")
        if basis and (basis == "REVISED") != bool(superseding):
            raise DomainError("VALIDATION_FAILED", reason="REVISION_BASIS_MISMATCH")
        if complete and basis == "REVISED" and not str(data.get("reason") or "").strip():
            raise DomainError("VALIDATION_FAILED", reason="REVISION_REASON_REQUIRED")
        if indicator and period and kind and basis:
            target_slot = slot(data)
            current = self.binding(c, ctx, indicator["object_id"], period["object_id"], target_slot)
            if superseding:
                revision(c, ctx, superseding, "Target", "targets.read")
                register = c.execute(
                    "SELECT * FROM impact.target_binding WHERE tenant_id=%s AND target_revision=%s",
                    (ctx.tenant_id, superseding),
                ).fetchone()
                if (
                    not register
                    or str(register["indicator_id"]) != data["indicator_id"]
                    or str(register["period_id"]) != data["period_id"]
                    or register["slot"] != target_slot
                ):
                    raise DomainError("VALIDATION_FAILED", reason="SUPERSEDED_TARGET_MISMATCH")
                if str(current["target_revision"]) != superseding:
                    raise DomainError("CONFLICT_VERSION", 409, reason="TARGET_CHANGED")
            elif current:
                raise DomainError("INVALID_STATE", 409, reason="TARGET_ALREADY_APPROVED")
        if complete and any(
            not data.get(k)
            for k in ["indicator_id", "period_id", "target_kind", "value_state", "direction", "target_basis"]
        ):
            raise DomainError("VALIDATION_FAILED", reason="SUBMISSION_INCOMPLETE")
        return indicator

    # Workflow hooks -----------------------------------------------------------------------------
    def validate(self, c, ctx, kind, data, owner_id=None):
        if kind == "Framework":
            self.validate_framework(c, ctx, data, owner_id=owner_id)
        else:
            self.validate_target(c, ctx, data)

    def prepare_submit(self, c, ctx, kind, row):
        payload = dict(row["payload"])
        if kind == "Framework":
            self.validate_framework(c, ctx, payload, complete=True, owner_id=str(row["owner_id"]))
        else:
            payload.pop("indicator_version", None)
            indicator = self.validate_target(c, ctx, payload, complete=True)
            payload["indicator_version"] = indicator["payload"]["definition_version"]
        return payload

    def check_approval(self, c, ctx, candidate):
        payload = candidate["payload"]
        if candidate["object_type"] == "Framework":
            self.validate_framework(c, ctx, payload, complete=True, owner_id=str(candidate["owner_id"]))
            return
        check = {k: v for k, v in payload.items() if k != "indicator_version"}
        indicator = self.validate_target(c, ctx, check, complete=True)
        if indicator["payload"].get("definition_version") != payload.get("indicator_version"):
            raise DomainError("CONFLICT_VERSION", 409, reason="TARGET_INDICATOR_CHANGED")

    def supersede(self, c, ctx, object_id):
        previous = load(c, ctx, object_id, lock=True)
        if previous["lifecycle_state"] == "Approved":
            write(
                c,
                ctx,
                previous["object_type"],
                previous["payload"],
                "Superseded",
                previous,
                track_author=False,
            )

    def record_approval(self, c, ctx, candidate, approved, workflow):
        payload = candidate["payload"]
        now = datetime.now(timezone.utc)
        if candidate["object_type"] == "Framework":
            current = self.baseline(c, ctx, payload["programme_id"])
            c.execute(
                "INSERT INTO impact.framework_baseline VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ctx.tenant_id,
                    payload["programme_id"],
                    current["baseline_version"] + 1 if current else 1,
                    str(candidate["object_id"]),
                    approved["revision_id"],
                    payload.get("supersedes_revision"),
                    payload["effective_from"],
                    str(workflow["object_id"]),
                    ctx.principal_id,
                    now,
                ),
            )
            if current:
                self.supersede(c, ctx, current["framework_id"])
            return
        target_slot = slot(payload)
        current = self.binding(c, ctx, payload["indicator_id"], payload["period_id"], target_slot)
        c.execute(
            "INSERT INTO impact.target_binding VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                ctx.tenant_id,
                payload["indicator_id"],
                payload["period_id"],
                target_slot,
                current["binding_version"] + 1 if current else 1,
                str(candidate["object_id"]),
                approved["revision_id"],
                payload.get("supersedes_revision"),
                str(workflow["object_id"]),
                ctx.principal_id,
                now,
            ),
        )
        if current:
            self.supersede(c, ctx, current["target_id"])

    def candidate_context(self, c, ctx, row):
        """What a reviewer sees beside a Framework or Target candidate: the approved record it
        supersedes and, for a framework, the completeness report with its change comparison."""
        from .service import revision

        extra = {}
        superseded = row["payload"].get("supersedes_revision")
        if superseded:
            previous = revision(
                c,
                ctx,
                superseded,
                row["object_type"],
                "frameworks.read" if row["object_type"] == "Framework" else "targets.read",
            )
            head = load(c, ctx, previous["object_id"])
            extra["superseded"] = {
                **envelope(head),
                "revision_id": str(previous["revision_id"]),
                "data": previous["payload"],
            }
        if row["object_type"] == "Framework":
            extra["completeness"] = self.completeness(c, ctx, row)
        return extra

    # Snapshot pin -------------------------------------------------------------------------------
    def approved_targets(self, c, ctx, programme_id, period_id):
        """Current approved target, baseline and milestone revisions of a programme period, pinned
        into the snapshot a period close creates."""
        rows = c.execute(
            "SELECT DISTINCT ON (b.indicator_id,b.slot) b.target_revision FROM impact.target_binding b JOIN impact.indicator_instance_current i ON i.tenant_id=b.tenant_id AND i.object_id=b.indicator_id WHERE b.tenant_id=%s AND b.period_id=%s AND i.programme_id=%s ORDER BY b.indicator_id,b.slot,b.binding_version DESC",
            (ctx.tenant_id, str(period_id), str(programme_id)),
        ).fetchall()
        return sorted(str(r["target_revision"]) for r in rows)

    # Read models --------------------------------------------------------------------------------
    def read(self, identity, tenant, op, obj):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, op, obj, hidden=True)
            if op == "framework_completeness":
                return self.completeness(c, ctx, load(c, ctx, obj, "Framework", "frameworks.read"))
            return self.targets_vs_actuals(c, ctx, load(c, ctx, obj, "Programme", "programmes.read"))

    def target_view(self, c, ctx, register):
        if not scopes(c, ctx, "targets.read", register["target_id"]):
            return None
        data = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s AND restriction_state='AVAILABLE'",
            (ctx.tenant_id, register["target_revision"]),
        ).fetchone()
        if not data:
            return None
        p = data["payload"]
        return {
            "target_id": str(register["target_id"]),
            "revision_id": str(register["target_revision"]),
            "target_kind": p["target_kind"],
            "target_basis": p["target_basis"],
            "direction": p["direction"],
            "value_state": p["value_state"],
            "value": p.get("value"),
            "low": p.get("low"),
            "high": p.get("high"),
            "milestone_label": p.get("milestone_label"),
            "due_at": p.get("due_at"),
            "binding_version": register["binding_version"],
        }

    def result_actual(self, c, ctx, row, source, snapshot_id=None, stale=False):
        p = row["payload"]
        return {
            "mode": p.get("mode", "PROVISIONAL"),
            "source": source,
            "value_state": p["value_state"],
            "value": p.get("value"),
            "displayed_value": p.get("displayed_value"),
            "result_id": str(row["object_id"]),
            "result_revision": str(row["revision_id"]),
            "snapshot_id": snapshot_id,
            "stale": stale,
        }

    def targets_vs_actuals(self, c, ctx, programme):
        from .service import revision

        pid = str(programme["object_id"])
        current = self.baseline(c, ctx, pid)
        framework = None
        baselines = {}

        def framework_at(register):
            if not register or not scopes(c, ctx, "frameworks.read", register["framework_id"]):
                return None
            key = str(register["framework_revision"])
            if key not in baselines:
                payload = revision(c, ctx, key, "Framework", "frameworks.read")["payload"]
                baselines[key] = {
                    "framework_id": str(register["framework_id"]),
                    "revision_id": key,
                    "baseline_version": register["baseline_version"],
                    "effective_from": register["effective_from"].isoformat(),
                    "version_label": payload.get("version_label", ""),
                    "nodes": payload.get("nodes", []),
                }
            return baselines[key]

        framework = framework_at(current)
        results_visible = scopes(c, ctx, "calculated-results.read")
        indicators = c.execute(
            "SELECT object_id FROM impact.indicator_instance_current WHERE tenant_id=%s AND programme_id=%s ORDER BY object_id LIMIT %s",
            (ctx.tenant_id, pid, MAX_INDICATORS + 1),
        ).fetchall()
        if len(indicators) > MAX_INDICATORS:
            raise DomainError("LIMIT_EXCEEDED", 422)
        rows = []
        for item in indicators:
            indicator_id = str(item["object_id"])
            if not scopes(c, ctx, "indicator-instances.read", indicator_id):
                continue
            instance = load(c, ctx, indicator_id, "IndicatorInstance")
            definition_rev = revision(
                c,
                ctx,
                instance["payload"]["definition_version"],
                "IndicatorDefinition",
                "indicator-definitions.read",
            )
            definition = definition_rev["payload"]
            places = definition.get("display_decimals", 2)
            periods = {
                str(r["period_id"])
                for r in c.execute(
                    "SELECT period_id FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s UNION SELECT period_id FROM impact.result_binding WHERE tenant_id=%s AND indicator_id=%s",
                    (ctx.tenant_id, indicator_id, ctx.tenant_id, indicator_id),
                ).fetchall()
            }
            # Fixture-era locked snapshots carry no programme; their OFFICIAL results are matched
            # to this instance through the same governed definition and labelled as unbound.
            unbound = {}
            if results_visible and scopes(c, ctx, "snapshots.read"):
                for snap in c.execute(
                    "SELECT s.object_id,s.period_id,s.result_versions FROM impact.snapshot_current s JOIN impact.object_registry r ON r.tenant_id=s.tenant_id AND r.object_id=s.object_id WHERE s.tenant_id=%s AND s.programme_id IS NULL AND r.lifecycle_state='Locked' ORDER BY s.object_id LIMIT 100",
                    (ctx.tenant_id,),
                ).fetchall():
                    for rev in snap["result_versions"] or []:
                        result = c.execute(
                            "SELECT v.object_id,v.revision_id,v.payload,d.object_id AS definition_id FROM impact.object_revision v JOIN impact.object_revision d ON d.tenant_id=v.tenant_id AND d.revision_id=(v.payload->>'indicator_version')::uuid WHERE v.tenant_id=%s AND v.revision_id=%s AND v.object_type='CalculatedResult' AND v.restriction_state='AVAILABLE'",
                            (ctx.tenant_id, rev),
                        ).fetchone()
                        if (
                            result
                            and result["payload"].get("mode") == "OFFICIAL"
                            and result["definition_id"] == definition_rev["object_id"]
                            and scopes(c, ctx, "calculated-results.read", result["object_id"])
                        ):
                            period = str(result["payload"]["period_id"])
                            unbound[period] = (result, str(snap["object_id"]))
                            periods.add(period)
            period_rows = []
            for period_id in periods:
                if scopes(c, ctx, "periods.read", period_id):
                    period_rows.append(load(c, ctx, period_id, "Period"))
            period_rows.sort(key=lambda r: (r["payload"].get("starts_at", ""), str(r["object_id"])))
            for period in period_rows[:100]:
                period_id = str(period["object_id"])
                state = self.service.periods.state(c, ctx, pid, period_id)
                snapshot = self.service.periods.latest_snapshot(c, ctx, pid, period_id)
                registers = []
                if snapshot:
                    pinned = load(c, ctx, snapshot["snapshot_id"], "Snapshot")["payload"].get(
                        "target_versions", []
                    )
                    registers = c.execute(
                        "SELECT * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s AND target_revision=ANY(%s::uuid[])",
                        (ctx.tenant_id, indicator_id, period_id, pinned),
                    ).fetchall()
                    governing = self.baseline(c, ctx, pid, at=snapshot["created_at"])
                else:
                    registers = c.execute(
                        "SELECT DISTINCT ON (slot) * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=%s AND period_id=%s ORDER BY slot,binding_version DESC",
                        (ctx.tenant_id, indicator_id, period_id),
                    ).fetchall()
                    governing = current
                views = {r["slot"]: self.target_view(c, ctx, r) for r in registers}
                actual = {
                    "mode": "NONE",
                    "source": "NONE",
                    "value_state": "MISSING",
                    "value": None,
                    "displayed_value": None,
                    "result_id": None,
                    "result_revision": None,
                    "snapshot_id": None,
                    "stale": False,
                }
                if results_visible and snapshot:
                    official = c.execute(
                        "SELECT o.result_id AS object_id,o.result_revision AS revision_id,v.payload FROM impact.official_result_snapshot o JOIN impact.object_revision v ON v.tenant_id=o.tenant_id AND v.revision_id=o.result_revision WHERE o.tenant_id=%s AND o.snapshot_id=%s AND o.indicator_id=%s AND v.restriction_state='AVAILABLE'",
                        (ctx.tenant_id, snapshot["snapshot_id"], indicator_id),
                    ).fetchone()
                    if official and scopes(c, ctx, "calculated-results.read", official["object_id"]):
                        actual = self.result_actual(
                            c, ctx, official, "PROGRAMME_SNAPSHOT", str(snapshot["snapshot_id"])
                        )
                elif results_visible and period_id in unbound:
                    result, snap = unbound[period_id]
                    actual = self.result_actual(c, ctx, result, "UNBOUND_SNAPSHOT", snap)
                elif results_visible:
                    latest = c.execute(
                        "SELECT b.result_id FROM impact.result_binding b JOIN impact.object_registry r ON r.tenant_id=b.tenant_id AND r.object_id=b.result_id WHERE b.tenant_id=%s AND b.indicator_id=%s AND b.period_id=%s AND r.lifecycle_state='Calculated' ORDER BY r.created_at DESC,r.object_id DESC LIMIT 1",
                        (ctx.tenant_id, indicator_id, period_id),
                    ).fetchone()
                    if latest and scopes(c, ctx, "calculated-results.read", latest["result_id"]):
                        row = load(c, ctx, latest["result_id"], "CalculatedResult")
                        shown = self.service.result(c, ctx, row)
                        actual = self.result_actual(
                            c,
                            ctx,
                            {
                                "object_id": row["object_id"],
                                "revision_id": row["head_revision"],
                                "payload": row["payload"],
                            },
                            "CALCULATION",
                            stale=bool(shown["data"].get("freshness", {}).get("stale")),
                        )
                        actual["mode"] = "PROVISIONAL"
                target = views.get("TARGET")
                baseline = views.get("BASELINE")
                milestones = sorted(
                    (v for k, v in views.items() if k.startswith("MILESTONE:") and v),
                    key=lambda v: (v["due_at"] or "", v["milestone_label"] or ""),
                )
                result = progress(actual, target, baseline, places)
                if actual["mode"] == "NONE" and not results_visible:
                    result["reason_code"] = "RESULT_ACCESS_REQUIRED"
                placed = framework_at(governing)
                rows.append(
                    {
                        "indicator_id": indicator_id,
                        "indicator_label": (
                            definition.get("name", "Indicator")
                            + (
                                " · " + instance["payload"]["local_applicability"]
                                if instance["payload"].get("local_applicability")
                                else ""
                            )
                        ),
                        "unit": definition.get("unit"),
                        "display_decimals": places,
                        "period_id": period_id,
                        "period_code": period["payload"].get("code"),
                        "period_state": state["lifecycle_state"],
                        "framework_revision": placed["revision_id"] if placed else None,
                        "node_ids": [
                            n["node_id"]
                            for n in (placed["nodes"] if placed else [])
                            if indicator_id in n.get("indicator_ids", [])
                        ],
                        "baseline": baseline,
                        "target": target,
                        "milestones": milestones,
                        "actual": actual,
                        "progress": result,
                    }
                )
                if len(rows) > 500:
                    raise DomainError("LIMIT_EXCEEDED", 422)
        return {"programme_id": pid, "framework": framework, "rows": rows}
