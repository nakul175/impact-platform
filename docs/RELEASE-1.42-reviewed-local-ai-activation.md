# Release 1.42 — reviewed local assistance activation

## Delivered

APL-533, APL-535, APL-537, APL-538, APL-597, APL-601 and APL-541 can run their existing deterministic assistance handlers under an explicit reviewed local server configuration. The owner authorized this local activation repair; that instruction is not security certification, release signoff or acceptance of the frozen criteria.

`IMPACT_AI_REVIEWED_USE_CASES` is a comma-separated closed allowlist: `INDICATOR_DESIGN`, `IMPORT_CLEANING`, `EVIDENCE_QUESTION`, `NUMERIC_ANALYSIS`, `QUALITATIVE_ASSISTANCE`, `PROACTIVE_FINDINGS`, `ACTION_PROPOSAL`. It defaults to empty. Unknown, duplicate or empty identifiers fail settings construction. A nonempty allowlist is forbidden in staging and production. It applies only to an explicitly configured development/test API process; no existing runtime, tenant policy, production identity or provider account is changed.

The server allowlist does not enable tenant policy. An authorized administrator must save a real immutable policy version with the required use case, data classification, destination, languages, purpose and explicit tools. Every fresh execution checks the frozen server configuration through the real policy gate and retains current authority, source version and safety shutdown checks. Policy discovery reports the remaining unactivated reserved cases for that process.

## Contract and persistence

No new request DTO, database migration, table grant, provider call or spending change. Applied migrations0001–0118 and frozen source criteria remain unchanged. `ai_enabled` continues to govern the separately configured advisory provider; the local reviewed allowlist governs the seven deterministic assistance handlers and does not imply live model qualification.

Activation-sensitive policy validation runs after current authorization and matching operation-receipt lookup. An exact committed policy or effect retry still returns its immutable receipt after server configuration rollback. A changed request under the same operation conflicts; a fresh operation under the rolled-back configuration is refused. Returning an already committed receipt is not new execution.

## Reproduction

`qualification/test_ai_reviewed_activation_live.py` starts separate actual loopback API processes with private synthetic configuration, no provider key and real policy/safety implementations. It saves tenant policy over HTTP and exercises all seven real routes. Each mapped journey additionally verifies default-runtime refusal of fresh operations despite a stored enabled policy, tenant-policy disablement, a real use-case safety shutdown, zero partial durable writes and ordinary manual programme access. The indicator draft also verifies committed exact replay after rollback. A separate policy-save scenario verifies exact replay, changed-operation conflicts and authorization before exposing local activation state.

`qualification/test_ai_reviewed_activation_unit.py` covers closed configuration, production/staging refusal, exact subset activation, tenant policy and runtime rollback. The previous component packs remain separately identified and retain their assertions; they are not used as external runtime evidence.

## Limits

Final clean-source combined qualification on `fba5d44279f10add768a6f53905bcc316bb601dd` passes: **2,671 passed, zero failures, 229 skipped and one deselected**. Source digests match before/after. The mapped bounded local positive, authorization/refusal and error/recovery gates each pass **56/56**, including the seven actual external HTTP nodes. Earlier49/56 receipts remain historical. See [run receipt](evidence/candidate-1.42/reviewed-activation-20261016/FINAL-RUN-RECEIPT.json) and [story gate evidence](evidence/candidate-1.42/reviewed-activation-20261016/STORY-GATE-RESULTS.json). This does not qualify staging/production activation, a paid/live model, hosted CI, all frozen assertions, independent human review or owner acceptance. IR-1.42-24 remains unconfirmed.

## Integration notes

One integration writer; independent read-only code review. The existing 49-story map is preserved and extended to the exact seven IDs above. Published historical evidence and earlier failed attempts remain retained; no existing test is weakened, removed or skipped. Focused failures during construction are exploratory evidence, not exact final-source qualification.
