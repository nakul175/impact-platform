# Imprana Commons outcome roadmap

Owner: Nakul Jain · Prepared 10 October 2026 · Status: proposed product planning baseline; product scope approval pending.

## Basis and sequencing

This roadmap connects the [vision](01-VISION.md) and [strategy objectives](02-STRATEGY.md) to the five release buckets already present in [backlog.csv](../backlog/backlog.csv). It changes no story's release or priority. The current snapshot contains 370 rows: 368 active stories and two retained split parents, across 54 epic/areas. Counts describe scope inventory, not effort, progress or accepted work.

| Phase / goal ID | Active stories | Proposed outcome and scope | Strategy | Measurable exit evidence | Dependencies |
| --- | ---: | --- | --- | --- | --- |
| Foundation / RG-FOUNDATION | 6 | Establish lawful ownership/licensing, product transition, one traceable backlog and a secure engineering process | STR-01 | Each of the six stories has its required review/decision evidence; tooling reproduces the active inventory; independent security review has an accountable scope and owner | Licence and transition decisions, repository/tool permissions, reviewer and approved spending where needed |
| R1 Pilot / RG-R1 | 172 | Prove diagnose → map → discover → assess → value case → deploy → adopt → improve, using trustworthy MEL reporting and governed AI | STR-01, STR-02, STR-03, STR-04, STR-05 | Selected pilot journeys pass agreed acceptance and rejection checks; release-assigned scope is accepted or explicitly revised by the owner; outcome comparison cites a recorded baseline; security and operations gates support the authorised environment | Foundation controls; structured diagnosis and baseline; reviewed options; AI policy/jobs before AI use; approved providers/data boundary; named people and operating readiness |
| R2 Scale / RG-R2 | 139 | Repeat delivery across organisations and sponsored cohorts, with grantee-controlled sharing, partner operations and wider collection/integration capabilities | STR-01, STR-03, STR-04, STR-05 | Representative cohort, multi-tenant, entitlement, disclosure, integration and recovery cases pass; operating workload and support limits are measured against owner-approved targets | R1 lessons and accepted core; sponsor/commercial terms; partner accountability; qualified integrations; capacity and support model |
| R3 Ecosystem / RG-R3 | 45 | Extend partner outcome accountability and advanced evaluation, analysis, finance and operations where evidence justifies them | STR-01, STR-03, STR-04, STR-05 | Each included capability has an approved value case, accountable owner and passing acceptance/rejection evidence; partner outcome access stays within disclosure authority | Accepted earlier controls; reliable comparable outcomes; financial and ecosystem responsibility decisions; specific data permissions |
| Later / RG-LATER | 6 | Keep optional research and advanced capabilities available for an explicit future investment decision | STR-01, STR-03, STR-04 | A story enters delivery only with a recorded problem, value case, scope decision and readiness evidence; otherwise it remains deferred | Evidence of unmet need and approved capacity, cost and controls |

Detailed evidence and decisions for every goal are in [04-RELEASE-GOALS](04-RELEASE-GOALS.md). No phase has an approved date, budget, ROI or numeric adoption target. Exit criteria above are proposed; owner approval of scope and thresholds remains required. The existing engineering Release 1 “Usable core” and its historical R1/R2/R3 requirement tags are separate from these Imprana backlog buckets; a build number does not establish acceptance of either.

## Proposed order inside R1

