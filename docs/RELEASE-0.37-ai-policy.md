# Build 0.37 explicit AI enablement and policy (FR-AI-001)

9 October 2026 · Local candidate on branch `sprint-1/fr-ai-001`, committed locally only (not pushed, merged or deployed) · build 0.37.0 · domain API 1.26.0 · platform API 1.10.0 (unchanged) · schema 41 (migration 0041) · 264 implemented domain operations (261 + 3).

An organisation administrator can now say exactly which AI use is allowed before anything is sent to a provider. AI runs only when three switches are on: the server switch (`ai_enabled` with a configured provider), the organisation's policy in force, and the use case inside it. Every change is a new, audited policy version; nothing is edited in place. Everyone who can read AI enablement sees a "Policy in force" card before the advisory request button, and every request names the policy version it was made against. Hosted CI has not run on this branch and nothing here is accepted: FR-AI-001 is "In review" in the backlog, not Done.

## Delivered behaviour

1. **Policy versions.** `PUT /v1/tenants/{t}/ai-enablement/policy` stores the next version (1, 2, 3 … without gaps) as the next immutable revision of the tenant's single `AIConfiguration` object, plus insert-only rows in `ai_policy_version` and `ai_use_case_policy`. It needs the new capability `ai.policy.manage` (TENANT_ADMIN only), authentication within the previous 300 seconds plus the configured assurance (the existing `store.authorize` policy-row mechanism), the tenant write lock, `expected_version` and an operation ID. Revision, audit event `ai_policy.changed`, outbox intent and receipt commit in one transaction.
2. **Rules per use case:** enabled; data classes (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED); destinations from a closed provider-and-region list (only `openai-us`, the existing adapter); approved purposes; languages (BCP 47); review mode (`HUMAN_REVIEW` only); budget units (0–1,000,000); tools (always empty). An enabled rule needs at least one class, destination, purpose and language. A use case that is not listed is off.
3. **Reserved use cases.** EXTRACTION, REPORT_DRAFT and CHAT may be recorded only as off (`AI_USE_CASE_RESERVED`), so nothing is pre-approved for features whose data flows are not designed. Any tool is refused (`AI_TOOLS_NOT_ALLOWED`), in the API and by a database CHECK.
4. **The gate.** `create_ai_advisory` reads the policy in force under the tenant lock after the replay lookup and before the daily-limit count, any reservation or any provider call. Order: server switch off → 503 `AI_NOT_CONFIGURED` (unchanged); request pinned to another version → 409 `CONFLICT_VERSION` / `AI_POLICY_CHANGED`; use case off or no policy → 503 `SERVICE_UNAVAILABLE` / `AI_USE_CASE_DISABLED` (same envelope as not-configured); any unmet rule → 422 `VALIDATION_FAILED` / `AI_POLICY_BLOCKED` with a message naming each rule. A brief marked "involves sensitive data" is CONFIDENTIAL, otherwise INTERNAL; the destination is the adapter's (`OpenAIAdvisory.destination = "openai-us"`); the English draft needs an `en` tag; budget 0 blocks; a requested tool not in the policy blocks. Every refusal leaves zero reservations, revisions, audit events and provider calls. A new reservation records the policy version that allowed it.
5. **Catalogue.** `advisory_available` is true only when server, policy and ADVISORY_DRAFT are all on (the policy is read only when the server switch is on).
6. **Web.** `AIPolicy.tsx`: the read-only "Policy in force" card (version, date, each rule, server switch state, reserved use cases, history) shown above the brief form; for holders of `ai.policy.manage` a "Change AI policy" dialog (operation ID kept for the dialog's life; states the fresh-sign-in requirement). The advisory request sends `policy_version`; a 409 `AI_POLICY_CHANGED` reloads the policy and the catalogue. `areaCapabilities` lists AI enablement for the `ai.policy.` prefix.

## Contract and persistence

| Method | Path | Operation | Capability | Roles | Fresh 300 s | Audit |
| --- | --- | --- | --- | --- | --- | --- |
| GET | `/v1/tenants/{t}/ai-enablement/policy` | `get_ai_policy` | `ai.enablement.read` | the seven AI readers | no | no |
| PUT | `/v1/tenants/{t}/ai-enablement/policy` | `update_ai_policy` | `ai.policy.manage` | TENANT_ADMIN | yes | `ai_policy.changed` |
| GET | `/v1/tenants/{t}/ai-enablement/policy/revisions` | `list_ai_policy_revisions` | `ai.enablement.read` | the seven AI readers | no | no |

- Closed `AIPolicyCommand` `{operation_id, expected_version, data:{use_cases:[AIUseCasePolicy]}}`; stale `expected_version` → 409 `AI_POLICY_CHANGED`; same operation ID with another payload → 409 `CONFLICT_OPERATION`; exact retry returns the original receipt. Revisions use the signed, principal/route-bound 15-minute cursors.
- `AIAdvisoryRequest` gains **required** `policy_version` (integer ≥ 0; 0 = no policy) and optional `tools`. A client that omits `policy_version` now gets 422. Schemas added: `AIUseCasePolicy`, `AIPolicyData`, `AIPolicyCommand`, `AIPolicy`, `AIPolicyDestination`, `AIPolicyRevision`, `AIPolicyRevisionList`, `AIPolicyReceipt`.
- **Migration `0041_ai_policy.sql`** (SHA-256 `46da4315e5bd13fede31dae08cb186f6588774046108e2d2779324c36f8822c2`, recorded in the [data dictionary](current/CURRENT-DATA-DICTIONARY.md)): `ai_policy_version` (PK tenant + version ID, UNIQUE tenant + number, typed FKs to the `AIConfiguration` revision, FK to the principal) and `ai_use_case_policy` (PK tenant + version + use case; CHECKs on every enum, the destination list, language tags, budget range, empty tools, reserved-only-off and complete-when-enabled); both insert-only (trigger, 42501), ENABLE + FORCE RLS with `tenant_fence`, `GRANT SELECT, INSERT TO impact_app` only. Partial unique index: one `AIConfiguration` object per tenant. `ai_advisory_request.policy_version_id` nullable with a tenant-keyed FK and a `NOT VALID` NOT NULL CHECK (new rows must name a version; earlier rows keep NULL). Registers the generated profile `14997060d0b7…ce133`. Migrations 0001–0040 are byte-identical.
- **Capability and profile.** `initial-access-v2` now proposes `ai.policy.manage` for TENANT_ADMIN; the profile hash changes. Existing tenants keep their ceilings: their administrators can hold the capability only after the reviewed access upgrade (0036 path) to the newly registered profile. Pending initial-access requests pinned to the old hash must be re-proposed.

## Acceptance scenarios and their evidence

| Scenario | Tests |
| --- | --- |
| Enable one use case with its policy | `test_ai_policy.py::test_administrator_enables_one_use_case_as_a_new_audited_policy_version` (stored version, rule rows, revision payload, `ai_policy.changed` audit, outbox, receipt; Programme Manager reads the card data); `test_ai_policy_unit.py::test_first_save_stores_version_1_with_exactly_that_use_case_and_audits`; `…::test_web_area_lists_ai_enablement_for_policy_holders_and_card_precedes_request` (source order only) |
| Core workflows complete with AI off | `test_ai_policy.py::test_core_workflows_complete_with_every_ai_use_case_off` (programme set-up, independent period close, report approval and export with every use case off; zero reservations; in-process request refused with zero provider calls); the existing AI-off period-close and reporting suites |
| Reject a request outside the policy | `test_ai_policy.py::test_sensitive_request_outside_the_policy_is_refused_before_reservation`, `…::test_destination_language_and_budget_rules_refuse_before_reservation`; `test_ai_enablement.py::test_sensitive_request_outside_policy_is_blocked_before_reservation`, `…::test_every_unmet_rule_blocks_before_reservation` |
| Reject a request made against an old policy | `test_ai_policy.py::test_request_made_against_an_old_policy_version_is_refused`; `test_ai_enablement.py::test_request_against_an_old_policy_version_conflicts_before_reservation` |
| Reject implicit tools | `test_ai_policy.py::test_tools_are_never_implicit_or_grantable`; `test_ai_enablement.py::test_requested_tool_is_refused_before_reservation`; `test_ai_policy_unit.py::test_invalid_reserved_or_tool_granting_policies_are_refused` |
| Reject change by a non-administrator or without fresh sign-in | `test_ai_policy.py::test_policy_change_refused_without_administration_or_fresh_sign_in` (MEL Manager and Programme Manager 403, stale 400 s and 301 s sign-in 403, no version created, denial recorded); `test_ai_policy_unit.py::test_real_authorizer_requires_mfa_and_sign_in_within_300_seconds` (MFA assurance) |
| Database guarantees | `test_ai_policy.py::test_policy_rows_are_insert_only_and_checked_by_the_database`; native `test_ai_policy_live.py` (RLS fence, forced RLS, insert-only, WITH CHECK, platform/identity/worker roles refused) |

## Qualification at this edition

Commands from the repository root; counts are from this branch's final code unless stated.

| Command | Result |
| --- | --- |
| `make lint` | ruff, ruff format and prettier clean |
| `make unit PY=.venv/bin/python` | 1,325 passed, 62 skipped |
| `npx tsc --noEmit` (apps/web), `npm run build` | clean; build succeeds |
| `python3 scripts/doc_index.py --check` | up to date |
| PGlite `scripts/run.py test --pytest-path qualification/test_ai_policy.py` | 11 passed |
| PGlite `… test_ai_enablement.py` / `… test_ai_enablement_live.py` / `… test_version_unit.py` | 38 passed, 1 skipped / 2 passed / 5 passed |
| PGlite full suite (`IMPACT_PORT=8125 scripts/run.py test`) | 2,131 passed, 96 skipped, 1 deselected, 0 failed, 0 errors (12 min 10 s) |
| Native PostgreSQL 16 (private `initdb` cluster), focused: `test_ai_enablement.py`, `test_ai_enablement_live.py`, `test_ai_policy.py`, `test_ai_policy_live.py`, `test_version_unit.py` | 62 passed, 0 skipped (includes the native-only advisory-table and policy real-role tests) |
| Native PostgreSQL 16, fresh database, `--native` without skips: `test_ai_policy.py`, `test_ai_policy_live.py`, `test_ai_enablement_live.py`, then the API restart check, restore drill and populated upgrade check | 18 passed; both restart phases pass; restore drill PASS (192 tables compared, 41 checksums); populated 40→41 upgrade PASS (only 0041 applied, 41 ledger rows, no checksum mismatch, data preserved) |

Only the 62-test native row was recorded before one last change (the revisions listing now reads a page's rules in one query); every other row, including the second native run, is on the final code. The first full PGlite run on this branch had 32 errors, all in `test_ai_plan_exports_live.py`, whose module fixture pinned `len(applied) == 40`; the pin (and the same schema-40 pins in five browser checks) now says 41. Evidence files written by these runs were restored; no evidence is published.

**Not run:** the four hosted CI jobs and `checks` (nothing can be pushed from this session); every browser check (no Chromium or `tools/browser` dependencies here), so the card, the editor dialog, their accessibility and the five moved schema pins are unexercised in a browser, and the story's `tools/browser/ai-policy-check.mjs` was not written; the live Keycloak suite (the MFA `acr` path is covered only by the unit test of `store.authorize`); the full native suite (only the focused native runs above); the CI native job's 33→41 upgrade from the deployed baseline.

## Limits

- **No destination is approved.** `openai-us` is the label of the existing adapter (global `api.openai.com`, no data-residency project), not a product-owner approval; the DPIA, provider region and retention remain open. Keep the server switch off on staging until a destination is approved.
- Budget units are recorded and 0 blocks the use case, but nothing is metered or deducted yet (FR-AI-016a); the existing 3-per-24-hours limit still applies.
- Purposes are free text: the request does not state a purpose; the gate requires at least one approved purpose. The language check covers only the English draft (`en` primary tag).
- A policy change that commits after a request's reservation does not stop that request's provider call (the window between the reservation commit and the call). An exact replay of an earlier completed request returns its stored draft after a policy change; it makes no new call.
- `AI_USE_CASE_DISABLED` uses the 503 envelope of `AI_NOT_CONFIGURED`, so it reports `retryable: true`.
- Reservations made before 0041 keep a NULL policy version; never run `VALIDATE CONSTRAINT ai_advisory_request_policy_required`.
- The separately operated historical gate `test_ai_plan_exports_upgrade.py` (skipped in every normal run) still pins schema 40 and the 0.33→0.40 capability delta; it describes that historical upgrade and was not changed.

## Deviations from the story card

1. Reserved use cases cannot be enabled, so the Given "CHAT is enabled with an empty tools list" is not reachable. Tested instead: enabling CHAT is refused, CHAT recorded off keeps an empty tools list, and a tool request under the enabled ADVISORY_DRAFT is refused before reservation.
2. Stricter than the card: tools are empty for every use case at the database level, and new reservations must name a policy version (`NOT VALID` CHECK).
3. "Policy version 1 is stored" is proven on a database-free first save; on the shared suite database the test proves gap-free numbering from 1, because earlier tests may already have stored versions.
4. "A Programme Manager sees the card before the request button" is proven by the Programme Manager's API read and a source-order check, not by a browser run.
5. Existing tests were adapted, never weakened: the fake-database fixture of `test_ai_enablement.py` answers the policy reads and records the new column; `test_ai_enablement_live.py` sends `policy_version` and enables a policy first (it also gains an assertion that the reservation names the policy version); schema pins move from 40 to 41.

## Reproduction

```
make lint && make unit PY=.venv/bin/python && (cd apps/web && npx tsc --noEmit)
IMPACT_PORT=8123 .venv/bin/python scripts/run.py test --pytest-path qualification/test_ai_policy.py
IMPACT_FIXTURE_DSN=postgresql://postgres:<pw>@127.0.0.1:<port>/impact_test_<x> \
  .venv/bin/python scripts/run.py test --native --pytest-path qualification/test_ai_policy_live.py
git checkout -- docs/evidence/ && git clean -f docs/evidence/
```

## Integration notes

- **Merge order:** first story of Sprint 1; it owns 0041, so US-MP-03 and US-DC-04 become 0042 and 0043. On merge, update the shared statements that describe `main`: the HANDOVER status block, AGENTS.md and ENGINEERING-BRIEF §4 rule 22 (keep them identical: "never change a byte of 0001–0041; next is 0042"), README's migration count, `docs/QUALIFICATION.md`, `docs/current/CURRENT-API-INVENTORY.md` (264 domain operations), the ledger and traceability files. Set `IMPACT_UPGRADE_BASELINE` in the CI native job only if staging's schema changes.
- **Requirement movement:** FR-AI-001 is "In review" in `docs/backlog/backlog.csv`. No completion-ledger promotion is proposed until hosted CI, a browser check of the card and editor, and a live-provider MFA run pass.
- **Owner decisions needed:** approve (or not) a destination and region; whether CHAT/EXTRACTION/REPORT_DRAFT may ever be pre-approved before their stories; whether disabled-by-policy should answer 403 instead of 503.
- **Files:** `apps/api/impact_api/ai_policy.py` (new), `ai_enablement.py`, `ai_enablement_contracts.py`, `ai_advisory_provider.py`, `main.py`, `bootstrap_profile.json`; `infrastructure/migrations/0041_ai_policy.sql`; `apps/web/src/AIPolicy.tsx` (new), `AIEnablement.tsx`, `main.tsx`, `ai-enablement.css`; `scripts/bootstrap.py`; regenerated `packages/contracts/*`, `docs/API-INVENTORY.md`; `VERSION.json`, `apps/web/package.json` and lock; tests `qualification/test_ai_policy.py`, `test_ai_policy_unit.py` (in `make unit`), `test_ai_policy_live.py`, `test_ai_enablement.py`, `test_ai_enablement_live.py`, `test_ai_plan_exports_live.py`; schema pins in five `tools/browser/*.mjs` checks; `Makefile`; documents.
