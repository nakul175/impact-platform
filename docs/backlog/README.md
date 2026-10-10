# Imprana Commons backlog

Owner: Nakul Jain · Generated 9 October 2026 · Update trigger: any change to scope, release or acceptance of a story.

This folder is the single product backlog for Imprana Commons: Impact Platform's 307 requirements and the Imprana Commons BRD's 83 stories, deduplicated into **366 user stories** (24 BRD stories were merged into existing requirements). Every story has a persona, a "so that", Gherkin acceptance criteria and at least one rejection scenario.

Since Sprint 1 planning the file holds 370 rows: two stories were split during refinement (US-DX-01 into 01a/01b, FR-AI-016 into 016a/016b); the parents stay with status `Split`. Sprint plans are in [`docs/sprints/`](../sprints/).

| File | What it is |
| --- | --- |
| `backlog.csv` | All 366 stories: ID, release, epic, priority, persona, user story, Gherkin acceptance and rejection criteria, rejection summary, build status today, source, merged duplicates, the original requirement text, and empty Story points / Sprint / Status columns |
| `features/*.feature` | The same criteria as Gherkin, one file per epic. Each story is a `Rule:`; every scenario is tagged with its ID, release and priority, e.g. `@FR-IND-001 @R1-Pilot @Must`. They have no step definitions yet, so they are a specification, not a test suite |
| `create_github_issues.py` | Creates one GitHub issue per story with labels (release, epic, priority, type) and a milestone per release. Skips stories that already have an issue, so it is safe to re-run |

## Releases

| Release | Stories | Already partly or fully built |
| --- | --- | --- |
| Foundation | 6 | 0 |
| R1 Pilot | 170 | 118 |
| R2 Scale | 139 | 18 |
| R3 Ecosystem | 45 | 3 |
| Later | 6 | 0 |

"Built today" comes from the requirement ledger (`docs/COMPLETION-LEDGER.json`, assessed at build 0.33). No story is accepted; a story is done only under the Definition of Done in [`docs/agile/WORKING-AGREEMENT.md`](../agile/WORKING-AGREEMENT.md).

## Create the GitHub issues

```bash
gh auth login
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --dry-run
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform --release "Foundation"
python3 docs/backlog/create_github_issues.py --repo nakul175/impact-platform
```

Once the issues exist, GitHub is the place to change status, points and sprint; this CSV is the import snapshot.
