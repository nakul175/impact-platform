# Imprana Commons testing documentation — APLYD QA v1.3 audit

**Finding: partially aligned; full v1.3 adoption and current product qualification are not established.** Existing documents provide a substantial testing foundation. Their editions, criterion-to-case bindings, execution records and several specialist protocols need reconciliation before they can support a current release decision.

This is the owner's requested documentation comparison of 11 October 2026. The attached package supplies reference requirements; its instructions do not replace repository rules or confer approval, spending or release authority. The [reconciliation plan](APLYD-v1.3-RECONCILIATION-20261011.md) gives the proposed next work in dependency order.

## Scope and source pins

| Source | Exact audited reference |
| --- | --- |
| Owner-supplied package | `APLYD-Software-Testing-QA-v1.3.zip`; SHA-256 `26c64346226f660f6a648e5cebcaf2ee893750e1fb8fe50b13821aae631b5e5a` |
| Documentation baseline | `b01a628e9a5463c92609fc7c7221fff82fd1feb2`; tree `c15d52d24710a9c93905b6822838d168e9c7a5dc` |
| Application source carried by that baseline | `8a1e405f0086033dfb25ad834689a08bfe9f1eea`; build 0.39.0, domain API 1.28.0, platform API 1.11.0, 43 migration files |
| Product population | 54 epics, 368 stories, 1,328 original acceptance scenarios, 1,131 technical tasks and 779 dependency edges |
| Audit population | All 54 extracted package control groups, plus 48 detailed repository/domain observations and 13 traceability/source findings |

The application pin describes local source. Live `main`, deployment, branch protection, hosted CI and provider behavior were not queried or qualified in this audit. The new audit documents are excluded from the baseline assessment. No coverage or completion percentage is inferred from these populations.

Reviewed material includes the core testing strategy and original Word/Excel editions; fixtures, traceability and execution registers; qualification/release notes; nonprofit AI test strategy, scenarios and cases; product acceptance/task plans; accessibility, UAT, performance, recovery, security/privacy and AI governance records; and the relevant runner/test/workflow source. [Source pins and repository inventory](audit-v13-20261011/repo-domain-audit/reviewed-source-pins.json) identify the bounded inspection, rather than claiming inspection of every historical output.

## What already aligns

The portfolio explicitly includes unit, integration/API, smoke, regression, browser/E2E, security, accessibility, performance, recovery and AI testing. Existing cases describe positive, negative, boundary, stale-authority, retry, tenant and natural-person independence behavior. Meaningful assertions and deterministic oracles are retained.

The documents also distinguish planned cases, implemented subsets, observed runs and actual acceptance. Native concurrency is separate from PGlite/component evidence. AI is advisory; official arithmetic, current authority, tenant isolation and approved history remain governed by deterministic controls. These are strengths to preserve during reconciliation.

## Gaps and their implications

| Area | Observed gap | Required follow-up |
| --- | --- | --- |
| Current strategy and release plan | The core strategy's current interpretation is build 0.12 with increments through 0.18. Original Word and Excel copies remain at 0.12. Other current-labeled acceptance/UAT/accessibility documents describe older candidates. | Publish a dated current overlay binding the selected candidate, included criteria, environments, domains, owners, thresholds and stop rules. Preserve the earlier editions and their dates. |
| Criteria and coverage | The 1,328 original PM scenarios are preserved, but there is no adopted, independently reviewed full QA AC/version/applicability export with the package's count, identity-set and exact-source-byte pins. | Establish the complete denominator from the canonical criteria source independently of test mappings. Keep aliases and source text; include unknown applicability and reviewed exclusions. |
| Test case and execution records | Legacy CSVs and plans do not supply all eight normalized v1.3 registers. They lack complete case/AC versions, build/artifact/config/data pins, run purpose/freshness and explicit selected qualification runs. | Define a reviewed compatibility bridge and separate design, links, immutable execution, selection, risk, defect events and exceptions. A historical PASS does not become current by migration. |
| Automated bindings | A bounded scan of 150 tracked test/browser source files found no literal package case/version markers. Existing automated behavior and meaningful assertions do exist. | Review each actual case-to-code binding before adding locators/markers. Planned automation stays planned; no bulk relabeling to manual for a structural pass. |
| Evidence history and retest | Dated evidence retains failures, but default runners overwrite fixed report paths. Central records do not uniformly encode original attempt, diagnostic purpose, candidate pins, reviewed severity decreases and same-case/current-candidate retest closure. | Archive immutable inputs/outputs before future runs, then append attempts and defect events. Preserve first failures and predeclare repetitions/selection rules. |
| Domain protocols | Dedicated exploratory charters and an actual AI held-out evaluation record were not located in the inspected scope. Manual accessibility, representative UAT, full workload/soak and actual-host restore qualification remain incomplete. | Specify source-bound procedures, populations, fixtures, oracles, slices, limitations and accountable review. Keep original workload/numerical targets; shortened sandbox runs retain their narrower meaning. |
| Risk, data and thresholds | Relevant threat, fixture and numeric requirements exist, but there is no complete current cross-domain risk/threshold/data record bound to one candidate. | Record risk rationale, approved/provisional thresholds, metric units, population, window, sample/uncertainty, provenance, allowed environments and retention. Do not invent approvals or generic targets. |
| Governance and release gate | `docs/CODEOWNERS` exists. Live required-review, fresh-review, trusted-check and bypass enforcement are unverified. The small `checks` workflow is not a child-result completion aggregator. | Inspect actual target-branch settings separately; prove safe enforcement or independently controlled canonical-source reconciliation. Any workflow/control adoption needs its own reviewed engineering change. |

