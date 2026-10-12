# Release 0.71 candidate — governed dimension alignment

Coding-only candidate for **FR-CAL-007 / APL-583**.

Revisioned crosswalks pin exact current approved source and target indicator-definition revisions and named dimension versions. They distinguish exact, many-to-one pooling and proportional estimation, record information loss, and validate every category against the pinned schemes. Exact mappings permit no weights or declared loss; pooling requires explicit loss; proportional splits require a named estimation method and non-negative weights that reconcile exactly to one.

Preview reports mapped target values separately from every unmapped and suppressed source category. Broad-to-narrow splitting is possible only through reviewed proportional estimation. Source categories explicitly coded `UNKNOWN` or `UNK` can map only to an unknown target, preventing silent precision invention.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
