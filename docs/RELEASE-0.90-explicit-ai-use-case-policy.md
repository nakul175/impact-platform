# 0.90 explicit AI use-case policy

FR-AI-001 / APL-338 completes the coding candidate for explicit named AI policy. An administrator can configure advisory drafting, extraction, report drafting and chat independently with exact data classes, destinations, purposes, languages, review mode and budget. Each use case has its own explicit tool allowlist; enabling chat or another use case never enables a tool implicitly.

Provider and tool execution remain separate implementation boundaries. Every runtime must call the shared policy gate with its exact use case and requested tools before reserving budget or transmitting content. Unimplemented runtimes remain unavailable even when a policy rule is enabled. Manual and deterministic workflows remain independent of AI configuration.

This is a coding-only candidate. Source formatting, compilation and contract generation are not qualification. Tests, CI, independent review, merge, staging deployment and owner acceptance remain pending.
