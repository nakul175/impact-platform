# Release 1.05 coding candidate — snapshot-bound report drafting

FR-AI-007 / APL-339 adds a report-drafting workspace for Authors, Programme Managers and MEL Administrators. Every proposal pins an exact current locked Snapshot revision, an exact current approved ReportTemplate revision, the policy version and language. Section inputs can reference only official result and Evidence revisions already present in that Snapshot; the existing Reporting reconciler enforces those bindings and current caller authority.

Official figures remain `{{binding_code}}` tokens backed by exact result revisions. A bare number or unknown token is refused, so drafted prose cannot invent or silently alter an official value. Required template sections and bindings absent from the selected snapshot stay visible as evidence gaps. Template caveat codes are copied into the immutable draft and must remain byte-for-byte present at human review.

Review records the AI-origin proposal, exact before/after corrections and final human wording without changing any Report or Snapshot. Review may edit narrative wording only; result bindings, evidence references, section identity and charts remain pinned. A later generation requires a reviewed prior draft plus an explicit list of sections to regenerate. All other reviewed human sections are copied forward unchanged, preventing silent overwrite.

Migration 0089 creates tenant-fenced, insert-only draft and review records with exact source ancestry and idempotent operation receipts. The feature does not create an official snapshot, result, report or publication.

The positive user journey is qualified on a disposable native PostgreSQL/API runtime by
`qualification/test_ai_report_drafting_live.py` (1 passed), alongside four reporting regressions.
The run proves exact locked snapshot, approved template, result binding and evidence pins; visible
gaps/caveats; a human narrative-only correction retaining AI ancestry; and no Report or Snapshot
creation during drafting or review. The insert-only review path remains serialized by the tenant
advisory lock without requesting database update rights. Ruff and the structural release review pass.

This evidence qualifies the positive-user-journey gate for APL-339. CI, independent review, merge,
staging deployment and owner acceptance remain pending.
