# AI features: evaluation and limits

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: first live evaluation of provider output, a new AI operation, a change in qualification counts, or any incident involving AI output.

Status: **agent-drafted 2026-10-08; not reviewed by a person or counsel; no certification is claimed.** Companion to [AI-MODEL-CARD](AI-MODEL-CARD.md). Facts come from [RELEASE-0.30-nonprofit-ai-enablement](../RELEASE-0.30-nonprofit-ai-enablement.md), [nonprofit-ai security and privacy](../nonprofit-ai/v1.0/09-SECURITY-AND-PRIVACY.md), the provider adapter and the `qualification/test_ai_*.py` files.

## 1. What has been evaluated

| Area | Evidence | What it shows |
|---|---|---|
| Provider adapter | `qualification/test_ai_advisory_provider.py` (synthetic responses) | Request shape, `store:false`, output and time bounds, error mapping; not model quality |
| Advisory authorisation and replay | `test_ai_enablement.py`, `test_ai_enablement_live.py` | Consent, capability, attempt budget, sealed replay, tenant isolation, on synthetic data |
| Deterministic AI-adjacent features | `test_ai_adoption_plans*.py`, `test_ai_solutions_catalog.py`, `test_ai_learning_content.py`, `test_ai_procurement_costs.py`, `test_ai_plan_exports*.py`, `test_ai_impact_references.py`, `test_human_advice*.py` | Behaviour of catalogue, plans, exports and advice cases |
| Whole-suite state | RELEASE-0.36 / HANDOVER for the 0.36 candidate: native 2,102, embedded 2,037, unit 1,242 passed with explicit skips (local run, not producer-generated, hosted CI not run) | Context only; counts overlap and say nothing about advisory quality |

## 2. What has not been evaluated

- **Output quality, accuracy, bias, harmful or unsupported claims, prompt-injection resilience against a live model:** no systematic evaluation exists. The security note lists "systematic output evaluation" as target work (T-NPA-003: the control is stated, not proven).
- **Live generation:** never succeeded in qualification (quota error on 2026-10-05).
- **Human-review effectiveness:** no study; reviewer guidance exists only as the instruction to review.
- **Evaluation set, metrics, acceptance thresholds, red-team record:** none: TBD (owner: Nakul Jain).

## 3. Known limits

1. Drafts can be wrong, generic or stale; the model may state vendor facts that are false despite the instruction not to. Catalogue content is dated editorial content with sources, not live market data; no real prices, certifications or rankings are claimed.
2. The `sensitive_data` flag on a brief is self-reported; it is not a detector and not permission to send sensitive text. Free text can contain prohibited information.
3. Three attempts per rolling 24 hours per tenant (failures count); no currency budget ledger or usage reconciliation.
4. `store:false` is not proof of zero retention at the provider; transfer destination and retention terms are not established.
5. Sealed outputs use the delivery keyring; retiring that secret makes older sealed results unreadable ([SECRETS-REGISTER](SECRETS-REGISTER.md)).
6. The 45-second deadline cancels the network wait but a resolver thread may not be cancellable (adapter docstring); it is not a hard process-wide bound.
7. No red-teaming of the combined human and model workflow; no accessibility review of AI output beyond the general client scans.
8. Pilot use is synthetic only. Enabling AI for a tenant that enters real organisation data needs the [DPIA](DPIA.md) row 7 and provider terms first.

## 4. Misuse that must stay blocked

Official arithmetic, approvals, grant widening, automatic purchases or supplier contact. These are product rules (repository rule 5; RELEASE-0.30: outputs cannot alter official results or grant authority), and each must keep a test if code near it changes.

## 5. Next steps (owner decisions)

Fund a project key and run a live check; define an evaluation set and thresholds before any non-synthetic pilot; decide provider region and retention terms; record results here with dates.
