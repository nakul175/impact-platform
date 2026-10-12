# 0.94 AI task trace

FR-AI-014 / APL-343 adds a closed trace to every successful advisory result. It records the requester, bounded use-case scope, exact source versions, the policy/use-case configuration used, model identifier, tool receipts, proposed changes, review decisions, applied domain receipts, a thirty-day retention deadline and a SHA-256 output version.

The advisory runtime exposes no tools or domain-change command, so its tool, proposed-change, review and applied-receipt lists are explicitly empty rather than invented. Later AI task runtimes can populate the same bounded trace fields when they actually execute those stages. The provider parser accepts only output text and numeric usage; hidden model reasoning is neither accepted, stored nor returned. Inspection shows concise evidence and decisions without chain-of-thought content.

This is a coding-only candidate. Source formatting, compilation and contract generation are not qualification. Tests, CI, independent review, merge, staging deployment and owner acceptance remain pending.
