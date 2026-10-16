# 0.90 explicit AI use-case policy

FR-AI-001 / APL-338 completes the coding candidate for explicit named AI policy. An administrator can configure advisory drafting, extraction, report drafting and chat independently with exact data classes, destinations, purposes, languages, review mode and budget. Each use case has its own explicit tool allowlist; enabling chat or another use case never enables a tool implicitly.

Provider and tool execution remain separate implementation boundaries. Every runtime must call the shared policy gate with its exact use case and requested tools before reserving budget or transmitting content. Unimplemented runtimes remain unavailable even when a policy rule is enabled. Manual and deterministic workflows remain independent of AI configuration.

The positive user journey is qualified on a disposable native PostgreSQL/API runtime by
`qualification/test_ai_policy.py` (12 passed). The evidence proves that one named use case can be
enabled and read as the current audited policy while every other use case remains independent;
manual reporting still completes with AI disabled and without a provider call; sensitive data,
unapproved destinations, languages, budgets and stale policy versions fail closed before any
reservation or provider call; and tools require both an explicit per-use-case allowlist and runtime
approval. The same run proves tenant fencing, fresh administrative authority, immutable policy
history and exact retry behavior.

This evidence qualifies the positive-user-journey gate for APL-338. CI, independent review, merge,
staging deployment and owner acceptance remain pending.
