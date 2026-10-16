# 0.95 AI evaluation gate

FR-AI-015 / APL-344 adds a code-owned, fail-closed evaluation manifest for each executable AI use case. A manifest names its owner, exact model/prompt/retrieval/tool configuration, governed held-out dataset reference, expected judgements, supported language/sector matrix, release report, regression result, critical findings and justified exceptions.

Controlled exposure requires an exact configuration match and a passed regression. Any cross-tenant leak, unsupported critical claim or unauthorised action blocks exposure regardless of average quality. Every exception needs a non-empty recorded justification. Model, prompt, retrieval, tool or policy-related configuration drift fails the exact-match gate and requires a new report before exposure.

The initial advisory manifest deliberately remains `PENDING`: no evaluation, appointed human owner or release report is invented by this coding increment, so advisory exposure is held until combined qualification supplies and reviews those records.

`qualification/test_ai_evaluation_gate_live.py` qualifies the code-owned gate with an exact synthetic passed manifest, configuration drift, pending regression, a critical cross-tenant finding, an unjustified exception and a missing owner. Every incomplete or changed candidate fails closed with `AI_EVALUATION_NOT_PASSED`. It also confirms that the repository's real advisory manifest remains truthfully blocked while its owner, dataset receipt and release report are pending. CI, independent review, staging deployment and owner acceptance remain separate gates.
