# 0.91 AI input and tool isolation

FR-AI-011 / APL-340 adds a reusable execution boundary between tenant policy and any AI runtime. A policy allowlist is only a ceiling: the runtime independently supplies the closed tool catalogue and argument schemas, and a requested tool absent from that catalogue is refused before reservation or provider execution.

Advisory source material is serialized beneath an explicit untrusted-source envelope, separate from server-owned instructions. The advisory provider receives no tool definitions, database access, export interface, tenant lookup, credentials or external-action surface. Embedded instructions therefore remain data. Recognized unsafe instruction patterns create an audit event containing only coarse categories and `executed_actions: 0`; source text, prompts, credentials and provider responses are not recorded.

This is a coding-only candidate. Source formatting, compilation and contract generation are not qualification. Tests, CI, independent review, merge, staging deployment and owner acceptance remain pending.
