# Imprana Commons Linear import status and handover

Nakul authorised creating the product planning hierarchy and integrating it into Linear on 10 October 2026. The [Imprana Commons project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) exists in Aplyd Sandbox, team APL. Product documents and five release milestones are saved there. Native issue import remains blocked; this is a planning handover, not a completed issue import or an accepted release.

## Completed planning

| Layer | Preserved result |
| --- | --- |
| Vision | VISION-IMPRANA-01: impact management and nonprofit technology adoption in one governed platform |
| Strategy | STR-01 through STR-05, with explicit priorities and proposed outcome measures |
| Roadmap | Foundation → R1 Pilot → R2 Scale → R3 Ecosystem; Later remains outside committed scope |
| Release goals | Five RG-* goals, scope, exit conditions and owner decisions |
| Epics | 54 planned parent issues, mapped to strategy objectives |
| Stories | 368 active stories, preserving source IDs, personas, benefits, requirements and acceptance/rejection criteria |
| Technical tasks | 24 proposed child tasks beneath US-DX-01a, US-DX-03, FR-AI-016a and US-CM-05; six per story |
| History | US-DX-01 and FR-AI-016 stay as retained Split parents, not duplicate active scope |

The [backlog catalogue](08-BACKLOG-CATALOGUE.md) is a readable planning index. The [import plan](linear/import-plan.json) contains complete issue descriptions, parent references, milestones and dependency IDs. The [local verification report](linear/manifest-verification.json) records source-preservation and structural checks.

## Actual external result

On 10 October 2026, the first epic creation was rejected with `invalid_request`, HTTP 400: “You've exceeded the free issue limit for this workspace.” No epic, story or task issue was created. The failed request ID is `a48491a96f6dbb10`. This is a workspace quota blocker; changing the story content will not resolve it.

[checkpoint.json](linear/checkpoint.json) contains real project, document, milestone and label IDs. [verification.json](linear/verification.json) distinguishes read-back-verified external objects from the pending 446-issue import. No other product's issues were changed or archived to make room. No upgrade, billing change, paid CI run, provider call or cloud resource creation was performed.

## Continue one step at a time

1. Ask Nakul to identify an existing paid Linear workspace, or to confirm that he has upgraded the current workspace. Obtain financial permission before any paid action; the structure request does not approve new spending.
2. Re-read the source manifest, checkpoint and this status. Run `python3 scripts/linear/build_imprana_import.py --check` and reconcile any human edits. If a different workspace is chosen, discover its team and status IDs and create a separate checkpoint; do not reuse APL object IDs there.
3. In the selected workspace, list current project issues and reconcile canonical source IDs before creating anything. An uncertain response requires a read or search before retrying.
4. Import 54 epic parents, then 368 story children, then 24 task children. Resolve each parent to its saved Linear UUID. Set story and task milestones from RG-* mappings. Create dependency relationships only after both task IDs exist.
5. Preserve the four In Review stories, ten existing estimates and original Gherkin. All other stories and proposed tasks remain Backlog. Do not invent Done statuses, assignees, due dates or committed sprint cycles.
6. Read every created object back. Verify unique canonical IDs, all parent and milestone mappings, original criteria, statuses, estimates and task dependencies. Save actual results and gaps in verification.json before reporting completion.
7. Ask Nakul for the next product decision or review one candidate story at a time. Product scope, pilot targets, estimates for unrefined stories, paid services and product acceptance remain separate decisions.

## Git and engineering handover

This planning change is on branch `docs/imprana-linear-planning-2026-10-10`, based on source commit `8a1e405f0086033dfb25ad834689a08bfe9f1eea`. The original integration checkout and historical drafts remain intact. Git preserves the documents, source hashes, complete import manifest, technical tasks and external checkpoint for Claude or another engineer.

Do not push directly to main. A pull request for this change would run CI because it adds a Python planner; obtain the repository's required financial permission before opening it. Merge and deployment require the current engineering gates and owner confirmation. The worktree's product source baseline is not a new verification of live staging.

Start engineering with [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md) and the current handover evidence. Existing tenant isolation, natural-person independence, official arithmetic, current authority and immutable approved history remain binding. No feature implementation, runtime version bump, migration or acceptance promotion is part of this planning change.
