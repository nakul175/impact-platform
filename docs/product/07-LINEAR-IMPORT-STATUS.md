# Imprana Commons Linear import status and handover

Nakul authorised creating the product planning hierarchy and integrating it into Linear on 10 October 2026. The [Imprana Commons project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) in Aplyd Sandbox, team APL, now contains **11 documents, five release milestones and all 446 read-back-verified native issues**: 54 epics, 368 stories and 24 proposed technical tasks, with 36 task dependencies. The planning import is complete. This does not declare an accepted release or completed development.

## Preserved planning

| Layer | Saved result |
| --- | --- |
| Vision | VISION-IMPRANA-01: impact management and nonprofit technology adoption in one governed platform |
| Strategy | STR-01 through STR-05, with explicit priorities and proposed outcome measures |
| Roadmap | Foundation → R1 Pilot → R2 Scale → R3 Ecosystem; Later remains outside committed scope |
| Release goals | Five RG-* milestones, scope, exit conditions and owner decisions |
| Epics | 54 native parent issues, mapped to strategy objectives |
| Stories | 368 native story children, preserving source IDs, personas, benefits, requirements and original acceptance/rejection criteria |
| Technical tasks | 24 proposed native child tasks beneath US-DX-01a, US-DX-03, FR-AI-016a and US-CM-05; six per story |
| Dependencies | All 36 proposed task blocking relationships; graph is acyclic |
| History | US-DX-01 and FR-AI-016 remain retained Split parents in the history document, not duplicate active scope |

The [backlog catalogue](08-BACKLOG-CATALOGUE.md) links all 446 source IDs to their native issues. The [import plan](linear/import-plan.json) contains complete descriptions and source mappings. The [local manifest verification](linear/manifest-verification.json) checks preservation and structure; the [native issue read-back report](linear/issue-readback-verification.json) checks the actual saved issues.

## Verified external result

The full native project listing contains exactly 446 unique issues. Every issue was fetched with its complete description because list responses truncate text. The read-back verifier passes with zero failures: all canonical IDs, parents, release milestones, strategy text, labels, statuses and estimates match. All **368 original Gherkin blocks match UTF-8 bytes exactly**; all **96 proposed task criteria** and **36 dependency edges** match. Four source stories remain In Review and ten existing estimates are preserved; other stories and tasks remain Backlog. No new estimates, assignments, due dates or sprint cycles were added.

[checkpoint.json](linear/checkpoint.json) contains real project, document, milestone, label, epic, story and task IDs. [verification.json](linear/verification.json) records the final project/document/milestone result; [issue-readback-verification.json](linear/issue-readback-verification.json) records per-issue checks and source hashes. The two parallel story shards retain creation receipts. Verification establishes planning-object preservation; it is not a product acceptance or execution of the story scenarios.

Linear's Markdown parser initially turned the literal technical names ai.usage.read and delivery.py in three proposed task descriptions into website links. Escaped input removed those unintended links; full native read-back now preserves the original literal wording. The original task source and manifest hashes remain unchanged.

## Resolved quota history

The earlier first-epic attempt on 10 October 2026 was rejected with HTTP 400 and “You've exceeded the free issue limit for this workspace.” Request ID: `a48491a96f6dbb10`. That rejected attempt created no issue. On Nakul's requested recheck, creation succeeded in the same project, starting with [APL-278](https://linear.app/aplyd-sandbox/issue/APL-278/epic-ai-capabilities-ai-capabilities); all remaining objects were then saved and verified.

This confirms issue creation is allowed. It does not establish that a subscription or billing setting changed. No other product's issues were changed or archived to make room. This integration performed no upgrade, billing change, paid CI run, provider call or cloud resource creation.

## Continue one step at a time

1. Read the product documents, source manifest, checkpoint and final reports. Run `python3 scripts/linear/build_imprana_import.py --check` to confirm the preserved source.
2. Continue in the existing project and APL team. **Do not rerun creation:** all 446 objects and dependencies already exist. Match canonical IDs and native UUIDs, and reconcile any human changes before future updates. After an uncertain response, read before retrying.
3. Use Linear for day-to-day planning status and Git for baselines, decisions and evidence. Keep both Split parents as history. Preserve the four In Review stories until Nakul records acceptance; merged code is not product acceptance.
4. Review the next proposed story with Nakul one decision at a time. Product scope, pilot targets, new estimates, delivery dates, AI destination, permitted data and paid services remain open decisions. The four proposed Sprint 2 stories and their tasks are not committed or Ready solely because they were imported.
5. Before building, satisfy the Definition of Ready and the existing engineering/security gates. Official arithmetic, tenant isolation, current authority, natural-person independence and immutable approved history remain binding.

## Git and engineering handover

This planning work is preserved on branch `docs/imprana-linear-planning-2026-10-10`, based on source commit `8a1e405f0086033dfb25ad834689a08bfe9f1eea`. The original integration checkout and historical drafts remain intact. Start at [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md) and the engineering evidence. Resolve runtime versions and migration numbers from VERSION.json and the actual frozen migration ledger before engineering; older handover header counts are retained history.

Do not push directly to main. A pull request for this change runs CI because the branch adds Python planning/verification tools; obtain the repository's required financial permission before opening it. Merge and deployment require the current gates and owner confirmation. The product source baseline is not a fresh verification of live staging. No runtime feature, version bump, migration or acceptance promotion is part of this planning change.
