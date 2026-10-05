# Build 0.33 slice — deliberate programme evidence for AI plans

This local development increment implements a bounded part of FR-NPA-024 in the unified Tola and nonprofit AI platform. It connects an existing saved AI adoption plan to governed programme evidence. Requirement acceptance, hosted operation and user acceptance remain separate from this slice's local evidence.

## User behaviour

A manager chooses one currently authorised programme, indicator instance and reporting period, with an optional interpretation note. The server pins their actual revisions, the indicator's definition revision, the period's calendar revision and the latest locked programme-period snapshot when one exists. Link, refresh and clear each create a new immutable AI-plan revision. Unsaved plan edits must be saved or discarded before the interface changes this relationship.

The evidence view keeps the pinned official result separate from the current provisional calculation. If no snapshot existed when the link was saved, a later period close does not populate its official block automatically. An explicit refresh creates a new plan revision with the current source pins and latest authorised snapshot. Revision-change indicators explain when a saved source has since changed. Pilot notes and self-reported evaluations remain distinct from governed results; the link establishes no causal attribution to AI.

Current authority governs visibility of historical figures. Restricting a current target, collection plan or calculated result withholds its frozen block; the original snapshot and its arithmetic stay intact. Unknown or withheld values remain null or unavailable and are never converted to zero.

## Implemented routes and permissions

| Method | Route below `/v1/tenants/{tenant_id}` | Operation | Existing plan capability |
|---|---|---|---|
| PUT | `/ai-enablement/plans/{object_id}/impact-reference` | `set_ai_impact_reference` | `ai.enablement.manage` plus current plan read |
| GET | `/ai-enablement/plans/{object_id}/impact-reference/result` | `get_ai_impact_reference_result` | `ai.enablement.read` |

The closed command is `{operation_id, expected_revision, data}`. `data` is exactly `{programme_id, indicator_id, period_id, interpretation_note}` or null for clear. Notes are bounded to 1,000 characters. Client-supplied IDs select records; they never establish authority. New links and refreshes require current read authority over the actual programme, indicator, definition, period and calendar, the actual programme dashboard scope, and any selected snapshot. The server verifies programme/indicator membership, calendar pins and period containment within the programme dates.

Only a currently authorised linked result returns the closed `AIImpactReferenceResult` DTO, with non-null `reference`, `reference_status`, `period` and `indicator`. An absent, hidden, malformed or unverifiable private reference returns the same opaque `RESOURCE_UNAVAILABLE` 404. This applies even when dashboard access is scoped to a different programme. The interface uses “No programme evidence is available to show” and supplies no inferred linkage badge.

Clear requires current plan read/manage and can succeed after core read access is revoked. Exact replay checks current plan authority and returns the original label- and value-free mutation receipt before revalidating current core content. Its receipt contains the plan object/revision, operation, state, saved time and correlation only.

## Private metadata dictionary

`impact_reference` is optional server metadata inside the existing immutable `AIAdoptionPlan` payload; explicit clear stores null. It introduces no tenant table or migration. Ordinary plan get/list project it out, and the closed generic client DTO cannot supply it. Generic edits deliberately retain the previous private value, including null. The dedicated result is the only response that exposes its core selectors and pins after current authority checks.

| Private field | Representation and meaning |
|---|---|
| `schema_version` | Exact `nonprofit-ai-impact-reference-v1` constant |
| `programme_id`, `programme_revision` | Programme UUID and deliberately pinned revision UUID |
| `indicator_id`, `indicator_revision` | IndicatorInstance UUID and pinned revision UUID |
| `definition_id`, `definition_revision` | IndicatorDefinition UUID and revision the pinned instance uses |
| `period_id`, `period_revision` | Period UUID and pinned revision UUID |
| `calendar_id`, `calendar_revision` | ReportingCalendar UUID and revision the pinned period uses |
| `snapshot_id`, `snapshot_revision`, `snapshot_version` | Exact locked programme-period binding; all null when no snapshot was pinned; edition is a positive integer |
| `interpretation_note` | User interpretation text, at most 1,000 characters |

No numeric result is copied into this metadata. The read model reuses the governed dashboard cell, including stored decimal precision, display rounding, official/provisional separation, approved target/baseline comparisons, coverage and source freshness. It additionally verifies current returned result, target and collection-plan authority. Reference statuses are `CURRENT` or `CHANGED` for the five core pins, and `CURRENT`, `CHANGED` or `ABSENT` for snapshot selection.