1. Finish the Foundation controls and record product acceptance of the Sprint 1 work: AI policy, threat review, organisation-weighted ranking and commercial disclosure. Sprint 1 code merged in [PR #94](https://github.com/nakul175/impact-platform/pull/94); product-owner acceptance remains unrecorded. The committed [Sprint 1 review](../sprints/SPRINT-01-REVIEW.md) contains older pre-merge wording; future changes retain the current [AGENTS](../../AGENTS.md) review, CI and owner gates.
2. Refine structured diagnosis, locked baseline and readiness. Verify dependencies for mapping, trials and the value case. Refine AI budget/job controls and usage before adding conversational intake or other generated work.
3. Connect trial evidence to a reviewed value case, deployment plan, training and observed adoption. Validate the linked MEL collection, independent review, deterministic calculation, locked period and frozen-report journey.
4. Review measured outcomes and delivery/support effort. Resolve the intended environment's identity, privacy, recovery, security, accessibility and operations gates before any approved real-data pilot.

This order is a proposal for refinement, not a sprint commitment. It neither accepts an existing partial implementation nor removes other R1 stories. Any smaller pilot slice must be approved with named inclusions, exclusions and shared controls before it is described as the R1 release.

## Change rules

Refresh the roadmap when evidence or an owner decision changes a release outcome. Record the reason, affected stories, dependencies and acceptance consequences in the delivery system; synchronise the repository's import snapshot when the integration workflow requires it. Keep split parents for traceability and schedule only their active children. Never silently move a Must story or label a release complete because its implementation tasks are closed. Tenant isolation, independence by natural person and deterministic official arithmetic constrain every phase.


<!-- imprana:bundle-v4.2:documentation:20261011 -->

Application source 8a1e405f0086033dfb25ad834689a08bfe9f1eea; planning source eb194fdbb6fc8247db8429fc23120aa0fe659ed8; build 0.39.0, domain API 1.28.0, platform API 1.11.0, schema 43. These are source pins, not a fresh deployed-runtime assertion.

This edition applies the attached Product Management Agent Bundle v4.2 / standard 3.0-generic to Imprana Commons. It adds source-bound product reasoning and executable evidence plans. Original requirements, Gherkin, estimates, priorities, workflow states, release allocations, historical decisions and human edits remain authoritative. Recommendations below are not user research, a test execution, Ready/Done, an approved sprint, financial authority or production acceptance. The current request authorises documentation refinement and Linear publication.

Use the eight-tier chain: vision → strategy → roadmap → release goal → epic → user story → acceptance criterion and technical task. Criteria and tasks are sibling children of their story. Existing native epics can span releases; retain each story's real release and primary epic. A checker-only release anchor is explicitly a proposed adapter convention, never a native reparenting or scope change.

## Refined outcome roadmap and scope rules — 11 October 2026

| Release bucket | Active source stories | Outcome gate before the next investment | Proposed learning evidence |
| --- | ---: | --- | --- |
| Foundation | 6 | Traceable secure engineering, licence/rebrand/archive/backlog decisions and independent assurance; current applicable findings resolved/dispositioned through the source policy | Inspect exact release candidate and a changed requirement through code/test/migration/review/approval links |
| R1 Pilot | 172 | A governed problem-to-follow-up journey and usable core MEL; included stories meet their original criteria and actual owner acceptance | Synthetic connected journey first; authorised representative pilot only with scoped purpose/data/baseline/operating owner |
| R2 Scale | 139 | Multi-organisation/cohort/grantee/partner behaviour without lost isolation, consent, entitlement, recovery or exit | Paired organisations, restricted participants, changed sponsorship/permissions, workload and recovery cases |
| R3 Ecosystem | 45 | Advanced services/analysis address approved observed needs with accountable data and commercial responsibility | Compare an advanced capability against simpler service/manual alternatives; preserve distributional and attribution limitations |
| Later | 6 | A specific investment decision supports an optional capability; it does not inherit acceptance or funding from another release | A scoped research/qualification question and explicit include/defer/stop record |

These 368 story allocations and all 54 epic memberships remain unchanged. Counts measure inventory, not effort, completion or an ETA. There is no approved calendar or converted points-to-date forecast. A narrower pilot slice requires an explicit scope decision that retains excluded Must stories in the full roadmap; this document does not silently mark them delivered or remove them.

**Connected learning path:** Diagnose supplies a reviewed problem revision and evidence/baseline references; Map supplies a reviewed option/priority mapping; Discover adds disclosed capability and commercial constraints; Assess supplies a bounded trial and evaluation; Value case separates assumptions/forecast from measured observations; Deploy supplies approved operating/data/exit responsibilities; Adopt supplies capacity/support and task follow-up; Improve uses comparable review evidence to continue, change or stop. Each handoff pins its input revision and current authority; stale/hidden/revoked inputs, unsupported provenance and unapproved commercial/data obligations stay visible refusals or decisions.

The next story is chosen only after its actual Ready gate: engineer/owner review, source scenarios, data/API/screen/NFR impact, prerequisites, estimate and capacity. A populated card, parser pass or synthetic smoke check does not select a sprint. The four existing In Review stories (FR-AI-001, US-DC-04, US-MP-03, FR-SEC-001) retain that state until actual acceptance is recorded.
