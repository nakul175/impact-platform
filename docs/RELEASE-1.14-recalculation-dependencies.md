# Release 1.14 coding candidate — durable recalculation dependency impact

FR-CAL-011 / APL-421 extends each provisional-result invalidation with an immutable dependency inventory captured in the same tenant-locked transaction. The register names the exact stale result revision, its live-dashboard dependency and every current unpublished Report revision that exactly pins that result. Work-centre tasks show dependency counts while withholding report content and identifiers.

Recalculation continues to create a replacement result and immutable lineage, atomically resolve pending invalidations and update the live result selection. Locked snapshots and published exports remain bound to their original result revisions until an independently approved restatement. Exact command retries continue through the existing operation receipt.

Migration 0093 creates only the tenant-fenced insert-only dependency register and grants `impact_app` SELECT/INSERT. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
