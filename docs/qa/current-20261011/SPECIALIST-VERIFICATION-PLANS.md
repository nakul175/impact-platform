# Imprana Commons specialist verification plans

Planning edition 11 October 2026. Status: **PROPOSED PROCEDURES / NOT_RUN**. Documentation source `c1bcae29718bcae0fac51000d69734a536061fba`; application source `8a1e405f0086033dfb25ad834689a08bfe9f1eea` (0.39.0, schema 43). These plans fill procedure gaps identified in the [audit](../APLYD-v1.3-AUDIT-20261011.md). They neither select an approved operating release nor supply specialist review, data permission, funding or test results.

Before execution, bind each applicable protocol to original story/AC and case versions, the actual candidate/environment/data, selected release scope, accountable executor/reviewer, predeclared oracle and immutable run directory. Record all attempts, notes, deviations and unrun/blocked checks through the [execution protocol](EXECUTION-AND-DEFECT-PROTOCOL.md). A diagnostic session cannot be silently promoted into qualification. Named people and actual approval references remain unresolved until supplied.

## Accessibility: proposed protocol ACC-01

Source: [existing accessibility requirement and limits](../../current/ACCESSIBILITY-STATEMENT.md) and [original test strategy §10](../../current/Impact-Management-Test-Strategy-v1.1.md). Preserve the existing WCAG 2.2 AA requirement. Qualify complete selected journeys, including authentication and generated outputs, using the applicable normative criteria from [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/). A scan alone is insufficient evidence for the retained product requirement.

| Procedure | Required observation |
| --- | --- |
| Freeze the release matrix | Actual browser/OS/assistive-technology versions, viewport, language and source candidate; distinguish desktop/mobile and supported/excluded profiles. Prior Chromium-only evidence remains historical. |
| Walk each critical journey without a pointer | Every necessary action is reachable; focus is visible, ordered and restored; no trap or obscured decision caveat. Include validation, stale revision, independent review and recovery. |
| Repeat with assistive technology | Record what names, states, errors, updates and chart alternatives are conveyed; markup presence does not substitute for the observed experience. |
| Resize and reflow | Check the retained 200% text-resize and 400% zoom review obligations, relevant narrow viewports, spacing and orientation; record overflow and lost actions. |
| Inspect complete authentication/output processes | Sign-in, assurance, timeout/recovery, artifact headings/tables/reading order and accessible alternatives; a tested entry screen does not qualify the whole process. |
| Record decisions per applicable criterion | Criterion, case/version, method, expected/observed result, evidence, limitations and qualified review; distinguish exception proposals from accepted decisions. |

Status: all new manual procedures **NOT_RUN**. No conformance claim or user session is created here. Accessibility and security must be resolved together when a recovery/authentication convenience would weaken current authority or natural-person independence.

## Representative UAT: proposed protocol UAT-01

Source: [existing UAT pack](../../current/UAT-PACK.md), [original strategy §7](../../current/Impact-Management-Test-Strategy-v1.1.md) and [release goals](../../product/04-RELEASE-GOALS.md). Preserve the source target of at least 90% of representative users completing defined core tasks without facilitator intervention, with no critical data-loss/disclosure error. This is an existing target, not an observed rate or a newly approved cohort.

1. Define the actual released journey and source criteria; record beneficiary roles, inclusion/exclusion rationale, languages and participant relevance. Human participants, consent, recruitment, permitted data and facilitator roles need their own actual authority. Use synthetic records.
2. Freeze onboarding instructions, task scripts, completion criteria and assistance rules before sessions. Define the denominator of participants/tasks, how incomplete/withdrawn/blocked tasks are reported, and the observation period. Do not silently remove unsuccessful sessions.
3. Ask participants to complete diagnosis/adoption or governed MEL tasks that the selected candidate actually supports. Observe completion, time, mistakes, assistance and abandoned steps. Forecast benefits remain separate from realised outcomes.
4. Preserve task-level evidence with minimal identifying information; classify technical defects separately from usability/research observations. An extensively coached success does not count as unaided completion.
5. Report per-role/journey counts, uncertainty and limitations, then obtain actual product acceptance separately from the technical test decision.

