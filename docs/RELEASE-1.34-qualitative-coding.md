# Release 1.34 coding candidate — qualitative coding

FR-EVD-005 / APL-641 adds versioned codebooks with stable code identities, meanings and inclusion/exclusion examples. Independent coder assignments pin source and codebook revisions and inherit the source classification.

Adjudication preserves both assignments, the exact codebook version and rationale. Agreement calculations include matched units only and never overwrite individual work.

## Positive-journey qualification status

The synthetic live journey is implemented in
`qualification/test_qualitative_coding_live.py`. It creates clean synthetic evidence, a versioned
codebook, two assignments by different natural people and an adjudication, then inspects the
durable revisions for both original assignments, the codebook pin and the rationale.

The initial 16 October 2026 run exposed missing policy operations and registry kinds. Migration 0108
now registers all four qualitative kinds behind restrictive delivery-worker fences, and the generated
policy limits the write operations to existing evaluation-edit authority. Adjudication additionally
requires a third natural person and comparable, current codebook revisions.

The repaired exact-candidate run passed the positive journey: **1 passed**. This is local synthetic
evidence only; CI, merge, staging deployment and owner acceptance remain separate gates.
