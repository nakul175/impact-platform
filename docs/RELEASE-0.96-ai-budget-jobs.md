# 0.96 AI budget reservation and durable jobs

FR-AI-016a / APL-345 adds an asynchronous advisory submission path. An accepted request returns HTTP 202 with a durable job ID, queued state, progress, estimated units and cancellation availability. The exact request is encrypted at rest; current policy, evaluation readiness, data handling and source authority are checked before any reservation.

One server-estimated unit is atomically reserved against the exact immutable policy version under the tenant lock. Existing reserved and settled units count against the policy budget; insufficient remainder returns `AI_BUDGET_EXHAUSTED` before a job or reservation is written. This ledger is independent of ordinary data approval, deterministic calculation and report generation, so exhausting AI budget does not gate core MEL work.

Requester-only status and cancellation endpoints expose bounded job metadata. Cancelling a queued job atomically marks it cancelled and releases the full reservation; a running job records a cancellation request for the fenced worker. The UI keeps the submitted brief on refusal and shows job progress, reserved units, refresh and Cancel controls.

This coding candidate establishes submission, reservation and cancellation. Worker execution and terminal settlement are the next split story, FR-AI-016b.

`qualification/test_ai_budget_jobs_live.py` uses the real disposable database with a synthetic configured provider and exact synthetic evaluation pass. It proves durable acceptance as a queued cancellable job, exact replay, requester status, one-unit reservation against the exact policy version, queued cancellation, and atomic release with zero actual units. CI, independent review, staging deployment and owner acceptance remain separate gates.
