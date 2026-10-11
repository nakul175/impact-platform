# Imprana Commons criteria and case bridge

Status: proposed planning contract, 11 October 2026. This document reconciles the original source at `c1bcae29718bcae0fac51000d69734a536061fba`. It creates no criteria export, normalized register, test case, execution, Native issue or source-owner approval. All existing scenario plans remain **Not run**.

The [QA audit](../APLYD-v1.3-AUDIT-20261011.md) found separate gaps in source completeness, versions, case bindings and current qualification. The recommendation is to settle their contracts before producing a checker-ready export. A checksum or an agent-authored plan cannot supply the missing source-owner decision.

## 1. Enumerate the original source before consulting test plans

The primary enumeration source is [backlog.csv](../../backlog/backlog.csv), specifically its original `Acceptance and rejection criteria (Gherkin)` field. Its [source README](../../backlog/README.md) defines 368 active stories and two retained `Split` parents. Do not derive the denominator from the acceptance-to-task matrix, test catalogue, case mappings or passing tests.

| Population at the pinned source | Observed count | Treatment |
| --- | ---: | --- |
| All original CSV story records | 370 | Preserve every record. |
| Active stories | 368 | The existing planning population, across all release buckets. This is not a selected operating release. |
| Original scenarios in active stories | 1,328 | Reconcile each scenario independently with the existing aliases. |
| Retained Split parents | 2 | `FR-AI-016` and `US-DX-01` remain historical source records. |
| Scenarios in those Split parents | 7 | Preserve as history; do not count again as active criteria. |
| Scenarios across all 370 CSV rows and the 54 feature files | 1,335 | Includes the seven historical parent scenarios. The feature files are specifications without step definitions, not executed tests. |
| Existing proposed technical tasks / prerequisite edges | 1,131 / 779 | Keep their IDs, story parents and every edge intact. |

The source CSV SHA-256 is `6cd4d418dbaf3ec09675947bce0f7840ccc97c3ede9ab3d882202dd6b6ceacbd`. The existing [criterion alias map](../../product/framework-v4-20261011/bundle-review/CRITERION-ALIAS-MAP.json) SHA-256 is `279c1bec0920f02dba67f43cb6fcb6ce5f2fa311c79dc98dc18ac0a4f29c99ee`.

The separate `PRIMARY-SOURCE-CENSUS.json` observation records the exact Git/source hashes, all story and scenario identities, seven historical scenarios and 1,328 reconciled alias records. Its source-only checks establish that the original scenario blocks concatenate back to each full Gherkin field exactly. They establish source preservation, not scope approval or product acceptance.

## 2. Preserve identity, text and existing aliases

The original CSV gives stable story IDs and scenario text. The [existing acceptance matrix](../../product/framework-v4-20261011/task-author/acceptance-task-matrix.proposed.json) and alias map provide supplementary local anchors for those same scenarios: the task-matrix `AC-…` ID, the story annotation ID and the `EVAL-…` plan ID. These aliases are not three criteria. Preserve the aliases and their source hashes rather than allocating a replacement acceptance population.

Use `(source story ID, scenario ordinal, exact source block hash)` to reconcile the retained snapshot. Preserve the entire original story Gherkin and its hash as well. An ordinal alone is insufficient after a source change. Do not trim, reflow, normalize whitespace or reorder original scenarios; the retained block convention includes the original separator/newline allocation. The source blocks must reconstruct the full original field byte for byte.

The 37 original scenarios without `Given`, seven groups of supplemental test-plan assertions and 13 stories without a qualification-kind task remain explicit gaps. The [task-author notes](../../product/framework-v4-20261011/task-author/README.md) distinguish proposed context, supplemental assertions and proposed verification duties from original Gherkin. Those supplements do not replace source `Then` clauses, create additional accepted criteria or introduce new task dependencies.

ACs and technical tasks keep their actual story parents. A task's proposed verification duty is a link to an AC, not a hierarchy change. Cross-release epics remain references to existing objects; do not duplicate epics or Native issues to make the QA chain look like a new backlog.

## 3. Define the future export without inventing versions or review

The attached QA v1.3 contract is `templates/criteria-source.json`, under ZIP SHA-256 `26c64346226f660f6a648e5cebcaf2ee893750e1fb8fe50b13821aae631b5e5a`. It requires these source fields:

| Export field | Required basis before a real export is used |
| --- | --- |
| `source_id` | An agreed canonical source identity, with the original CSV and alias provenance retained. |
| `source_version` | The reviewed source-snapshot/version convention. Record the exact Git commit and source bytes; a documentation edition is not automatically a criterion revision. |
| `scope_id` | The actual reviewed planning scope or operating candidate. The full active backlog census does not select a release. |
| `review_ref` | The actual source-owner completeness/applicability decision. An agent name, placeholder or local checksum is not that decision. |
| `criteria` | Every criterion in the selected source scope, including unresolved and reviewed exclusions. |

Each criterion requires `ac_id`, `ac_version` and `applicability` (`YES`, `NO` or `UNKNOWN`). Preserve the existing same-scenario IDs/aliases and source text in the accompanying provenance bridge. The checker checks identity/version/applicability consistency; it does not evaluate the Gherkin or authenticate its completeness.

