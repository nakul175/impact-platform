# Imprana Commons Linear import status and handover

## Complete native refinement — 10 October 2026

Nakul directly approved the remaining task/story expansion in the existing [Imprana Commons project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d). All **1,553 unique native project issues** are saved and fully read-back verified: **54 epics, 368 stories and 1,131 proposed technical tasks**, with **779 task prerequisite relationships**. All 368 stories have additive scope, inspected reuse, decisions, dependencies, tasks and test plans for all **1,328 original scenarios**. [Full native verification](refinement/readback-verification.json) passes with zero failures. Eleven existing product documents and five release milestones remain in the same project.

This completes planning integration. The scenario plans are unrun; Ready, sprint commitments, implementation evidence, release qualification and owner acceptance remain separate. Twelve executed guard checks validate the planning/import tools. Four source stories remain In Review and ten existing estimates are preserved; no new estimates, assignments, due dates or cycles were added.

Only the optional additional overview document is awaiting its separate upload approval. Automatic approval review rejected creating that new document because the human approval covered tasks and story updates. The [complete overview](10-COMPLETE-BACKLOG-REFINEMENT.md) is preserved in Git and all approved native task/story changes are complete; [document-import.json](refinement/document-import.json) records the precise pending scope.

## Preserved planning

| Layer | Saved result |
| --- | --- |
| Vision | VISION-IMPRANA-01: impact management and nonprofit technology adoption in one governed platform |
| Strategy | STR-01 through STR-05, priorities and proposed outcome measures |
| Roadmap | Foundation → R1 Pilot → R2 Scale → R3 Ecosystem; Later remains outside committed scope |
| Release goals | Five RG-* milestones, scope, exit conditions and owner decisions |
| Epics | 54 native parent issues mapped to strategy objectives |
| Stories and criteria | 368 native story children; source IDs, personas, benefits, requirements and original Gherkin preserved |
| Technical tasks | 1,131 proposed native children: 24 original cores plus 1,107 new tasks |
| Scenario plans | 1,328 proposed entries in the 368 additive story sections; no product-test execution claimed |
| Prerequisites | 779 exact native task relationships: 36 original plus 743 new; graph acyclic |
| History | Two Split parents retained in the history document; no duplicate active scope |

## Verified evidence and history

The final project listing was fully paginated. Every one of its 1,553 issues has a full native GET description and relation read-back merged with explicit selected metadata; truncated list bodies were not used as proof. The verifier preserves the original 446-object baseline, every original Gherkin UTF-8 block, all 96 original task criteria, the original 36 edges and protected workflow fields. It also validates every new task body, native parent, milestone, identity and prerequisite, and every once-only additive story section with its actual task links.

[Full proposal](refinement/backlog-refinement.json), [native task plan](refinement/native-task-plan.json), [refreshed payloads](refinement/native-payloads.json), [local validation](refinement/local-validation.json), [full native read-back](refinement/readback-verification.json) and [project/document/milestone verification](refinement/native-metadata-verification.json) are separate records. The initial [checkpoint](linear/checkpoint.json), [446-issue verification](linear/issue-readback-verification.json), [initial document/project verification](linear/verification.json), [493-issue partial report](refinement/partial-readback-verification.json) and [pre-import payload](refinement/native-payloads-pre-import.json) remain unchanged historical evidence. Initial counts in those records are historical, not the current expanded count.

Three erroneous duplicate task creations were discovered during interruption recovery. Each is marked Duplicate of its unchanged original, detached from the active project/parent/prerequisite graph, and retained without deletion. [Duplicate-cleanup evidence](refinement/duplicate-cleanup-248-367.json) records the original milestones, automatic Linear status/milestone changes and successful original-object checks. Native errors and uncertainty history remain in the relevant slice receipts.

## Resolved quota history

The earlier first-epic attempt on 10 October 2026 was rejected with HTTP 400 and “You've exceeded the free issue limit for this workspace.” Request ID: `a48491a96f6dbb10`. That rejected attempt created no issue. On Nakul's requested recheck, creation succeeded in the same project, starting with [APL-278](https://linear.app/aplyd-sandbox/issue/APL-278/epic-ai-capabilities-ai-capabilities); all remaining objects were then saved and verified.

This confirms issue creation is allowed. It does not establish that a subscription or billing setting changed. No other product's issues were changed or archived to make room. This integration performed no upgrade, billing change, paid CI run, provider call or cloud resource creation.

## Continue one step at a time

1. Start with [README](README.md), the [complete refinement](10-COMPLETE-BACKLOG-REFINEMENT.md) and the full read-back report. Review the proposed slice against current code and capacity before choosing it.
2. Reconcile the original checkpoint and all original/root/helper task and story receipts before any sync. The three original task slices cover 360 + 382 + 365 new tasks; the original story slices cover 124 + 124 + 120 stories. Mirror receipt objects are identical. Do not count mirrors as additional issues or recreate any saved canonical ID.
3. Resolve the next story's owner/engineer decisions and Definition of Ready. Pilot targets, estimates, dates, external AI destination, permitted data and paid services remain explicit choices. A saved proposal is not Ready or committed.
4. After an interrupted or uncertain native write, reload durable receipts, fully paginate exact canonical titles and fetch complete content before retrying. Source criteria and human status/estimate/assignment changes are never reset by a sync.
5. Preserve deterministic arithmetic, current authority, tenant isolation, natural-person independence and immutable approved history. Qualification, merge, deployment and owner acceptance require their existing separate gates.

## Git and engineering handover

The planning branch is `docs/imprana-linear-planning-2026-10-10`, based on product source commit `8a1e405f0086033dfb25ad834689a08bfe9f1eea`. Source CSV, initial import plan, original task manifest, historical drafts, applied migrations and runtime code are unchanged. Complete native receipts and evidence are preserved on this branch. Start at [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md) and [HANDOVER](../HANDOVER.md); resolve runtime versions and migration numbers from VERSION.json and the actual frozen migration ledger before engineering. Older header counts retain their original observation dates.

No runtime feature, version bump, migration, acceptance promotion, main merge, deployment or paid CI/provider action is part of this planning change. Do not push directly to main. Opening a PR for the branch's Python planning/verification tools runs CI and requires the repository's financial permission; merging and deployment also retain their qualification and owner gates.