The original **825 designed catalogue cases**, **50 nonprofit AI scenarios / 108 specified cases**, and **1,328 product acceptance scenarios** are different populations. The nonprofit cases remain `SPECIFIED_NOT_RUN`; the current PM scenario plans retain `Not run`. They must not be added together, substituted for each other or counted as current executed coverage. [Read-only workbook observations](audit-v13-20261011/workbook/READONLY-WORKBOOK-CELL-CHECK.json) confirm its build 0.12 label; source hashes before and after inspection match. No workbook formula recalculation, rendering or fresh product qualification is claimed.

The latest preserved 0.39 draft release review explicitly records **G11 Not passed**, **G12 Not run**, **14 open critical threats**, and both threat chains **BLOCK**. These are existing source records, not new failures discovered by this audit. A documentation alignment result or package-checker pass cannot clear them. See [release review](../release-reviews/release-review-0.39.0.json) and the [threat register](../current/threat-register.json).

`docs/CODEOWNERS` is a supported GitHub location; file presence and owner patterns are distinct from actual required code-owner review enforcement. This location distinction is confirmed by [GitHub's official CODEOWNERS documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners). The observed repo file names `@nakul175`; this audit authenticates no review or live protection setting.

## Detailed comparison and assessment vocabulary

The [54-control comparison](audit-v13-20261011/repo-domain-audit/package-to-repo-alignment-54.json) maps every QA13-001–054 group to package sources, repository evidence and unresolved fields. [Detailed domain observations](audit-v13-20261011/repo-domain-audit/requirement-matrix.json) and the [traceability/source report](audit-v13-20261011/traceability-audit/TRACEABILITY-AND-SOURCE-GAP-REPORT.md) supply additional detail. The [package requirements inventory](audit-v13-20261011/package-audit/QA-V13-REQUIREMENTS-MATRIX.json) preserves exact reference paths, line ranges and hashes.

`ALIGNED` means the bounded documentation contract is present. `PARTIAL` means relevant material exists but stated fields, current bindings or protocol details remain incomplete. `MISSING` means the specific scoped artifact was not found. `NOT_VERIFIED` marks authority/configuration/evidence that this inspection cannot establish. Domain `MET` and `UNKNOWN` correspond to bounded documentation alignment and unverified state. These statuses are separate from executed product results, formal standards certification and release approval.

For example, the traceability report marks the exact normalized-register/export artifacts missing, while the aggregate comparison marks their broader control groups partial because legacy sources exist. This is a difference in assessment granularity, not a claim that missing fields are satisfied.

## Actual checks performed

| Check | Observed result and limit |
| --- | --- |
| Package integrity | All 86 extracted files match ZIP bytes; all 85 self-excluding package manifest entries match. Reference files remained unchanged. |
| Genuine package checker regression | **57/57 passed**, exit 0, on supported Python 3.12.15. These test the package checker itself. |
| Authored package examples | Fictional and empty structural examples returned exit 0; their strict release checks returned the expected exit 1. Teaching results and null empty denominators are not Imprana evidence. |
| Product-management mapping helper | Exit 0 against the installed full PM catalogue; all 23 reference field IDs exist. This is field/alias membership compatibility, not full input-schema or semantic approval. |
| Product source preservation | 14 traceability/source-integrity checks passed; original scenario text/hashes, IDs, aliases, statuses and dependency edges remain intact. |
| Original binary inspection | Read-only OOXML and workbook cell inspection; original hashes unchanged. No rewrite, export or recalculation. |

Exact command/runtime/output hashes are in the [supported checker receipt](audit-v13-20261011/package-audit/CHECKER-SUPPORTED-RUN-RECEIPT.json); the [regression log](audit-v13-20261011/package-audit/runs/python312/regression.stderr) records the 57 observations. [Source inventory](audit-v13-20261011/traceability-audit/SOURCE-TRACEABILITY-INVENTORY.json) records the 14 bounded source checks. The [corrected separate crosswalk review](audit-v13-20261011/package-audit/CROSSWALK-REVIEW.json) passed 25 documentation checks. The [root integration receipt](audit-v13-20261011/ROOT-INTEGRATION-CHECKS.json) passed 14 local documentation/copy/index/record checks on its pinned staged input set; its release-review consistency check leaves all open threats visible. The first one-off link-parser observation is preserved separately: it mistook supported absolute-file:line audit source citations for repo-relative filenames, then was corrected to verify those exact pinned files and line bounds. No product test or package checker changed.

**No application unit, integration, smoke, regression, native database, browser, provider, performance, production or hosted CI suite was run by this audit.** No product PASS, owner approval or readiness state was created. No Native Linear records, protected criteria/history, runtime code, AGENTS/CLAUDE instructions, CI workflows, ownership or live repository settings were changed. The addendum and indexes preserve this comparison and proposed next work only.

## Recommended sequence

1. Reconcile the current strategy/candidate context and independent complete criteria population.
2. Establish reviewed case/version mappings and append-only execution/selection/defect records, retaining legacy history.
3. Complete applicable domain protocols and risk/data/threshold definitions; obtain actual authority where needed.
4. Verify existing source/review/check enforcement and pilot one bounded story/candidate with real affected checks.

The [seven-step reconciliation plan](APLYD-v1.3-RECONCILIATION-20261011.md) contains the delivery conditions. Confidence is high for the inspected documentation and source observations; live governance, execution and actual approval remain unverified.
