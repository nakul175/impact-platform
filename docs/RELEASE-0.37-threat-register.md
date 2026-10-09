# Build 0.37 threat register v2 and release security review (FR-SEC-001)

9 October 2026 · Local candidate on branch `sprint-1/fr-sec-001` (from `sprint-1/fr-ai-001`), committed locally only (not pushed, merged or deployed) · build 0.37.0 unchanged · no runtime, contract, migration or schema change.

Every release now has a security review that a script checks instead of a general sign-off. Each threat is linked to the controls that address it, a named owner role, tests that really exist and a residual decision, and the review must list every critical threat that is still open. The uncomfortable result for build 0.37.0: **14 of the 21 critical threats are unresolved**, gate G11 is "Not passed", and no decision has been confirmed by a person yet (every decision is the drafting agent's proposal). FR-SEC-001 is "In review" in the backlog, not Done; hosted CI has not run.

## Delivered

1. **Threat register v2**, `docs/current/threat-register.json`, with its JSON schema `docs/current/threat-register.schema.json`. All 32 threats of the preserved register (TH01 to TH32, same titles and impact) plus three AI provider threats the narrative model lacks: **TH33** prompt injection through the advisory brief (High), **TH34** AI data leaving the boundary contrary to policy (Critical) and **TH35** AI policy bypass (Critical), mapped to the FR-AI-001 controls and tests. Each threat has one of eight categories (identity, tenant boundary, source data, files, offline devices, publication, AI, support), `control_refs` into a catalogue of 72 controls (layer, built or target design, the files that implement it, what it depends on), an owner role (no role is appointed to a person yet; until then Nakul Jain (owner) is accountable), `test_refs` (pytest node IDs or browser check names), a verification status with its gaps, and `residual_decision` {ACCEPT, MITIGATE or BLOCK, `decided_by`, `decided_on`, `confirmed_by`, rationale}.
2. **Verification status, honestly graded.** TESTED: named tests exist for the listed controls and passed in their latest recorded runs: `make unit` here, the PGlite full suite and focused native and browser runs of build 0.37.0 ([RELEASE-0.37-ai-policy](RELEASE-0.37-ai-policy.md)), and the native, live identity-provider and browser jobs of build 0.36.0 on `main` for tests this branch did not run (not an independent assessment). PARTIAL: tests cover part of it; gaps listed. PENDING: the control or its verification does not exist; any listed test only checks a blocking condition. A threat counts as resolved only when its decision is ACCEPT or MITIGATE **and** it is TESTED. ACCEPT was not used: accepting a risk needs a person.
3. **Chains.** CH01 document injection to export (TH21 → TH03 → TH15): seven implemented controls with evidence on six layers (API policy gate and database CHECK refuse tools, the provider adapter keeps only assistant text, the draft is never a record, closed plan bodies, the export renderer's projection and server-set restriction, the separate export capability). CH02 support escalation (TH25 → TH02 → TH07): recorded as **BLOCK** because support sessions do not exist; today the path is closed by the absence of any support operation (contract) and the database's control-plane separation, with scoped grants and natural-person independence behind them.
4. **Release review** `docs/evidence/release-review-0.37.0.json` (schema `docs/current/release-review.schema.json`): `open_critical` and `open_other` exactly as the register leaves them, gates G11 "Not passed" and G12 "Not run", and impact review IR-0.37-01 for this build's material changes (migration 0041, `ai_policy.py`, `ai_enablement.py`, `ai_advisory_provider.py`, `ai_enablement_contracts.py`, `access-policy.json`).
5. **`scripts/release_review.py --check`** (offline, deterministic, about half a second): validates the register and the review against their schemas; resolves every test reference (a pytest function or `Class::method` in `qualification/`, or a `test("...")` name declared in that `tools/browser/*.mjs` file); checks that version 1 is byte-identical and every baseline threat is carried over; checks control, owner and category references, that chains have two independent implemented controls with resolvable evidence (independent: different layers and no shared control in their dependency closures); fails when the review hides an open threat or is marked passed (or G11 "Pass") while a critical threat is open or a decision or impact review is unconfirmed; requires an impact-review entry naming each changed migration, `*_contracts.py` under `apps/` or `scripts/`, `packages/contracts/access-policy.json` or `apps/api/impact_api/ai_*.py`; refuses credential-like text. `--open` prints the open lists for a new review.
6. **CI.** The `checks` workflow runs `release_review.py --check --base HEAD^1` after `make unit`, with `fetch-depth: 2` so the change set is the pull request (first parent of the test merge commit) or the merged change on `main`.

## How to run it

```
.venv/bin/python scripts/release_review.py --check                 # change set since the merge-base with origin/main
.venv/bin/python scripts/release_review.py --check --base HEAD^1   # what CI runs
.venv/bin/python scripts/release_review.py --open                  # open lists to paste into a new review
```

## Open critical threats at build 0.37.0 (14)

| Threat | Why it is open | Proposed decision |
| --- | --- | --- |
| TH04 Confused identity token | Provider signing-key rotation untested | MITIGATE |
| TH05 Invitation and recovery takeover | Live MFA enrolment, factor reset and changed-email cases not qualified; a compromised worker can mint links for existing invitations | MITIGATE |
| TH06 Stale grant after revocation | Bearer tokens live 120 s, beyond the 60 s target | MITIGATE |
| TH09 Lost update or close race | Edit/edit and approval/candidate-edit races not run natively | MITIGATE |
| TH11 Unsafe expressions and imports | Archive bombs, malformed encodings not tested; parsing not isolated | MITIGATE |
| TH13 Outbound request forgery | No address policy; no connector may ship | BLOCK |
| TH17 Plaintext on a lost device | No device client or encrypted storage | BLOCK |
| TH21 Prompt injection in retrieved content | No retrieval or tools may ship until scoped retrieval and injection evaluation exist | BLOCK |
| TH25 Privileged support escalation | Support sessions do not exist | BLOCK |
| TH26 Incomplete privacy deletion | Backups keep erased data; AI plans, plan export bytes and advisory results are outside the erasure plan | MITIGATE |
| TH27 Backup resurrects deleted records | No deletion or revocation replay before reopening a restore | BLOCK |
| TH28 Audit modification or truncation | No independently retained checkpoint | MITIGATE |
| TH29 Compromised dependency or build | No provenance, SBOM verification or immutable promotion | MITIGATE |
| TH34 AI data leaving the boundary | No destination approved, DPIA open, sensitive flag self-reported: keep the server AI switch off for real data | BLOCK |

Resolved, pending the owner's confirmation and the independent assessment: TH01, TH03, TH07, TH10, TH14, TH15, TH35. The other twelve open threats (High) are listed in the review's `open_other`.

## Acceptance scenarios and their evidence

| Scenario | Tests |
| --- | --- |
| Every threat is categorised and linked | `test_release_review_unit.py::test_a_threat_missing_a_required_field_fails` (category, control_refs, owner, test_refs, residual_decision, verification), `…::test_empty_links_unknown_category_invented_owner_and_unknown_control_fail`, `…::test_acceptance_needs_a_person_and_tested_needs_an_implemented_control`; passing case `…::test_a_sound_register_and_release_review_pass` and, on the real files, `…::test_the_repository_register_and_release_review_pass_the_check` |
| Chained abuse paths have independent controls | `…::test_a_chain_without_two_independent_evidenced_controls_fails` (same layer, dependent, shared dependency, unresolvable evidence, unbuilt control, one control, threat outside the path); the real CH01 and CH02 in the repository test; the CH01 chained-abuse test below |
| A material change requires an impact review | `…::test_material_paths_map_to_areas`, `…::test_a_material_change_without_an_impact_review_fails` |
| Reject a release review that hides a critical path | `…::test_an_unresolved_critical_threat_cannot_be_hidden_or_passed` (PARTIAL, PENDING, BLOCK and ACCEPT-without-test; hidden, `passed` and G11 "Pass"), `…::test_review_lists_must_match_the_register_exactly`, `…::test_a_passed_review_needs_confirmed_decisions_and_impact_reviews` |
| Reject an unresolvable test reference | `…::test_test_references_resolve_to_real_tests_and_browser_checks`, `…::test_an_unresolvable_test_reference_fails_the_check` |
| CH01 chained abuse (advisory brief injection reaching plan export) | `test_threat_chains_unit.py::test_ch01_injected_brief_cannot_reach_a_plan_export_as_model_output_or_forged_authority`: the real request validation, policy gate, OpenAI adapter (an in-memory transport plays a model that obeys the injection, returning a tool call and forged approval, official and restriction fields), plan validator and export renderer run in sequence on the fake database of `test_ai_enablement.py`. A tool request is refused before reservation; the brief travels only as data under fixed instructions; the tool call and provider fields are dropped and the result is a server-labelled sealed DRAFT that is never written as a record; forged fields are refused in a plan body; the export request cannot widen its restriction; an export of a stored payload carrying forged fields drops them and stays INTERNAL_SELF Draft. Checked against three deliberate weakenings (gate ignores tools, adapter passes provider metadata, renderer relabels the restriction): each makes it fail |
| Blocked surfaces stay absent | `…::test_blocked_attack_surfaces_are_absent_from_the_implemented_api`: no offline-sync, device, support, connector or webhook route and no AI apply, proposal, tool or retrieval route in the implemented domain and platform contracts or `main.py` (evidence for the BLOCK decisions on TH13, TH17, TH18, TH23, TH25 and CH02) |

## Qualification at this edition

Commands from the worktree root with `IMPACT_PORT=8131 IMPACT_DEV_DB_PORT=0`.

| Command | Result |
| --- | --- |
| `make lint` | ruff check, ruff format (242 files) and prettier clean |
| `make unit PY=.venv/bin/python` | 1,365 passed, 62 skipped in 28 s (1,338 before; the 27 new tests are the two new files) |
| `.venv/bin/python scripts/release_review.py --check` | passed in 0.7 s: 35 threats, 72 controls, 2 chains; 14 critical and 12 other threats open; 812 changed paths since `origin/main`, six material, all covered by IR-0.37-01. Also passes with `--base HEAD^1`. A tampered copy of the review (impact review removed, TH34 left out, marked passed) failed with 42 problems and was restored |
| `python3 scripts/doc_index.py --check` | current |

**Not run:** the PGlite, native, browser and live identity-provider suites (no runtime code changed; the referenced database, browser and identity-provider tests are resolved by name, and their last recorded results are in [RELEASE-0.37-ai-policy](RELEASE-0.37-ai-policy.md) and, for jobs that branch did not run, the 0.36.0 CI run on `main`); the four hosted CI jobs and `checks` (nothing can be pushed from this session). The check proves that each referenced test exists, not that it passes; the suites prove that.

## Limits and deviations from the story card

1. **Where the register lives.** The card names `specification/contracts/threat-register.json`, but AGENTS.md and the engineering brief forbid editing `specification/` (the preserved package; its hash is recorded in `docs/verification`). Version 1 stays byte-identical there; version 2 is `docs/current/threat-register.json`, and the check fails if version 1 changes or loses a threat.
2. **Decisions are proposals.** `decided_by` is the drafting agent and `confirmed_by` is null everywhere; the review cannot pass until a person confirms them. Owners are the threat model's roles, none appointed.
3. **"At least one resolvable test reference" for surfaces that do not exist** (offline devices, support sessions, connectors, retrieval): the reference is a test of the blocking condition, and the verification status is PENDING, so the threat stays open.
4. **The CH01 test is database-free**: the export's HTTP authority checks are not re-run there; they are the existing live tests cited in the chain's evidence.
5. **Change set**: committed changes only (`git diff` from the merge-base); uncommitted edits are not seen. `specification/contracts/release-gates.json` is not edited; the G11 and G12 status lives in each release review.

## Integration notes

- **Every build needs `docs/evidence/release-review-<build>.json`.** A branch that bumps `VERSION.json` fails `checks` and `make unit` until it adds one (`--open` prints the lists). US-MP-03 (migration 0042, `ai_*` modules, contracts, access policy) and US-DC-04 (migration 0043, `ai_*` catalogue, contracts) must add impact-review entries naming their material paths, and update the register when they change a referenced test or add a threat.
- **Owner decisions needed:** confirm or change the proposed residual decisions (start with the 14 open critical ones); appoint role holders or keep owner accountability; commission the independent review (FR-SEC-010); approve a destination before TH34 can leave BLOCK.
- **Requirement movement:** FR-SEC-001 is "In review" in `docs/backlog/backlog.csv`; no ledger promotion.
- **Files:** new `docs/current/threat-register.json`, `threat-register.schema.json`, `release-review.schema.json`, `docs/evidence/release-review-0.37.0.json`, `scripts/release_review.py`, `qualification/test_release_review_unit.py`, `qualification/test_threat_chains_unit.py`, this note; changed `Makefile` (unit target), `.github/workflows/checks.yml`, `docs/current/CHANGELOG.md`, `docs/NEXT-DELIVERY.md`, `docs/current/Impact-Management-Security-Threat-Model-v1.1.md` (one increment paragraph), `docs/backlog/backlog.csv`, `docs/DOCUMENTATION-INDEX.md` (regenerated).
- **Risks:** the register must be kept current by hand (a renamed test fails the check, which is the point, but adds work to every change); the material-path rule sees only the listed paths, so a security-relevant change elsewhere (for example `store.py` or `auth.py`) needs no impact review yet.