## Atomicity and actual historical guidance

The dedicated write takes the tenant advisory lock before resolving current write authority, then the operation lock. Plan head/revision, verified existing guidance binding, audit/outbox and insert-once receipt commit together. Changed payloads under an existing operation ID conflict; stale revisions conflict; expired receipts are refused. A failed binding or audit step rolls back the entire save. Concurrent exact commands are qualified separately on native PostgreSQL.

A relationship edit retains the previous plan's catalog/solution/practice versions and inputs. It inherits only the previous revision's actual verified guidance archive. If no archive existed, the new relationship revision also has no archive; no old wording is reconstructed and no current guide is stamped as an earlier edition. The underlying archived catalog already includes its learning content.

## Local evidence status

The integrated pure suite passes 149 checks: 51 impact-reference regressions, 93 existing adoption/planning/archive checks and five version checks. Raw evidence is `docs/evidence/nonprofit-ai-impact-reference-unit-tests.xml`. It covers private projection and generic retention, forged private fields, immutable pins, exact retries, atomic rollback, truthful guidance inheritance, current core authority and absent/hidden/corrupt lookup equivalence.

The final focused real-API suite passes 104 checks with four explicit native-only skips and no failures or errors. Raw evidence is `docs/evidence/nonprofit-ai-impact-reference-api-tests.xml`; `nonprofit-ai-impact-reference-api-qualification.json` binds unchanged source hashes and confirms exact restoration of shared baseline reports. `nonprofit-ai-impact-reference-applied-migrations.json` records all 38 migrations actually applied. This covers the 26 impact cases plus existing adoption, planning and content-archive integration. The first actor-selection failure and second audit-fixture comparison failure are retained under distinct attempt names; both fixture corrections preserve existing capabilities and exact mandatory audit/outbox/receipt assertions. Native contention, full regression, browser and hosted acceptance remain separate scopes. No original requirement is marked accepted by these local checks.

The initial current-classification diagnostic reproduced restricted Target, CollectionPlan and CalculatedResult blocks in older dashboards despite direct current GET returning 404. Its original three-case evidence is retained in `docs/evidence/nonprofit-ai-dashboard-visibility-reproduction.json`; a passing diagnostic count describes reproduction, not a security fix. The shared core fix is qualified by independent current-classification and current-head cases while asserting unchanged historical payload hashes and original values.

The subsequent retained-wording diagnostic independently reproduced IndicatorDefinition and Framework leaks under both current classification and current-head restriction. Original evidence remains in `docs/evidence/nonprofit-ai-retained-label-visibility-reproduction.json`. The minimal shared guards retain the exact historical payload query and verify current source authority before returning its wording. The strict four cases, the preceding six current-value visibility cases, and adjacent dashboard/planning/measurement/impact checks pass 95 checks with two explicit native-only skips (97 total). Named evidence is `docs/evidence/sprint-0.33-retained-visibility-pglite-tests.xml`; source hashes were unchanged during that run, all 38 applied migration hashes matched and shared reports were restored. `sprint-0.33-retained-visibility-promotion.json` records the byte-identical promotion to the collected regression module. These overlapping focused runs are separate evidence scopes and their counts must not be added as distinct product coverage.

The final schema39 local gate passes 96 checks with two explicit native-only skips (98 total), including the ten current-value/wording cases, the additional exact-old-Framework-pin case and adjacent governed/impact integration. Its frozen focused copies are `docs/evidence/sprint-0.33-retained-visibility-schema39-focused-tests.xml`, `-source-proof.json` and `-applied-migrations.json`. All 39 observed migration hashes matched, source was unchanged throughout and shared baseline reports were restored exactly. Earlier schema38 evidence remains under `sprint-0.33-retained-visibility-initial-current-guards-*`. Native/backend role checks, browser and full release regression remain separate evidence scopes.

The exact-old-Framework-pin fixture is explicitly a storage-valid append-only negative. It inserts an unavailable historical revision/register and a readable current head while leaving foreign keys and immutable triggers enabled; it does not claim a supported approval or Framework privacy API workflow. The latest and open-period governing wording is withheld. The locked row pinned to a separate available baseline keeps its original nodes and `46.363636363636` value with unchanged snapshot hashes. Red before-fix evidence remains in `sprint-0.33-framework-old-pin-red-*`; the passing module was promoted byte-identically to `qualification/test_framework_old_pin_visibility.py`, recorded by its named promotion proof.
