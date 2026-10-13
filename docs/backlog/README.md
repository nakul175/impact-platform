# Imprana Commons backlog

Owner: Nakul Jain · Generated 9 October 2026 · Update trigger: any change to scope, release or acceptance of a story.

This folder retains the source backlog for Imprana Commons: Impact Platform's 307 requirements and the Imprana Commons BRD's 83 stories, initially deduplicated into 366 user stories (24 BRD stories were merged into existing requirements). Refinement produced **368 active user stories and two retained Split parents**. Every story has a persona, a "so that", Gherkin acceptance criteria and at least one rejection scenario. The [product planning structure](../product/README.md) connects these stories to vision, strategy, roadmap, release goals and proposed technical tasks.

Since Sprint 1 planning the file holds 370 rows: two stories were split during refinement (US-DX-01 into 01a/01b, FR-AI-016 into 016a/016b); the parents stay with status `Split`. Sprint plans are in [`docs/sprints/`](../sprints/).

| File | What it is |
| --- | --- |
| `backlog.csv` | 370 source records: 368 active stories plus two Split parents. Stable IDs, persona, story, original requirement, Gherkin criteria, rejection summary, source references and retained planning fields; ten existing estimates and four In review statuses are preserved |
| `features/*.feature` | The same criteria as Gherkin, one file per epic. Each story is a `Rule:`; every scenario is tagged with its ID, release and priority, e.g. `@FR-IND-001 @R1-Pilot @Must`. They have no step definitions yet, so they are a specification, not a test suite |
| `create_github_issues.py` | Creates one GitHub issue per story with labels (release, epic, priority, type) and a milestone per release. Skips stories that already have an issue, so it is safe to re-run |

## Releases

| Release | Active stories |
| --- | --- |
| Foundation | 6 |
| R1 Pilot | 172 |
| R2 Scale | 139 |
| R3 Ecosystem | 45 |
| Later | 6 |

"Built today" comes from the requirement ledger (`docs/COMPLETION-LEDGER.json`, assessed at build 0.33). No story is accepted; a story is done only under the Definition of Done in [`docs/agile/WORKING-AGREEMENT.md`](../agile/WORKING-AGREEMENT.md).

## Linear and the retained GitHub importer

The [Linear project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) is the day-to-day planning board. Its 54 epics, 368 active stories and 24 proposed technical tasks are read-back verified, with original criteria and 36 task dependencies. The [import manifest, checkpoint and verification](../product/linear/README.md) preserve all source records and native IDs. This source CSV remains the original import baseline; reconcile future changes with Linear rather than blindly re-importing it. The GitHub importer below remains an optional retained tool; do not run it as a second active backlog for this integration.

```bash
gh auth login
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --dry-run
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --release "Foundation"
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform
```

After a verified Linear import, Linear owns current status, points and sprint planning; this CSV remains the source snapshot. GitHub owns code, PRs and evidence. A merged PR does not automatically mark a story accepted.
