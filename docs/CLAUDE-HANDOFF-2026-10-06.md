# Claude handover — 6 October 2026

Build **0.35.0** is integrated and locally qualified on `integration/0.32-tola-ai-sprint`. The exact complete checkpoint is **`be65086636804027a5fe33943478446b557ebff9`**. Build 0.36 proposals are preserved separately and have **not** been integrated or qualified as a product. Continue from this branch; do not restart from the older deployed main.

The owner requested consolidation, Git preservation and a Claude handover. Parallel development stopped when Codex reached its account usage limit around 22:03 UTC on 5 October. Subsequent scheduled wakeups are not evidence of further development. The development heartbeat is paused for this handover. The requested eight-hour deadline was 08:47:34 IST on 6 October; it does not override release gates.

## Start here

Read [AGENTS.md](../AGENTS.md), [CLAUDE.md](../CLAUDE.md), this document, the [0.35 release](RELEASE-0.35-practical-ai-workspace.md) and its [development record](nonprofit-ai/v1.0/DEVELOPMENT-0.35.md). Then read the [0.36 draft handoff](nonprofit-ai/v1.0/drafts/0.36/HANDOFF.md).

This is one unified Impact Platform/Tola-style monitoring, evaluation and learning product with a nonprofit AI enablement extension. The extension covers adoption planning, tool comparison, team learning, manual practice, procurement preparation, cost comparisons, programme evidence and bounded advisory workflows. It shares tenant identity, current-authority checks, independent decisions, revisions, audit and receipts with the core.

Domain API **1.25.0: 261 operations**; platform API **1.10.0: 52 operations**; schema **40**. Migrations 0001–0040 are frozen. Next migration is 0041. Do not expand capabilities, reset passwords, relax natural-person independence or let AI supply official arithmetic. Synthetic fixture accounts remain separate from real organisation onboarding.

## What is saved

The branch already contains the preceding locally qualified increments:

| Checkpoint | Commit | Main contribution |
| --- | --- | --- |
| 0.31 | `5c6c761bf670b371a2d360f6c6e08ec727395568` | Nonprofit AI costing and guided practice |
| 0.32 | `91de7cbc3bde3d76b080d9a235167744df6a39e2` | Independently reviewed access extensions and archived guidance |
| 0.33 | `861c2a807e774ec6bb53ef05c1ee25f853591085` | Programme evidence links, internal peer advice and visibility controls |
| 0.34 | `740f81339acf97ad49d3212dec7f1aa1555139b1` | Exact saved-plan JSON copies and private receipt-cleanup disclosure correction |
| 0.35 product | `7cf440513fcb8ba4402636345792b7f4c934aff9` | Guided manual practice, canonical saved-plan review, cost-category clarity and fictional walkthrough |
| Complete 0.35 preservation | `be65086636804027a5fe33943478446b557ebff9` | Adds 87 exact sanitized qualification logs omitted by Git's standard log ignore |

The [saved-checkpoint proof](evidence/sprint-0.35-saved-checkpoint.json) verifies all **494 source/verification**, **726 evidence** and **14 documentation** fingerprints against the complete checkpoint's committed blobs. The original [qualification manifest](evidence/sprint-0.35-local-summary.json), SHA-256 `77c60b7c1acf7d79f49534c2454ce1f6146bc10b5829a181a6232459258724dd`, is unchanged.

The handover commit adds documentation and unintegrated drafts after that checkpoint. Its runtime code is the same 0.35 code. Verify historical manifest hashes against the named checkpoint, because current instruction leads intentionally point to this newer handover.

The original BRD/FSD/HLD/LLD, wireframes, data dictionary and test specifications remain in the repository. Source-reference files in the enclosing ChatGPT project's `sources/` are read-only. No source reference was edited.

## Qualification that actually ran

| Scope | Actual result |
| --- | --- |
| Strict TypeScript and dual-entry production build | Both commands passed; 72 closed inputs, eight built files |
| Fresh lint | Passed; 108 closed inputs unchanged |
| Native PostgreSQL 17.11 | 2,102 passed, 26 skipped, one deselected |
| Full embedded-database suite | 2,037 passed, 91 skipped, one deselected |
| Exact unit collection | 1,242 passed, 62 skipped |
| Design reference | 143 passed; explicitly not product acceptance |
| Native restarts | Both phases passed using genuinely separate API processes |
| Native restore | 190 tables/108,188 rows; 71,506,951-byte dump; data, RLS, grants, functions, checksums and official arithmetic preserved |
| Populated deployed-schema upgrade | 33→40 passed with existing data preserved |
| Final browser regression | All 26 modes passed: 281 workflow groups, zero failures/skips/unknowns |
| Pure browser prerequisites | Four prerequisites, 66 passing groups |
| Tracker tooling | 42 passing cases, eight unchanged source inputs |

The final browser run verified 423 sources, eight served/built files and all 40 owning SQL checksums across separate fresh fixtures. It restored 965 historical evidence files and the packaged browser executable. Failed setup/browser attempts and their subsequent corrections are retained; do not rewrite them as successes.

These counts overlap. They do not establish whole-platform completion, production readiness or formal acceptance. The original 307 core requirements remain 113 PARTIAL/194 PENDING/zero accepted. The 40 nonprofit requirements and 108 specified test cases were not promoted by these runs. The execution register now has 2,380 rows; its preceding 2,022-row prefix is unchanged.

Accessibility limits: 54 named axe scans report zero violations; 39 explicitly record zero incomplete entries, while 15 walkthrough scans did not record that field. The broader audit covers 44 pages and retains 50 incomplete entries needing manual review. Final screenshots have bounded OCR/pixel reviews, not WCAG or arbitrary-secret certification.

