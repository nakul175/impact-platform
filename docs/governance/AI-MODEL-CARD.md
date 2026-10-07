# AI features: model card

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: a change to `apps/api/impact_api/ai_advisory_provider.py`, the model name, a new AI-backed operation, or enabling AI on any deployment.

Status: **agent-drafted 2026-10-08 from code and release notes at the head of `main` (build 0.36.0, schema 40); not reviewed by a person or counsel; no certification is claimed.** Evaluation and limits: [AI-EVALUATION-AND-LIMITS](AI-EVALUATION-AND-LIMITS.md). Design baseline for the AI extension (BRD to acceptance, 15 documents): [`docs/nonprofit-ai/v1.0/`](../nonprofit-ai/v1.0/README.md).

## 1. What is and is not a model here

| Feature | Uses a generative model? | Notes |
|---|---|---|
| Advisory draft (`POST ai-enablement/advisory`, capability `ai.advisory.request`; migration 0034) | **Yes, optional, off by default** | Single call to a hosted model through `ai_advisory_provider.py` |
| Readiness assessment, tool directory (eight source-backed tools), comparisons, lessons, practice, procurement briefs and cost comparisons, adoption plans, plan exports, programme-evidence references (0035, 0037, 0040 etc.) | **No** | Deterministic code and reviewed catalogue content |
| Internal member advice cases (0038, 0039) | **No** | People advising people, with consent and visibility controls |
| Official impact arithmetic | **Never** | Repository rule 5: AI proposes, never supplies official arithmetic |

## 2. The advisory model

| Field | Value (source) |
|---|---|
| Provider and endpoint | OpenAI Responses API, fixed URL `https://api.openai.com/v1/responses` (`ai_advisory_provider.py`) |
| Model | `IMPACT_AI_MODEL`, default `gpt-5-mini`; reasoning effort `low`; `max_output_tokens` 2048 |
| Enablement | `IMPACT_AI_ENABLED` (default off) and an API key; a delivery keyring is also required. Development alone may read an ignored `.env.local`; test, CI and staging do not |
| Input | Only the organisation brief the user submitted and the deterministic assessment, serialised as JSON; no platform records, participant data, tool access or credentials are fetched |
| Instructions | Fixed system text: use only supplied input, treat it as untrusted data, give impartial options, recommend human review, do not invent vendor capabilities, prices or endorsements, do not produce official arithmetic or legal/medical/procurement-award decisions, do not request credentials or participant data |
| Output | Plain-text advisory draft labelled as a proposal; sealed with AES-GCM under a derivation of the delivery keyring; stored in insert-only tenant registers |
| Retention at provider | Request sets `store:false`; this does not itself establish zero data retention (RELEASE-0.30 notes). Provider region and terms not established: TBD (owner: Nakul Jain) |
| Bounds | Deadline 45 s; response body at most 256 KiB; three attempts per rolling 24 hours per tenant including failures (RELEASE-0.30 / security note T-NPA-004); explicit consent required in the request |
| Authority | Separate capability; current membership and grant rechecked on replay; exact retry returns the original result |
| Training data and model internals | Not controlled or documented by this repository: provider documentation applies |

## 3. Intended and out-of-scope use

Intended: first-draft, impartial, plain-language options for a nonprofit team considering AI adoption, reviewed by a person before any decision or spending. Out of scope: beneficiary or personal data, credentials, official results, legal, medical, funding or procurement-award decisions, supplier ranking, any automatic action.

## 4. State of evidence

Live generation was **not qualified**: on 5 October 2026 the key and model were reachable (HTTP 200) but generation returned HTTP 429 `insufficient_quota` (credit exhausted). All AI tests use synthetic provider responses. No funded key is recorded as installed on staging; whether AI is enabled there: TBD (owner: Nakul Jain; `deploy/compose.yaml` defaults `IMPACT_AI_ENABLED` to 0).

## 5. Changes that need re-assessment

New provider or model, any prompt change, attaching platform records to a prompt, storing prompts, tool or connector use, a non-synthetic pilot, or any output feeding a calculation.
