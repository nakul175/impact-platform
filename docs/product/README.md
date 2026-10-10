# Imprana Commons product planning

This is the planning entry point for Imprana Commons: one platform for impact management and nonprofit AI or technology adoption. It connects product direction to release outcomes, epics, user stories, acceptance criteria and technical tasks. Nakul requested this structure and Linear integration on 10 October 2026. That request approves setting up the structure; proposed product choices, pilot targets, spending and release acceptance remain explicit decisions.

## Read in order

| Layer | Document or working record | Purpose |
| --- | --- | --- |
| Vision | [Product vision](01-VISION.md) | Who the product serves and the outcome it seeks |
| Strategy | [Product strategy](02-STRATEGY.md) | Choices, priorities, tradeoffs and success measures |
| Roadmap | [Outcome roadmap](03-ROADMAP.md) | Dependency order across Foundation, Pilot, Scale and Ecosystem |
| Release goals | [Release goals](04-RELEASE-GOALS.md) | Scope, exit conditions and open decisions per release |
| Epics | Linear parent issues; [import plan](linear/import-plan.json) | Outcome groups mapped to strategy objectives |
| User stories | Linear story sub-issues; [source backlog](../backlog/backlog.csv) | Personas, benefits and stable requirement IDs |
| Acceptance criteria | Each story description; [Gherkin files](../backlog/features/) | Positive and rejection behaviour, retained from the source |
| Technical tasks | [Story and task standard](05-STORY-AND-TASK-STANDARD.md), [next-sprint refinement](06-NEXT-SPRINT-REFINEMENT.md), [task manifest](technical-tasks.json) | Proposed implementation and evidence work beneath the next sprint's stories |

The [Linear project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) contains 11 product documents, five release milestones and the verified hierarchy of 54 epics, 368 stories and 24 proposed technical tasks, with 36 task dependencies. [Import status and continuation](07-LINEAR-IMPORT-STATUS.md) records the completed import and evidence; [integration and recovery](linear/README.md) explains the mapping. Use Linear for day-to-day planning and Git for the preserved source and decisions.

## Source and status

The initial source is repository commit `8a1e405f0086033dfb25ad834689a08bfe9f1eea`. Its CSV contains 370 rows: 368 active stories and two retained Split parents, across 54 epic/area groups. The active release counts are Foundation 6, R1 Pilot 172, R2 Scale 139, R3 Ecosystem 45 and Later 6. These are scope counts, not a completion percentage.

Four Sprint 1 stories remain In Review pending recorded product-owner acceptance. Ten active stories have source estimates; all other estimates remain unset. Sprint 2 and its technical tasks are proposed, without committed dates or assignments. A story enters a sprint only after the Definition of Ready is evidenced. Longer-term technical work is refined before its sprint rather than represented as fully designed now.

Linear owns day-to-day planning status. Git retains stable source IDs, criteria, planning baselines, import receipts and product decisions. Preserve historical specifications and release evidence; the new roadmap does not accept old requirements, rewrite applied migrations or discard the governed impact core.

## Traceability and acceptance

Each story links to its epic, release goal and applicable strategy objectives. Each technical task links to one original story ID and states a verifiable output. Evidence records the environment and exact candidate commit. Merge, deployment, test success and product-owner acceptance remain separate facts; linking a pull request must not automatically imply product acceptance.

Official arithmetic remains deterministic. AI output is a proposal. Current tenant authority, natural-person independence and immutable approved history apply to every layer.
