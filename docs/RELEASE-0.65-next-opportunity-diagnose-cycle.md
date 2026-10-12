# Release 0.65 candidate — next opportunity Diagnose cycles

Coding-only candidate for **US-IM-04 / APL-569**. The frozen source is `docs/backlog/features/adoption-improve.feature`; the exact US-IM-04 rule SHA-256 is `31515d30af8ac81632fa4edaea16e2884a580d2fc86ee95874b8dd3c1ee46ce6`.

An Executive Director who is the current tenant owner can view deterministic suggestions only after a completed quarterly value review. Each suggestion pins that review and the prior diagnosis problem that fed its reviewed outcome. Taking up a suggestion atomically creates a distinct blank `AIDiagnosis` in `Draft` plus an immutable `AIImproveDiagnosisCycle` in `Diagnose`. It cannot create an assessment, baseline, plan, procurement, pilot, deployment, or claimed benefit.

Domain API 1.56 adds the list and take-up routes. Schema 59 adds durable exact source, authority, operation, cycle, and created-diagnosis pins with tenant RLS, immutability, suggestion uniqueness, and restrictive worker fences. Exact operation retries remain recoverable from the durable cycle binding after the ordinary receipt expires.

Tests, CI, merge, deployment, product acceptance, and human certification are intentionally pending under the owner's coding-first instruction.
