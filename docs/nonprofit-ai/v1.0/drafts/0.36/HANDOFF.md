# Preserved 0.36 proposals — controlled continuation

**NOT INTEGRATED / NOT PRODUCT QUALIFIED.** Current product remains 0.35.0. [The main handover](../../../../CLAUDE-HANDOFF-2026-10-06.md) explains the completed checkpoint, release gates and outstanding limitations.

[PRESERVATION-MANIFEST.json](PRESERVATION-MANIFEST.json) maps exact copied bytes to their original private locations. Original handoffs, superseded candidates and synthetic proofs are retained unchanged. Do not bulk-copy this directory into runtime source. Files marked private/root-review-pending retain their original historical status; this handover does not upgrade them.

## Apply the final proposals in this order

1. Verify the current registered0.35 Workspace SHA `b1c807582555e362800b7db5cef93e65927fd4b9ab461dc7bb0c13f8bb561eda`, planning checker SHA `d83752e823e5f47d4a0cddaea014937db17b05821397601a96485497e267d790`, unchanged contracts/profile and all40 migrations.
2. Read [the original procurement package checklist](integration-package/INTEGRATION-CHECKLIST.md) and [package handoff](integration-package/PACKAGE-HANDOFF.json).
3. Copy its exact `files/apps/web/src/AIProcurementPreviewModel.ts` (1718d6fe…) and `AIProcurementPreview.tsx` (c2b59be6…). The existing four generator strings/order/fallback/UTF16 behavior are retained.
4. For Workspace use [the FINAL composed-from035 patch](profile-preservation/composed-workspace.from-035.patch), SHA `8a83cadf1f260c41ffbb67a7c00a77eee68e043a84ffbc3b470216da25f6ea0f`, producing exact final `profile-preservation/proposed/AIAdoptionWorkspace.tsx` SHA `5a853988b3c3035ea84305a0f857d0a958113bc2913d3e26a8a7946c7d2b5230`. **Do not also apply** the older ac1c preview Workspace patch. Alternatively apply that older preview patch and then the narrow final profile patch; never both compositions.
5. Use final [enablement checker](profile-preservation/ai-enablement-check.proposed.mjs), SHA `71219064a7e56352f45a3a92e58017bc0cdb184b3a40339c8970f13d007a7dc9`, rather than older package d742. All14 groups run normally; no custom environment guard or skip is added.
6. Copy the package's pure model checker `files/tools/browser/ai-procurement-preview-model-check.mjs`, SHA `d4fb4d7cfb3e1a73efe5c48878069e9f6680e083862bea03343bdd6de9dd69ea`. Apply its one-line [Makefile prerequisite patch](integration-package/patches/Makefile.proposed.patch), SHA02e4b516… .
7. Apply the exact [availability-neutral practice-copy patch](practice-copy/availability-neutral-practice-copy.patch), SHA `7e812fe0485ee884935ac8c7f13b3da3a7f52ec10b9d8b4b74b8dad0370c3009`, on the d837 planning checker/current AITaskPractice parent. It changes two paragraphs, two existing waits and a label while retaining all260 assertions, native keyboard and table checks.
8. Apply only [build metadata patch](integration-package/patches/build-version-only.proposed.patch): build0.36.0 in VERSION/package/lock. Domain1.25/platform1.10/schema40/documentation1.1/dependencies stay unchanged.
9. Review [model/design documentation proposal](integration-package/review/DEVELOPMENT-procurement-preview.proposed.md) and register its narrow FSD/HLD/LLD/transient-field/wireframe notes in a new0.36 release/development document. Do not promote requirement acceptance.
10. Add a narrow local-tour reporting change to retain axe incomplete entries if no completed proposal exists. This was assigned when the agent hit its usage limit; do not claim it implemented.

## Evidence boundaries

- Procurement: original28 pure/model checks and12 synthetic React/Chrome UI cases; later35 generator/model checks retain exact Python public-generator strings and UTF16 limits. These are overlapping/private scopes, not actual API or award tests.
- Profile: actual old035 local-input-loss reproduction; reviewed fix16 synthetic cases, repeated after conditional dialog wording. Both16 reports are preserved and not counted as32 new cases. Mocked requests are explicitly not API/current-authority/database qualification.
- The final always-on actual14-group browser checker was prepared but never executed against an integrated0.36 product. It retains real canonical-read/current-count/no-write, independent authority-loss, held response and committed-lost-save exact-retry controls.
- The wrapper has16 offline guard groups on a labelled synthetic future recipe/assets fixture. Actual0.36 broad qualification is NOT_RUN.
- The read-only deployment verifier has23 offline tests; no new main commit/CI/build/hosting was supplied to it.
- The four producer drafts and root checkpoint proposal were interrupted before complete handoff/independent review. AST or source presence does not qualify their execution.

The exact expected boundaries are application420/browser426 source files, build74/lint111 closed inputs, five pure prerequisites (101 groups), 26 browser modes, actual40-migration ledger and successful current eight-file build. Confirm against the real integrated graph; do not waive a changed inventory/asset graph to get green.

## Producers and portable use

[producer-drafts/](producer-drafts/) preserves all work found on disk, including preparation templates and three original035 predecessors. It has no completed final handoff. Review source before running.

[browser wrapper handoff](browser-wrapper/handoff.json) binds its exact proposal and offline proof. Root [checkpoint proposal](checkpoint-manifest.proposed.py) SHA `21aaa2b284eeba7c7e66dfcdeb453b62494644e0d772e0a473e706968c78bf05` requires the explicit saved035 baseline commit; it is unexecuted and needs independent review. Use `be65086636804027a5fe33943478446b557ebff9` as the complete historical checkpoint, not the unintegrated current draft.

Absolute Mac/private paths, native credential-map names and installed-runtime assumptions are original provenance. Adapt them deliberately for Claude's environment; no credential map/database/raw runtime log was copied. Do not provision or reset a real user's password. For new test fixtures follow the repository's governed test setup.

Preserve every failed or superseded result before rerunning. A new source change invalidates affected gates. Qualification must include strict build/lint, actual14-group enablement, final all26 modes/five pure prerequisites, fresh full native/embedded/unit/reference, separate restarts, restore and populated33→40 upgrade. Hosted four-job checks and actual deployment remain separate.
