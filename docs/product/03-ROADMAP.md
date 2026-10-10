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
