# Imprana Commons current testing edition

Prepared 11 October 2026 after the [QA v1.3 documentation audit](../APLYD-v1.3-AUDIT-20261011.md). Status: **SOURCE-BOUND PLANNING EDITION; adoption/qualification/approval unresolved**. Documentation baseline `c1bcae29718bcae0fac51000d69734a536061fba`; application source `8a1e405f0086033dfb25ad834689a08bfe9f1eea`. Source build 0.39.0, domain API 1.28.0, platform API 1.11.0, schema 43. These pins describe local source; live deployment and candidate qualification remain unverified.

This edition makes the next QA work concrete. It supplements the stale current-interpretation sections in earlier test editions while preserving their original criteria, numerical targets, dated results, Word/Excel copies and historical evidence. It does not replace the repository's authority or product requirements. No new release, sprint, role assignment, supported platform, spending, production or real-data permission is selected by writing these documents.

## Read in this order

1. [Current test strategy](CURRENT-TEST-STRATEGY.md): portfolio, scope, risk and affected-check selection.
2. [Release test plan](RELEASE-TEST-PLAN.md): candidate inputs, entry/exit conditions, execution order and actual decision dependencies.
3. [Test data and environments](TEST-DATA-AND-ENVIRONMENTS.md): synthetic fixtures, environment profiles and evidence boundaries.
4. [Criteria and case bridge](CRITERIA-AND-CASE-BRIDGE.md): canonical source, aliases, version policy recommendation and case/run relationships.
5. [Execution and defect protocol](EXECUTION-AND-DEFECT-PROTOCOL.md): immutable attempts, result/freshness separation, defect retest and exceptions.
6. [Specialist verification plans](SPECIALIST-VERIFICATION-PLANS.md): concrete manual accessibility, UAT, exploratory, AI quality, performance and recovery procedures.

Use the source-bound [product continuation](../../product/framework-v4-20261011/START-HERE.md) and original Ready/Done rules alongside this edition. Do not infer that documenting a procedure makes a story Ready, a test run passed or a requirement accepted.

## Decisions and recommended defaults

| Decision | Recommendation for preparation now | Required evidence before dependent qualification |
| --- | --- | --- |
| Working data/environment | Isolated development with synthetic fixtures; preserve deterministic/manual fallback | Actual candidate, fixture hashes, current roles, independent reviewers, tool/environment pins and authorised scope; native/browser/provider evidence remains separate |
| Criterion revision identity | Preserve canonical AC/story IDs and source text; use an explicitly proposed source-hash revision scheme for future reviewed export | Source-owner-approved revision/applicability/scope rules plus independent complete canonical export and pins; no version is invented in this edition |
| Operating release/slice | Retain existing release-goal allocations and proposed Sprint 2 candidates | Actual included population, dependencies, capacity, candidate artifact/configuration and owner decision; no smaller slice silently qualifies all R1 stories |
| Platforms/locales | Retain the original target matrix and record current observed limitations | Actual supported profiles/versions at release and reviewed exclusions; historic Chromium evidence does not qualify other profiles |
| Quality thresholds | Carry original source targets forward exactly; design measurements and uncertainty | Applicable threshold/version/population/window/repetition and real decision authority; no smaller local measurement replaces a target |
| Corpus/provider/UAT/specialist execution | Prepare synthetic protocols and safe data/label/consent design | Actual permitted participants/data/provider/region/reviewer, financial authority when required, predeclared oracles and immutable attempt records |
| Source/review enforcement | Keep existing `docs/CODEOWNERS`; inspect actual enforcement separately | Trusted source completeness and review/check/bypass configuration with real evidence; local consistency cannot authenticate it |

These decisions are bounded recommendations. There is no fake owner signature or expiry date. Unknown applicability remains unknown; an unresolved required gate cannot become an approved exclusion.

## What this closes, and what remains

This edition supplies a current source context and usable strategy, candidate-plan, environment, bridge, execution and specialist procedures. Its exact source observations and separate document review are preserved under `evidence/` when performed. Documentation adequacy and execution evidence remain separate.

The [primary-source census](evidence/PRIMARY-SOURCE-CENSUS.json) preserves the 1,328 active scenario identities/texts and seven retained historical scenarios, plus the alias/source observations. Its [authoring receipt](evidence/BRIDGE-AUTHORING-RECEIPT.json) records scope and exact bytes. These are source observations, not a reviewed canonical QA export, human approval or product execution.

The complete independently reviewed AC/version export, reviewed case/code bindings, normalized execution/selection records, actual environment/corpus/UAT qualification, human reviews and live enforcement remain open. The current draft 0.39 source still contains G11 Not passed, G12 Not run, 14 critical and 13 other open threats, and two BLOCK chains. No threat is closed here.

**Next implementation step:** establish one bounded story's actual source/oracle/version/case bindings, satisfy its Ready prerequisites, then run its genuinely affected checks in an authorised isolated environment while preserving first failures. Broader regression, native/provider/operating checks and actual release decisions follow the selected scope and existing authority. No hosted or paid actions are started by this documentation step.

## Recorded document checks

The separate [bridge/source review](evidence/bridge-independent-review/REVIEW-RECEIPT.json) records 19 source/contract checks; the separate [six-document review](evidence/current-doc-review/INDEPENDENT-CURRENT-QA-DOCUMENT-REVIEW.json) records 33 source/document checks and binds the added risk-scoring paragraph. Both found no blocking documentation defect in their bounded scope. These are AI reviews, not appointed specialist review, source-owner completeness approval, product test results or release acceptance.

The [initial root integration observation](evidence/ROOT-INTEGRATION-CHECKS.json) records 14 source-only checks before the risk paragraph was added; it remains dated history. The [first final-integration observation](evidence/ROOT-INTEGRATION-FINAL-CHECKS.json) retains its 13/14 result: this README linked that receipt before the copy existed. The missing copy was then saved; a separate `ROOT-INTEGRATION-POST-LINK-CHECKS.json` observation in the [evidence directory](evidence/) pins the resulting document bytes. The [first review-adapter observation](evidence/current-doc-review/INDEPENDENT-CURRENT-QA-DOCUMENT-REVIEW.initial-adapter-observation.json) preserves two parser/locator errors; only those review adapters were corrected, with no weakened source requirement or product-test result inferred.

Archived review helpers are records of these bounded observations, not installed product runners or adopted QA gates. Reproduction requires fresh owned output destinations; do not run over retained receipts. GitHub/Linear publication of this new QA edition and actual product execution remain pending.
