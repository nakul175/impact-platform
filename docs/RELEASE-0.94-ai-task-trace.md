# 0.94 AI task trace

FR-AI-014 / APL-343 adds a closed trace to every successful advisory result. It records the requester, bounded use-case scope, exact source versions, the policy/use-case configuration used, model identifier, tool receipts, proposed changes, review decisions, applied domain receipts, a thirty-day retention deadline and a SHA-256 output version.

The advisory runtime exposes no tools or domain-change command, so its tool, proposed-change, review and applied-receipt lists are explicitly empty rather than invented. Later AI task runtimes can populate the same bounded trace fields when they actually execute those stages. The provider parser accepts only output text and numeric usage; hidden model reasoning is neither accepted, stored nor returned. Inspection shows concise evidence and decisions without chain-of-thought content.

The positive user journey is qualified on a disposable native PostgreSQL/API runtime by
`qualification/test_ai_task_trace_live.py` (1 passed). The successful synthetic task records the
requester, bounded scope, exact policy configuration, model identifier, empty server-owned tool and
change receipts, SHA-256 output version and thirty-day retention deadline. Exact replay returns the
same sealed trace without a second provider call and one completion audit remains. Provider-supplied
hidden reasoning and forged tool receipts are discarded rather than stored or exposed.

This evidence qualifies the positive-user-journey gate for APL-343. CI, independent review, merge,
staging deployment and owner acceptance remain pending.
