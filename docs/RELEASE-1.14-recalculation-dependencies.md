# Release 1.14 coding candidate — durable recalculation dependency impact

FR-CAL-011 / APL-421 extends each provisional-result invalidation with an immutable dependency inventory captured in the same tenant-locked transaction. The register names the exact stale result revision, its live-dashboard dependency and every current unpublished Report revision that exactly pins that result. Work-centre tasks show dependency counts while withholding report content and identifiers.

Recalculation continues to create a replacement result and immutable lineage, atomically resolve pending invalidations and update the live result selection. Locked snapshots and published exports remain bound to their original result revisions until an independently approved restatement. Exact command retries continue through the existing operation receipt.

Migration 0093 creates only the tenant-fenced insert-only dependency register and grants `impact_app` SELECT/INSERT.

The story-specific disposable live HTTP journey in `qualification/test_recalculation_dependencies_live.py` now proves the positive correction path: independent approval makes the original result stale, exposes one work item with the exact result and live-dashboard dependency counts, creates one fresh replacement, resolves the invalidation and returns the same completion receipt on an exact retry. The focused journey passed locally on 16 October 2026. This is positive-journey evidence only; CI, independent review, merge and deployment gates remain separate.
