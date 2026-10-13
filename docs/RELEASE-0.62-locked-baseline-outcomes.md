# Release 0.62 candidate — locked-baseline usage and outcomes

## Delivered

US-IM-01 / APL-371 has a coding-only candidate for Executive Director tracking of current usage and outcomes after an adoption plan has an actual deployment attestation. Each observation is immutable and self-reported. The server binds it to the current completed plan revision, exact deployment attestation, exact locked problem-baseline revision, diagnosis problem and source-derived mapped opportunity.

The dashboard always shows usage, time, cost, quality and reach. Usage explicitly says the locked baseline did not record it. For the other four measures, a signed current-minus-baseline difference is returned only when unit and basis match exactly; incompatible measures remain visible without conversion. The response and UI state that this is not proof of causality, realised ROI or independent verification.

## Contract and persistence

Domain API 1.53 adds create-only outcome observations and a read-only comparison dashboard. Schema56 registers `AICurrentOutcomeObservation` in the immutable generic object store and adds restrictive worker policies. No historical migration, source baseline, deployment attestation or observation is rewritten.

## Limits

This candidate does not establish that the deployed solution technically implements the mapped opportunity. It records the authorised manager's explicit tracking association after validating both source chains. There is no baseline usage value in the frozen baseline contract, no unit conversion, no provider telemetry and no official impact arithmetic.

## Reproduction

Only source formatting, Python compilation, generated-contract parsing and TypeScript compilation are permitted in this coding phase. Tests, CI, independent human review, merge and staging deployment remain later combined gates.

## Integration notes

Register migration0056 after0055. Rebuild contracts and API inventory. Keep release review `passed=false` until the later test and review phase supplies actual evidence.
