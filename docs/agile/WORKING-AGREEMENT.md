# Imprana Commons working agreement

Owner: Nakul Jain · Adopted 9 October 2026 (draft until the team confirms it at the first sprint planning) · Update trigger: any retrospective that changes how we work.

We work fully agile. [Product planning](../product/README.md) connects vision, strategy, roadmap and release goals to the backlog. The [Imprana Commons Linear project](https://linear.app/aplyd-sandbox/project/imprana-commons-cf62fc3d7e9d) is the intended working board after issue import; [`docs/backlog/`](../backlog/README.md) retains the source IDs and acceptance baseline. The current workspace issue limit blocks issue creation, so use the repository backlog and refinement records until [the import is verified](../product/07-LINEAR-IMPORT-STATUS.md). Existing business and engineering specifications retain their rules and historical scope. Each story is detailed just before it is built, not months ahead.

## Cadence

| Event | When | Output |
| --- | --- | --- |
| Sprint | 2 weeks | Working, reviewed increments on `main` |
| Backlog refinement | Mid-sprint, 1 hour | Next sprint's stories meet the Definition of Ready |
| Sprint planning | Day 1 | Sprint goal and committed stories on the board |
| Review / demo | Last day | Demo to the product owner and, when useful, an advisor or pilot organisation |
| Retrospective | Last day | One or two changes to this agreement or our tooling |

## Definition of Ready (a story may enter a sprint when)

- [ ] It has a persona, an "I want" and a "so that" the product owner agrees with.
- [ ] Its Gherkin scenarios cover the expected behaviour and at least one `Scenario: Reject ...`, reviewed with the engineer who will build it.
- [ ] Its story card notes say what changes in the data layer (tables, migration number, row-level security), the API and the screens, or say "none".
- [ ] Story-specific non-functional needs are written down (e.g. works offline, response time); platform-wide NFR stories apply to every story anyway.
- [ ] It is small enough to finish in one sprint (otherwise split it), estimated in points, and its dependencies are done or in the same sprint.

## Definition of Done (a story is done when)

- [ ] Every scenario, including every rejection scenario, passes as an automated test in CI, or the product owner has accepted a named manual check for it.
- [ ] A person other than the author has reviewed and approved the pull request; AI-written code is reviewed like any other.
- [ ] `make lint`, `make unit` and the relevant qualification jobs are green; no test was weakened, skipped or deleted.
- [ ] The rules in [`AGENTS.md`](../../AGENTS.md) hold (deny by default, independence, row-level security, frozen migrations, no secrets or personal data).
- [ ] User-facing text is in plain language; new screens pass the accessibility check.
- [ ] The issue records what was built and the product owner has accepted it at the sprint review.

## Story card (filled in at refinement, in the Linear issue)

```
Story:            As a <persona>, I want <capability>, so that <benefit>.
Traceability:     <original story ID, strategy objective, release goal, epic, Linear ID>
Why / objective:  <business objective or BRD objective it serves>
Functional notes: screens and flows, business rules, permissions by role, edge cases
Data layer:       tables/columns, migration number, RLS policy, events, API endpoints
Non-functional:   story-specific needs + platform NFR stories that apply
Acceptance:       Gherkin scenarios (from the backlog, refined)
Rejection:        Gherkin "Scenario: Reject ..." blocks + one-line "Reject if ..."
Dependencies:     other story IDs, connectors, partners
Estimate:         points
Technical tasks:  <child tasks, dependencies, verifiable outputs and evidence>
```

## Branches and reviews

- `main` deploys itself to staging. Never push to it; open a pull request from a branch.
- One story per pull request where possible; the PR title starts with the story ID, e.g. `[FR-IND-004] Target amendments`.
- Merge only with green CI, one human approval and the product owner's go-ahead.
