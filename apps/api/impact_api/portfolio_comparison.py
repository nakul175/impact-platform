"""FR-ANA-007 fair, permission-safe portfolio comparison projection."""

from decimal import Decimal, InvalidOperation


def _number(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def build_comparison(versions, programmes, period, scope, coverage_threshold):
    """Group exact-compatible cells and produce qualified rankings only.

    The caller has already permission-filtered ``programmes``.  This projection deliberately
    reports no hidden count, identifier or inferred total when scope is partial.
    """
    groups = []
    by_revision = {row["definition_revision"]: row for row in versions}
    for revision in sorted(by_revision, key=lambda value: value or ""):
        members = [row for row in programmes if row.get("definition_revision") == revision]
        ranked, excluded = [], []
        for row in members:
            official = row.get("official") or {}
            coverage = row.get("coverage") or {}
            percent = coverage.get("approval_percent")
            reason = None
            if official.get("value_state") != "PRESENT" or official.get("value") is None:
                reason = "OFFICIAL_VALUE_UNAVAILABLE"
            elif coverage.get("applicability") == "APPLICABLE" and (
                percent is None or Decimal(str(percent)) < coverage_threshold
            ):
                reason = "BELOW_COVERAGE_THRESHOLD"
            value = _number(official.get("value"))
            item = {
                "indicator_id": row["indicator_id"],
                "programme_id": row["programme_id"],
                "programme_title": row.get("programme_title"),
                "displayed_value": official.get("displayed_value"),
                "denominator": official.get("denominator"),
            }
            if reason or value is None:
                excluded.append({**item, "reason_code": reason or "VALUE_NOT_NUMERIC"})
            else:
                ranked.append((value, item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]["indicator_id"]))
        groups.append(
            {
                "compatibility_key": {
                    "definition_revision": revision,
                    "period_id": period["period_id"],
                    "starts_at": period.get("starts_at"),
                    "ends_at": period.get("ends_at"),
                },
                "compatible": True,
                "mismatch_flags": [],
                "ranking": {
                    "status": "QUALIFIED" if ranked else "UNAVAILABLE",
                    "method": "DESCENDING_OFFICIAL_VALUE_WITHIN_EXACT_DEFINITION_VERSION",
                    "unqualified_league_table": False,
                    "review_status": "REQUIRED_FOR_UNQUALIFIED_RANKING",
                    "items": [{**item, "rank": index + 1} for index, (_, item) in enumerate(ranked)],
                    "excluded": excluded,
                },
            }
        )
    mismatch = []
    if len(groups) > 1:
        mismatch.append("DEFINITION_REVISION")
        for group in groups:
            group["mismatch_flags"] = list(mismatch)
    return {
        "coverage_threshold": str(coverage_threshold),
        "visible_scope": "ALL_AUTHORISED_MEMBERS" if scope == "COMPLETE" else "PARTIAL_AUTHORISED_SCOPE",
        "hidden_members_disclosed": False,
        "raw_cross_group_ranking": "REFUSED",
        "groups": groups,
    }
