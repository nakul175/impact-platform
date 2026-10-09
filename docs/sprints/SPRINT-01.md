# Sprint 1: governed AI and a trustworthy shortlist

Owner: Nakul Jain · Planned 9 October 2026 · Dates: [start] to [start + 2 weeks] · Update trigger: sprint planning, mid-sprint refinement, review.

**Sprint goal:** an organisation can see and control exactly which AI use is allowed before anything is sent to a provider, and its opportunity shortlist is ranked by its own priorities with every commercial relationship disclosed. Release reviews start recording threats against tests.

**Capacity assumption:** one senior engineer who owns review, AI coding agents for most implementation, product owner available daily. About 26 points committed.

| ID | Story | Points | Migration |
| --- | --- | --- | --- |
| FR-AI-001 | Explicit AI enablement and policy | 8 | 0041 |
| FR-SEC-001 | Security threat assessment in every release review | 8 | none |
| US-MP-03 | Rank opportunities with the organisation's weights | 5 | 0042 |
| US-DC-04 | Disclose commercial relationships on every listing | 5 | 0043 |

Migrations 0001–0040 are frozen and numbering must stay contiguous: merge in the order above, or renumber before merging. Personas map to roles as in [PERSONA-ROLE-MAP.md](../agile/PERSONA-ROLE-MAP.md).

**Foundation carry-over (not engineering points):** US-RT-01 licence signed; US-RT-02 repository renamed to `imprana-commons` (GitHub setting); US-RT-05 issues imported with `docs/backlog/create_github_issues.py`; FR-SEC-008 branch protection on `main` (green `checks` + one human approval); FR-SEC-010 independent security review commissioned.

---

## FR-AI-001 Explicit AI enablement and policy (8 points)

**Story:** As an Organisation Administrator, I want to enable named AI use cases with their allowed data classes, destinations, language coverage, budget and required review, so that AI only runs where we have approved it and every workflow still works without it.

**Why:** every pilot AI feature (intake agent, report drafting) needs this gate first; it is a go-live gate item.

**Today:** AI is one server-wide switch (`config.py` `ai_enabled`, `ai_model`); one operation `create_ai_advisory` (`ai_enablement.py`), consent checkbox only, 3 attempts per tenant per 24 hours. No per-tenant or per-use-case policy. `AIConfiguration` is already an allowed registry type with no table.

**Functional notes**
- New "AI policy" screen in AI enablement for TENANT_ADMIN, capability `ai.policy.manage` (sensitive action: authentication within 300 s plus MFA assurance; audited).
- One policy version per change, never edited in place. Per use case: enabled, allowed data classes (PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTED), destinations (closed provider-and-region list), purposes, languages (BCP-47), review mode, budget units, tools (empty by default).
- Use cases now: ADVISORY_DRAFT. Reserved for later stories: EXTRACTION, REPORT_DRAFT, CHAT.
- AI runs only when server switch, tenant policy and use case are all on. Everyone who can read AI enablement sees a "Policy in force" card before the request button.
- Checks run before any reservation or provider call.

**Data layer (migration 0041_ai_policy.sql)**
- `ai_policy_version` (tenant_id, policy_version_id, object_id, version_no, created_by, created_at); PK (tenant_id, policy_version_id); UNIQUE (tenant_id, version_no).
- `ai_use_case_policy` (tenant_id, policy_version_id, use_case, enabled, data_classes[], destinations[], purposes[], languages[], review_mode, budget_units, tools[]); PK (tenant_id, policy_version_id, use_case); CHECK constraints on enums.
- Both insert-only, ENABLE + FORCE ROW LEVEL SECURITY, `tenant_fence`, `GRANT SELECT, INSERT TO impact_app` only.
- `ai_advisory_request.policy_version_id` added, nullable, tenant-keyed foreign key (existing rows stay null; table is insert-only).
- API: `GET /v1/tenants/{t}/ai-enablement/policy`, `PUT …/policy` (closed `AIPolicyCommand` with `expected_version`), `GET …/policy/revisions`; `AIAdvisoryRequest` gains required `policy_version`.
- Wiring: `augment()` row in `ai_enablement_contracts.py`, fixture grant in `scripts/bootstrap.py`, `scripts/build_access_profile.py`, `areaCapabilities` prefix `ai.policy.` in `apps/web/src/main.tsx`; regenerate contracts.