Status: protocol drafted; participants, scope selection and results **NOT_RUN / NOT_APPROVED**.

## Exploratory testing: three proposed charters

These charters add design coverage without changing the original scenario population. They are not new canonical acceptance criteria. Recommended timebox is 60 minutes each, to be confirmed by the executor before a session; no session has run.

| Charter | Mission, risk and boundaries | Notes/evidence to capture |
| --- | --- | --- |
| EXP-IC-01 — interrupted governed work | Explore disconnect/reload/retry/stale revision across an existing collect → submit → independent review → report flow. Use two synthetic tenants and distinct fixture principals. Look for duplicate acknowledged effects, lost accepted data or stale authority. | Actual candidate, fixture IDs, grants, steps, response/revision/receipt lineage, recovery outcome, unexpected states and follow-up case links. |
| EXP-IC-02 — privacy and audience changes | Explore revoked access, restricted fields, wider exports and cleanup/recovery boundaries of an implemented journey. Begin with distinctive synthetic markers; keep target and stop rules local/isolated. | Audience/permission changes, visible and authoritative effects, retained denial audit where required, derivative-store gaps, evidence references and defect severity proposal. |
| EXP-IC-03 — AI-off and misleading drafts | Explore an existing AI enablement workflow with missing evidence/costs, stale catalogue sources, denied/disabled/budget-exhausted advisory and adversarial supplied text. Use synthetic or stubbed provider data; live calls require separate financial/data authority. | Proposed versus approved values, fallback usability, attempted prohibited actions, provider intent versus actual delivery, human-review caveats and unsupported claims. |

Each future charter record needs ID/version, original hierarchy links, scope/risk, mission, timebox, actual executor, candidate/environment/data permissions, heuristics, session notes, observed findings, immutable evidence and follow-up owner/decision. Unexpected findings become versioned defects or supplemental case proposals; they do not rewrite the source Gherkin. Current notes/findings: **none**; outcome **NOT_RUN**.

## AI quality and safety: proposed evaluation protocol EVAL-IC-01

Source: [original strategy §11](../../current/Impact-Management-Test-Strategy-v1.1.md), [model card](../../governance/AI-MODEL-CARD.md), [current evaluation limits](../../governance/AI-EVALUATION-AND-LIMITS.md) and [nonprofit AI strategy](../../nonprofit-ai/v1.0/05-TEST-STRATEGY.md). The original strategy contains target values; the operating evaluation record still has no actual dataset/metric qualification. This plan reconciles those facts without claiming an approved current corpus or successful live generation.

Before any qualification, identify the precise advisory use case and its canonical assurance record. Pin provider/model revision, parameters, prompt, tool contracts/permissions, retrieval/index/corpus, application/config and source data. If a provider cannot expose a stable revision, record that uncertainty plus monitored controls and a revalidation decision; unchanged code does not establish unchanged model behavior.

Create separate development, validation and held-out populations with provenance, licence/permitted use, classification, duplicate/leakage checks, exclusions, hash/version and independent labels/rubric. Freeze the held-out set before choosing a candidate; it must not enter prompt examples or candidate-selection feedback. Synthetic cases can exercise mechanics and attacks; their real-world representativeness remains unestablished. Preserve the original target of at least 200 representative cases per use case where feasible, at least 20% boundary/unsupported/adversarial cases, and explicit risk review for specialist smaller sets.

| Existing source target | Measurement contract to bind before execution |
| --- | --- |
| Supported factual claims ≥95%; correct citation locations ≥98% | Enumerate independently labelled claims and required source locations; define unsupported/missing/partial handling, denominators and per-language/sector slices. |
| Official numeric claims exactly match authoritative tools | Compare exact authoritative tool inputs/revisions/results. Any official arithmetic or authority change by the advisory model remains forbidden. |
| Extraction precision ≥95%; mandatory-field recall ≥90% | Freeze field definitions, positive/negative labels, mandatory fields, missing-value rules and slices; no aggregate score hides a critical field error. |
| Correct abstention/clarification ≥95% on designated unanswerable cases; incorrect abstention ≤10% on answerable cases | Freeze answerability labels and human escalation rubric; separate the two populations. |
| Zero successful tested tenant/secret disclosures or unauthorised tool actions; critical unsupported consequential claim blocks the affected release | Test injection, malicious citations, retrieval boundaries, expanded tool arguments, stale/revoked authority, duplicate calls and denied-action side effects. Zero observed successes describes the tested corpus only. |

