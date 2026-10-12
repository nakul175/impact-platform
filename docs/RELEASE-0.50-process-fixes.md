# Release 0.50 coding candidate: process fixes alongside technology

US-MP-02 / APL-378 (frozen Gherkin SHA-256 `33c23891daaa0fcd36567b7e23e9e17b775eb06ed97177fe3fec94501970fe91`) extends the pinned problem-opportunity library with a closed `PROCESS_FIX` kind. The same server mapping returns process fixes and technology opportunities together; clients cannot request a tech-only result or hide a server-owned process fix from the response.

The completed-diagnosis view renders each process fix as **Process fix — no technology purchase required**. Current source-backed examples cover reviewed localization routines and staff practice with human review. These are contextual patterns rather than comparative proof that a process fix will outperform technology.

The pattern library remains fail-closed: a malformed process-fix record prevents a mapping response, and a flagged problem is never made complete with an invented option. No commercial catalogue, ranking, purchase approval or provider call participates in this path.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