**Non-functional:** disabled means zero provider calls; fail closed when the policy cannot be read; audit event `ai_policy.changed` on every version.

**Acceptance and rejection criteria**

```gherkin
Scenario: Enable one use case with its policy
  Given an Organisation Administrator who signed in with MFA within the last 300 seconds
  When they enable ADVISORY_DRAFT for INTERNAL data, destination "openai-us", purpose "planning advice", languages "en", review mode "human review", budget 100 units
  Then policy version 1 is stored with exactly that use case enabled
  And an audit event "ai_policy.changed" is recorded
  And a Programme Manager sees the "Policy in force" card before the request button

Scenario: Core workflows complete with AI off
  Given the tenant policy has no enabled use case
  When a programme is set up, a period is closed and a report is generated
  Then each completes
  And no provider call is made

Scenario: Reject a request outside the policy
  Given ADVISORY_DRAFT allows INTERNAL data only
  When a request marked as containing sensitive data is submitted
  Then the response is 422 "AI_POLICY_BLOCKED"
  And no reservation is made and no provider call is made

Scenario: Reject a request made against an old policy
  Given policy version 2 is in force
  When a request carries policy_version 1
  Then the response is 409 "AI_POLICY_CHANGED"

Scenario: Reject implicit tools
  Given CHAT is enabled with an empty tools list
  When any request asks to use a tool
  Then it is refused

Scenario: Reject policy change by a non-administrator or without fresh sign-in
  Given a MEL Manager, or an Organisation Administrator whose last sign-in is older than 300 seconds
  When they try to change the policy
  Then the change is refused and no policy version is created
```

**Tests:** `qualification/test_ai_policy.py`; `test_ai_policy_live.py` (native roles: RLS fence, insert-only, negative role tests); additions to `test_ai_enablement.py` (blocked before reservation); `tools/browser/ai-policy-check.mjs`. Existing AI-off runs of period close and reporting are the "works without AI" evidence.

**Dependencies and risks:** new capabilities change the `initial-access-v2` profile hash; tenants that already applied initial access need a reviewed ceiling widening before they can grant them. No destination is approved yet (DPIA and provider region/retention open), so the pilot's destination list starts empty until the product owner approves one.

---

## FR-SEC-001 Security threat assessment in every release review (8 points)

**Story:** As a Platform Operator, I want each release review to record threat scenarios linked to controls, owners, tests and residual decisions, so that critical attack paths across modules are verified rather than hidden under a general security sign-off.

**Why:** feeds the independent security review (FR-SEC-010) and the pilot go-live gate.

**Today:** `specification/contracts/threat-register.json` has TH01–TH32, all "Verification pending", no categories, test links or residual decisions; `release-gates.json` G01–G14 all "Not run"; nothing in CI reads them; the narrative threat model predates the AI provider.

**Functional notes**
- Threat register v2 (`specification/contracts/threat-register.json`, schema version 2): each threat gets one of 8 categories (identity, tenant boundary, source data, files, offline devices, publication, AI, support), `control_refs`, named `owner`, `test_refs` (pytest node IDs) and `residual_decision` {ACCEPT | MITIGATE | BLOCK, decided_by, decided_on}.
- `chains[]`: CH01 document injection → export (TH21 → TH03 → TH15); CH02 support escalation (TH25 → TH02 → TH07); each needs at least two independent controls with evidence.
- Each release has `docs/evidence/release-review-<version>.json` with `open_critical[]`; gate G11 cannot pass while any critical threat is unresolved.
- A path-to-area map (migrations, `*_contracts.py`, access policy, `ai_*`) requires an impact-review entry when those paths change.
- Add the AI provider threats (prompt injection via advisory brief, data leaving the boundary) that the narrative model misses.

**Data layer:** repository files only; new `scripts/release_review.py --check` run in `.github/workflows/checks.yml`. No migration.