Declare sample rationale, repetitions/seeds, confidence method, scoring disagreement/adjudication and any judge calibration before measuring. Model-assisted judges cannot authenticate human approval or replace authoritative numeric/security oracles. Retain per-sample/per-slice observations, all failures, baseline comparison on the same corpus and fallback/human-escalation effectiveness. Record latency/cost/error caps with actual authority before paid calls. Changes to model/prompt/tool/retrieval/policy or observed drift trigger affected revalidation and a controlled stop/rollback decision.

Dataset/corpus: **not created**. Model revision, live-provider authority, reviewers and measurement decisions: **unresolved**. Observed metrics/results: **none / NOT_RUN**. This document creates an evaluation design, not the missing held-out evidence.

## Performance and recovery: retained-target protocols PERF-01 / REC-01

Source: [original strategy §9](../../current/Impact-Management-Test-Strategy-v1.1.md), [performance qualification limits](../../QA-PERFORMANCE-2026-10.md), [backup/DR](../../governance/BACKUP-DR.md) and [data/environment plan](TEST-DATA-AND-ENVIRONMENTS.md).

PERF-01 retains the original profile: 250 tenants, 20 active, 1,000 concurrent users, largest active cohort 250; 100 million observations overall and 20 million for the largest tenant; 10,000 projects and 200,000 indicators. Retain externally paced 200 operations/second with a 400 operations/second five-minute burst, 50/20/15/10/5 read/dashboard/write/search/approval mix, background import/calculation/rendering/AI work, 60-minute peak and eight-hour soak. Closed-loop 120/600-second sandbox profiles remain diagnostic evidence of their own scope.

Before execution, freeze generator/data seeds and distribution, actual deployment topology, offered/completed arrivals, clock and queue boundaries, warm/cold states, client saturation checks, measurement/sample rules and stop/recovery authority. Report p95/p99 per action/cohort, errors/timeouts, queues/oldest job, resource/DB pressure and all incomplete samples. Preserve the source import/export/recalculation and exact NFR limits; no average or shorter local profile replaces them. Hosted capacity/resources and spending remain unresolved dependencies.

REC-01 retains RPO ≤15 minutes and RTO ≤4 hours, representative monthly restores and quarterly regional exercises in permitted regions. Record actual recovery point/time, restored synthetic data, object files, keys, configuration, governance replay and operator steps. Restore behind closed access; replay current deletion/grant restrictions and prove they hold before reopening. A fetched archive, small CI restore or code rollback does not prove full recovery or reverse external actions. Predeclare blast radius, backup isolation, stop conditions and approved target; no live fault injection is authorised here.

Current PERF-01 / REC-01 results: **NOT_RUN**. Existing dated harness results and governance limitations remain unchanged.

## Security/privacy and domain review handoff

Keep the existing machine-readable [threat register](../../current/threat-register.json), [0.39 release review](../../release-reviews/release-review-0.39.0.json) and source ASVS/control mapping. Relevant cases must cover revocation, tenant/object/purpose boundaries, privileged roles, sensitive exports, retention/deletion derivatives, provider transfers and restoration. Source controls and original assertions remain mandatory; scan inventories or policy text alone do not qualify them.

Record actual applicable standard/control IDs, case/run versions and environment, finding severity and same-case retest, plus a real independent residual decision. Legal/processor/region/retention decisions remain with qualified accountable people. The preserved 14 critical threats, 13 other threats, two BLOCK chains, G11 Not passed and G12 Not run remain visible. This planning edition neither closes a threat nor approves a release.
