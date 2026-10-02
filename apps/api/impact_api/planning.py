"""Results framework, targets, baselines and milestones (v0.18).

A framework is one governed object per programme version: typed nodes with stable identities, an
intended result level, an owner and the indicator instances placed on them. Targets, baselines and
milestones are governed objects per indicator instance and programme period. Both follow the
definition lifecycle (Draft -> Submitted/InReview -> Approved | Returned | Rejected; Approved ->
Superseded) through the single independent review stage of `Service.submit`/`Service.review`.
Approval appends a row to an insert-only register (`framework_baseline`, `target_binding`) that
names the approved revision and the revision it supersedes; nothing approved is re-pointed.

v0.27 (planning slice): a framework revision also carries typed theory-of-change relationships
between its nodes (FR-PLN-002) and assumption, risk and context records (FR-PLN-007), both
validated here and frozen with the revision; a REVISED target superseding the target pinned at a
period's close is accepted and applies prospectively, shown beside the official comparison and
never in its place (FR-IND-004); a target may carry reviewed status thresholds, and
`performance_band` turns a comparison into an on-track / at-risk / off-track band without hiding
any separately visible state (FSD 32.2).

All writes run inside `Service.command`'s tenant lock and receipt transaction.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation, localcontext

from .domain import DomainError, decimal_value, display, stored
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
    # Theory of change (FR-PLN-002) and assumptions (FR-PLN-007): refused on every save too.
    "DUPLICATE_RELATIONSHIP_ID",
    "DUPLICATE_RELATIONSHIP",
    "RELATIONSHIP_SELF",
    "RELATIONSHIP_ENDPOINT_MISSING",
    "RELATIONSHIP_LEVEL_ORDER",
    "RELATIONSHIP_CYCLE",
    "RELATIONSHIP_ASSUMPTION_MISSING",
    "DUPLICATE_ASSUMPTION_ID",
    "ASSUMPTION_NODE_MISSING",
}
PLANNING_KINDS = {"Framework", "Target"}
OPEN_PROGRAMME = {"Draft", "Ready", "Active"}
MAX_INDICATORS = 200
FLAGGED_ASSUMPTION = {"AT_RISK", "INVALID"}


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def causal_edge(relationship):
    """The contribution a relationship states, as (contributor, beneficiary): CONTRIBUTES_TO reads
    from -> to, DEPENDS_ON states the same contribution from the dependent side."""
    a, b = relationship["from_node_id"], relationship["to_node_id"]
    return (a, b) if relationship["relationship_type"] == "CONTRIBUTES_TO" else (b, a)


def relationship_issues(by_id, relationships, assumption_ids):
    """Pure rules over the theory-of-change links: identities, endpoints, the level order of a
    contribution (a result contributes to the same or a higher level; alternative pathways are
    allowed), no causal cycle, and assumptions that exist. A link never creates a numeric rule."""
    issues, seen, edges, graph = [], set(), set(), {}
    for rel in relationships:
        rid = rel["relationship_id"]
        if rid in seen:
            issues.append(
                ("ERROR", "DUPLICATE_RELATIONSHIP_ID", rid, "Each relationship needs its own identity.")
            )
        seen.add(rid)
        a, b = rel["from_node_id"], rel["to_node_id"]
        if a == b:
            issues.append(("ERROR", "RELATIONSHIP_SELF", rid, "A node cannot contribute to itself."))
            continue
        if a not in by_id or b not in by_id:
            issues.append(
                (
                    "ERROR",
                    "RELATIONSHIP_ENDPOINT_MISSING",
                    rid,
                    "Both ends of a relationship must be nodes of this framework.",
                )
            )
            continue
        key = (a, b, rel["relationship_type"])
        if key in edges:
            issues.append(("ERROR", "DUPLICATE_RELATIONSHIP", rid, "Record each relationship once."))
        edges.add(key)
        contributor, beneficiary = causal_edge(rel)
        if LEVELS[by_id[contributor]["node_type"]] > LEVELS[by_id[beneficiary]["node_type"]]:
            issues.append(
                (
                    "ERROR",
                    "RELATIONSHIP_LEVEL_ORDER",
                    rid,
                    "A result contributes to the same or a higher result level, never a lower one.",
                )
            )
        else:
            graph.setdefault(contributor, set()).add(beneficiary)
        for assumption in rel.get("assumption_ids", []):
            if assumption not in assumption_ids:
                issues.append(
                    (
                        "ERROR",
                        "RELATIONSHIP_ASSUMPTION_MISSING",
                        rid,
                        "A relationship names only assumptions recorded in this framework.",
                    )
                )
        if rel.get("evidence_strength") == "UNTESTED":
            issues.append(
                ("WARNING", "UNTESTED_RELATIONSHIP", rid, "The evidence for this contribution is untested.")
            )
    # A causal cycle (only possible between nodes of one level) is refused like a containment cycle.
    state, cyclic = {}, set()

    def visit(node, path):
        state[node] = 1
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                cyclic.update(path[path.index(nxt) :])
            elif nxt not in state:
                visit(nxt, path + [nxt])
        state[node] = 2

    for start in sorted(graph):
        if start not in state:
            visit(start, [start])
    for node in sorted(cyclic):
        issues.append(("ERROR", "RELATIONSHIP_CYCLE", node, "Contributions must not form a cycle."))
    return issues


def assumption_issues(by_id, assumptions, today=None):
    """Pure rules over assumption, risk and context records: identities and linked nodes exist
    (structural), an owner is assigned, an assumption or risk is linked to a node, an invalid status
    highlights every linked node, and a passed review date asks for a reassessment."""
    issues, seen, flagged = [], set(), set()
    for item in assumptions:
        aid = item["assumption_id"]
        if aid in seen:
            issues.append(
                ("ERROR", "DUPLICATE_ASSUMPTION_ID", aid, "Each assumption needs its own identity.")
            )
        seen.add(aid)
        linked = []
        for node in item.get("node_ids", []):
            if node not in by_id:
                issues.append(
                    (
                        "ERROR",
                        "ASSUMPTION_NODE_MISSING",
                        aid,
                        "An assumption links only to nodes of this framework.",
                    )
                )
            else:
                linked.append(node)
        if not item.get("owner_id"):
            issues.append(("ERROR", "ASSUMPTION_INCOMPLETE", aid, "Assign an owner to this assumption."))
        if item["kind"] != "CONTEXT" and not item.get("node_ids"):
            issues.append(
                (
                    "WARNING",
                    "UNLINKED_ASSUMPTION",
                    aid,
                    "This assumption is not linked to any result it conditions.",
                )
            )
        if item["status"] == "INVALID":
            flagged.update(linked)
        if today and item["review_date"] < today:
            issues.append(
                (
                    "WARNING",
                    "ASSUMPTION_REVIEW_DUE",
                    aid,
                    "The assumption's review date has passed; reassess it.",
                )
            )
    for node in sorted(flagged):
        issues.append(
            (
                "WARNING",
                "ASSUMPTION_INVALID",
                node,
                "An assumption this result relies on is invalid; review the result.",
            )
        )
    return issues


def slot(data):
    if data.get("target_basis") == "BASELINE":
        return "BASELINE"
    if data.get("target_kind") == "MILESTONE":
        return "MILESTONE:" + (data.get("milestone_label") or "")
    return "TARGET"


def structure_issues(nodes, relationships=(), assumptions=(), today=None):
    """Pure structural and completeness rules over a node list, its theory-of-change relationships
    and its assumptions (no database): returns issues as (severity, rule, object_id, message)."""
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
    issues.extend(relationship_issues(by_id, relationships, {a["assumption_id"] for a in assumptions}))
    issues.extend(assumption_issues(by_id, assumptions, today))
    return issues


def threshold_issue(target):
    """Why a target's `status_thresholds` are refused, or None. ATTAINMENT_PERCENT needs a
    higher-is-better value target (attainment is defined only there); DEVIATION applies to value and
    range targets; a milestone needs an assessment, not a band. Bands are ordered so that on-track
    is at least as demanding as at-risk."""
    thresholds = target.get("status_thresholds")
    if not thresholds:
        return None
    kind, direction = target.get("target_kind"), target.get("direction")
    if kind == "MILESTONE":
        return "THRESHOLDS_NOT_ALLOWED"
    on_track, at_risk = decimal_value(thresholds["on_track"]), decimal_value(thresholds["at_risk"])
    if on_track < 0 or at_risk < 0:
        return "THRESHOLD_NEGATIVE"
    if thresholds["scheme"] == "ATTAINMENT_PERCENT":
        if kind != "VALUE" or direction != "HIGHER":
            return "THRESHOLD_SCHEME_MISMATCH"
        return None if on_track >= at_risk else "THRESHOLD_ORDER"
    return None if on_track <= at_risk else "THRESHOLD_ORDER"


def performance_band(value, target, stale=False):
    """Pure banding of one PRESENT stored actual against a PRESENT target that carries status
    thresholds: (band, reason). The band is None, with the reason, whenever a separately visible
    state comes first (FSD 32.2): no thresholds, a stale actual, an undefined attainment, a milestone.
    ATTAINMENT_PERCENT: attainment >= on_track is ON_TRACK, >= at_risk AT_RISK, else OFF_TRACK.
    DEVIATION: the adverse distance from the target (below a higher target, above a lower one, outside
    a range; never negative) <= on_track is ON_TRACK, <= at_risk AT_RISK, else OFF_TRACK.
    Dashboards and other read models may call this with the same arguments."""
    thresholds = (target or {}).get("status_thresholds")
    if not thresholds:
        return None, "NO_THRESHOLDS"
    if stale:
        return None, "STALE_ACTUAL"
    if target.get("target_kind") == "MILESTONE":
        return None, "MILESTONE_ASSESSMENT"
    on_track, at_risk = decimal_value(thresholds["on_track"]), decimal_value(thresholds["at_risk"])
    with localcontext() as c:
        c.prec = 60
        if thresholds["scheme"] == "ATTAINMENT_PERCENT":
            goal = decimal_value(target["value"])
            if goal <= 0:
                return None, "ATTAINMENT_UNDEFINED"
            measure = value / goal * 100
            if measure >= on_track:
                return "ON_TRACK", None
            return ("AT_RISK" if measure >= at_risk else "OFF_TRACK"), None
        if target["target_kind"] == "RANGE":
            low, high = decimal_value(target["low"]), decimal_value(target["high"])
            adverse = low - value if value < low else value - high if value > high else Decimal(0)
        elif target["direction"] == "LOWER":
            adverse = max(Decimal(0), value - decimal_value(target["value"]))
        else:
            adverse = max(Decimal(0), decimal_value(target["value"]) - value)
        if adverse <= on_track:
            return "ON_TRACK", None
        return ("AT_RISK" if adverse <= at_risk else "OFF_TRACK"), None


def progress(actual, target, baseline, places):
    """Target attainment per the declared direction (LLD: uncapped higher attainment, signed lower
    deviation, inclusive range bounds); zero or negative higher targets and zero baselines are
    undefined, never divided. Arithmetic uses stored decimals, never displayed values. The band
    comes from the target's own thresholds (`performance_band`) and is never a substitute for the
    status, the actual's mode or its staleness."""
    result = {
        "status": "NO_ACTUAL",
        "attainment_percent": None,
        "deviation": None,
        "displayed_deviation": None,
        "change_from_baseline": None,
        "change_from_baseline_percent": None,
        "change_from_baseline_reason": None,
        "reason_code": None,
        "band": None,
        "band_reason": None,
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
            if base <= 0:
                # A percentage change from a zero or negative baseline needs an approved
                # interpretation (FR-ANA-003); none exists, so it stays undefined.
                result["change_from_baseline_percent"] = "Undefined"
                result["change_from_baseline_reason"] = "NON_POSITIVE_BASELINE"
            else:
                result["change_from_baseline_percent"] = display((value - base) / base * 100, 2)
        if value is None:
            result["reason_code"] = "NO_PRESENT_ACTUAL" if actual.get("mode") != "NONE" else "NO_RESULT"
            return {**result, "band_reason": result["reason_code"]}
        if target is None:
            return {
                **result,
                "status": "NO_TARGET",
                "reason_code": "NO_APPROVED_TARGET",
                "band_reason": "NO_TARGET",
            }
        if target.get("value_state") != "PRESENT":
            reason = "TARGET_" + target["value_state"]
            return {**result, "status": "NO_TARGET", "reason_code": reason, "band_reason": reason}
        kind, direction = target["target_kind"], target["direction"]
        if kind == "MILESTONE":
            return {
                **result,
                "status": "ASSESSMENT_REQUIRED",
                "reason_code": "MILESTONE_ASSESSMENT",
                "band_reason": "MILESTONE_ASSESSMENT",
            }
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
        band, band_reason = performance_band(value, target, stale=bool(actual.get("stale")))
        result.update(
            status=status,
            deviation=stored(deviation),
            displayed_deviation=display(deviation, places),
            band=band,
            band_reason=band_reason,
        )
        return result


def safe_progress(actual, target, baseline, places):
    """`progress` for one row of a read model: an arithmetic result outside the NUMERIC(38,12)
    transport range leaves that row's arithmetic empty with a reason, never failing the read."""
    try:
        return progress(actual, target, baseline, places)
    except (DomainError, InvalidOperation, ArithmeticError):
        return {
            "status": "NOT_COMPUTABLE",
            "attainment_percent": None,
            "deviation": None,
            "displayed_deviation": None,
            "change_from_baseline": None,
            "change_from_baseline_percent": None,
            "change_from_baseline_reason": None,
            "reason_code": "ARITHMETIC_OVERFLOW",
            "band": None,
            "band_reason": "ARITHMETIC_OVERFLOW",
        }


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
    def framework_issues(self, c, ctx, data, owner_id=None, strict=True):
        """strict (every write): an indicator the actor cannot see is not found. Not strict (the
        completeness and candidate reads): such an indicator is reported by identifier only."""
        from .service import revision

        nodes = data.get("nodes", [])
        relationships, assumptions = data.get("relationships", []), data.get("assumptions", [])
        today = c.execute("SELECT current_date AS today").fetchone()["today"].isoformat()
        found = list(structure_issues(nodes, relationships, assumptions, today))
        by_id = {n["node_id"]: n for n in nodes}
        # Who resolves an issue on a relationship (the contributing node's owner) or an assumption
        # (its owner); nodes resolve their own, the framework owner the rest.
        resolvers = {a["assumption_id"]: a.get("owner_id") for a in assumptions}
        for rel in relationships:
            resolvers[rel["relationship_id"]] = (by_id.get(causal_edge(rel)[0]) or {}).get("owner_id")
        for item in assumptions:
            if item.get("owner_id") and not self.service.measurement.principal(c, ctx, item["owner_id"]):
                found.append(
                    (
                        "ERROR",
                        "OWNER_INELIGIBLE",
                        item["assumption_id"],
                        "The assumption owner must be an active member.",
                    )
                )
        programme_id = data.get("programme_id")
        for node in nodes:
            for indicator in node.get("indicator_ids", []):
                if not strict and not scopes(c, ctx, "indicator-instances.read", indicator):
                    continue
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
            if item["review_date"] < today:
                # A lapsed exception no longer accepts its warning; the author renews or resolves it.
                found.append(
                    (
                        "ERROR",
                        "EXCEPTION_REVIEW_DATE_PASSED",
                        item["object_id"],
                        "The exception's review date has passed.",
                    )
                )
                continue
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
                    "resolver_id": (node or {}).get("owner_id") or resolvers.get(obj) or owner_id,
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
        lapsed = [i for i in issues if i["rule"] == "EXCEPTION_REVIEW_DATE_PASSED"]
        if lapsed:
            raise DomainError(
                "VALIDATION_FAILED",
                reason="EXCEPTION_REVIEW_DATE_PASSED",
                fields=[{"path": "exceptions." + i["object_id"], "message": i["rule"]} for i in lapsed[:20]],
            )
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
        issues, base, empty = self.framework_issues(c, ctx, data, str(row["owner_id"]), strict=False)
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

    def stamp_exceptions(self, c, ctx, previous, data):
        """Server-owned authorship of each documented exception and of each assumption's assessment:
        an unchanged exception keeps who recorded it and when; an assumption keeps who assessed its
        status until the status changes; anything new or changed is stamped with the acting principal
        at database time. Clients never supply these fields (the draft schema is closed). A child
        draft (no previous revision of its own) inherits the stamps of the approved revision it
        supersedes, so an unchanged assessment is not re-attributed to the drafter."""
        if "exceptions" not in data and "assumptions" not in data:
            return data
        if previous is None and data.get("supersedes_revision"):
            superseded = c.execute(
                "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s AND object_type='Framework' AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, data["supersedes_revision"]),
            ).fetchone()
            previous = superseded["payload"] if superseded else None
        now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"].isoformat()
        data = dict(data)
        if "exceptions" in data:
            known = {}
            for item in (previous or {}).get("exceptions", []):
                if item.get("recorded_by"):
                    known[(item["object_id"], item["rule"], item["reason"], item["review_date"])] = item
            stamped = []
            for item in data["exceptions"]:
                core = {k: item[k] for k in ["object_id", "rule", "reason", "review_date"]}
                kept = known.get(tuple(core.values()))
                stamped.append(
                    {
                        **core,
                        "recorded_by": kept["recorded_by"] if kept else ctx.principal_id,
                        "recorded_at": kept["recorded_at"] if kept else now,
                    }
                )
            data["exceptions"] = stamped
        if "assumptions" in data:
            # An assumption keeps who assessed its status, and when, until the status changes; a
            # changed status is assessed by the acting principal now (FR-PLN-007: a past assessment
            # stays in the earlier revision with its date).
            earlier = {a["assumption_id"]: a for a in (previous or {}).get("assumptions", [])}
            assessed = []
            for item in data["assumptions"]:
                core = {k: v for k, v in item.items() if k not in {"assessed_by", "assessed_at"}}
                kept = earlier.get(item["assumption_id"])
                same = kept and kept.get("status") == item["status"] and kept.get("assessed_by")
                assessed.append(
                    {
                        **core,
                        "assessed_by": kept["assessed_by"] if same else ctx.principal_id,
                        "assessed_at": kept["assessed_at"] if same else now,
                    }
                )
            data["assumptions"] = assessed
        return data

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
            if state["lifecycle_state"] != "Open" and not (
                data.get("target_basis") == "REVISED" and data.get("supersedes_revision")
            ):
                # A frozen period keeps the comparison its close pinned. Only an amendment that
                # supersedes the approved target may follow, and it applies prospectively: the
                # official comparison stays against the pinned target (FR-IND-004).
                raise DomainError("INVALID_STATE", 409, reason="PERIOD_LOCKED")
        kind, direction, basis = data.get("target_kind"), data.get("direction"), data.get("target_basis")
        if kind and data.get("status_thresholds") and (issue := threshold_issue(data)):
            raise DomainError("VALIDATION_FAILED", reason=issue)
        allowed = {"VALUE": {"HIGHER", "LOWER"}, "RANGE": {"RANGE"}, "MILESTONE": {"MILESTONE"}}
        if kind and direction and direction not in allowed[kind]:
            raise DomainError("VALIDATION_FAILED", reason="DIRECTION_KIND_MISMATCH")
        if basis == "BASELINE" and kind and kind != "VALUE":
            raise DomainError("VALIDATION_FAILED", reason="BASELINE_REQUIRES_VALUE")
        present = data.get("value_state") == "PRESENT"
        if not present and any(data.get(k) is not None for k in ["value", "low", "high"]):
            raise DomainError("VALIDATION_FAILED", reason="BLANK_TARGET_HAS_NO_VALUE")
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
        # REVISED always supersedes an approved target; an approved BASELINE is corrected by a
        # BASELINE that supersedes it; ORIGINAL never supersedes anything.
        if basis and ((basis == "REVISED" and not superseding) or (basis == "ORIGINAL" and superseding)):
            raise DomainError("VALIDATION_FAILED", reason="REVISION_BASIS_MISMATCH")
        if complete and superseding and not str(data.get("reason") or "").strip():
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
        now = c.execute("SELECT statement_timestamp() AS now").fetchone()["now"]
        if candidate["object_type"] == "Framework":
            current = self.baseline(c, ctx, payload["programme_id"])
            c.execute(
                "INSERT INTO impact.framework_baseline(tenant_id,programme_id,baseline_version,framework_id,framework_revision,supersedes_revision,effective_from,workflow_id,approved_by,approved_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
            "INSERT INTO impact.target_binding(tenant_id,indicator_id,period_id,slot,binding_version,target_id,target_revision,supersedes_revision,workflow_id,approved_by,approved_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
        payload = row["payload"]
        if superseded:
            # FR-IND-004: the review compares original, currently effective and proposed values.
            # The chain is walked through the register, which names each superseded revision.
            first, seen = superseded, set()
            while first not in seen:
                seen.add(first)
                register = c.execute(
                    "SELECT supersedes_revision FROM impact.target_binding WHERE tenant_id=%s AND target_revision=%s",
                    (ctx.tenant_id, first),
                ).fetchone()
                if not register or not register["supersedes_revision"]:
                    break
                first = str(register["supersedes_revision"])
            if first != superseded:
                original = revision(c, ctx, first, "Target", "targets.read")
                extra["original"] = {
                    **envelope(load(c, ctx, original["object_id"])),
                    "revision_id": str(original["revision_id"]),
                    "data": original["payload"],
                }
        if payload.get("indicator_id") and payload.get("period_id"):
            indicator = load(c, ctx, payload["indicator_id"], "IndicatorInstance", "indicator-instances.read")
            state = self.service.periods.state(
                c, ctx, indicator["payload"]["programme_id"], payload["period_id"]
            )["lifecycle_state"]
            extra["amendment"] = {"period_state": state, "prospective_only": state != "Open"}
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

    def governing_framework(self, c, ctx, programme_id, period):
        """The approved baseline that governs a period: the latest one whose effective date falls
        before the period ends. Every row of the register is already committed, so this is the
        database's current state; a close pins the answer into the snapshot."""
        return c.execute(
            "SELECT * FROM impact.framework_baseline WHERE tenant_id=%s AND programme_id=%s AND effective_from<%s ORDER BY baseline_version DESC LIMIT 1",
            (ctx.tenant_id, str(programme_id), period["payload"]["ends_at"]),
        ).fetchone()

    # Read models --------------------------------------------------------------------------------
    def read(self, identity, tenant, op, obj, limit=50, cursor=None, period_id=None):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, op, obj, hidden=True)
            if op == "framework_completeness":
                return self.completeness(c, ctx, load(c, ctx, obj, "Framework", "frameworks.read"))
            if not 1 <= limit <= 100:
                raise DomainError("VALIDATION_FAILED")
            programme = load(c, ctx, obj, "Programme", "programmes.read")
            period = load(c, ctx, period_id, "Period", "periods.read") if period_id else None
            bound = self.service.cursor_binding(
                ctx, "programmes/" + str(obj) + "/targets-vs-actuals?period=" + str(period_id or "")
            )
            key = self.service.cursor_key(bound, cursor)
            result = self.targets_vs_actuals(c, ctx, programme, limit, key, period)
            last = result.pop("more")
            if last:
                result["next_cursor"] = self.service.next_cursor(bound, [last])
            return result

    def target_views(self, c, ctx, registers):
        payloads = {
            str(r["revision_id"]): r["payload"]
            for r in c.execute(
                "SELECT revision_id,payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=ANY(%s::uuid[]) AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, [str(r["target_revision"]) for r in registers]),
            ).fetchall()
        }
        views = {}
        for register in registers:
            p = payloads.get(str(register["target_revision"]))
            if not p or not scopes(c, ctx, "targets.read", register["target_id"]):
                continue
            views[(str(register["indicator_id"]), str(register["period_id"]), register["slot"])] = {
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
                "status_thresholds": p.get("status_thresholds"),
            }
        return views

    def targets_vs_actuals(self, c, ctx, programme, limit, key, period):
        """One page of indicators (keyset on the indicator identifier) with one row per period.
        OFFICIAL values come only from a snapshot bound to this programme and period
        (`official_result_snapshot` for this indicator) whose result used the definition revision the
        instance pins; PROVISIONAL values only from this indicator's own calculations under the same
        pin. Nothing is attributed through a shared definition."""
        from .store import visible_sql

        pid = str(programme["object_id"])
        baselines = {}

        def framework_at(register):
            if not register or not scopes(c, ctx, "frameworks.read", register["framework_id"]):
                return None
            rev = str(register["framework_revision"])
            if rev not in baselines:
                payload = c.execute(
                    "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=%s",
                    (ctx.tenant_id, rev),
                ).fetchone()["payload"]
                baselines[rev] = {
                    "framework_id": str(register["framework_id"]),
                    "revision_id": rev,
                    "baseline_version": register["baseline_version"],
                    "effective_from": register["effective_from"].isoformat(),
                    "version_label": payload.get("version_label", ""),
                    "nodes": payload.get("nodes", []),
                    "relationships": payload.get("relationships", []),
                    "assumptions": payload.get("assumptions", []),
                }
            return baselines[rev]

        framework = framework_at(self.baseline(c, ctx, pid))
        predicate, args = visible_sql(ctx, "indicator-instances.read")
        instances = c.execute(
            "SELECT r.object_id,v.payload FROM impact.indicator_instance_current i JOIN impact.object_registry r ON r.tenant_id=i.tenant_id AND r.object_id=i.object_id JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE i.tenant_id=%s AND i.programme_id=%s AND r.classification<>'RESTRICTED' AND v.restriction_state='AVAILABLE' AND "
            + predicate
            + (" AND r.object_id>%s::uuid" if key else "")
            + " ORDER BY r.object_id LIMIT %s",
            [ctx.tenant_id, pid, *args, *([key[0]] if key else []), limit + 1],
        ).fetchall()
        more = len(instances) > limit
        instances = instances[:limit]
        ids = [str(r["object_id"]) for r in instances]
        definitions = {
            str(r["revision_id"]): r
            for r in c.execute(
                "SELECT revision_id,object_id,payload FROM impact.object_revision WHERE tenant_id=%s AND revision_id=ANY(%s::uuid[]) AND object_type='IndicatorDefinition' AND restriction_state='AVAILABLE'",
                (ctx.tenant_id, [r["payload"].get("definition_version") for r in instances]),
            ).fetchall()
        }
        # Periods per indicator: the requested one, or those holding targets, results or snapshots.
        if period:
            pairs = {(i, str(period["object_id"])) for i in ids}
        else:
            pairs = {
                (str(r["indicator_id"]), str(r["period_id"]))
                for r in c.execute(
                    "SELECT indicator_id,period_id FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=ANY(%s::uuid[]) UNION SELECT indicator_id,period_id FROM impact.result_binding WHERE tenant_id=%s AND indicator_id=ANY(%s::uuid[])",
                    (ctx.tenant_id, ids, ctx.tenant_id, ids),
                ).fetchall()
            }
        period_ids = sorted({p for _, p in pairs})
        periods = {
            str(r["object_id"]): r
            for r in c.execute(
                "SELECT r.object_id,v.payload FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.tenant_id=%s AND r.object_id=ANY(%s::uuid[]) AND r.object_type='Period' AND v.restriction_state='AVAILABLE'",
                (ctx.tenant_id, period_ids),
            ).fetchall()
            if scopes(c, ctx, "periods.read", r["object_id"])
        }
        states = {p: self.service.periods.state(c, ctx, pid, p) for p in periods}
        snapshots = {
            str(r["period_id"]): r
            for r in c.execute(
                "SELECT DISTINCT ON (b.period_id) b.period_id,b.snapshot_id,v.payload FROM impact.period_snapshot_binding b JOIN impact.object_revision v ON v.tenant_id=b.tenant_id AND v.revision_id=b.snapshot_revision WHERE b.tenant_id=%s AND b.programme_id=%s AND b.period_id=ANY(%s::uuid[]) ORDER BY b.period_id,b.snapshot_version DESC",
                (ctx.tenant_id, pid, list(periods)),
            ).fetchall()
        }
        pinned = [t for snap in snapshots.values() for t in snap["payload"].get("target_versions", [])]
        open_periods = [p for p in periods if p not in snapshots]
        registers = (
            c.execute(
                "SELECT * FROM impact.target_binding WHERE tenant_id=%s AND target_revision=ANY(%s::uuid[]) AND indicator_id=ANY(%s::uuid[])",
                (ctx.tenant_id, pinned, ids),
            ).fetchall()
            + c.execute(
                "SELECT DISTINCT ON (indicator_id,period_id,slot) * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=ANY(%s::uuid[]) AND period_id=ANY(%s::uuid[]) ORDER BY indicator_id,period_id,slot,binding_version DESC",
                (ctx.tenant_id, ids, open_periods),
            ).fetchall()
        )
        views = self.target_views(c, ctx, registers)
        # FR-IND-004: the latest approved target of a locked period, when it is not the one the
        # close pinned, is an amendment shown beside the official comparison, never in its place.
        amended = self.target_views(
            c,
            ctx,
            c.execute(
                "SELECT DISTINCT ON (indicator_id,period_id,slot) * FROM impact.target_binding WHERE tenant_id=%s AND indicator_id=ANY(%s::uuid[]) AND period_id=ANY(%s::uuid[]) AND slot='TARGET' ORDER BY indicator_id,period_id,slot,binding_version DESC",
                (ctx.tenant_id, ids, list(snapshots)),
            ).fetchall(),
        )
        results_visible = scopes(c, ctx, "calculated-results.read")
        official, provisional = {}, {}
        if results_visible:
            for r in c.execute(
                "SELECT o.indicator_id,o.period_id,o.snapshot_id,o.result_id AS object_id,o.result_revision AS revision_id,v.payload FROM impact.official_result_snapshot o JOIN impact.object_revision v ON v.tenant_id=o.tenant_id AND v.revision_id=o.result_revision WHERE o.tenant_id=%s AND o.snapshot_id=ANY(%s::uuid[]) AND o.indicator_id=ANY(%s::uuid[]) AND v.restriction_state='AVAILABLE'",
                (ctx.tenant_id, [str(s["snapshot_id"]) for s in snapshots.values()], ids),
            ).fetchall():
                official[(str(r["indicator_id"]), str(r["period_id"]))] = r
            for r in c.execute(
                "SELECT DISTINCT ON (b.indicator_id,b.period_id) b.indicator_id,b.period_id,b.result_id FROM impact.result_binding b JOIN impact.object_registry r ON r.tenant_id=b.tenant_id AND r.object_id=b.result_id WHERE b.tenant_id=%s AND b.indicator_id=ANY(%s::uuid[]) AND b.period_id=ANY(%s::uuid[]) AND r.lifecycle_state='Calculated' ORDER BY b.indicator_id,b.period_id,r.created_at DESC,r.object_id DESC",
                (ctx.tenant_id, ids, open_periods),
            ).fetchall():
                provisional[(str(r["indicator_id"]), str(r["period_id"]))] = str(r["result_id"])
        rows = []
        for instance in instances:
            indicator_id = str(instance["object_id"])
            pin = instance["payload"].get("definition_version")
            definition_row = definitions.get(str(pin))
            definition = (
                definition_row["payload"]
                if definition_row
                and scopes(c, ctx, "indicator-definitions.read", definition_row["object_id"])
                else {}
            )
            places = definition.get("display_decimals", 2)
            mine = sorted(
                (periods[p] for i, p in pairs if i == indicator_id and p in periods),
                key=lambda r: (r["payload"].get("starts_at", ""), str(r["object_id"])),
            )[:100]
            for period_row in mine:
                period_id = str(period_row["object_id"])
                snapshot = snapshots.get(period_id)
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
                found = official.get((indicator_id, period_id)) if snapshot else None
                if (
                    found
                    and found["payload"].get("indicator_version") == pin
                    and scopes(c, ctx, "calculated-results.read", found["object_id"])
                ):
                    actual = self.result_actual(found, "PROGRAMME_SNAPSHOT", str(snapshot["snapshot_id"]))
                elif not snapshot and (indicator_id, period_id) in provisional:
                    result_id = provisional[(indicator_id, period_id)]
                    if scopes(c, ctx, "calculated-results.read", result_id):
                        row = load(c, ctx, result_id, "CalculatedResult")
                        if row["payload"].get("indicator_version") == pin:
                            shown = self.service.result(c, ctx, row)
                            actual = self.result_actual(
                                {
                                    "object_id": row["object_id"],
                                    "revision_id": row["head_revision"],
                                    "payload": row["payload"],
                                },
                                "CALCULATION",
                                stale=bool(shown["data"].get("freshness", {}).get("stale")),
                            )
                            actual["mode"] = "PROVISIONAL"
                target = views.get((indicator_id, period_id, "TARGET"))
                baseline = views.get((indicator_id, period_id, "BASELINE"))
                milestones = sorted(
                    (
                        v
                        for (i, p, k), v in views.items()
                        if i == indicator_id and p == period_id and k.startswith("MILESTONE:")
                    ),
                    key=lambda v: (v["due_at"] or "", v["milestone_label"] or ""),
                )
                result = safe_progress(actual, target, baseline, places)
                if actual["mode"] == "NONE" and not results_visible:
                    result["reason_code"] = "RESULT_ACCESS_REQUIRED"
                if snapshot:
                    governing_revision = (snapshot["payload"].get("policy_context") or {}).get(
                        "framework_revision"
                    )
                    governing = (
                        c.execute(
                            "SELECT * FROM impact.framework_baseline WHERE tenant_id=%s AND framework_revision=%s",
                            (ctx.tenant_id, governing_revision),
                        ).fetchone()
                        if governing_revision
                        else None
                    )
                else:
                    governing = self.governing_framework(c, ctx, pid, period_row)
                placed = framework_at(governing)
                applicability = instance["payload"].get("local_applicability")
                node_ids = [
                    n["node_id"]
                    for n in (placed["nodes"] if placed else [])
                    if indicator_id in n.get("indicator_ids", [])
                ]
                current = amended.get((indicator_id, period_id, "TARGET")) if snapshot else None
                if current and target and current["revision_id"] == target["revision_id"]:
                    current = None
                rows.append(
                    {
                        "indicator_id": indicator_id,
                        "indicator_label": definition.get("name", "Indicator")
                        + (" · " + applicability if applicability else ""),
                        "unit": definition.get("unit"),
                        "display_decimals": places,
                        "period_id": period_id,
                        "period_code": period_row["payload"].get("code"),
                        "period_state": states[period_id]["lifecycle_state"],
                        "framework_revision": placed["revision_id"] if placed else None,
                        "node_ids": node_ids,
                        "baseline": baseline,
                        "target": target,
                        "milestones": milestones,
                        "actual": actual,
                        "progress": result,
                        "amended_target": current,
                        "amended_progress": (
                            safe_progress(actual, current, baseline, places) if current else None
                        ),
                        "amended_after_close": current is not None,
                        "assumption_flags": [
                            {
                                "assumption_id": a["assumption_id"],
                                "kind": a["kind"],
                                "status": a["status"],
                                "statement": a["statement"],
                            }
                            for a in (placed["assumptions"] if placed else [])
                            if a["status"] in FLAGGED_ASSUMPTION
                            and any(n in node_ids for n in a.get("node_ids", []))
                        ],
                    }
                )
        return {
            "programme_id": pid,
            "framework": framework,
            "rows": rows,
            "next_cursor": None,
            "more": ids[-1] if more else None,
        }

    def result_actual(self, row, source, snapshot_id=None, stale=False):
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