**Non-functional:** deterministic, offline, runs in seconds; no secrets in the register.

**Acceptance and rejection criteria**

```gherkin
Scenario: Every threat is categorised and linked
  Given threat register v2
  When "scripts/release_review.py --check" runs
  Then every threat has a category, at least one control, a named owner, at least one resolvable test reference and a residual decision

Scenario: Chained abuse paths have independent controls
  Given chains CH01 and CH02
  When the check runs
  Then each chain lists at least two independent controls with evidence

Scenario: A material change requires an impact review
  Given a pull request that changes a migration, an access policy or an "ai_" module
  When the check runs without an impact-review entry for that release
  Then the check fails

Scenario: Reject a release review that hides a critical path
  Given a critical threat whose residual decision is not ACCEPT or MITIGATE with evidence
  When the release review is marked passed
  Then the check fails and lists the open critical threat

Scenario: Reject an unresolvable test reference
  Given a threat whose test reference names a test that does not exist
  When the check runs
  Then the check fails
```

**Tests:** `qualification/test_release_review_unit.py` (missing fields, unresolvable references, hidden critical, chain without independent controls) added to `make unit`; one real chained-abuse test for CH01 (advisory brief injection reaching plan export).

**Dependencies and risks:** the reviewer must be a different person (needs branch protection, carry-over above). Support sessions do not exist yet, so TH25 is recorded as BLOCK.

---

## US-MP-03 Rank opportunities with the organisation's weights (5 points)

**Story:** As an Operations Head, I want opportunities ranked by impact, effort, cost and readiness, so that we tackle the right one first.

**Today:** `assess()` in `ai_enablement_catalog.py` sorts the 8 editorial use cases by keyword matches, gaps and ID and returns an integer priority only; nothing is saved; tests pin today's order.

**Functional notes**
- Ranking panel in AI enablement: rank, four scores, weighted total per opportunity. Weights editor with four labelled inputs (0–100, must total 100).
- Readiness is computed from the profile gaps `assess()` already finds. Impact, effort and cost come from a new versioned editorial score module (`ai_opportunity_scores.py`) owned by Imprana, kept outside `catalog()` so the guidance archive is unchanged. Effort and cost count in reverse (lower is better).
- Opportunities missing any score appear under "Not ranked: scores incomplete", never in the ranked list.
- Read with `ai.enablement.read`; change weights with `ai.enablement.manage`.

**Data layer (migration 0042_ai_ranking_weights.sql)**
- New registry kind `AIRankingWeights` (tenant singleton): closed data {impact, effort, cost, readiness}, integers 0–100, sum 100. Widen `object_registry_object_type_check`; partial unique index on `object_registry(tenant_id) WHERE object_type = 'AIRankingWeights'`.
- API: `GET` and `PUT /v1/tenants/{t}/ai-enablement/ranking-weights` (PUT with `expected_revision`); `POST …/ai-enablement/ranking` with `{profile}` returns the ranking and the `weights_revision_id` used.

**Non-functional:** deterministic exact-decimal totals, ties broken by ID; every ranking proves which weights produced it.

**Acceptance and rejection criteria**

```gherkin
Scenario: Ranked list with scores
  Given an organisation profile and default weights 25/25/25/25
  When the Operations Head opens the ranking
  Then opportunities appear in descending weighted total
  And each shows impact, effort, cost and readiness scores and its total
  And the response names the weights revision used

Scenario: Changing weights reorders the ranking
  Given weights are changed to impact 70, effort 10, cost 10, readiness 10
  When the ranking is requested again
  Then it is recalculated with the new weights and cites the new weights revision

Scenario: Reject weights that do not total 100
  Given weights of 50, 30, 30 and 10
  When they are saved
  Then the response is 422 and the previous weights remain in force

Scenario: Reject a stale weights update
  Given two administrators edit weights from the same revision
  When the second saves
  Then the response is 409 and no weights are overwritten

Scenario: Reject ranking an opportunity without all four scores
  Given an opportunity missing its cost score
  When the ranking is shown
  Then it appears only under "Not ranked: scores incomplete"
```