No original per-scenario AC version is declared in the primary CSV or alias map. Do not fill `ac_version` with an invented `v1`, the document edition, a task status or an apparent test version. Recommend a **proposed source-hash revision policy**: an immutable, validly encoded revision identifier derived from the exact original scenario block digest, with the full story/source digest also retained. This records actual content identity, but the namespace, version policy and treatment of changed scope/applicability still need the real source owner's decision. It is not an already approved convention.

Applicability also needs its own scope decision. Unknown stays `UNKNOWN`; it is not silently changed to `YES` or excluded as `NO`. A `NO` exclusion needs scope-covering source, rationale and actual review. Even an unchanged text hash cannot approve a changed release population.

**Current decision: do not generate a checker-ready `criteria-source.json` or normalized register population yet.** The source census and this design can be preserved now. The missing scope/version/completeness/review fields stay unresolved rather than being manufactured to obtain structural success.

After those decisions exist, store the reviewed canonical snapshot inside the controlled local evidence root. A proposed future location is `docs/qa/evidence/<reviewed-scope>/<reviewed-source-version>/criteria-source.json`; it is a design path, not an existing artifact. Set `criteria_source_ref`, exact source-byte SHA-256, full `expected_ac_count`, sorted `[ac_id, ac_version]` identity-set SHA-256 and `criteria_source_review_ref` in the separate scope record. Count includes `YES`, `NO` and `UNKNOWN`.

The package helper `checker/criteria_pin.py --source <reviewed-export>` prints candidate pin values only. It does not write a scope or approve the source. Its identity-set hash uses lexicographically sorted pairs, JSON `ensure_ascii=False` and `separators=(',', ':')`, UTF-8 with no trailing newline. The source-byte hash covers the exact saved export bytes. Neither hash can detect a source omitted before the export, so independent completeness review remains necessary.

## 4. Bridge criteria to existing cases before allocating new ones

The original 825-case workbook, 50 nonprofit AI scenarios / 108 specified cases and 1,328 active product scenarios have different units and overlapping purposes. Do not join them by row number, similar title or matching totals. Preserve their original IDs, versions where actually declared, historical statuses, expected outcomes and evidence links.

For each proposed criterion-to-case link, record:

1. The exact source criterion/alias and revision convention, once resolved.
2. The existing case ID and actual procedure/version; retain its original requirement references.
3. The specific source outcomes it covers, fixture/actor/current-authority boundary and prohibited side effects.
4. Whether it is required for this criterion and actual scope, with any exclusions or gaps made explicit.
5. The real manual procedure or reviewed automated locator and case/version marker, when implemented.

A similar existing case can be a reuse candidate without yet being a validated mapping. Multiple cases may be required for one AC; a case may cover several ACs only when it asserts each linked outcome. Existing automated assertions remain intact. File presence, a test name or a proposed primary verification task is not execution evidence.

Only allocate a new case when reviewed comparison identifies an uncovered source/risk outcome. Use collision-resistant `TC-<scope>-<unique>` identity and an explicit reviewed immutable case version; do not allocate by CSV row count. An unimplemented automated binding stays unbound. Do not relabel it manual or add a decorative marker merely to satisfy a checker. Manual cases need a concrete procedure and the required actual environment/reviewer.

No cases, code markers or bindings are created by this document.

## 5. Link actual runs and retests without rewriting history

Case design, AC-to-case links, immutable executions and selected qualification runs are separate records. A designed case has no execution row until an actual attempt. Missing selected run derives `NOT_RUN`.

A later run must retain the exact AC/case versions, operating candidate source/artifact/configuration/environment/data/tools, procedure, executor, timestamps, expected and observed outcomes, evidence and purpose. Select `QUALIFICATION` explicitly; diagnostics do not replace failed qualification. Keep every first failure, uncertain attempt, retry, skip and blocked result. Latest timestamp alone is not a safe selection rule.

Historical `PASS` is not automatically `CURRENT`. Reuse needs documented relevance to the selected source/case/candidate; missing pins remain unassessed. Changing source, mappings, case or environment versions invalidates affected selections through a reviewed change. A later fix creates a new run and defect event; same-case current passing qualification on the actual candidate is required for closure, with original failure retained.

Current coverage cannot be inferred from the counts in this document. For a future reviewed scope, the complete AC inventory is the denominator; all required mappings must select matching `PASS/CURRENT/QUALIFICATION` evidence for validated coverage. Unknown applicability remains conservative and never validates. A zero denominator is null, not 100%.

## 6. Preconditions for the next bounded pilot

Proceed with one existing story only after its actual source scope/version/applicability, case procedures/oracles, dependency outputs, synthetic data and environment authority are available. Keep the full source catalogue visible; a one-story pilot does not certify all 1,328 criteria or silently narrow a release denominator.

Before real release reliance, verify independent source-review protection or trusted external canonical-source reconciliation. The supported `docs/CODEOWNERS` already exists; live required-review and bypass settings remain unverified. This planning work changes no owner configuration, AGENTS/CLAUDE instruction, CI workflow, Native metadata, application code, applied migration, historical binary, spending permission or release authority.

Reference package contracts: `workflow/CRITERIA-SOURCE-PINNING.md:2–24`, `workflow/TRACEABILITY.md:2–13`, `workflow/CODE-IDS-AND-CONCURRENCY.md:2–11`, `checker/criteria_pin.py:8–17`. They are pinned attachment references, not files installed by this proposal or proof of owner approval.
