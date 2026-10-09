<!-- main deploys itself to staging. Open a DRAFT pull request from a branch; never push to main. -->

## Story
<!-- Story ID(s) from docs/backlog (e.g. FR-IND-004) and the GitHub issue. Title the PR "[ID] Short title". -->

## What and why
<!-- One paragraph, plain language. Link the release note or issue. -->

## Definition of Done (docs/agile/WORKING-AGREEMENT.md)
- [ ] Every acceptance and rejection scenario of the story passes as an automated test (or a named manual check the product owner accepted)
- [ ] Reviewed and approved by a person other than the author
- [ ] Product owner accepted at sprint review

## Kind of change
- [ ] Documentation only (`docs/**` or `**.md`; starts no CI)
- [ ] Code (affected checks listed below)
- [ ] Migration (next number is 0041; applied migrations are never edited)
- [ ] Contract or capability change (regenerated contracts and onboarding profile)
- [ ] Deployment (`deploy/**`)

## Rules check (AGENTS.md)
- [ ] No secrets, real personal data, `.local/` or generated passwords committed; synthetic data only
- [ ] Independence and deny-by-default rules not relaxed; no test weakened or skipped to get green
- [ ] Shared documents updated together (release note, IMPLEMENTATION, QUALIFICATION, NEXT-DELIVERY, CHANGELOG), or this is a parallel slice and the integrator will do it
- [ ] Requirement status moved only with named passing tests

## Checks run (exact commands and results; say what was NOT run)

## Risks and open owner decisions

## Merge
Not to be merged without all four CI jobs green and the owner's confirmation.
