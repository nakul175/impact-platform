# QA v1.3 documentation audit records

Read the [audit](../APLYD-v1.3-AUDIT-20261011.md) and [proposed reconciliation plan](../APLYD-v1.3-RECONCILIATION-20261011.md) first. This folder preserves reference requirements, source observations, the complete 54-control comparison, checker observations and separate audit reviews. It contains no adopted live AC/case/run/selection register population.

- `package-audit/`: 54 extracted reference controls, unchanged package-checker observations on supported Python, authored teaching-example outputs, and separate crosswalk review.
- `repo-domain-audit/`: corrected final domain findings, inventory, source pins and exact baseline comparisons. `docs/CODEOWNERS` exists; actual enforcement remains unverified.
- `traceability-audit/`: source census and gaps; original criteria, task relationships and statuses stay intact.
- `workbook/`: read-only Excel/Word observations; the binaries remain unchanged.
- `COPY-MANIFEST.json`: exact-byte provenance for selected copies. Local absolute source paths identify the originating observation; they do not authenticate a decision owner or make those paths portable evidence roots.
- `ROOT-INTEGRATION-CHECKS.json`: bounded local documentation/copy/index/record checks on the pinned staged input set. Its initial link-parser observation is preserved separately; valid absolute-file:line audit source citations needed explicit pinned-source handling. Product tests and the package checker were not changed.

The package ZIP and extracted reference remain outside this audit folder. They are pinned by the archive SHA and per-file source inventory; no full package installation is implied. The package's source citations can be reconciled against those exact ZIP bytes.

The preliminary crosswalk review preserves a detected CODEOWNERS-location error. The active final domain matrix/crosswalk and final review correct it. Earlier sealed outputs remain in the originating audit output directory as superseded observations; their mistake is not a current finding.

Checker examples are explicitly fictional teaching data. Their authored PASS/FAIL values and expected release-mode rejections are not Imprana test executions. Audit checks and reviewer reports are agent-authored documentation evidence; they do not stand in for authenticated human approval or current product release gates.