**Tests:** `qualification/test_ai_ranking.py`, additions to `test_ai_enablement_catalog.py` (existing order still holds when no weights are saved), `tools/browser/ai-ranking-check.mjs`.

**Dependencies and risks:** pattern library is still 8 editorial use cases (US-MP-01). Who scores impact, effort and cost is decided: Imprana editorial, reviewed by an advisor (aligns with US-DC-02).

---

## US-DC-04 Disclose commercial relationships on every listing (5 points)

**Story:** As an Executive Director, I want any commercial relationship with a listed solution disclosed, so that I can judge neutrality.

**Today:** 8 static listings in `ai_solutions_catalog.py` with commercial model and nonprofit offer, no disclosure field; saved plans archive the catalogue against `ai_content_schema_v1.json`, whose items are closed.

**Functional notes**
- Every tool card (`AIAdoptionWorkspace.tsx`) and comparison column (`AIToolComparison.tsx`) shows a disclosure label: "No commercial relationship known" or the relationship type(s) and statement.
- `commercial_disclosure`: {status: NONE_KNOWN | DISCLOSED, relationship_types[] (referral fee, revenue share, reseller, sponsorship, ownership), statement, declared_on}.
- A listing without a valid disclosure fails closed: the catalogue does not load and the unit check fails.

**Data layer (migration 0043_ai_guidance_v2.sql)**
- Bump `CONTENT_VERSION`; new archive schema `nonprofit-ai-guidance-v2` with the v1 reader kept; replace the `ai_content_snapshot` schema-version CHECK with `IN ('nonprofit-ai-guidance-v1', 'nonprofit-ai-guidance-v2')`. No RLS change, no new endpoint; tighten the `AISolutionsCatalog` contract.

**Non-functional:** saved plan revisions keep the disclosure that was current when saved; label readable by screen readers.

**Acceptance and rejection criteria**

```gherkin
Scenario: Every listing shows its disclosure
  Given the solution catalogue
  When an Executive Director views any tool card or comparison column
  Then it shows a disclosure label with status and, if disclosed, the relationship type and statement

Scenario: Saved plans keep the disclosure they were made with
  Given a plan saved under guidance v1 and another saved under v2
  When both are opened
  Then both load, and the v2 plan shows the disclosure captured at save time

Scenario: Reject a listing without a disclosure
  Given a listing whose commercial_disclosure is missing or has status DISCLOSED without a statement
  When the catalogue is validated
  Then validation fails and the catalogue is not served
```

**Tests:** additions to `test_ai_solutions_catalog.py` and `test_ai_content_archives.py` (v1 still readable, v2 captured); browser check that every card carries the label.

**Dependencies and risks:** the archive schema change is the main hazard; who declares a relationship: Imprana editorial, recorded with `declared_on`.

---

## Refinement changes made while planning

| Change | Why |
| --- | --- |
| US-DX-01 split into **US-DX-01a** "Record and prioritise the organisation's problems (structured form, no AI)" and **US-DX-01b** "Conversational intake agent" | There is no "problem" entity yet; US-DX-03 (baseline per problem) needs DX-01a first. DX-01b needs FR-AI-001 and FR-AI-016 |
| FR-AI-016 split into **FR-AI-016a** "AI jobs with budget reservation and cancellation" (8) and **FR-AI-016b** "Timeouts and labelled partial drafts" (5) | 13 points is too large for one sprint |
| US-CM-05 (usage and alerts, 5) follows FR-AI-016a | It reads the budget ledger 016a creates |

## Sprint 2 preview (not committed)

US-DX-01a (5), FR-AI-016a (8), US-CM-05 (5), US-DX-03 (8): about 26 points. Then FR-AI-016b, FR-UX-006 (language and locale, groundwork for Hindi) and US-DX-01b.

## Decisions taken by default (change at review if needed)

- Persona-to-role mapping: [PERSONA-ROLE-MAP.md](../agile/PERSONA-ROLE-MAP.md).
- Opportunity scores and commercial disclosures are Imprana editorial content, reviewed by an advisor.
- The AI destination list starts empty until the product owner approves a provider and region for the pilot.
