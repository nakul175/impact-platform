# Mercy Corps TolaData reuse trial

**Implementation after the trial (5 October):** local branch `release/0.29-logframe-reuse`
now adds the governed approved-logframe CSV/XLSX export described in
[RELEASE-0.29-logframe-reuse.md](../RELEASE-0.29-logframe-reuse.md), with direct header-style
adaptation, license/notice and 17 passing export tests. The full local run has seven baseline
Linux-tool failures on macOS; qualification details are in [QUALIFICATION.md](../QUALIFICATION.md).
No merge, deployment or requirement acceptance. The trial findings below retain their original scope.

5 October 2026. Impact Platform baseline: `5676e02ef48a1f3f98db5a851dcdcc37ba9c6b55`
(main, including PRs #81–#83). Upstream baseline:
[`7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d`](https://github.com/mercycorps/toladata/tree/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d)
(3 November 2022). Local trial branch: `qa/2026-10-toladata-reuse`.

## Finding

The strongest reuse opportunities are reporting layouts, results-framework export scenarios,
indicator tracking views and regression scenarios. This is useful prior domain work, but not a
drop-in application: upstream uses Django ORM, Django permissions and MobX, while this platform
uses FastAPI, tenant-fenced PostgreSQL, immutable reviewed revisions and a React client.

High confidence in the inspected source and the offline checks. Medium confidence in estimated
feature savings: no complete feature has yet been ported. No production runtime code changed,
no staging deployment was attempted and no requirement status changes are proposed.

## Source-backed reuse map

All upstream links below are pinned to the inspected commit, rather than a moving branch.

| Candidate | Upstream evidence | Fit here | Concrete adaptation |
|---|---|---|---|
| Logframe / results-framework XLSX export | [export scenarios](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/tests/test_rf_export.py), [cell styling](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/xls_export_utils.py) | Best next feature candidate; backlog slice 5 includes a missing logframe export | Adapt hierarchy layout and test cases; supply approved framework revisions, assumptions and exact indicator bindings from our own service. Require separate export authority, audit, safe cell text and deterministic bytes. Reuse our current styling, not Mercy Corps branding. Do not copy the old merged-cell workaround without proving it is still necessary. |
| Indicator Performance Tracking Table (IPTT) | [renderer](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/export_renderers.py), [scenario matrix](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/tests/iptt_tests/scenarios.py) | Useful for backlog slice 2 and FR-ANA-003, already PARTIAL | Adopt baseline / target / actual / period columns and empty-data scenarios. Render pinned OFFICIAL snapshots and clearly separate provisional values. Never reconstruct historic reports from mutable current rows. |
| Cumulative indicators and target semantics | [target queries](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/queries/targets_queries.py), [indicator model](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/models.py) | Reuse scenario vocabulary, not query arithmetic | Distinguish summing flows over several periods from already-cumulative positions. Our LAST_VALID/CUMULATIVE method covers the latter only; cumulative target comparisons remain separate work. |
| Reporting calendars and boundary cases | [period-generation tests](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/tests/test_generate_periodic_target.py) | Useful regression inputs for existing reference-data functionality | Translate upstream date-only inclusive ends into our UTC instant / half-open boundaries. Add leap-year, partial-period and calendar-overlap scenarios to the relevant tests. Do not copy date arithmetic unchanged. |
| Framework ordering and unassigned indicators | [ordering tests](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/js/models/__tests__/program.rfLevelOrdering.test.js) | Useful display / export acceptance scenarios | Adapt order and empty-group cases to stable node IDs and versioned framework nodes. Changes still require a superseding reviewed draft. |
| Multilingual reporting | [language tests](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/indicators/tests/iptt_tests/iptt_excel_export_functional_language.py) | Test inspiration for backlog slices 6 and 10 | Reuse accented-label and translated-header scenarios. These are not a Devanagari PDF font solution or a complete React message catalogue. |
| Kobo/ONA connector | No matching provider implementation found by word-boundary search of tracked Python and JavaScript source, excluding built bundles | No reusable connector established in this trial | Keep the planned connector on our executor and its independent SSRF, credential and authority controls. Current commercial TolaData capabilities do not prove their presence in this older Mercy Corps repository. |

## First adaptation executed

Added `tools/reuse/toladata_probe.py`: twelve independently authored synthetic checks inspired by
upstream IPTT scenario families, executed against the actual `impact_api.domain.calculate` function.
The tool needs only Python's standard library and reads local source; it makes no external request,
database connection, authentication attempt or write to application data.

Executed on 5 October 2026: **12 passed, 0 failed, 0 errors**.

Covered: no data; one and several flow results; zero versus missing; exclusion of unapproved rows;
latest cumulative position; refusal of cumulative decline; event ordering; conflicting latest
positions; pooled percentages; undefined zero denominator.

The important incompatibility is explicit: upstream's target query uses the latest achieved
percentage for a period. Our pooled example `50/100 + 1/10` must display **46.36**, neither the
latest **10** nor the average **30**. No automatic mapping from upstream percentage values is safe
without their meaning and original components. The trial protects our behavior instead of importing
the upstream query.

These are offline compatibility checks, not a port of IPTT or evidence of API authorisation,
period membership, snapshot freezing, staging health, throughput or release acceptance. Several
cases overlap existing golden tests; their value here is an explicit reusable source comparison.
The trial is outside the normal qualification suite until a feature adaptation needs these cases.

Reproduce from the repository root:

```sh
python3 tools/reuse/toladata_probe.py
```

## Recommended next implementation

Start with a governed logframe export, the most concrete missing feature demonstrated by the
inspected code. Adapt the upstream hierarchy scenarios and workbook layout into our export path;
do not add an upstream Django service or its permission model.

Inputs: one visible programme and an exact approved framework revision, its typed hierarchy,
approved indicator bindings and assumptions. Outputs: CSV/XLSX with explicit revision context and
a readable hierarchy. Any targets and actuals must be pinned to an explicitly selected snapshot;
do not silently join current targets into an old export.

Acceptance checks: hidden programme and hidden linked indicator cannot leak; read alone cannot
export; approved revision survives later amendments; Unicode labels, empty tiers and deep trees;
formula-injection protection; deterministic content; audit and exact retry. Persistence, contracts
and release documentation follow AGENTS.md if the implementation adds operations or jobs.

This recommendation does not supply the other parts of backlog slice 5 (a governed indicator
library and external standard mappings). Neither their status nor the completion ledger changes.

## Attribution and publishing boundary

Upstream's [LICENSE](https://github.com/mercycorps/toladata/blob/7ca89ab1e5f55cbe4577d16d7281c6cf0936fc3d/LICENSE)
is Apache 2.0. This trial imports no upstream code, assets, datasets or dependencies; the checks
are newly written and the scenario inspiration is attributed. Any subsequent literal code reuse
must retain applicable notices, include the license and mark modified files; check the individual
files and any third-party assets before copying them.

Changes remain local and reviewable. No paid CI was triggered and nothing was pushed or merged.
AGENTS.md requires owner confirmation before spending CI minutes or merging into auto-deploying
main. This trial does not need a deployment to establish its findings.
