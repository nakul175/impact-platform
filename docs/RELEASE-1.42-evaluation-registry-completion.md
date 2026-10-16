# Release 1.42 — controlled evaluation registry completion

## Delivered

APL-625 / FR-EVA-001 adds governed baseline, midline, endline and other evaluation registrations. Each registration pins a programme and observation period, records questions, method, evaluator, budget, deliverables and policy documents, and begins at `REGISTERED` without approving sensitive processing.

Field collection and publication use ordered, revision-checked stage gates. The server always requires methodology evidence; sensitive evaluations additionally require ethics and safeguarding evidence; publication also requires disclosure review. These gates never approve sensitive processing, which remains a separate governed decision outside this registration flow. Missing evidence creates a durable blocked decision. Passed and blocked decisions remain in immutable revision history.

Independence claims require a current exact evidence revision and remain labelled `EVIDENCE_ATTACHED_UNVERIFIED`; registration cannot convert a self-declaration into verified independence.

## Contract and persistence

The API exposes create, list, read, stage-gate and gate-history operations with dedicated capability metadata. Migration 0104 registers `EvaluationRegistration` and prevents delivery-worker access to its registry and revision rows.

## Limits

This coding checkpoint is not merged, deployed or owner-accepted. It does not verify evaluator independence, approve a methodology, or provide consent for participant-level sensitive processing outside the explicit pinned gate evidence.

## Reproduction

Run `make lint`, `make unit`, `.venv/bin/python scripts/release_review.py --check`, and regenerate implemented contracts and the access profile.

## Integration notes

Requirement FR-EVA-001 may move to coding-complete after review of the exact commit. Test, CI, merge, staging deployment and acceptance remain separate gates.
