# Release 0.56 coding candidate: locked value-case baseline

US-VC-05 / APL-392 (frozen story Gherkin SHA-256 `1902027ca028ec888299bc06caf47385b22a780559f8f58e359b5d8033f0d457`; containing feature-file SHA-256 `b72f197ce6422287c47a34c8e154d7dac7016fdc83a9247b7cdbc1b5eb414646`) adds versioned self-reported value cases and a locked baseline revision.

A tenant administrator can save a server-calculated value-case draft. A different authorised natural person must approve it under fresh assurance; the service refuses an author recorded for the object. An approved revision can then be locked under a second fresh-assurance action. The approved revision records server time and the approving principal. Every mutation uses an exact operation ID, current expected revision, tenant lock, append-only audit and seven-day receipt replay; changed-payload reuse and stale revisions are refused. The browser retains the exact operation ID and request bytes after an uncertain failure so a retry is the same operation.

Editing a locked case uses the explicit revise action. It appends a new Draft revision, records that revision's natural-person author, and records the prior locked revision as `baseline_revision`; the immutable locked revision remains addressable through the exact revision read. The opportunity identity cannot change across the revision boundary. Locking the new draft creates a new baseline revision without rewriting history. This replacement behavior is provisional pending the owner's correction-policy decision.

The approval and lock actions provisionally use `TENANT_ADMIN` because the current role model has no separate Executive Director template. This requires owner review. The generated bootstrap profile records future/bootstrap authority only and does not widen existing tenants automatically.

The candidate preserves the prior locked revision as a baseline pointer. No realised-ROI workflow consumes that pointer yet, so the criterion that later ROI is measured against the locked version remains an explicitly disclosed integration gap. Replacement/correction policy for a subsequently locked baseline also remains an owner decision; history itself is never rewritten.

This is a coding-only candidate. Tests, CI, independent review, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
