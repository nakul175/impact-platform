# Release 1.05 coding candidate — snapshot-bound report drafting

FR-AI-007 / APL-339 adds a report-drafting workspace for Authors, Programme Managers and MEL Administrators. Every proposal pins an exact current locked Snapshot revision, an exact current approved ReportTemplate revision, the policy version and language. Section inputs can reference only official result and Evidence revisions already present in that Snapshot; the existing Reporting reconciler enforces those bindings and current caller authority.

Official figures remain `{{binding_code}}` tokens backed by exact result revisions. A bare number or unknown token is refused, so drafted prose cannot invent or silently alter an official value. Required template sections and bindings absent from the selected snapshot stay visible as evidence gaps. Template caveat codes are copied into the immutable draft and must remain byte-for-byte present at human review.

Review records the AI-origin proposal, exact before/after corrections and final human wording without changing any Report or Snapshot. Review may edit narrative wording only; result bindings, evidence references, section identity and charts remain pinned. A later generation requires a reviewed prior draft plus an explicit list of sections to regenerate. All other reviewed human sections are copied forward unchanged, preventing silent overwrite.

Migration 0089 creates tenant-fenced, insert-only draft and review records with exact source ancestry and idempotent operation receipts. The feature does not create an official snapshot, result, report or publication. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
