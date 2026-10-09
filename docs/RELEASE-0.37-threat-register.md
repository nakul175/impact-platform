# Build 0.37 threat register v2 and release security review (FR-SEC-001)

9 October 2026 · Local candidate on branch `sprint-1/fr-sec-001` (from `sprint-1/fr-ai-001`), committed locally only (not pushed, merged or deployed) · build 0.37.0 unchanged · no runtime, contract, migration or schema change. Two commits: the story and the fixes from its independent review (see "Review fixes").

Every release now has a security review that a script checks instead of a general sign-off. Each threat is linked to the controls that address it, the tests that exercise each control, a named owner role and a residual decision, and the review must list every threat and chain that is still open. The uncomfortable result for build 0.37.0: **14 of the 21 critical threats are unresolved, both chains are BLOCK**, gate G11 is "Not passed", and no decision has been confirmed by a person yet (every decision is the drafting agent's proposal). FR-SEC-001 is "In review" in the backlog, not Done; hosted CI has not run.

## Delivered

1. **Threat register v2**, `docs/current/threat-register.json`, with its JSON schema `docs/current/threat-register.schema.json`. All 32 threats of the preserved register (TH01 to TH32, same titles, impact and owner roles) plus three AI provider threats the narrative model lacks: **TH33** prompt injection through the advisory brief (High), **TH34** AI data leaving the boundary contrary to policy (Critical) and **TH35** AI policy bypass (Critical), mapped to the FR-AI-001 controls and tests. Each threat has one of eight categories (identity, tenant boundary, source data, files, offline devices, publication, AI, support), `control_refs` into a catalogue of 74 controls (layer, built or target design, the files that implement it, what it depends on), an owner role (no role is appointed to a person yet; until then Nakul Jain (owner) is accountable), `test_refs` (pytest node IDs or browser check names), `coverage` (which test exercises which control), a verification status with its gaps, and `residual_decision` {ACCEPT, MITIGATE or BLOCK, `decided_by`, `decided_on`, `confirmed_by`, rationale}.
2. **Verification status, honestly graded.** TESTED: every listed control is built and has at least one mapped test that exists, and those tests passed in their latest recorded runs (`make unit` here; the PGlite full suite and focused native and browser runs of build 0.37.0 in [RELEASE-0.37-ai-policy](RELEASE-0.37-ai-policy.md); the native, live identity-provider and browser jobs of build 0.36.0 on `main` for tests these branches did not run). It is not an independent assessment. PARTIAL: tests cover part of it; gaps listed. PENDING: the control or its verification does not exist; any listed test only checks a blocking condition. A threat counts as resolved only when its decision is ACCEPT or MITIGATE **and** it is TESTED; a chain only when its decision is ACCEPT or MITIGATE and every threat on its path is resolved. ACCEPT was not used: accepting a risk needs a person.
3. **Chains, both BLOCK.** CH01 document injection to export (TH21 → TH03 → TH15) is BLOCK because TH21 is: no retrieval of documents, evidence or metadata and no AI tool may ship. For the one model input that exists, the advisory brief, seven implemented controls with evidence on six layers break every link (API policy gate and database CHECK refuse tools, the provider adapter keeps only assistant text, the draft is never a record, closed plan bodies, the export renderer's projection and server-set restriction, the separate export capability). CH02 support escalation (TH25 → TH02 → TH07) is BLOCK because support sessions do not exist; today the path is closed by the absence of any support operation (contract) and the database's control-plane separation, with scoped grants and natural-person independence behind them.
4. **Release review** `docs/release-reviews/release-review-0.37.0.json` (schema `docs/current/release-review.schema.json`; outside `docs/evidence/`, which agents restore and clean after focused runs): `open_critical`, `open_other` and `open_chains` exactly as the register leaves them, gates G11 "Not passed" and G12 "Not run", and impact review IR-0.37-01 (change FR-AI-001) for this build's material changes (migration 0041, `ai_policy.py`, `ai_enablement.py`, `ai_advisory_provider.py`, `ai_enablement_contracts.py`, `access-policy.json`).
5. **`scripts/release_review.py --check`** (offline, deterministic, under a second). It fails when:
   - the register or the review does not match its schema, or contains credential-like text (raw file text and every decoded string are scanned);
   - version 1 no longer matches its independent hash record (`docs/verification/application-v0.12-original-sha256.json`), or a baseline threat is not carried over with its title, impact and owner role;
   - a test reference does not resolve: a pytest function or `Class::method` in `qualification/`, with a `[suffix]` accepted only when it is one of the ids that literal `parametrize` decorators generate (cross-checked against pytest's own collection); or a `test("...")` name declared in that `tools/browser/*.mjs` file;
   - a built control listed for a threat has no mapped test, or a TESTED threat lists an unbuilt control;
   - a chain lacks two independent implemented controls with resolvable evidence (different layers and no shared control in their dependency closures), or is looser than its threats (a chain with a BLOCK threat must be BLOCK);
   - compared with the register at the base of the change set, a threat or chain was removed, an impact lowered, or a decision or verification loosened without `confirmed_by`;
   - the current build's review is missing (the message names the file and how to create it), hides an open threat or chain, or is marked passed (or G11 "Pass") while a critical threat or a chain is open or a decision or impact review is unconfirmed;
   - the change set touches `infrastructure/migrations/*`, a `*_contracts.py` under `apps/` or `scripts/`, `packages/contracts/access-policy.json` or `apps/api/impact_api/ai_*.py` without modifying the review with a **new** `impact_reviews` entry naming the path. Entries are append-only: one already in the review at the base neither covers a later edit nor may be changed or removed.

   `--init --prepared-by "<name>"` creates the current build's review with the open lists and no impact reviews; `--open` prints the open lists.
6. **CI.** The `checks` workflow runs `release_review.py --check --base HEAD^1` after `make unit`, with `fetch-depth: 2` so the change set (and the base register and review) are the pull request's first parent, that is its base branch, or on `main` the previous commit.
7. **Binding docs.** The gate is written into `AGENTS.md` (the `checks` description, the Versions rule and a new security impact review rule, the command list), `docs/current/ENGINEERING-BRIEF.md` §8 (step 7 and the Versions paragraph), `docs/current/ENGINEERING-GUIDE.md` §7.2 and `docs/handover/PARALLEL-WORK.md` (builder rule 6, integrator steps 6 and 7). §4 of AGENTS.md and the brief is untouched.

## How to run it

```
.venv/bin/python scripts/release_review.py --check                 # change set since the merge-base with origin/main
.venv/bin/python scripts/release_review.py --check --base HEAD^1   # what CI runs
.venv/bin/python scripts/release_review.py --init --prepared-by "<name>"   # a new build's review
.venv/bin/python scripts/release_review.py --open                  # the open lists
```

## Open critical threats at build 0.37.0 (14) and open chains (2)

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

Open chains: CH01 (BLOCK, through TH21) and CH02 (BLOCK, through TH25). Resolved, pending the owner's confirmation and the independent assessment: TH01, TH03, TH07, TH10, TH14, TH15, TH35. The twelve open High threats are in the review's `open_other`.

## Acceptance scenarios and their evidence

All in `qualification/test_release_review_unit.py` unless named otherwise.

| Scenario | Tests |
| --- | --- |
| Every threat is categorised and linked | `test_a_threat_missing_a_required_field_fails` (category, control_refs, owner, test_refs, coverage, residual_decision, verification), `test_empty_links_unknown_category_invented_owner_and_unknown_control_fail`, `test_the_owner_role_is_carried_over_from_the_baseline`, `test_acceptance_needs_a_person`, `test_every_built_control_needs_a_mapped_test_and_tested_needs_only_built_controls`; passing case `test_a_sound_register_and_release_review_pass` and, on the real files, `test_the_repository_register_and_release_review_pass_the_check` |
| Chained abuse paths have independent controls | `test_a_chain_without_two_independent_evidenced_controls_fails` (same layer, dependent, shared dependency, unresolvable evidence, unbuilt control, one control, threat outside the path), `test_a_chain_is_no_looser_than_its_threats_and_counts_as_open`; the real CH01 and CH02 in the repository test; the CH01 chained-abuse test below |
| A material change requires an impact review | `test_material_paths_map_to_areas`, `test_a_material_change_without_an_impact_review_fails`, `test_only_an_entry_added_by_this_change_set_covers_it_and_entries_are_append_only`; through real git history: `test_a_later_edit_to_a_reviewed_ai_module_needs_a_new_impact_review`, `test_the_change_set_and_base_files_come_from_git`, `test_init_starts_a_review_that_the_check_accepts` |
| Reject a release review that hides a critical path | `test_an_unresolved_critical_threat_cannot_be_hidden_or_passed` (PARTIAL, PENDING, BLOCK and ACCEPT-without-test; hidden, `passed` and G11 "Pass"), `test_review_lists_must_match_the_register_exactly`, `test_a_passed_review_needs_confirmed_decisions_chains_and_impact_reviews` |
| Reject an unresolvable test reference | `test_test_references_resolve_to_real_tests_and_browser_checks` (including unknown and underivable `[suffix]`es), `test_derived_parameter_ids_match_what_pytest_collects`, `test_an_unresolvable_test_reference_fails_the_check` |
| No silent weakening | `test_baseline_threats_cannot_be_dropped_or_reworded`, `test_the_baseline_must_match_its_independent_hash_record` (version 1 edited together with its declared hash), `test_the_register_cannot_lose_threats_or_get_looser_than_at_the_base_without_a_person`, `test_the_register_is_compared_with_its_version_at_the_base` (git), `test_credentials_in_the_register_or_review_are_refused` |
| CH01 chained abuse (advisory brief injection reaching plan export) | `test_threat_chains_unit.py::test_ch01_injected_brief_cannot_reach_a_plan_export_as_model_output_or_forged_authority`: the real request validation, policy gate, OpenAI adapter (an in-memory transport plays a model that obeys the injection, returning a tool call and forged approval, official and restriction fields), plan validator and export renderer run in sequence on the fake database of `test_ai_enablement.py`. A tool request is refused before reservation; the brief travels only as data under fixed instructions; the tool call and provider fields are dropped and the result is a server-labelled sealed DRAFT that is never written as a record; forged fields are refused in a plan body; the export request cannot widen its restriction; an export of a stored payload carrying forged fields drops them and stays INTERNAL_SELF Draft. Checked against three deliberate weakenings (gate ignores tools, adapter passes provider metadata, renderer relabels the restriction): each makes it fail |
| Blocked surfaces stay absent | `test_blocked_attack_surfaces_are_absent_from_the_implemented_api`: no offline-sync, device, support, connector or webhook route and no AI apply, proposal, tool or retrieval route in the implemented domain and platform contracts or `main.py` (evidence for the BLOCK decisions on TH13, TH17, TH18, TH21, TH23, TH25 and CH02) |

## Qualification at this edition

Commands from the worktree root with `IMPACT_PORT=8131 IMPACT_DEV_DB_PORT=0`, on the second commit.

| Command | Result |
| --- | --- |
| `make lint` | ruff check, ruff format (242 files) and prettier clean |
| `make unit PY=.venv/bin/python` | 1,377 passed, 62 skipped in 26 s (1,338 before this story; 39 new tests in the two new files) |
| `.venv/bin/python scripts/release_review.py --check` | passed in under a second: 35 threats, 74 controls, 2 chains; 14 critical, 12 other threats and 2 chains open; 826 changed paths since `origin/main`, six material, all named by IR-0.37-01, which is new against the base. Also passes with `--base HEAD^1` |
| `python3 scripts/doc_index.py --check` | current |

First commit only: `make unit` 1,365 passed, 62 skipped; the check passed; a tampered copy of the review (impact review removed, TH34 left out, marked passed) failed with 42 problems and was restored.

**Not run:** the PGlite, native, browser and live identity-provider suites (no runtime code changed; the referenced database, browser and identity-provider tests are resolved by name, and their last recorded results are in [RELEASE-0.37-ai-policy](RELEASE-0.37-ai-policy.md) and, for jobs that branch did not run, the 0.36.0 CI run on `main`); the four hosted CI jobs and `checks` (nothing can be pushed from this session). The check proves that each referenced test exists, not that it passes; the suites prove that.

## Review fixes (second commit)

The independent review approved with fixes; all were applied.

- **An old entry no longer covers a later edit.** Coverage was keyed only on the path being named; now the change set must modify the review with a new entry (with a `change_id`), and entries at the base are append-only.
- **The gate is in the binding docs** (item 7 above), and a missing review names the file and the `--init` command.
- **Silent weakening is caught.** The baseline is checked against its independent hash record. The register is compared with its version at the base: removals, lowered impact and unconfirmed loosening fail.
- **Minor fixes:**
  - credentials are scanned in the raw text and every decoded string;
  - `[suffix]`es are validated against literal `parametrize` ids, or refused when not derivable;
  - TESTED now requires every listed control to have a mapped test; until then the code and this note disagreed;
  - chains are no looser than their threats and count in the passed logic, so CH01 changed from MITIGATE to BLOCK;
  - owner roles must carry over from version 1;
  - `changed_paths` and base-ref handling are tested on a throwaway git repository;
  - reviews moved from `docs/evidence/` to `docs/release-reviews/`.

## Limits and deviations from the story card

1. **Where the register lives.** The card names `specification/contracts/threat-register.json`, but AGENTS.md and the engineering brief forbid editing `specification/` (the preserved package). Version 1 stays byte-identical there and is checked against its independent hash record; version 2 is `docs/current/threat-register.json`. The card's `docs/evidence/release-review-<version>.json` became `docs/release-reviews/` (see Review fixes).
2. **Decisions are proposals.** `decided_by` is the drafting agent and `confirmed_by` is null everywhere; the review cannot pass until a person confirms them. Owners are the threat model's roles, none appointed.
3. **"At least one resolvable test reference" for surfaces that do not exist** (offline devices, support sessions, connectors, retrieval): the reference is a test of the blocking condition, and the verification status is PENDING, so the threat stays open.
4. **The CH01 test is database-free**: the export's HTTP authority checks are not re-run there; they are the existing live tests cited in the chain's evidence.
5. **Change set**: committed changes only (`git diff` from the merge-base); uncommitted edits are not seen. The base comparison needs the base commit locally (CI fetches two commits). `specification/contracts/release-gates.json` is not edited; the G11 and G12 status lives in each release review.
6. **Parameter ids**: only literal `parametrize` decorators are derivable; a `[suffix]` on any other test is refused, so reference such tests without one.

## Integration notes

- **Every build needs `docs/release-reviews/release-review-<build>.json`.** A branch that bumps `VERSION.json` fails `checks` and `make unit` until it adds one (`--init`). US-MP-03 (migration 0042, `ai_*` modules, contracts, access policy) and US-DC-04 (migration 0043, `ai_*` catalogue, contracts) must each add a new impact-review entry naming their material paths in the same change set, and update the register when they rename a referenced test or add a threat. After renumbering a migration, the entry must name the final path.
- **Owner decisions needed:** confirm or change the proposed residual decisions (start with the 14 open critical ones and the two chains); appoint role holders or keep owner accountability; commission the independent review (FR-SEC-010); approve a destination before TH34 can leave BLOCK.
- **Requirement movement:** FR-SEC-001 is "In review" in `docs/backlog/backlog.csv`; no ledger promotion.
- **Files:**
  - new: `docs/current/threat-register.json`, `threat-register.schema.json`, `release-review.schema.json`, `docs/release-reviews/release-review-0.37.0.json`, `scripts/release_review.py`, `qualification/test_release_review_unit.py`, `qualification/test_threat_chains_unit.py`, this note;
  - changed: `Makefile` (unit target), `.github/workflows/checks.yml`, `AGENTS.md`, `docs/current/ENGINEERING-BRIEF.md`, `docs/current/ENGINEERING-GUIDE.md`, `docs/handover/PARALLEL-WORK.md`, `docs/current/CHANGELOG.md`, `docs/NEXT-DELIVERY.md`, `docs/current/Impact-Management-Security-Threat-Model-v1.1.md` (one increment paragraph), `docs/backlog/backlog.csv`, `docs/DOCUMENTATION-INDEX.md` (regenerated).
- **Risks:**
  - the register is kept current by hand, so a renamed test fails the check (intended, but it adds work to each change);
  - the material-path rule sees only the listed paths, so a security-relevant change elsewhere (for example `store.py` or `auth.py`) needs no impact review yet;
  - loosening a decision now needs `confirmed_by`, which only a person may fill in.
