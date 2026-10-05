# Nonprofit AI Enablement Decisions and Risks

Edition 1.0 · 5 October 2026 · All decisions below are open

## Decision process

The product owner approves scope and appoints accountable role owners. Each decision records its rationale, supporting evidence, approving natural person, date, affected requirements and follow-up actions. Role suggestions below are not appointments. No date, geography, price, revenue model, financial responsibility or data permission becomes approved because this register is populated. Resolve the decision before its dependent implementation or pilot use.

## Open decisions

| ID | Decision and evidence needed | Proposed accountable role | Dependency |
|---|---|---|---|
| DEC-NPA-001 | First cohort, organisation types, geography, languages and accessibility needs. Obtain representative user interviews and an agreed pilot list. | Product owner and organisation sponsors | R1 onboarding and FR-NPA-028, 033 |
| DEC-NPA-002 | First tasks and quality measures. Specify comparable baseline tasks, human review effort, acceptable errors and stopping conditions. | Organisation sponsor and adoption lead | FR-NPA-003, 021, 024 |
| DEC-NPA-003 | Allowed inputs, recipients and consent boundaries. Approve a synthetic pilot policy; separately assess any future personal-data use. | Organisation data owner with security review | FR-NPA-010, 012, 014, 026, 035 |
| DEC-NPA-004 | Marketplace operator, ownership, commercial relationships and neutrality. Decide whether listings, introductions or operated engagements are offered, and how conflicts are disclosed. | Product owner | FR-NPA-017, 018, 019, 020 |
| DEC-NPA-005 | Supplier verification scope, evidence, expiry and independent publication review. Define what each badge may actually claim. | Marketplace owner and security lead | FR-NPA-004, 017, 031 |
| DEC-NPA-006 | Human adviser responsibilities, case sharing, conflicts, engagement boundaries and escalation. Identify qualified accountable people. | Advisory service owner | FR-NPA-011, 019, 032 |
| DEC-NPA-007 | Procurement thresholds, eligible approvers, natural-person independence, recent authentication and exact quote bindings. Use the organisation's agreed policy. | Procurement owner | FR-NPA-014, 015, 016, 035 |
| DEC-NPA-008 | Competency rubric, evidence, assessor independence and appeals/remediation. Specify how practice differs from certification. | Learning owner | FR-NPA-008, 009 |
| DEC-NPA-009 | Retention, removal, backup limitations, exports and exit rights by data category. Do not invent durations or promise instant erasure. | Data owner and operations lead | FR-NPA-026, 030 |
| DEC-NPA-010 | Support ownership, hours, severity, incident escalation, availability and recovery objectives. Choose measurable values before performance/service qualification. | Operations lead | FR-NPA-029, 032, 040 |
| DEC-NPA-011 | Provider choice, budget, funding, approved models, monetary reservation rules and overrun response. Current attempt caps are not currency controls. | Product owner and finance owner | FR-NPA-010, 012, 023 |
| DEC-NPA-012 | Content curators, review cadence, stable lesson identifiers, stale-offer behavior and saved-version interpretation. Approve a migration policy before reordering lessons. | Content owner | FR-NPA-004, 007, 031, 038 |
| DEC-NPA-013 | Reviewed capabilities, onboarding and ceiling widening for existing organisations. Specify approval and reproposal behavior; no automatic widening. | Platform authority owner and tenant owner | FR-NPA-025, 033 |
| DEC-NPA-014 | Integration providers, scopes, destinations, credential custody, revocation and deployment authority. Define synthetic qualification per connector. | Integration owner and security lead | FR-NPA-022, 029 |
| DEC-NPA-015 | Conditional payment model, party moving funds, reconciliation, refunds, disputes and financial approval. Resolve operator responsibility before R3 design approval. | Product owner and finance owner | FR-NPA-020 |
| DEC-NPA-016 | Outcome attribution, feedback consent, baseline/quality evidence and links to governed impact indicators. Define who may accept conclusions. | Organisation sponsor and MEL owner | FR-NPA-024, 034, 035 |

## Risks and controls

| ID | Risk and consequence | Planned mitigation and evidence | Accountable role |
|---|---|---|---|
| RISK-NPA-001 | Treating a working draft tool as the whole marketplace creates misleading delivery promises. | Current/target labelling, phase gates and traceability; validate enabled journeys against real code. | Product owner |
| RISK-NPA-002 | Outdated product or discount claims lead to unsuitable purchases. | Dated primary sources, unknown-term labels, curator review and written offer comparison. | Content owner |
| RISK-NPA-003 | Unsafe information enters free text or is disclosed to a provider/supplier. | Synthetic first pilot, trained users, minimum inputs, explicit consent and reviewed recipient scopes; security cases. | Data owner |
| RISK-NPA-004 | Advisory calls or paid services exceed approved spending. | Attempt caps today; proposed money ledger and reconciliation; owner-funded generation and paid CI only. | Finance owner |
| RISK-NPA-005 | Same-person or stale approvals invalidate procurement and delivery accountability. | Natural-person independence, exact revision binding, current authority and negative tests on each decision. | Procurement owner |
| RISK-NPA-006 | Checkboxes are represented as competency or accepted delivery. | Distinct self-progress, assessment and acceptance states; evidence rubrics and independent decisions. | Learning and delivery owners |
| RISK-NPA-007 | Reusing old permissions or arithmetic weakens the platform. | Reuse layouts and scenario vocabulary with licence provenance; retain forced RLS and deterministic calculations. | Engineering lead |
| RISK-NPA-008 | Existing tenants cannot access new capabilities or receive unreviewed access. | Governed ceiling review and pending-profile reproposal; deny by default. | Platform authority owner |
| RISK-NPA-009 | Successful local checks are mistaken for release qualification. | Record environment and exact commit, preserve failing/skipped evidence and run four hosted gates before approved merge. | Release owner |
| RISK-NPA-010 | Accessibility gaps exclude staff despite automated zero-violation counts. | Manually investigate incomplete checks; keyboard, narrow-screen and assistive-technology UAT with representative users. | UX owner |
| RISK-NPA-011 | A crash between external action and recorded result causes duplicate work or payment. | Committed intent, external idempotency and reconciliation; no blind fresh-ID retry. | Operations lead |
| RISK-NPA-012 | Undefined commercial and service obligations block operated marketplace delivery. | Resolve operator/adviser/supplier/finance policies before R2/R3 activation; record signed scope and responsibility. | Product owner |

Probability and impact ratings remain unscored until owners review the pilot context. No risk is marked accepted. A risk record needs an owner, assessment, treatment evidence and explicit residual-risk decision before closure.

## Assumptions and change history

The design assumes reuse of the existing multi-tenant impact platform, synthetic initial pilots, human-controlled decisions, an editorial catalogue and optional bounded generated drafts. It does not assume supplier inventory, working payments, approved data permissions, production performance or fixed provider pricing. A changed assumption requires impact analysis across the BRD, FSD, designs, dictionary, wireframes, tests and operations.

Edition 1.0 establishes the proposed nonprofit AI extension. Earlier impact-platform specifications and their 307 requirement statuses remain intact. No sign-off is recorded in this edition.
