# Design and decision process (design notes, RFCs, ADRs)

Owner: Nakul Jain · Last reviewed: 2026-10-08 · Update trigger: the first design note filed under this process, or a change to the integrator checklist.

This page records how design changes are made today (observed from the repository) and adds a minimal, lightweight route so a change has a place to be argued before code. It is a process proposal from an agent on 2026-10-08, not yet used or approved by the owner.

## 1. What exists

| Practice | Where | Notes |
|---|---|---|
| Architecture decision records ADR01 to ADR22 for the platform | [Architecture Decision Records v1.1](../current/Impact-Management-Architecture-Decision-Records-v1.1.md) (original: `specification/docs/09-...`, history `docs/history/v1.0`) | Append new ADRs after ADR22 |
| Extension ADRs for nonprofit AI (ADR NPA 001 onward), marked "proposed, not an owner sign-off" | [13-ARCHITECTURE-DECISIONS](../nonprofit-ai/v1.0/13-ARCHITECTURE-DECISIONS.md) | |
| Change control for the AI extension | [15-ACCEPTANCE-AND-CHANGE-CONTROL](../nonprofit-ai/v1.0/15-ACCEPTANCE-AND-CHANGE-CONTROL.md) | Review order BRD, FSD, HLD, LLD, tests |
| Per-increment release note with Delivered, Contract and persistence, Limits, Reproduction (and Integration notes for parallel slices) | `docs/RELEASE-*.md`; template pattern in ENGINEERING-BRIEF.md section 8 step 6 | The de facto design record after the fact |
| Parallel builder and integrator rules | [PARALLEL-WORK](../handover/PARALLEL-WORK.md) | |
| Engineering implementation plan and delivery plan (scope decision SD-01) | [Plan](../current/Impact-Management-Engineering-Implementation-Plan-v1.1.md), [DELIVERY-PLAN](../DELIVERY-PLAN.md) | |
| Requirement baseline and ledger | BRD/FSD v1.1, [COMPLETION-LEDGER](../COMPLETION-LEDGER.md), [TRACEABILITY.csv](../current/TRACEABILITY.csv) | A requirement is not removed or weakened by a design change |

There is no separate RFC template, numbering or approval record in the repository.

## 2. Lightweight route (proposed)

1. **When:** a change to a contract, data model, security property, capability model, deployment topology, retention rule or AI use, or anything touching a repository invariant (ENGINEERING-BRIEF.md section 4).
2. **Design note:** a short markdown file in a draft pull request, `docs/design/NNNN-<slug>.md` (create the folder on first use; documentation-only, starts no CI). Sections: problem, options with trade-offs, decision wanted, effects on requirements, security and privacy, migration and rollback, tests and evidence, open questions. Owner and last-reviewed lines as in every governance document.
3. **Decision:** the owner records the outcome in the note (accepted, rejected, superseded) and, for a lasting architectural choice, appends an ADR after ADR22 in `docs/current/Impact-Management-Architecture-Decision-Records-v1.1.md`.
4. **Then code:** the implementing slice links the note; its release note records deviations.

An architecture invariant is never changed by a note alone: the invariant text in AGENTS.md and ENGINEERING-BRIEF.md section 4 must be changed deliberately, with the owner's approval, in the same pull request.
