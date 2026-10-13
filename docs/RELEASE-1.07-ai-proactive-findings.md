# Release 1.07 coding candidate — governed proactive finding suggestions

FR-AI-009 / APL-601 adds immutable detection-task configurations for one exact current Programme revision. Each configuration names an accountable active human owner, an explicit enabled state, a cooldown and a rolling noise limit. A disabled task cannot generate a suggestion; a changed scope revision, inactive owner, active cooldown or exhausted noise allowance refuses generation.

Each suggestion pins exact governed CalculatedResult and Evidence revisions and states its summary, limitations and proposed follow up. The visible and API status is always `SUGGESTED`, with `confirmed_finding=false`; it is never silently presented as confirmed fraud, impact or programme risk.

Review records one immutable `VERIFIED`, `DISMISSED` or `ASSIGNED` decision with a reason and optional active human assignee. Dismissal and every other decision write feedback only: source results and evidence are never updated. Exact operation receipts make uncertain retries deterministic.

Migration 0091 creates tenant-fenced, insert-only configuration, suggestion and feedback records. `PROACTIVE_FINDINGS` remains reserved-disabled until combined qualification activates it. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
