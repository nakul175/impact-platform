# Release 0.64 candidate — quarterly value reviews

## Delivered

US-IM-03 / APL-374 has a coding-only candidate for an authorised Imprana Advisor to start a due quarterly value review from a fixed server-owned template. The review pins the exact current outcome observation, completed plan revision, deployment attestation, locked baseline revision and mapped opportunity. The observation period end is the recorded due date and must not be in the future.

The review records explicit agreements separately from tracked actions. Each tracked action links exactly one agreement, names a current active internal natural-person owner, records a due date and starts with an OPEN status. Progress updates append immutable review revisions with a closed status and note. Completion refuses the transaction unless every agreement has exactly one linked action with a current owner and tracked status.

## Contract and persistence

Domain API 1.55 adds start, read, agreement, action, progress and completion routes under the existing advisor capability. Schema58 registers `AIQuarterlyValueReview` in the immutable generic object store and adds restrictive worker policies. Every mutation uses an expected revision and exact operation receipt; current source, advisor and action-owner authority are rechecked.

## Limits

A completed review means its record is complete; tracked actions may remain open, blocked or in progress. This candidate does not schedule reminders, send messages, call a provider, certify review quality or establish causal/official results. Due status is based on the self-reported observation period end because the frozen story supplies no separate quarterly calendar decision.

## Reproduction

Only source formatting, Python compilation, generated-contract parsing and TypeScript compilation are permitted in this coding phase. Tests, CI, independent human review, merge and staging deployment remain later combined gates.

## Integration notes

Register migration0058 after0057. Rebuild contracts and API inventory. Keep release review `passed=false` until the later test and review phase supplies actual evidence.