## Fix these before the next release

1. **Fresh brief preservation:** in 0.35, editing only organisation-profile fields on a blank new plan does not mark the draft dirty. Opening a saved plan can replace that unsaved brief without confirmation. A reproduced private React/Chrome case and reviewed 0.36 fix are preserved. The fix captures a fresh profile baseline, preserves saved-snapshot/read/draft/epoch/pending gates and clarifies the Open versus New discard dialog.
2. **Archive wording:** Unknown/Stale practice copy claims historical guidance is unavailable before checking the archive. The reviewed copy correction makes archive lookup conditional on a saved revision without inferring availability or completeness.
3. **Procurement preview:** a reviewed 0.36 proposal lets users inspect the four generated procurement fields before deliberately replacing them. It preserves all other draft work, rejects stale source/context/head/authority/pending states and adds no API, storage, award or payment.
4. **Accessibility reporting:** preserve raw incomplete entries from the local walkthrough's axe results. The separate post-merge verifier already does this. The local reporting-only patch was assigned but interrupted; check for a completed proposal before inventing one.

Do not deploy 0.35 as if the two known UI limitations were fixed. Apply the reviewed 0.36 work in a new increment and freshly qualify it.

The schema39 private receipt-cleanup disclosure and draft SQL audit/sealing findings were already corrected and qualified in registered schema40/0.34. Do not reopen the old draft SQL or apply a second copy. Private advice/export expiry still does not implement an operated erasure/retention service; exported local files cannot be recalled.

## Resume implementation

Use the [draft preservation manifest](nonprofit-ai/v1.0/drafts/0.36/PRESERVATION-MANIFEST.json) and [controlled application order](nonprofit-ai/v1.0/drafts/0.36/HANDOFF.md). Exact source/proof bytes and superseded candidates are preserved. Private-path references are historical provenance; they are not portable runtime paths.

Keep build-only version changes at 0.36.0; domain/platform/documentation edition, dependencies and schema remain unchanged. Expected full source inventories are 420 application and 426 browser inputs, 74 build and 111 lint inputs, five pure prerequisites and the same 26 browser modes. The proposed enablement checker has 14 always-on groups with all ten original groups retained. These are planned boundaries, not 0.36 execution results.

Producer/checkpoint drafts were interrupted before final review. Review them and adapt workspace/runtime paths, fresh database ownership, credential-map access and source inventories before execution. Never use an old 0.35 build/evidence fallback or silently overwrite failed evidence. Run strict build/lint, actual enablement/browser cases, full native/embedded/unit/reference gates, restart, restore, populated upgrade and all 26 browser suites against the final integrated source. Save a fresh 0.36 manifest.

For portable commands and native role preparation use AGENTS.md/CLAUDE.md and `scripts/run.py`. The preserved local producers use absolute Mac/private paths and installed runtime assumptions. PostgreSQL was 17.11 with six NOINHERIT/NOBYPASSRLS runtime logins; API processes never receive the migration/admin role. No login password map, database dump, real credentials or raw browser logs are in the handover.

## Git, CI and demo gates

Remote: `https://github.com/nakul175/impact-platform.git`. Branch: `integration/0.32-tola-ai-sprint`. Latest fetched main at handover is `69c2cca618ae8dcde8f981c48ece8a1e60f0ff70` (old build 0.29/schema 33). No pull request was created, no hosted qualification was triggered and no new main merge/deployment occurred.

The owner has authorised merging completed work to main. Separate permission for paid GitHub CI remains pending. A previous question proposed at most 540 nominal runner-minutes: initial run, up to two fix runs and a reserved automatic-main run. This is not an invoice guarantee and never authorises raising a spending limit.

The sole workflow runs on pushes to main, pull requests or manual dispatch; a non-main branch push alone does not trigger it. Preserve the owned branch remotely now. Before main merge, obtain the financial permission and require these four genuinely executed successful checks on the exact current candidate:

- `local-reference-and-browser`
- `live-identity-provider`
- `native-postgresql-gate`
- `container-stack`

Keep PR head, base and synthetic merge checkout distinct. Fetch again before merge; changed base/head requires fresh qualification. Stop on instant zero-step billing failures. Use a real merge with the expected head, verify the merged tree and its main checks. Main auto-deploys about every three minutes, so do not bypass these gates with a direct push.

Last observed public deployment remains [the old staging app](https://168-144-78-191.sslip.io/). A future tour URL is `https://168-144-78-191.sslip.io/ai-walkthrough.html`; it has **not** been verified as the new hosted demo. Verify actual merged commit, schema40, health, services, built bytes/CSP and fresh anonymous tour behavior before sharing it as delivered.

The local 0.35 fictional tour was available at `http://127.0.0.1:8171/ai-walkthrough.html` and the local tracker at `http://127.0.0.1:8170`. They depend on this computer and running processes. The tour is synthetic, memory-only and requires no account; it is not a live tenant or saved-plan service. The preserved read-only deployment verifier remains NOT_RUN against a new hosted release.

## Suggested first message to Claude

“Continue from integration/0.32-tola-ai-sprint. Read AGENTS.md, CLAUDE.md and docs/CLAUDE-HANDOFF-2026-10-06.md. Preserve the qualified0.35 checkpoint and integrate the exact reviewed0.36 procurement-preview/profile-preservation/archive-copy proposals in the documented order. Review unfinished producer drafts, requalify the final source, update documents and preserve historical evidence. Main merge is authorised after all four exact-head CI checks pass; paid CI permission remains pending. Do not reset real accounts, relax independence or claim a hosted demo before actual commit/schema/health verification.”
