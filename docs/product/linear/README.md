# Imprana Commons Linear integration

The [Imprana Commons project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) in the connected Aplyd Sandbox workspace contains the product documents, five release milestones and product-specific labels. All 1,553 native project issues are saved and read-back verified: 54 epics, 368 stories and 1,131 proposed technical tasks, with 779 prerequisites. Every story includes its additive refinement and scenario-test proposal. The complete import plan, identities and verification receipts are preserved in Git; see [current status and continuation](../07-LINEAR-IMPORT-STATUS.md). It uses the existing APL team. Other products in that workspace are outside this integration.

## Native structure

| Product layer | Linear object |
| --- | --- |
| Vision and strategy | Project documents with stable vision and strategy objective IDs |
| Roadmap | Project document and ordered release milestones |
| Release goals | Foundation, R1 Pilot, R2 Scale, R3 Ecosystem and Later milestones, with measurable exit conditions |
| Epics | Parent issues labelled Imprana Epic; an epic may span releases |
| User stories | Sub-issues of their epic, labelled Imprana Story and assigned their release milestone |
| Acceptance and rejection criteria | Original Gherkin in the story description |
| Technical tasks | Sub-issues of the relevant story, labelled Imprana Technical task |

Release membership belongs to the story. Epic parents spanning releases have no misleading single release assignment. The source story ID stays in the issue title and description; Linear's APL identifier is an additional tracking identifier.

## Preserve meaning

- Import all 368 active stories. Keep the two Split parents in the source manifest and history rather than create duplicate active scope.
- Keep every persona, story, original requirement, merged-duplicate reference and acceptance/rejection criterion.
- Map source Backlog to Backlog and the four source In review stories to In Review. Do not infer Done from merged code.
- Preserve the ten existing estimates; leave all others unset. Do not create committed cycles, due dates, assignments or new numeric targets from a planning proposal.
- Mark unrefined scope with Imprana Needs refinement. Proposed technical tasks remain Backlog until their story is Ready.

## Import and recovery

`scripts/linear/build_imprana_import.py` creates [import-plan.json](import-plan.json) from the unchanged source CSV and [technical-tasks.json](../technical-tasks.json). It performs no external writes. The plan records the source commit and checksum, stable canonical IDs and exact descriptions. [checkpoint.json](checkpoint.json) records real Linear IDs and URLs as each object is saved. [verification.json](verification.json) records the final project/document/milestone result. [issue-readback-verification.json](issue-readback-verification.json) records all 446 issue checks and exact original Gherkin hashes. The two story-import shards preserve parallel creation receipts.

The original 446-issue import and its 24-task/36-edge reports remain unchanged baseline history. The [complete expansion report](../refinement/readback-verification.json) covers all 1,553 current native project issues, 1,107 new tasks, 368 exact additive sections and 743 new prerequisite edges. Read both the original checkpoint and all `refinement/task-import-*.json` / `story-import-*.json` receipts before a continuation; root/helper mirrors must contain identical objects. Three erroneous duplicates are now linked to their original tasks outside active project scope; [cleanup evidence](../refinement/duplicate-cleanup-248-367.json) preserves that history. Only the optional new overview document awaits separate approval.

Before a continuation, read the checkpoint and list the project's existing objects. Match canonical IDs and content markers before creating anything. After an uncertain response, fetch the known identifier or search the exact canonical title and marker; do not blindly repeat a create call. Do not overwrite a person's changed status, estimate or description during a later sync without reconciling the difference.

Read-back verification compares the project, milestones, parent relationships, release membership, story IDs, status and original criteria with the plan. All 368 story Gherkin payloads match UTF-8 bytes exactly; all 96 proposed task criteria and 36 dependency edges match. No active story is missing or duplicated. `scripts/linear/verify_imprana_readback.py` checks a full native snapshot without external writes; fetch full `get_issue` descriptions because list responses truncate them. Keep explicit null fields from the list projection. The report records hashes and identities without description content or personal names. Its scope is planning-object verification, not an executed product test suite.

## GitHub and ongoing use

The project links to the repository and the exact source backlog. Future branches and PR descriptions should include both the Linear identifier and original story ID, and link to the relevant issue. Product acceptance remains explicit after the demo; use a PR link rather than a closing keyword where an automation would otherwise mark the story Done before acceptance.

The documents, milestones, issues and dependency relationships are saved through connected Linear tools. Linear is the working board; the source CSV remains the preserved import baseline. A native GitHub OAuth app, webhook, automatic bidirectional sync, paid agent loop or sprint cycle has not been enabled. Configure those separately if needed, with the intended repository and permissions established first.

## Open owner decisions

The product documents retain proposed pilot users, outcome targets, commercial responsibility, AI destination, residual security decisions and editorial confirmation as open choices. Ask Nakul one decision at a time. Imported scope and written scenarios are not an accepted release or an executed test suite.
