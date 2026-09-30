# Impact Management Platform

Business Requirements Document

Prepared for product and engineering review

Version 1.1   27 September 2026

Status Proposed baseline for product and engineering review

This document defines an enterprise platform for planning, monitoring, evaluation, learning and impact reporting. It covers the complete path from a programme proposal and results framework to field evidence, approved indicators, portfolio analysis, donor reporting and management decisions. It also defines the identity, privacy, security, AI governance and operating requirements needed to trust that path.

The intended outcome is a product with the functional breadth of a mature monitoring and evaluation platform and demonstrably less manual work. Every reported result must be explainable through its definition, source, calculation, approval and reporting context. AI must help users set up and operate the system while preserving that chain of evidence.

The product name is a working title. This BRD establishes business behaviour and quality targets. The FSD will specify detailed functional behaviour, the HLD will allocate responsibilities across system components, and the LLD will specify implementation contracts. Technology vendors, database schemas, service boundaries and screen designs are intentionally left to those later documents.

307 individually identified requirements   |   40 sections   |   30 integrated acceptance scenarios

## Contents

1 Document governance and interpretation

2 Business purpose and success measures

3 Scope and operating assumptions

4 People and responsibility model

5 End to end business journeys

6 Core information model and lifecycle

7 Organisation and tenant administration

8 Identity and user lifecycle

9 Authorisation and sharing policy

10 Strategy and results frameworks

11 Programme and delivery management

12 Indicator definitions targets and periods

13 Calculation aggregation and reconciliation

14 Forms surveys and collection rounds

15 Offline and field operation

16 Data import management and transformation

17 Data quality and completeness

18 Participants institutions and programme records

19 Evidence documents and qualitative analysis

20 Evaluation learning and management response

21 Collaboration review and workflow

22 Analytics dashboards and exploration

23 Reporting publication and donor obligations

24 Funding budgets and cost effectiveness

25 Integrations APIs and interoperability

26 AI assisted product capabilities

27 Security and assurance requirements

28 Privacy data governance and retention

29 Service administration and product operations

30 Migration onboarding and exit

31 User experience accessibility and localisation

32 Non functional requirements and qualification targets

33 Mandatory business rules and invariants

34 Business acceptance scenarios

35 Delivery sequencing dependencies and release gates

36 Risks assumptions and decision register

37 Traceability and downstream specification contract

38 Glossary

39 Reference sources

40 Baseline review and acceptance record

## Release interpretation

Documentation edition 1.1 is reconciled with application build 0.12.0 on 27 September 2026. The document edition and application build use different version sequences. The original business requirements and their acceptance conditions remain authoritative. No requirement has been removed or weakened to match the current code.

Build 0.13.0 increment (28 September 2026): reviewed renewal of unexpired delegated administrative authority (owner proposal, second-administrator consent, independent operator approval) is now implemented; renewal of expired authority, administrator replacement and external notices remain open. The increment is recorded in RELEASE-0.13.md, IMPLEMENTATION.md, QUALIFICATION.md and TRACEABILITY.csv; FR-TEN-001, FR-IAM-008 and FR-IAM-009 remain PARTIAL and the ledger is unchanged at 74 PARTIAL and 233 PENDING. Recorded qualification is now 353 application, 143 design-reference and 91 browser checks; edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.14.0 increment (29 September 2026): native PostgreSQL qualification with separately provisioned login roles is now recorded in RELEASE-0.14.md, IMPLEMENTATION.md, QUALIFICATION.md and TRACEABILITY.csv; no business requirement, priority or release tag changed. The ledger moves to 76 PARTIAL and 231 PENDING: NFR-DIN-002 (VF-DIN-002, concurrent change integrity) and NFR-DR-003 (VF-DR-003, recovery testing and backups) become PARTIAL on raced native writes and an executed CI-scale restore drill respectively, BR-SEC-003 and BR-OPS-005 gain login-role and readiness-topology evidence, and NFR-DR-002 stays PENDING because only the API process was restarted and no component was interrupted during a write. Recorded qualification is 354 PGlite and 379 native application checks, 143 design-reference and 91 browser checks; edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.15.0 increment (29 September 2026): live identity-provider qualification is recorded in RELEASE-0.15.md, IMPLEMENTATION.md, QUALIFICATION.md and TRACEABILITY.csv; no business requirement, priority or release tag changed. The ledger stays at 76 PARTIAL and 231 PENDING: BR-IAM-002, BR-IAM-003 and BR-IAM-006 (FR-IAM-002, FR-IAM-003, FR-IAM-006) gain live-provider evidence for issuer and subject binding, TOTP step-up and provider logout, BR-IAM-009 gains the bounded delegable-capability set, and NFR-IAM-001 (VF-IAM-001, revocation time) stays PENDING because bearer access tokens outlive a provider logout until they expire and no revocation latency is measured. Recorded qualification is 372 PGlite and 397 native application checks, 16 + 16 live-provider checks, 143 design-reference, 91 browser and 2 live-provider browser checks; edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.16.0 increment (29 September 2026): the worker runtime, outbox dispatcher and email adapter are recorded in RELEASE-0.16.md, IMPLEMENTATION.md, QUALIFICATION.md and TRACEABILITY.csv; no business requirement, priority or release tag changed. The ledger stays at 76 PARTIAL and 231 PENDING: BR-IAM-001 (FR-IAM-001) gains invitation email with superseded earlier links, BR-TEN-001 (FR-TEN-001) gains suspension holds honoured without replay, cancellation of queued jobs and recovery-contact email confirmation as evidence, BR-WFL-006 (FR-WFL-006) gains per-recipient in-app delivery status and idempotent reminders; BR-IAM-007 (FR-IAM-007) and BR-ACC-008 (FR-ACC-008) stay PENDING. Recorded qualification is 405 PGlite and 437 native application checks, 16 + 16 live-provider checks, 143 design-reference, 93 browser and 2 live-provider browser checks; edition 1.1 figures elsewhere in this document describe build 0.12.0. The Word copy is unchanged and will be regenerated at the next documentation edition.

Build 0.18.0 increment (29 September 2026): BR-PLN-001, BR-PLN-003 and BR-PLN-010 now have implemented bounded subsets through FR-PLN-001 (typed results hierarchy with stable node identities and structural validation), FR-PLN-003 (independently approved, immutable framework baselines with effective dates, pinned into period snapshots) and FR-PLN-010 (completeness review with documented exceptions); BR-IND-003 and BR-ANA-003 through targets, baselines and milestones and a targets-versus-actuals table. No business requirement changed and none is accepted. See RELEASE-0.18.md. The ledger moves to 81 PARTIAL and 226 PENDING (0 accepted).

The application is a development delivery. The requirement ledger records 74 PARTIAL and 233 PENDING requirements, with zero fully accepted. PARTIAL means a bounded implementation and some evidence exist, not that all acceptance conditions are satisfied. PENDING means the requirement has no accepted implementation coverage in the ledger; a read-only surface or reference example does not establish delivery.

Recorded qualification contains 325 application checks, 143 design-reference checks and 81 browser checks. One expired-offline-grant test is deselected and is not a pass. Local integration uses fresh in-memory PGlite PostgreSQL 17.5 with serialized transactions. Native PostgreSQL concurrency, live identity-provider assurance, disaster recovery, load qualification and production acceptance remain open.

The original BRD and FSD use R1, R2 and R3 requirement assignments. The later 16-stage delivery roadmap is an implementation sequence. Roadmap stage 1 and baseline R1 are different groupings; neither is complete. Requirement release assignments remain unchanged.

The sections explicitly marked current implementation describe this build. Retained target-design sections describe required future behavior unless the current implementation section states otherwise. Complete source, contracts, test evidence and original documents accompany this edition. Start at DOCUMENTATION-INDEX.md and TRACEABILITY.csv for exact locations and evidence boundaries.

## Current business delivery

The implemented path supports a reviewed managed-tenant setup, verified registered-account recovery contact, explicit initial administrator provisioning, independently reviewed business grants, programme and manual measurement setup, collection, review, provisional calculation, period close, internal reporting and controlled named-recipient publication. No tenancy or custody action automatically grants business-data access.

Recovery-contact management adds owner nomination, nominee consent with fresh configured MFA assurance, independent operator approval, expiry, replacement, renewal and revocation. A contact cannot reset an account, assume custody or bypass an unavailable owner. External email or SMS verification is still required future work.

This delivery does not implement the complete forms, offline, ingestion, evidence, evaluation, participant, finance, analytics, integration or AI scope in the BRD. Numeric results remain deterministic. The product has no model-provider workflow and no production infrastructure qualification.

## Acceptance and ownership

The baseline business owner and approvers are still unassigned. Documentation reconciliation records implementation facts; it does not constitute sponsor signoff. Business acceptance requires the original outcome, boundary and recovery conditions, plus the applicable nonfunctional gates. Named owners, accepted deviations and dated evidence must be entered in the release acceptance register before any production acceptance claim.

Each requirement below now carries its current delivery status. The original requirement wording, priority, release assignment and acceptance criteria are retained. The detailed assessment and source/evidence references for every requirement are in TRACEABILITY.csv and the implementation workbook.

## Retained requirements and target design

The following baseline sections retain their requirement IDs and intended behavior. Implementation status is governed by the current profile above and the accompanying traceability register. Planned components are not represented as deployed services.

## 1 Document governance and interpretation

### 1 1 Document control

| Item | Baseline |
| --- | --- |
| Sponsor | Product sponsor to be confirmed |
| Proposed business owner | Product leadership to be confirmed |
| Intended reviewers | MEL lead, engineering lead, design lead, security lead, privacy lead, platform operations and implementation lead |
| Document purpose | Agree complete product scope, business rules, operating controls and measurable acceptance targets |
| Product scope | Multi organisation monitoring evaluation learning and impact management software |
| Decision status | Proposed requirements and targets pending sponsor review |
| Version policy | Preserve requirement IDs across revisions; record changed meaning, rationale and acceptance impact |
| Next controlled artifact | Functional Specification Document mapped to this BRD |

Named review roles are proposed accountabilities rather than staffing commitments. A person may hold multiple roles, but sensitive approvals must preserve separation of duties. Sponsor approval establishes a product baseline; it does not constitute security certification, legal clearance, a delivery date or a commercial service commitment.

### 1 2 Requirement language and identifiers

“Shall” is mandatory for the specified release. “May” describes an administrator or user choice within supported behaviour. A requirement has an immutable ID, title, priority, release and acceptance evidence. Module owners own interpretation and acceptance. Cross cutting requirements apply to every feature, including later releases and AI generated operations, even when not repeated in each requirement.

| Code | Meaning |
| --- | --- |
| P0 | Essential control or core workflow. Required before production use of the affected capability |
| P1 | Required enterprise capability in the assigned release |
| P2 | Advanced target capability in the assigned release; explicit scope change is needed to remove it |
| R1 | Controlled production release with complete core workflows and all applicable safeguards |
| R2 | Enterprise breadth including additional integrations, advanced reporting and operations |
| R3 | Advanced evaluation, automation and deployment options |
| Acceptance | Minimum observable evidence; the FSD and test plan expand this into positive, negative and boundary cases |

Release labels express sequencing, not calendar dates. Delivery estimates require scope decomposition and engineering review. Core security, privacy, accessibility and data integrity controls cannot be deferred while exposing an affected feature. No feature is “done” because its happy path works.

### 1 3 Baseline change control

Each change request shall record the affected IDs, reason, user impact, data compatibility, security impact, acceptance changes, dependency impact and decision owner. Deleted requirements remain as retired entries in the revision register. FSD elaboration must not silently reduce scope or relax a numerical target. When requirements conflict, the privacy and security constraints and approved data definitions take precedence; unresolved conflicts require a documented product decision.

## 2 Business purpose and success measures

### 2 1 Problems to solve

Programme teams repeatedly reconstruct project structures, indicator plans and donor reports from documents and spreadsheets. Different partners use different definitions for similar indicators. Data arrives late or in inconsistent formats. Corrections can change totals without a clear explanation. Portfolio managers struggle to distinguish an actual zero from missing or unapproved data. Evidence is often separated from the result it supports. Manual work grows as projects, partners, indicators and reporting obligations multiply.

The platform shall make these relationships explicit and reusable. Its value comes from reduced preparation work, dependable calculations, visible quality limitations, controlled collaboration and faster access to usable evidence. Customer acquisition, sales channels, market sizing and distribution strategy are outside this technology BRD. Product administration, subscription entitlements and operational support remain in scope because they affect software behaviour.

### 2 2 Product outcomes

| Outcome | Proposed measure | Evaluation method |
| --- | --- | --- |
| Faster programme setup | At least 50 percent less median setup time than the agreed manual baseline | Same representative proposal, logframe and reviewer across comparable tasks; count corrections and review time |
| Faster periodic reporting | At least 60 percent less median preparation time | Approved source data to reviewed report on the same donor template; include reconciliation time |
| Reliable calculations | 100 percent agreement with the approved deterministic calculation corpus | Versioned expected results covering boundaries, corrections and aggregation |
| Traceable reporting | Every published numeric result links to a definition version, source set, calculation and approval context | Automated lineage coverage and sampled reviewer reconstruction |
| Easier use | At least 90 percent unaided completion of the six core role tasks | Moderated testing with at least 15 representative users across at least three roles |
| Clear data quality | Every overdue, invalid or incomplete submission has a visible status and accountable owner | Workflow and dashboard acceptance testing |
| Trustworthy AI | Meet the per use case quality gates in this BRD | Held out evaluations, adversarial tests and reviewer acceptance |
| Safe operation | Meet the security, privacy, recovery and service quality gates | Evidence based release review and production monitoring |

These are proposed product targets, not observed results. Baselines must be recorded before pilots. A faster AI draft that requires more correction does not count as an improvement. Metrics shall distinguish new users from trained users and small projects from complex portfolios. Product analytics must respect the tenant’s telemetry policy.

### 2 3 Product principles

Use one controlled definition of each indicator. Preserve raw evidence and the history of changes. Show limitations next to results. Design ordinary tasks for the person doing them. Make advanced configuration available without placing it in every workflow. Keep calculations deterministic and reproducible. Make AI actions inspectable and reversible where possible. Apply permissions to derived information as well as source records. Maintain useful core workflows when AI or a third party integration is unavailable.

## 3 Scope and operating assumptions

### 3 1 Full target scope

The target includes organisation administration; enterprise identity; scoped permissions; programme and portfolio structures; theories of change and results frameworks; indicators and targets; participant and institution registries; forms and field collection; offline work; imports and connectors; data quality; evidence management; qualitative analysis; evaluation and learning; activities and budgets; approvals and collaboration; analytics; donor reporting; controlled publication; AI assistance; APIs; migration; subscription administration; and production support.

The platform shall support NGOs, foundations, public programmes, research and evaluation teams, implementing partners, social enterprises and advisory organisations. Sector terminology and templates shall be configurable. Health, education, agriculture, livelihoods, climate and governance programmes are representative configurations, not separate products.

### 3 2 Boundaries

| Boundary | Included | Outside the default product |
| --- | --- | --- |
| Finance | Grant context, programme budgets, imported expenditure, variance and cost effectiveness | General ledger, payroll, banking, payment execution and statutory accounting |
| Participant data | Consented programme records and service events where justified | A national identity system or compulsory biometric identity |
| Health | Monitoring programme delivery and outcomes | Clinical diagnosis, treatment recommendations and medical device functionality |
| Evaluation | Plans, instruments, evidence, findings and methodological metadata | Automatic proof of causation or replacement of scientific review |
| AI | Drafts, extraction, controlled analysis and approved workflow assistance | Autonomous grant awards, eligibility denial, clinical decisions or unreviewed external publication |
| Integrations | Defined connectors and a governed API | An unlimited promise to integrate every customer system |
| Deployment | Managed hosted service and later qualified dedicated deployment | Unspecified on premises or disconnected sovereign deployments at launch |
| Product comparison | Publicly documented TolaData capability benchmark | A claim of source code equivalence, exhaustive parity or verified superiority |

### 3 3 Assumptions and decisions

The baseline assumes a hosted, multi tenant product; English as the first complete interface language; responsive desktop and mobile workflows; optional sensitive participant data; configurable regional hosting; and existing model services or qualified self hosted models for AI. These are planning assumptions. An organisation shall be able to use the core product with AI disabled. The product shall not require a specific model vendor to define an indicator or approve a report.

The first production cohort is assumed to contain a limited number of organisations with named MEL and administration owners. The load profile in section 32 is the engineering qualification envelope, not a forecast of customer demand. Actual hosting regions, interface languages, authentication policies, paid entitlements, retention schedules and deployment variants require decisions listed in section 36.

### 3 4 Reference product baseline

Public TolaData material documents data collection, results frameworks, indicators, dashboards, aggregation, workflows, approvals and integrations. Its release notes also describe MFA, discussion threads, file uploads and change history. Its current website announces AI knowledge search, analytics and reporting for Q4 2026. Announced capability must be distinguished from generally available and independently tested capability. [S1 to S8]

The target product will be assessed through end to end task performance, correctness, permission enforcement and operational evidence. A cleaner interface or an AI chat box alone does not establish superiority. A controlled benchmark should test equivalent inputs and workflows in both applications where authorised access is available.

## 4 People and responsibility model

### 4 1 Product personas

| Persona | Primary responsibility | Information needed |
| --- | --- | --- |
| Organisation owner | Account custody, delegation and continuity | Ownership, subscription and accountable administrators |
| Identity administrator | Members, federation, groups and access reviews | Identity status and effective permissions without automatic access to programme content |
| MEL administrator | Definitions, methods, validation and reporting standards | Indicator versions, evidence rules and quality exceptions |
| Portfolio manager | Performance across authorised programmes | Comparable results, funding context, risks and missing data |
| Programme manager | Delivery, partners, activities and reporting | Workplan, submissions, decisions and variance |
| Data steward | Imports, cleaning, mapping and corrections | Raw data, lineage, rejected records and reconciliation |
| Enumerator or field worker | Collect assigned data | Minimal participant information, local tasks and sync status |
| Reviewer or approver | Independent quality and publication decisions | Evidence, changes, conflicts and approval history |
| Analyst or evaluator | Analysis and evaluation | Authorised datasets, methods, uncertainty and reproducible extracts |
| Partner contributor | Report on an assigned grant or project | Own submissions, feedback and shared definitions |
| Funder or external viewer | Review agreed results | Authorised portfolio views and approved reports |
| Privacy or safeguarding officer | Sensitive data governance | Restricted cases, retention, access and incident evidence |
| Auditor | Examine approved scope without modification | Frozen snapshots, audit records and provenance |
| Integration identity | Exchange authorised machine data | Explicit scopes, quotas, expiry and accountable owner |
| Platform operator | Availability, support and service administration | Operational metadata; customer content only through controlled access |

### 4 2 Default access matrix

The following defaults are role templates. All actions are constrained by tenant, project, partner, record, field and purpose policies. “Scoped” means explicit assignment; it does not mean access to every project. PII, restricted evidence, downloads, external sharing and approval are separately granted capabilities. Owning an account does not automatically expose participant records.

| Role template | Administer members | Configure plans | Enter data | Approve data | Publish reports | Read restricted data |
| --- | --- | --- | --- | --- | --- | --- |
| Organisation owner | Delegate | By grant | By grant | By grant | By grant | By grant |
| Identity admin | Scoped | No | No | No | No | No |
| MEL admin | No | Scoped | Scoped | Separate assignment | Separate assignment | By grant |
| Programme manager | Invite if delegated | Scoped | Scoped | Separate assignment | Separate assignment | By grant |
| Data steward | No | Data mappings | Scoped | Separate assignment | No | By grant |
| Enumerator | No | No | Assigned records | No | No | Minimum assigned fields |
| Reviewer | No | Read | Return for correction | Assigned queue | No | Minimum evidence |
| Analyst | No | Read | Derived drafts | No | No | By grant |
| Partner contributor | No | Read shared plan | Own scope | No | No | Own permitted scope |
| External viewer | No | No | No | No | No | No by default |
| Auditor | No | Read granted versions | No | No | No | Explicit audit scope |
| Platform operator | Service metadata | No | No | No | No | Time limited exceptional access |

### 4 3 Decision accountability

The product owner accepts workflows and usability. The MEL lead accepts indicator semantics, aggregation and evaluation behaviour. The security lead accepts access controls and verification evidence. The privacy lead approves personal data purposes, sharing and lifecycle rules. Platform operations accepts monitoring, incident handling, backups and recovery. Engineering owns technical feasibility and implementation. None of these roles may waive another domain’s critical gate alone.

## 5 End to end business journeys

Each journey includes a normal path and required failure handling. Journeys are acceptance scenarios across modules rather than proposed screens.

### 5 1 Establish an organisation

The owner establishes a tenant, hosting policy, identity controls, initial administrators and retention policy. Administrators create groups and scoped roles, import or invite users, and test access with sample data. Before real data is loaded, the owner confirms data handling and AI policies. Invalid invitations, federation failures and a departed sole administrator must have recoverable paths that preserve identity verification and audit history.

### 5 2 Convert a proposal into a programme

A manager uploads a proposal and logframe, optionally asks AI to extract a draft, and reviews the objectives, outcomes, outputs, activities, indicators, targets and assumptions. A MEL reviewer resolves unsupported or ambiguous definitions. The approved framework becomes a versioned baseline. The system must distinguish a stated target from an AI suggestion and flag a missing denominator, period or evidence source.

### 5 3 Collect and approve field evidence

A supervisor publishes a form and assigns a collection round. An enumerator downloads the permitted assignments, records consent where required and captures data online or offline. Synchronisation validates the record and places it in the correct review queue. A reviewer approves or returns it. Duplicate attempts, an obsolete form, revoked access and conflicting edits must not silently overwrite accepted evidence.

### 5 4 Bring partner spreadsheets into a portfolio

A data steward imports a partner file, previews mappings and identifies identifiers, units and dates. Validation separates accepted, rejected and duplicate records. The steward resolves exceptions and submits the batch. Only approved results enter official reporting. A corrected file must update the intended records through a traceable revision, not append duplicate achievements.

### 5 5 Close a reporting period

A programme manager reviews completeness, overdue partners, quality issues and target changes. Required reviewers approve the period. The system freezes the official snapshot and generates the donor report against that snapshot. A late correction follows a reopen or restatement process with impact analysis. Previously issued reports remain discoverable with a clear superseded status.

### 5 6 Inspect portfolio performance

A portfolio manager compares compatible indicators across programmes, drills into a result, inspects missing coverage and reviews explanatory evidence. Any restricted contributing data remains protected. An aggregate over authorised published inputs can be shared without revealing protected raw records when explicitly approved. Overlapping populations and incompatible units prevent misleading totals.

### 5 7 Produce an evidence based AI answer

A user asks a programme question. The system identifies the permitted data and time scope, retrieves authorised evidence, calculates numbers through approved methods and presents an answer with references. It states when the evidence is incomplete or contradictory. A question requiring a write operation produces a proposed change and approval path. Restricted information must remain protected in citations, snippets and conversation history.

### 5 8 Conduct an evaluation and record learning

An evaluator registers questions, design, instruments, sampling assumptions and evidence needs. They analyse an authorised versioned extract, attach findings and limitations, and route conclusions for review. Management records its response, actions and follow up. A change in programme design links back to the evidence and decision, allowing later review of whether the action improved results.

### 5 9 Manage a participant data request

A privacy officer verifies a request, locates the relevant records and checks applicable retention and hold conditions. The system produces an authorised access package or controlled correction, restriction or deletion. Derived datasets, AI indexes, cached artifacts and downstream recipients are included in the action plan. The system records what was completed and what remains constrained without exposing information about other participants.

### 5 10 Offboard a user or partner

An administrator revokes membership or partnership access, ends sessions, disables relevant credentials, cancels unauthorised queued jobs and transfers tasks. Historical attribution remains. Reports or copies already downloaded cannot be remotely recalled; live links and future access must be revoked. Offline device exposure is bounded by expiry, minimisation and the device policy.

### 5 11 Recover from an operational incident

Operations detects a service failure or security event, restricts affected processing, informs authorised contacts and restores service within the agreed recovery objectives. Restored data must preserve tenant isolation, approvals, deletion instructions and audit continuity. Recovery is verified against recent accepted writes and reporting snapshots before normal publication resumes.

### 5 12 Migrate and exit

The implementation lead maps legacy structures, runs trial imports, reconciles calculations and approves cutover with a rollback plan. At contract exit, an authorised owner exports data, definitions, attachments, histories and relationships in documented formats. Service closure follows the agreed retention and deletion schedule. Migration and exit must not depend on undocumented proprietary identifiers alone.

## 6 Core information model and lifecycle

### 6 1 Business entities

| Entity group | Required relationships and meaning |
| --- | --- |
| Tenant and organisation unit | Security boundary; legal or operational units within it; region and policy ownership |
| User membership and role grant | Identity belongs to one or more tenants through separate memberships and explicit scopes |
| Portfolio programme and project | Configurable reporting hierarchy with governed cross portfolio memberships |
| Partner funder and agreement | Reporting responsibilities, sharing boundaries, grants and accountable contacts |
| Results framework and node | Versioned objectives, outcomes, outputs, assumptions and causal claims |
| Indicator definition and instance | Reusable definition plus project context, targets, periods and permitted dimensions |
| Dataset record and submission | Source records, transformations, versions, quality state and approval state |
| Participant household and institution | Optional programme entities with purpose limited identifiers and service events |
| Evidence and finding | Files, references, qualitative excerpts, evaluation claims and their limitations |
| Approval and decision | Actor, authority, evidence version, timestamp, reason and transition |
| Dashboard report and publication | Configuration, approved snapshot, audience, expiry and distribution history |
| AI task and proposed change | Input scope, model and policy version, output, review and resulting action |
| Integration job and credential | Source ownership, mapping version, run history, service permissions and expiry |
| Audit event and retention action | Attributable event metadata and policy controlled lifecycle evidence |

### 6 2 Data identity and semantics

Every business object shall have a stable identifier independent of its display name. External IDs require a source namespace. Renaming an organisation, moving a project or changing an indicator label must not break history. Event time, reporting period, ingestion time, approval time and publication time are separate concepts. The FSD shall define mandatory and conditional fields, validation, cardinality, uniqueness and lifecycle for each entity without treating this table as a database schema.

### 6 3 Lifecycle rules

| Object | Minimum states | Required transition safeguards |
| --- | --- | --- |
| Membership | Invited, active, suspended, revoked, expired | Verified acceptance; no privilege after suspension; task reassignment |
| Programme | Draft, active, paused, closing, closed, archived | Approved baseline; closure checks; authorised reopen |
| Definition or form | Draft, under review, approved, published, superseded, retired | Versions remain attributable; historical records retain original meaning |
| Submission | Draft, submitted, validating, rejected, returned, approved, superseded | Quality status is separate; correction creates traceable revision |
| Reporting period | Open, closing, locked, reopened, restated | Publication uses approved snapshot; reopen needs reason and authority |
| Report | Draft, in review, approved, published, superseded, withdrawn | Approval and distribution are separate actions |
| AI task | Requested, processing, proposed, reviewed, applied, failed, cancelled | No implicit approval; recheck access and source version before application |
| Deletion request | Requested, validated, held or scheduled, executing, completed | Scope, authority, retention conflicts and deletion evidence |

Archiving is not deletion. Rejection is not deletion. An approved record cannot be silently edited in place. A later restriction or lawful deletion may limit access to historical content; the audit trail shall retain permissible event metadata without retaining prohibited personal values.

## 7 Organisation and tenant administration

Business owner: Product owner with identity and privacy leads. Dependencies: identity, permissions, retention, audit and service administration.

BR-TEN-001   Tenant lifecycle   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-001.

The platform shall support controlled tenant creation, activation, suspension, reactivation, archival and closure. Each tenant shall have an accountable owner, policy set, hosting region and lifecycle history. Suspension must preserve agreed owner access for billing, support and authorised export without exposing ordinary operational actions.

Acceptance: Exercise every transition, verify permitted actions and demonstrate that suspension neither deletes data nor leaves scheduled writes operating without policy authority.

BR-TEN-002   Organisation structures   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-002.

Administrators shall configure country offices, departments, teams and delivery units without creating accidental security inheritance. Organisational reporting relationships and access scopes shall be independently configurable. A restructure shall retain historical ownership and reporting context.

Acceptance: Move a project between units, preserve earlier reports and show the exact access changes before committing the move.

BR-TEN-003   Multiple memberships   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-003.

A person shall be able to hold separate memberships in multiple tenants. Tenant switching shall be explicit and visible. Roles, search, recent items, AI conversations, notifications, drafts and exports shall not mix contexts.

Acceptance: A user with different roles in two tenants sees only each tenant’s authorised content, including after rapid switching and opening multiple browser tabs.

BR-TEN-004   Configuration and terminology   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-004.

The platform shall support configurable labels, programme hierarchies, controlled lists, fiscal calendars, time zones, currencies, units and status vocabularies. Configuration changes shall be versioned and previewable. They shall not redefine approved historical values silently.

Acceptance: Change the fiscal year and a status label while prior period reports remain reproducible and affected future schedules are identified.

BR-TEN-005   Custom fields and templates   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-005.

Authorised administrators shall define typed custom fields, required conditions, allowed values, visibility, validation and reusable templates. Custom fields shall participate in search, reports, imports and permissions where appropriate. Retiring a field shall preserve its historical interpretation.

Acceptance: Create a restricted custom field, import it, report on it and confirm that unauthorised users cannot retrieve it through any supported channel.

BR-TEN-006   Partner and consortium boundaries   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-006.

Partner collaboration shall use explicit project or dataset grants with purpose, owner, start date and expiry. Cross tenant exchange shall create a governed agreement and approved data contract; it shall not imply shared membership or unrestricted database access.

Acceptance: Two partners collaborate on one programme without seeing each other’s private records; expiring an agreement prevents new exchange and marks existing copies for the agreed lifecycle action.

BR-TEN-007   Policy inheritance and exceptions   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-007.

Tenant policies shall provide secure defaults for child units and projects. A project may tighten restrictions. Relaxing a tenant minimum requires an authorised, reasoned and time bounded policy exception where permitted; nonwaivable security requirements remain enforced.

Acceptance: Attempt a weaker project export rule under a stricter tenant policy and confirm denial or a visible approved exception workflow.

BR-TEN-008   Configuration promotion   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-008.

Administrators shall test templates, rules and workflow changes in an isolated configuration workspace before applying them to production. Promotion shall show dependencies, changed behaviour and rollback options. Test records shall never enter official results.

Acceptance: Promote a reviewed rule version and demonstrate that production data remains isolated from sample records and obsolete configuration.

BR-TEN-009   Branding and external identity   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-009.

Tenants shall configure approved logos, report themes and external portal identity without weakening authentication, accessibility or disclosure rules. Custom domains, when supported, shall require verified control and lifecycle management.

Acceptance: Apply branding across supported artifacts and verify clear organisation identity, accessible contrast and continued enforcement of sharing controls.

BR-TEN-010   Ownership continuity   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-TEN-010.

The platform shall support owner transfer, multiple accountable administrators and verified recovery when the last administrator is unavailable. A tenant cannot remove its last eligible owner without a successor or an approved closure procedure.

Acceptance: Attempt last owner removal and perform a verified transfer; demonstrate full audit history and no support shortcut that bypasses identity checks.

## 8 Identity and user lifecycle

Business owner: Identity administrator and security lead. The baseline shall be mapped to NIST SP 800 63B 4 during the FSD; an assurance level claim requires separate evidence. [S11]

BR-IAM-001   Invitations and onboarding   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-001.

Invitations shall specify tenant, role scope, inviter and expiry. Users shall verify control of the intended identity before acceptance. Invites shall be revocable, single use and resistant to forwarding to a different identity. Domain membership alone shall not grant access to programme data.

Acceptance: Test expired, replayed, revoked and wrong identity invitations, including bulk invitations and partially failed deliveries.

BR-IAM-002   Enterprise federation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-002.

The platform shall support tenant governed single sign on through standard enterprise federation, including SAML 2.0 and OpenID Connect. Administrators shall validate configuration before enforcement, manage certificate changes and retain a tightly controlled emergency recovery path.

Acceptance: Verify normal login, invalid assertions, wrong tenant audience, certificate rotation, enforced federation and identity provider outage without opening a bypass.

BR-IAM-003   Multifactor and passkeys   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-003.

Privileged accounts shall require MFA. The product shall support phishing resistant authenticators or passkeys and controlled alternatives for other users. Tenants shall enforce stronger authentication for sensitive data, external publication and credential management. SMS alone shall not satisfy privileged MFA.

Acceptance: Demonstrate enrolment, step up, lost factor recovery, factor removal and refusal of a sensitive action when the required assurance is absent.

BR-IAM-004   Local account security   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-004.

Where local passwords are enabled, users shall be able to use long passphrases, password managers and paste. Compromised password screening, protected credential storage, rate limits and secure reset are required. Arbitrary periodic changes and composition rules shall not substitute for evidence based controls.

Acceptance: Verify reset token expiry and replay protection, enumeration resistant responses, brute force controls and no password exposure in logs or exports.

BR-IAM-005   Provisioning and deprovisioning   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-005.

Enterprise customers shall provision, update, suspend and revoke memberships and group assignments through SCIM 2.0 or an approved equivalent integration. Conflicting manual and directory changes shall have an explicit authority rule.

Acceptance: Provision and revoke a user through the identity provider; confirm that downstream permissions, sessions and assigned work reflect the intended state within NFR-IAM-001.

BR-IAM-006   Session control   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-006.

Users and authorised administrators shall inspect and end active sessions. Session lifetime, idle timeout and reauthentication shall reflect role and data sensitivity. Device trust shall be explicit; a shared device shall not retain unrestricted access or visible personal records after logout.

Acceptance: Revoke one and all sessions, test browser restart and idle expiry, and confirm that protected pages do not reappear through browser history or stale application state.

BR-IAM-007   Recovery and identity changes   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-007.

Changes to login identity, MFA or recovery channels shall require appropriate verification and notify relevant account contacts. Recovery shall avoid knowledge questions and informal support overrides. Recovery codes shall be single use and protected.

Acceptance: Test stolen session attempts to change recovery details, recovery replay, disputed email changes and verified restoration without privilege escalation.

BR-IAM-008   Membership status and expiry   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-008.

Memberships shall support expiry, suspension, revocation and reactivation with independent status in each tenant. Temporary consultants and reviewers shall receive bounded access. Suspension shall not erase their past attribution or transfer ownership implicitly.

Acceptance: Expire a contractor with pending approvals and demonstrate immediate online enforcement, preserved attribution and reassignment of pending work.

BR-IAM-009   Delegated user administration   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-009.

Delegated administrators shall manage only permitted users and scopes and shall not grant a privilege they are not authorised to delegate. Sensitive role changes shall support independent approval and step up authentication.

Acceptance: A project administrator cannot grant tenant administration, expand to another project or approve their own elevation.

BR-IAM-010   Group management   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-010.

The platform shall support reusable groups, scoped group grants and effective permission inspection. Changes to group membership shall affect all derived access. Nested groups, if enabled, shall prevent cycles and clearly show effective scope.

Acceptance: Remove a member from a group and verify access removal from search, dashboards, APIs, reports, AI and scheduled exports.

BR-IAM-011   Access certification   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-011.

Owners shall conduct periodic and event triggered access reviews showing users, service identities, grants, last relevant activity, expiry and sensitive capabilities. Review decisions and overdue actions shall be tracked.

Acceptance: Run a review, revoke selected grants and retain evidence of reviewer, decision and completion without revealing restricted content to the reviewer.

BR-IAM-012   Service identities   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-012.

Machine access shall use identifiable service accounts with an accountable owner, purpose, minimum scopes, expiry and rotation policy. Personal credentials shall not be embedded in shared integrations. Orphaned service identities shall be detectable and disableable.

Acceptance: Rotate a credential without duplicate ingestion, revoke it and confirm failure of subsequent requests while preserving job attribution.

BR-IAM-013   User profile and preferences   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-013.

Users shall manage permitted profile details, language, time zone, notification preferences and accessibility preferences. Identity source controlled fields shall show their authoritative source. Profile changes shall not change ownership or audit identity.

Acceptance: Change display name and locale while historical actions remain linked to the same identity and dates render consistently.

BR-IAM-014   Departure and work reassignment   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IAM-014.

Offboarding shall identify owned data sources, forms, reports, schedules, API credentials and approval tasks. Administrators shall reassign or cancel them explicitly. Revocation shall recheck queued work rather than allowing it to complete under stale authority.

Acceptance: Offboard the owner of a pending report export and connector; demonstrate the specified cancellation or reassignment and blocked unauthorised delivery.

## 9 Authorisation and sharing policy

Business owner: Security lead with programme and privacy owners. Permissions are enforced on the server and across all channels; hiding a user interface control is insufficient.

BR-ACC-001   Deny by default   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-001.

Every read, write, approve, export, share, delete and administrative action shall require an explicit effective authorisation. Tenant boundaries shall not depend on user supplied identifiers. Unknown or conflicting policy states shall deny sensitive access.

Acceptance: Tamper with object IDs, bulk requests, file references and tenant context and verify denial without confirming protected object existence.

BR-ACC-002   Fine grained scope   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-002.

Roles shall combine with tenant, organisational unit, project, partner, record and field restrictions. Read, create, edit, approve, publish, export, administer and view sensitive data shall be independently controllable capabilities.

Acceptance: A reviewer sees required evidence and may approve assigned submissions but cannot edit source data, download all records or grant others access.

BR-ACC-003   Effective permissions   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-003.

Administrators and affected users shall understand why an action is allowed or denied through a permission explanation that does not disclose restricted resources. Explicit restrictions and sensitivity policies shall take precedence over broader inherited grants.

Acceptance: Combine conflicting roles and show the effective result; a broad reader role shall not override a restricted participant field policy.

BR-ACC-004   Separation of duties   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-004.

The platform shall prevent self approval for governed submissions, definitions, external reports and privileged role changes. Delegation shall preserve reviewer independence. Emergency exceptions shall require distinct authority, justification, expiry and subsequent review.

Acceptance: Test direct self approval, group mediated self approval, delegated approval and approving a revision the reviewer authored.

BR-ACC-005   Permission safe derivation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-005.

Derived datasets, aggregates, search indexes, AI results and exports shall preserve source restrictions unless an authorised publication process creates an approved disclosure artifact. Access to a total shall not imply access to its underlying people or records.

Acceptance: Combine public and restricted inputs, drill down and query through AI; verify only the approved disclosure level is available.

BR-ACC-006   External access lifecycle   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-006.

External users and links shall have an owner, audience, permitted actions, expiry and revocation mechanism. Public links shall be disabled by default and available only for approved public artifacts. Sensitive information shall require authenticated access.

Acceptance: Expire or revoke a link, change the source sensitivity and verify old URLs no longer provide unauthorised access.

BR-ACC-007   Export and bulk access   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-007.

Downloading and bulk extraction shall be distinct permissions with scope checks, sensitivity controls and audit events. Export authority shall be rechecked both at job execution and at download. Long lived static download links shall not defeat revocation.

Acceptance: Revoke access while an export is queued and after it is generated; confirm no subsequent authorised platform download is possible.

BR-ACC-008   Privileged support access   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-008.

Support personnel shall use time limited, purpose bound access approved through the applicable tenant policy. Access shall identify the real operator, record actions and notify designated contacts. Impersonation shall never conceal the operator or inherit unrestricted privilege.

Acceptance: Inspect and terminate a support session; verify expiry, attribution and inability to perform prohibited publication or identity changes.

BR-ACC-009   Privacy preserving aggregates   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-009.

Shared views shall support minimum cell sizes, suppression, complementary suppression and restrictions on filters that could reveal individuals. Thresholds shall reflect the use case. Removing names alone shall not count as anonymisation.

Acceptance: Attempt inference by subtracting totals and by repeated narrow filters; verify the agreed disclosure policy across charts, tables, API responses and downloads.

BR-ACC-010   Partner limited collaboration   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-010.

Partners shall see only explicitly shared definitions, their assigned work and permitted joint artifacts. Comments, task lists, participant lookup and completion statistics shall follow the same boundary. A funder role shall not automatically expose all implementing partner data.

Acceptance: A partner searches for another partner’s record and opens a guessed report URL; both paths remain restricted.

BR-ACC-011   Access changes and existing artifacts   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-011.

Permission changes shall propagate to cached views, generated artifacts, search and AI retrieval within the defined revocation window. Shared conversation content and previously generated reports shall be rechecked on access. The platform shall state that already downloaded copies are outside remote revocation.

Acceptance: Remove access after content has been cached and generated, then reaccess through every supported channel and verify the new policy.

BR-ACC-012   Administrative review and simulation   P1 R2

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ACC-012.

Administrators shall preview the effects of role and sharing changes on representative users before applying them. Sensitive bulk changes shall show affected people, projects, external links and scheduled jobs and support independent approval.

Acceptance: Preview a proposed group expansion and identify newly exposed sensitive resources before any access is granted.

## 10 Strategy and results frameworks

Business owner: MEL lead. The framework describes intended change; a connection in a theory of change is a hypothesis or stated relationship, not evidence that causation has been established.

BR-PLN-001   Results hierarchy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-001.

Users shall model goals, impacts, outcomes, outputs and activities with configurable labels and depth. Nodes shall have descriptions, owners, timing, assumptions and evidence needs. The platform shall support a tabular logframe and an accessible relationship view of the same approved structure.

Acceptance: Edit one representation and verify consistent content in the other without losing identifiers or historical versions.

BR-PLN-002   Theory of change relationships   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-002.

Users shall define directional relationships, assumptions, external factors and evidence strength between framework nodes. Alternative pathways and cross programme links shall be supported. Framework relationships shall not automatically become numeric aggregation relationships.

Acceptance: Link two outcomes to a shared impact and confirm that no results are double counted or aggregated without a separately approved calculation rule.

BR-PLN-003   Framework baselines   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-003.

Frameworks shall move through draft, review and approved baseline states. Changes shall show additions, removals and affected indicators, activities, reports and commitments. Earlier approved baselines shall remain available for comparison.

Acceptance: Revise an outcome midyear and reproduce the first quarter report against its original framework version.

BR-PLN-004   Reusable libraries   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-004.

Organisations shall maintain governed libraries of frameworks, indicators, instruments and reporting templates with owner, version, applicability and review date. Copying a template shall establish whether future updates are linked or independently managed.

Acceptance: Update a library indicator and show which projects may adopt it, without silently changing existing approved definitions.

BR-PLN-005   Standard mappings   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-005.

Users shall map their own framework nodes and indicators to SDGs, donor frameworks and sector taxonomies with source version and rationale. Many to many mappings shall not imply equivalence or additive measurement.

Acceptance: Map a local indicator to two standards, retain both references and avoid counting its achievement twice in portfolio totals.

BR-PLN-006   Measurement plan   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-006.

Each indicator shall identify collection method, evidence source, reporting frequency, accountable collector, reviewer, expected coverage and data quality checks. The platform shall expose missing planning elements before programme activation.

Acceptance: Attempt activation with missing mandatory measurement fields and identify exact remediation tasks and responsible owners.

BR-PLN-007   Assumptions and context   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-007.

Users shall maintain assumptions, dependencies and contextual factors with evidence, review dates and status. Changes shall link to affected outcomes and management responses. Qualitative context shall be available alongside numeric performance.

Acceptance: Mark a critical assumption invalid and identify the affected framework nodes, owner and review actions without altering historical results.

BR-PLN-008   Planning scenarios   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-008.

Users shall compare alternative targets, budgets, delivery plans and assumptions in clearly labelled scenarios. Scenarios shall not change approved baselines or official results until an authorised adoption workflow completes.

Acceptance: Compare two funding scenarios, export assumptions and promote one only after approval while preserving the original baseline.

BR-PLN-009   Document assisted setup   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-009.

Users shall create a programme manually, from a template or through AI assisted extraction from documents. Extracted fields shall retain source references and unresolved ambiguities. The same validation and approval rules shall apply to all three paths.

Acceptance: Import a proposal with inconsistent dates and ambiguous targets; the draft flags the issues and cannot silently invent missing commitments.

BR-PLN-010   Framework completeness review   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PLN-010.

The system shall provide a review of unmeasured outcomes, orphan indicators, missing owners, unsupported assumptions and incompatible reporting commitments. Reviewers may accept a documented exception where business policy permits.

Acceptance: A framework with an output lacking any measure is visibly flagged, assigned and resolved or explicitly accepted before baseline approval.

## 11 Programme and delivery management

Business owner: Programme management lead. This module coordinates delivery context and reporting; it does not replace a complete enterprise resource planning system.

BR-PRG-001   Programme and project registry   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-001.

Users shall maintain projects and programmes with identifiers, dates, sectors, geographies, partners, owners, status, funding references and reporting obligations. Relationships may support multiple portfolio views under controlled aggregation rules.

Acceptance: Create, find, filter, archive and reopen a project while preserving indicators, evidence and historical portfolio membership.

BR-PRG-002   Activities and milestones   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-002.

Managers shall create activities, deliverables, milestones, dependencies, assignees, due dates and completion evidence and link them to framework nodes. Completion status shall distinguish planned, underway, blocked, completed and cancelled work.

Acceptance: Delay a prerequisite and show affected milestones, accountable owners and reporting implications without automatically changing actual outcome values.

BR-PRG-003   Workplans and calendars   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-003.

Users shall view workplans and reporting calendars by project, person, partner and period. Recurring tasks shall respect local time zones, working calendars and changed programme dates. Rescheduling shall retain prior deadlines and reasons.

Acceptance: Shift a programme end date and preview dependent reporting tasks, while locked period deadlines remain part of historical records.

BR-PRG-004   Risks issues and dependencies   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-004.

Managers shall maintain risk and issue registers with likelihood, impact, owner, mitigation, review date and escalation. Links to indicators, activities and evidence shall make consequences visible. Automated flags shall remain distinguishable from confirmed issues.

Acceptance: Escalate an overdue high impact issue and preserve its full decision history and linked evidence.

BR-PRG-005   Geography and sites   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-005.

Projects shall support hierarchical geographies, named sites and optional coordinates with boundary source and version. Sensitive locations shall be generalised or hidden according to policy. Geographic changes shall not reclassify past results without an explicit rule.

Acceptance: Update a district boundary and retain reproducibility of reports based on the earlier boundary version.

BR-PRG-006   Partner responsibilities   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-006.

Managers shall assign partners to activities, indicators, collection rounds and reporting obligations with acceptance, due dates and scoped access. Partners shall see their responsibilities and receive actionable feedback on rejected submissions.

Acceptance: Transfer an indicator’s reporting responsibility and preserve the prior partner’s approved submissions without granting the new partner unrelated access.

BR-PRG-007   Programme change control   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-007.

Changes to scope, dates, responsible partners or contractual targets shall record rationale, approval and effects on plans, budgets and reports. The platform shall distinguish a proposed amendment from an effective amendment.

Acceptance: Review and approve a scope change with affected objects listed; historical outputs remain attached to the applicable agreement version.

BR-PRG-008   Closure and archival   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-008.

Project closure shall check outstanding submissions, approvals, deliverables, data quality issues and retention duties. Closure shall restrict normal editing while allowing authorised audit and correction procedures. Reopening requires reason and approval.

Acceptance: Close a project with an unresolved issue, enforce the configured block or documented exception, and preserve export and audit access.

BR-PRG-009   Cross project dependencies   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-009.

Managers shall link dependencies across authorised projects while controlling what each project can see. A shared dependency may expose an approved status summary without exposing confidential operational records.

Acceptance: A partner sees the published status of a shared prerequisite but cannot retrieve the originating project’s restricted budget or records.

BR-PRG-010   Bulk administration   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRG-010.

Authorised users shall bulk assign owners, update permitted metadata and apply templates with preview, validation, per item outcomes and recoverable failures. Bulk actions shall obey the same approvals and audit rules as individual changes.

Acceptance: Process a mixed valid and invalid batch, display exact results and prevent a retry from duplicating successful changes.

## 12 Indicator definitions targets and periods

Business owner: MEL lead. An indicator definition is a governed measurement contract. A label such as “people reached” is insufficient without population, period, unit, counting rule and source.

BR-IND-001   Complete indicator definition   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-001.

Each indicator shall record name, code, definition, type, unit, population, inclusion and exclusion rules, frequency, source, method, owner, limitations and approved calculation. Conditional fields such as numerator, denominator and direction of improvement shall be mandatory where relevant.

Acceptance: A percentage indicator without denominator meaning or period cannot become an approved production definition.

BR-IND-002   Supported measurement types   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-002.

The system shall support counts, decimals, percentages, ratios, rates, currency, ordinal scales, binary milestones, qualitative assessments and externally calculated composite scores. Each type shall declare valid operations and display precision.

Acceptance: Configure representative indicators of every type and block invalid operations such as summing ordinal labels or treating an unbounded rate as a percentage.

BR-IND-003   Baselines and targets   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-003.

Indicators shall support dated baselines, periodic targets, cumulative targets, end targets, ranges and disaggregated targets. Target type and direction shall be explicit. Actuals above a target shall not be silently capped at 100 percent.

Acceptance: Display a lower is better indicator, a range target and an overachieved count correctly, including the formula used for progress status.

BR-IND-004   Target amendments   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-004.

Target changes shall be proposed, approved and effective dated with rationale and prior values retained. Reporting shall allow comparison against original and revised targets with clear labels. Historic performance shall not improve silently because a target was lowered.

Acceptance: Revise a target after a period closes and reproduce both the original performance report and an explicitly restated comparison.

BR-IND-005   Reporting periods   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-005.

The platform shall support calendar and fiscal months, quarters, years and custom intervals with defined time zones and boundaries. Event dates and period assignment rules shall handle late entry, overlapping intervals and changed calendars explicitly.

Acceptance: Assign records around midnight and fiscal year boundaries and prove each is included in the intended period exactly as defined.

BR-IND-006   Disaggregation dimensions   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-006.

Indicators shall support controlled breakdowns such as gender, age, disability, geography, partner and cohort with versioned categories. Dimensions shall identify whether categories are exclusive, exhaustive or overlapping. Unknown and declined responses shall be representable.

Acceptance: A multiselect category does not falsely reconcile to a unique person total; category changes preserve historical values and labels.

BR-IND-007   Missing and exceptional values   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-007.

Zero, missing, not applicable, not collected, suppressed, invalid and pending approval shall be distinct states. Each state shall have defined aggregation, display and completeness behaviour. A missing value shall never default to zero without an approved explicit transformation.

Acceptance: A dashboard and export show all states consistently, with a correct denominator for completeness and no false performance total.

BR-IND-008   Definition versioning   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-008.

Changes to units, population, methods, denominators or classification shall create a material definition version. The system shall flag breaks in comparability and require approval before aggregating across versions.

Acceptance: Change a definition from households to individuals and confirm that earlier data cannot be treated as a continuous series without an approved conversion and disclosure.

BR-IND-009   Indicator library reuse   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-009.

Projects shall instantiate governed indicators with local context while preserving the parent definition version. Permitted local overrides and prohibited changes shall be explicit. Updates shall offer impact review and selective adoption.

Acceptance: Two projects share a standard indicator; one adopts a revision and the portfolio identifies their changed comparability.

BR-IND-010   Manual and calculated results   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-010.

An indicator shall declare whether actuals are entered, imported, calculated or aggregated. Changing the method shall require review. Manual overrides of calculated values shall preserve the calculated value, reason, approver and affected period.

Acceptance: Override an actual, display both values with the override status and reproduce the official report using the approved choice.

BR-IND-011   Evidence requirements   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-011.

Indicators shall specify required evidence types, acceptable sources and minimum approval conditions. Evidence may be attached or linked but must have provenance and access rules. A broken external link shall not silently satisfy evidence requirements.

Acceptance: Submit an achievement lacking required evidence and confirm that approval is blocked or follows an explicitly permitted exception process.

BR-IND-012   Responsibility and collection schedule   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-012.

Each active indicator shall have accountable collection and review roles, reporting dates and escalation policy. Changes in staff or partners shall not leave an active reporting obligation unowned.

Acceptance: Revoke the collector’s membership and show the resulting reassignment task and overdue risk to the responsible manager.

BR-IND-013   Status and thresholds   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-013.

Performance status shall use explicit thresholds, direction, period and completeness rules. Status may be quantitative or reviewed qualitative assessment. Missing or stale data shall not appear as successful performance.

Acceptance: Configure an indicator whose lower value is better and verify that stale results are labelled separately from its red amber green assessment.

BR-IND-014   Retirement and replacement   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-014.

Users shall retire indicators without erasing their data and identify replacements, effective dates and continuity rules. Reports shall distinguish retired, inactive and active measures. Dependencies shall be shown before retirement.

Acceptance: Retire an indicator used by a dashboard and an aggregate; identify and resolve future dependencies while retaining earlier publications.

BR-IND-015   Reference sheets and dictionary export   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-IND-015.

The platform shall generate indicator reference sheets and machine readable dictionaries containing definition versions, units, methods, dimensions, periods and ownership. Exports shall preserve semantic meaning rather than provide numbers without context.

Acceptance: An evaluator reconstructs the meaning of an exported indicator without relying on undocumented application settings.

## 13 Calculation aggregation and reconciliation

Business owner: MEL lead with data engineering. This module is a release critical capability. The FSD shall define an approved calculation catalogue and golden test corpus before implementation.

BR-CAL-001   Deterministic calculation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-001.

All official numeric results shall use approved, versioned deterministic rules. Inputs, rule version, filters, periods, dimensions and rounding shall be recoverable. AI may propose a rule but shall not independently supply the official arithmetic result.

Acceptance: Recompute a frozen result independently from its source snapshot and obtain the same value at the defined precision.

BR-CAL-002   Type and unit compatibility   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-002.

Calculations shall validate units, types, population definitions, reporting periods and dimension compatibility. Incompatible inputs shall be blocked or transformed through an approved conversion with provenance.

Acceptance: Attempt to combine hectares with acres and people with households; require the appropriate governed conversion or reject the operation.

BR-CAL-003   Ratios rates and percentages   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-003.

Aggregation shall preserve numerators, denominators, multipliers and eligibility rules. Pooled ratios shall be recomputed from compatible component quantities. Unweighted averaging shall be available only when explicitly defined and labelled as the intended statistic.

Acceptance: Combine 50 of 100 with 1 of 10 and obtain 51 of 110, or 46.3636 percent before display rounding, rather than 30 percent.

BR-CAL-004   Population overlap   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-004.

Unique reach shall use an approved deduplication scope and reliable identifiers where available. Without sufficient evidence, the system shall report contact or gross reach and clearly state overlap uncertainty. It shall not invent unique counts from aggregate partner totals.

Acceptance: Two sets of 100 people with 20 known shared identities yield 180 unique people; unknown overlap is labelled rather than assumed absent.

BR-CAL-005   Time aggregation semantics   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-005.

Each indicator shall define whether values are period flows, cumulative totals, snapshots or events. Summation, latest eligible value and cumulative difference shall follow that definition. Summing monthly cumulative totals shall be blocked unless intentionally defined.

Acceptance: Cumulative values of 10, 15 and 20 produce an end position of 20; stock and event indicators follow their separately approved rules.

BR-CAL-006   Hierarchical aggregation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-006.

The platform shall support at least ten reporting levels and governed cross hierarchy links. It shall prevent cycles and detect when the same contributing result reaches an aggregate through multiple paths. Each edge shall have an explicit combination rule.

Acceptance: A diamond shaped dependency does not double count a shared source; a circular dependency is rejected with a clear explanation.

BR-CAL-007   Dimension alignment   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-007.

Aggregation shall map categories through approved, versioned crosswalks. It shall distinguish unmapped, unknown and suppressed categories. Different age bands or geographic classifications shall not be merged by similar labels alone.

Acceptance: Partners using ages 0 to 14 and 0 to 17 cannot be combined into one exact age group without compatible underlying data.

BR-CAL-008   Missingness and coverage   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-008.

Results shall state expected and received contributors, approval coverage and missingness. Partial totals shall be labelled. Completeness denominators shall reflect the active reporting obligations for the period rather than current project membership alone.

Acceptance: A portfolio with three of five required submissions shows a partial result and 60 percent submission coverage with the missing contributors identifiable to authorised users.

BR-CAL-009   Precision and rounding   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-009.

The platform shall retain adequate numeric precision, apply explicit rounding and separate calculation precision from display precision. Currency and large counts shall avoid silent truncation. Exports shall declare whether values are raw or display rounded.

Acceptance: Aggregate many fractional values before rounding and reconcile the official total with an independent calculation and the declared rounding policy.

BR-CAL-010   Zero denominators and invalid inputs   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-010.

Undefined ratios, nonfinite values, invalid dates and impossible quantities shall produce explicit validation states. Policies for negative values, adjustments and out of range percentages shall depend on indicator meaning.

Acceptance: A zero denominator produces an undefined status, not zero or success; an approved negative correction is handled without allowing an impossible participant count.

BR-CAL-011   Corrections and recalculation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-011.

Source corrections shall identify affected indicators, aggregates, dashboards and unpublished reports. Recalculation shall preserve earlier result versions and expose processing status. Locked publications shall remain unchanged until an approved restatement.

Acceptance: Correct one source record and trace all affected outputs; repeat processing without duplicate effects and preserve the original published snapshot.

BR-CAL-012   Formula authoring and validation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-012.

Authorised users shall configure supported functions, filters and derived measures with validation, sample previews and dependency inspection. Formula execution shall be constrained and shall not provide arbitrary code execution or unrestricted data access.

Acceptance: Reject circular references, invalid functions, unauthorised fields and malicious expressions before activation.

BR-CAL-013   Weighted and composite indicators   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-013.

Composite scores shall specify component eligibility, weights, normalisation, missing component treatment and interpretation. Weighted statistics shall retain their weighting basis. Changes to weights shall be versioned and sensitivity visible.

Acceptance: Reproduce a composite score from its components and show how an approved weight change affects the result without changing the historical version.

BR-CAL-014   Cross portfolio attribution   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-014.

A project may belong to multiple portfolio views, but summing those views shall follow explicit attribution or deduplication rules. Funding shares and implementation responsibility shall not automatically imply fractional impact ownership.

Acceptance: A project in two thematic portfolios appears in both views but is counted once in an organisation wide unique project total.

BR-CAL-015   Reconciliation and explainability   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-015.

Users shall inspect calculation steps, included and excluded source counts, adjustments, approval state and differences from earlier runs. Comparison tools shall distinguish source change, rule change, period change and access related differences.

Acceptance: A reviewer explains every difference between two period report versions using the recorded reconciliation evidence.

BR-CAL-016   Statistical interpretation   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-CAL-016.

Analyses shall declare aggregation method, sample basis, weighting, uncertainty and comparability limits. Summary statistics such as medians shall be recomputed from adequate inputs; a median of subgroup medians shall not be misrepresented as a pooled median.

Acceptance: An attempted pooled estimate with insufficient underlying data is blocked or explicitly labelled as a different statistic with its limitation.

## 14 Forms surveys and collection rounds

Business owner: Field operations and MEL leads. Forms are governed instruments whose version and collection context remain attached to every submission.

BR-FRM-001   Form builder   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-001.

Authorised users shall build forms with text, numeric, date, time, single and multiple choice, ranking, calculated, identifier, location, attachment and consent fields. Groups and repeat groups shall support household members, visits and repeated observations. Field sensitivity and export policy shall be configurable.

Acceptance: Build and submit a repeated household survey with validation, calculations and restricted fields through desktop and mobile workflows.

BR-FRM-002   Conditional logic and validation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-002.

Forms shall support relevance rules, skip logic, required conditions, ranges, cross field checks and context dependent choices. Hidden fields shall follow an explicit clear or retain rule. Critical validation shall also run on the server.

Acceptance: Change an earlier answer, verify downstream field treatment, and reject a tampered submission that bypasses client validation.

BR-FRM-003   Form lifecycle and compatibility   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-003.

Forms shall support draft, test, review, publish, supersede and retire states. Published versions shall remain identifiable. Policy shall determine whether older offline versions are accepted, quarantined or rejected after a change.

Acceptance: Submit an older downloaded form after a required field changes and show the correct version aware treatment without silently applying new semantics.

BR-FRM-004   Multilingual instruments   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-004.

Forms shall support translated labels, instructions and choices while preserving stable codes. Missing translations shall be visible. Approved translations shall be versioned and distinct from unreviewed machine translations.

Acceptance: Collect the same instrument in two languages and aggregate responses by stable codes, preserving the language used during collection.

BR-FRM-005   Collection rounds and assignments   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-005.

Supervisors shall define round dates, eligible population, sites, enumerators, assignments and expected submissions. Reassignment, replacement samples and callbacks shall be traceable. Assigned work shall expose only the necessary participant fields.

Acceptance: Reassign a pending household visit without duplicating the expected sample or exposing the rest of the project’s participant registry.

BR-FRM-006   Save resume and correction   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-006.

Collectors shall save drafts, resume interrupted forms and correct returned submissions. The interface shall clearly distinguish local save, server receipt and approval. Final submission shall prevent accidental duplicate clicks and preserve revision history.

Acceptance: Interrupt a form, resume it and submit twice; one intended submission is recorded with an unambiguous status.

BR-FRM-007   Media and location evidence   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-007.

Forms may capture images, audio, files and location when permitted and necessary. Consent, metadata removal, file limits, content scanning and access controls shall apply. GPS refusal or unavailability shall have a clear policy outcome.

Acceptance: Collect without optional GPS, reject prohibited media and confirm that an exported image does not expose disallowed embedded location metadata.

BR-FRM-008   Respondent and public forms   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-008.

Where self completion is enabled, public or token based forms shall restrict data lookup, prevent submission abuse and support notice and consent. Tokens shall have controlled expiry and reuse rules. A respondent shall not access other responses.

Acceptance: Guess or replay a response token and attempt enumeration; verify the defined restrictions and safe submission acknowledgement.

BR-FRM-009   Longitudinal and repeat visits   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-009.

The platform shall link repeated observations to the appropriate participant, institution or site, with event type, visit date, collection round and cohort. Previous values may be shown only when authorised and methodologically appropriate.

Acceptance: Record baseline and follow up visits, preserve each original observation and distinguish missing follow up from a zero outcome.

BR-FRM-010   Instrument testing and reuse   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FRM-010.

Users shall preview forms under representative conditions, inspect logic paths and test translations before publication. Test submissions shall be isolated. Form libraries shall support copying and governed reuse of questions and response sets.

Acceptance: Exercise alternative skip paths and a test import and confirm no test response contributes to production indicators.

## 15 Offline and field operation

Business owner: Field operations and security leads. Offline access introduces a period during which central revocation cannot reach a disconnected device. The product must make that limit explicit and minimise local data.

BR-OFF-001   Offline task packages   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-001.

Assigned collectors shall download an authorised, time limited package of forms, reference lists and minimal work assignments. The package shall state its version, last sync time and expiry. Downloading all programme records by default is prohibited.

Acceptance: Complete an assigned form without connectivity and verify that unrelated participants and projects are unavailable locally.

BR-OFF-002   Durable local capture   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-002.

The field client shall preserve saved drafts and submissions across application restart and ordinary device interruption within the supported device profile. It shall warn about storage exhaustion and unuploaded records. A server sync acknowledgement shall be distinct from a local save acknowledgement.

Acceptance: Restart during collection and sync, recover saved work and show which records still require server receipt.

BR-OFF-003   Idempotent synchronisation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-003.

The platform shall safely retry interrupted uploads using stable submission identity. Media may resume independently, but a record shall not appear complete before required evidence is received and validated.

Acceptance: Repeatedly interrupt and retry a batch; every intended record appears once, with incomplete media explicitly flagged.

BR-OFF-004   Conflict handling   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-004.

Concurrent edits, reassigned tasks, duplicate participant records and incompatible form versions shall produce explicit conflicts. The platform shall preserve competing versions for authorised resolution rather than silently accepting the last device write.

Acceptance: Two devices edit the same record offline; a reviewer can identify both versions, resolve the conflict and inspect the resulting history.

BR-OFF-005   Device protection and expiry   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-005.

Offline data shall be protected at rest with controlled unlock and automatic expiry. Sensitive offline packages shall require an approved managed device posture. Revocation shall be enforced on reconnect; remote wipe shall be best effort and never presented as guaranteed for an offline device.

Acceptance: Expire a package, revoke a user during disconnection and verify local access bounds and server rejection or quarantine on reconnect.

BR-OFF-006   Shared device operation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-006.

Shared devices shall separate user workspaces and avoid exposing previous users’ forms or participants. Logout shall handle unsynchronised work explicitly, with secure handover or a clear risk warning. Common credentials shall not replace individual attribution.

Acceptance: Switch collectors with unsynced records and confirm that each record retains its real author and permitted local visibility.

BR-OFF-007   Sync and quality supervisor view   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-007.

Supervisors shall see expected devices or collectors, latest contact, pending submissions where known, conflicts and expired packages. Unknown offline progress shall not be represented as zero completed work.

Acceptance: A disconnected device is shown as stale or unknown, with a follow up action and no fabricated current record count.

BR-OFF-008   Constrained connectivity   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OFF-008.

Collection shall minimise mandatory network traffic, support manual sync and avoid downloading large media without clear user control. Network failure shall not erase drafts. Language packs and reference data shall be available before field work.

Acceptance: Complete the constrained network and offline scenarios in section 32, including text first submission and later permitted media upload.

## 16 Data import management and transformation

Business owner: Data steward. Raw evidence, curated data and approved indicator results shall remain distinct, linked layers of business information.

BR-DAT-001   File ingestion   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-001.

Users shall import CSV and XLSX with explicit sheet, encoding, delimiter, header, date, locale and identifier mapping. Leading zeros, large identifiers and text that resembles a date shall not be silently corrupted.

Acceptance: Import a fixture containing mixed date formats, quoted delimiters, long IDs and leading zeros and show the exact interpreted values before commitment.

BR-DAT-002   Mapping and preview   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-002.

Import mappings shall be reusable, versioned and source specific. The preview shall show required fields, type conversions, unmapped columns, units, rejected rows and proposed updates. AI suggestions shall require the same explicit review as manual mappings.

Acceptance: A changed source column is detected and does not silently populate a different field or publish an incorrect result.

BR-DAT-003   Import mode and identity   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-003.

Every load shall explicitly choose append, keyed update, controlled replacement or another approved mode with stable source identifiers. Updates shall preserve revision history. Replacement shall show deletion and downstream impact before execution.

Acceptance: Reimport an identical file without duplicate achievements; import a correction and identify the updated record and changed result.

BR-DAT-004   Validation and quarantine   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-004.

Loads shall separate received, accepted, rejected, duplicate and quarantined records. Partial acceptance shall be an explicit policy and provide row level outcomes. Failed batches shall be recoverable without hiding partially applied changes.

Acceptance: Reconcile input rows with all outcome categories and retry only failed items without duplicating accepted rows.

BR-DAT-005   Immutable raw source   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-005.

The platform shall retain source file or payload identity, receipt time, source owner and original values according to retention policy. Transformations shall not overwrite raw evidence. Restricted sources shall retain protection in derived tables and previews.

Acceptance: Trace an approved result through a transformation back to the permitted original source and its exact import run.

BR-DAT-006   Governed transformations   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-006.

Users shall clean, recode, derive, filter, join and reshape data through approved operations with versioned rules and preview. Join cardinality, unmatched keys and row multiplication shall be visible. Destructive transformations require impact review.

Acceptance: Join one participant to multiple visits and show the multiplication risk before any unique reach calculation is approved.

BR-DAT-007   Schema drift   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-007.

The platform shall detect added, removed, renamed and type changed fields from recurring sources. Material changes shall pause affected processing or require a reviewed mapping revision. Previously valid loads shall remain reproducible.

Acceptance: A connector changes a numeric column to text and the affected indicator shows a source issue instead of silently using zero.

BR-DAT-008   Data catalogue and lineage   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-008.

Users shall discover authorised datasets by owner, purpose, source, sensitivity, coverage, refresh time and quality. Lineage shall show source to transformation to indicator to report relationships and impacted downstream objects.

Acceptance: Select a failing dataset and identify all affected active reports without revealing unrelated restricted catalogue entries.

BR-DAT-009   Data editing and amendments   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-009.

Authorised corrections shall capture old and new values where lawful, reason, actor and approval. Bulk edits shall provide preview and item results. Approved data changes shall trigger recalculation and reporting controls.

Acceptance: Correct a wrong unit after approval and preserve both the amendment decision and the prior reported result.

BR-DAT-010   Refresh scheduling and freshness   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-010.

Sources shall have expected refresh cadence, last successful run, next attempt and responsible owner. Stale or failed sources shall be visible wherever their results are used. Successful receipt is not equivalent to completed validation or approval.

Acceptance: Pause a scheduled source and show a stale data label in every dependent dashboard and generated report.

BR-DAT-011   Data exports and portability   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-011.

Authorised users shall export selected or complete datasets with stable identifiers, dictionary, units, codes, source and version metadata in documented formats. Spreadsheet exports shall neutralise formula injection without changing the represented source value silently.

Acceptance: Open an export containing malicious formula like text safely and use the dictionary to interpret each field correctly.

BR-DAT-012   Data retention and dependency review   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DAT-012.

Archiving or deleting a dataset shall show affected reports, indicators, AI indexes and evidence relationships and enforce the retention policy. Permitted retained snapshots shall be distinguishable from live data. Deletion shall not leave readable orphan copies.

Acceptance: Delete an eligible source dataset and verify the prescribed handling of dependent artifacts and indexes with a recorded lifecycle result.

## 17 Data quality and completeness

Business owner: MEL lead and data steward. Rule outcomes, review status and statistical uncertainty are different concepts and shall not be collapsed into one unexplained quality score.

BR-DQ-001   Quality rule catalogue   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-001.

Users shall configure requiredness, uniqueness, range, referential integrity, cross field consistency, temporal logic and source reconciliation checks with severity and scope. Rules shall have owners, versions and effective dates.

Acceptance: Apply representative rules at field, record, dataset and indicator levels and identify the exact rule version causing each failure.

BR-DQ-002   Blocking and warning behaviour   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-002.

Rules shall distinguish blocking errors, review required warnings and informational observations. Exceptions shall require authorised rationale and expiry where applicable. A reviewer shall not resolve an error merely by dismissing its notification.

Acceptance: Attempt to approve a blocking invalid record, then resolve or validly except it with an attributable decision.

BR-DQ-003   Duplicate detection   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-003.

The platform shall detect exact and suspected duplicates under a declared scope. Fuzzy matches shall be reviewable candidates, not automatic identity facts. Merging shall preserve source lineage, permissions and a reversal or correction path.

Acceptance: Two people with the same name remain separate unless sufficient authorised evidence supports a reviewed merge.

BR-DQ-004   Reconciliation checks   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-004.

Checks shall compare compatible totals, components, expected submissions and external control totals. The system shall account for overlapping categories and missing dimensions rather than assuming every breakdown must sum to the headline.

Acceptance: A mutually exclusive breakdown reconciles; a multiselect breakdown is labelled nonadditive and evaluated under its own rule.

BR-DQ-005   Quality issue workflow   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-005.

Quality issues shall have owner, severity, affected objects, evidence, due date and resolution history. Returned data shall preserve the issue context. Escalation shall make unresolved impact visible to reporting owners.

Acceptance: Trace an import error through assignment, correction, revalidation and closure, including its effect on a delayed reporting period.

BR-DQ-006   Completeness and timeliness   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-006.

Dashboards shall distinguish expected, received, valid, approved and late submissions by period and responsible party. Revised obligations shall have effective dates. Quality percentages shall show their numerator and denominator.

Acceptance: An inactive partner is excluded only for periods after its obligation ends, preserving earlier missing submissions.

BR-DQ-007   Anomaly assistance   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-007.

Statistical and AI checks may flag unusual values, abrupt changes and inconsistent narratives with explanations and relevant context. Flags shall not alter source records or imply confirmed fraud. Reviewers shall provide feedback and monitor false positives.

Acceptance: A legitimate seasonal spike can be retained with rationale, and the flag history remains available for model evaluation.

BR-DQ-008   Quality disclosure   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-DQ-008.

Reports and dashboards shall expose material missingness, stale sources, unresolved issues and approved exceptions alongside affected results. Users shall not remove required disclosures merely through visual customisation.

Acceptance: Export a report with incomplete coverage and verify that the same material caveat is retained in the final artifact.

## 18 Participants institutions and programme records

Business owner: Programme lead and privacy officer. Participant level collection is optional and must be justified by purpose; programmes shall be able to operate on aggregate data alone.

BR-PAR-001   Optional registries   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-001.

The product shall support participant, household, group, institution, facility and site records with configurable relationships and stable programme identifiers. It shall not mandate national identity numbers or biometric identifiers for ordinary monitoring.

Acceptance: Configure both an aggregate only programme and a participant based programme without unnecessary personal fields in the former.

BR-PAR-002   Purpose limited identity   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-002.

Personal identifiers shall be separated in visibility from analytical attributes. Pseudonymous identifiers shall support longitudinal analysis within approved scope. Matching across projects or tenants shall require a separately authorised purpose and process.

Acceptance: An analyst links follow up outcomes without seeing names, and cannot use the identifier to search an unrelated programme.

BR-PAR-003   Notice consent and lawful handling   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-003.

Records shall capture the applicable data collection notice, lawful handling basis selected by the tenant, consent where required, language, scope, timestamp and withdrawal or restriction. Consent shall not be assumed to be the only valid basis or a universal permission for reuse.

Acceptance: Restrict a participant’s optional media use and prevent their image from entering a report while retaining other legitimately permitted programme records.

BR-PAR-004   Service and participation events   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-004.

The platform shall record enrolment, attendance, referrals, service events, completion and exit with dates and evidence. Event counts and unique participant counts shall remain distinct. Corrections and duplicate events shall be traceable.

Acceptance: Three visits by one participant count as three eligible service events and one person where that is the approved definition.

BR-PAR-005   Household and group membership   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-005.

Membership relationships shall be effective dated, permit changes over time and distinguish heads, guardians and other roles where needed. Changes shall not rewrite household composition used by earlier surveys.

Acceptance: A person moves between households and each survey retains the correct household relationship at the time of observation.

BR-PAR-006   Cohorts and follow up   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-006.

Users shall define cohorts, eligibility rules, observation windows and follow up status. Loss to follow up, withdrawal, death and ineligibility shall be separately coded where appropriate and handled under approved analysis rules.

Acceptance: Generate a cohort outcome with transparent denominator changes and no automatic treatment of missing participants as successful outcomes.

BR-PAR-007   Safeguarding and vulnerable people   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-007.

Programmes involving children or other vulnerable groups shall configure stricter visibility, guardian or consent rules where applicable, safe contact methods and restricted evidence. Safeguarding incidents shall route to a separate authorised channel with minimal disclosure.

Acceptance: A sensitive concern is visible only to assigned safeguarding personnel, while ordinary programme users see an appropriate restricted status.

BR-PAR-008   Participant requests and corrections   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PAR-008.

Authorised staff shall locate and correct participant records through verified workflows, including merge review, restriction and privacy requests. Identity verification shall avoid exposing another person’s participation or allowing arbitrary public lookup.

Acceptance: Resolve a mistaken identity case with corrected downstream records and a history that preserves accountability without retaining disallowed personal data.

## 19 Evidence documents and qualitative analysis

Business owner: MEL and evaluation leads with privacy oversight.

BR-EVD-001   Evidence repository   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-001.

Users shall attach or reference documents, spreadsheets, images, recordings, transcripts and external sources with owner, type, date, source, sensitivity, version and retention. Evidence shall link to projects, results, decisions and findings.

Acceptance: Locate the approved evidence for a published claim, distinguish newer versions and enforce the evidence object’s own permissions.

BR-EVD-002   Evidence verification and provenance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-002.

Evidence shall show origin, submitter, receipt time, integrity identity and verification status. A file’s presence shall not imply authenticity. Users shall record limitations, provenance concerns and review decisions.

Acceptance: Flag disputed evidence, identify affected claims and prevent unqualified publication where the evidence is mandatory.

BR-EVD-003   Search and knowledge retrieval   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-003.

Users shall search permitted document content and metadata with filters and source version references. Text extraction and indexing shall follow sensitivity, deletion and AI policies. Unsupported formats shall have an explicit status.

Acceptance: A restricted document never appears in another user’s result count, snippet, suggested query or AI citation.

BR-EVD-004   Document versioning and annotations   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-004.

Evidence revisions, comments and annotations shall retain author and location context. Citations shall identify the actual source version and relevant page, section or record where available. Replacing a file shall not silently change a published citation.

Acceptance: Upload a revised evaluation report and preserve the meaning of citations in a previously published donor report.

BR-EVD-005   Qualitative coding   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-005.

Analysts shall maintain codebooks, code excerpts, attach memos and compare themes across authorised sources. Codes shall have definitions and versions. Multiple coders and adjudication shall be supported without overwriting independent coding.

Acceptance: Two analysts code the same transcript, review disagreement and preserve both original decisions and the adjudicated result.

BR-EVD-006   Transcription and translation   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-006.

Where enabled, transcription and translation shall preserve the original, identify automated output and support correction. Language, timestamps and speaker attribution shall be captured when reliable. Sensitive recordings shall only use approved processing destinations.

Acceptance: Correct a transcript segment and trace its translated quotation back to the original recording location with appropriate access.

BR-EVD-007   Quotations and disclosure   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-007.

Using participant quotations, images or stories in external materials shall require the applicable consent and disclosure checks. Redacted versions shall be separate artifacts with traceable provenance; redaction must remove recoverable hidden content.

Acceptance: Produce an external case story with approved quotation use and verify that source identifiers and hidden document text are not exposed.

BR-EVD-008   Findings and triangulation   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVD-008.

Users shall record findings linked to supporting and contradictory evidence, methods, confidence rationale and limitations. Evidence strength shall be a reviewed assessment, not an unexplained AI confidence percentage.

Acceptance: A finding with contradictory interview and survey evidence retains both, with a reviewer’s documented interpretation.

## 20 Evaluation learning and management response

Business owner: Evaluation lead. The platform organises evaluation work and evidence; methodological validity remains subject to qualified review.

BR-EVA-001   Evaluation registry   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-001.

Users shall register evaluation purpose, questions, scope, design, timing, evaluator independence, stakeholders, ethics requirements, budget and deliverables. Evaluations shall link to the applicable programme baseline and indicator versions.

Acceptance: Register baseline, midline and endline studies against one programme and distinguish their methods and evidence periods.

BR-EVA-002   Sampling and methodological metadata   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-002.

Evaluations shall retain sampling frame, inclusion criteria, assignment method, weighting, nonresponse treatment and analysis plan where applicable. Changes shall be versioned. Survey estimates shall not be presented as population counts without their method.

Acceptance: An exported study dataset includes enough metadata to understand the sample basis and stated limitations.

BR-EVA-003   Analysis packages   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-003.

Analysts shall create frozen, permission controlled analysis extracts with dictionary, source versions and analysis date. They may attach reviewed scripts, notebooks and results without allowing uncontrolled execution inside ordinary user workflows.

Acceptance: Reproduce a submitted evaluation result from its recorded extract and method without using subsequently changed live records.

BR-EVA-004   Causal claims and uncertainty   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-004.

Reports and AI outputs shall distinguish observed change, association, contribution and a supported causal claim. Estimates shall carry applicable uncertainty, method and limitations. The system shall not infer causation from a dashboard trend alone.

Acceptance: Ask AI why an outcome improved; it shall identify evidence limitations and avoid attributing the change to the intervention without support.

BR-EVA-005   Outcome harvesting and contribution   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-005.

Users shall record observed outcomes, significance, contribution claims, independent substantiation and stakeholder perspectives. Multiple organisations may contribute to the same outcome without implying exclusive ownership.

Acceptance: Review a shared outcome with separate contribution claims and publish an approved narrative that preserves attribution limits.

BR-EVA-006   Learning agenda   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-006.

Teams shall maintain learning questions, evidence gaps, planned inquiries and review dates linked to strategic decisions. Questions may evolve, but earlier conclusions and unresolved uncertainty shall remain visible.

Acceptance: Link a management decision to a learning question, its evidence and the unresolved assumptions requiring follow up.

BR-EVA-007   Management responses and actions   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-007.

Evaluation recommendations shall support accept, partially accept or reject responses with reason, accountable owner, due date and completion evidence. Overdue actions shall escalate. Closing an action shall not automatically prove improved outcomes.

Acceptance: Track a recommendation through response, action and subsequent review of outcome evidence.

BR-EVA-008   Institutional learning library   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-EVA-008.

Organisations shall reuse approved lessons, methods and evaluation findings with context, applicability, quality and review date. Cross tenant sharing shall require explicit licensing and disclosure approval.

Acceptance: Reuse a lesson in a new programme with a link to its source context while restricted interviews remain inaccessible.

## 21 Collaboration review and workflow

Business owner: Programme lead with MEL and security leads.

BR-WFL-001   Configurable approvals   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-001.

The platform shall support sequential and parallel reviews, thresholds, role based routing and required evidence for definitions, data, budgets and reports. A workflow version shall remain attached to each approval instance.

Acceptance: Change a workflow while reviews are underway and preserve an explicit migration or completion rule for the existing instances.

BR-WFL-002   Reviewer independence and authority   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-002.

Approval shall verify current authority, separation of duties and the exact object version. Approvers shall not approve an object changed after they opened it without reviewing the new version.

Acceptance: Edit a submission while a reviewer has it open; the old approval attempt is rejected or requires a fresh review.

BR-WFL-003   Return reject and resubmit   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-003.

Reviewers shall return work with actionable reasons, reject it where policy permits and review a subsequent revision with a clear comparison. Rejection shall not erase submitted evidence or prior decisions.

Acceptance: Follow two correction cycles and inspect each author, reason, changed field and approval state.

BR-WFL-004   Delegation escalation and absence   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-004.

Approvers may delegate within permitted scope and dates, preserving independence and attribution. Overdue work shall escalate. Departed reviewers shall not permanently block critical workflows or cause silent automatic approval.

Acceptance: A reviewer leaves during period close and the workflow reassigns to an eligible independent reviewer with audit evidence.

BR-WFL-005   Comments mentions and discussions   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-005.

Users shall discuss authorised objects, mention eligible collaborators and resolve threads. Comment visibility and notifications shall respect object and field restrictions. Editing or deleting comments shall leave appropriate history.

Acceptance: A mention cannot expose a restricted result in email or notification previews to a person lacking access.

BR-WFL-006   Task and notification centre   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-006.

Users shall see assigned work, overdue obligations, returned submissions and relevant alerts in one place. Notifications shall support preferences, digests and escalation while retaining mandatory security notices. Delivery failures shall be visible to authorised administrators.

Acceptance: An overdue collection task produces a controlled reminder and escalation without duplicate messages from job retries.

BR-WFL-007   Period close and lock   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-007.

Closing a period shall check completeness, approvals and unresolved exceptions before locking an official snapshot. Users shall see what is included and excluded. Locking shall prevent ordinary edits from changing reported values.

Acceptance: A late submission after lock remains outside the published snapshot until a controlled reopen or restatement completes.

BR-WFL-008   Reopen and restate   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-008.

Authorised users shall reopen or restate a period with reason, impact review and independent approval. The system shall retain original and revised versions and identify previously distributed artifacts needing correction notices.

Acceptance: Restate a quarter and trace its effect on year to date totals, reports and authorised recipient notifications.

BR-WFL-009   Automation rules   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-009.

Administrators shall configure bounded triggers, conditions and actions with preview, execution history, retries and cancellation. Rules shall prevent loops and unauthorised actions. High impact actions retain approval requirements.

Acceptance: A reminder rule can run automatically, but a rule cannot bypass report publication approval or repeatedly create the same task.

BR-WFL-010   Decisions and signoff   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-WFL-010.

Business signoff shall record identity, authority, object version, timestamp and decision. Where a legally recognised electronic signature is required, it shall be a separately qualified integration and claim rather than an implied property of a click.

Acceptance: Export a period approval history containing the exact approved versions and decision evidence without claiming unsupported legal signature status.

## 22 Analytics dashboards and exploration

Business owner: Portfolio and MEL leads. Every visual shall expose sufficient definition, time scope, freshness and quality context to avoid misleading interpretation.

BR-ANA-001   Dashboard authoring   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-001.

Users shall compose dashboards from authorised metrics, tables, trends, target comparisons, narrative and evidence references. Layouts shall work across supported screen sizes and remain understandable without colour alone.

Acceptance: Create a dashboard, use it on desktop and mobile and verify consistent values and accessible alternatives to graphical widgets.

BR-ANA-002   Filters and drill down   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-002.

Dashboards shall support period, geography, partner, project and indicator dimensions with visible filter state. Drill down shall obey permissions and disclosure rules. Saved views shall retain meaning when source definitions change.

Acceptance: A viewer drills from portfolio to project but cannot reach restricted participant data or infer suppressed cells through filter combinations.

BR-ANA-003   Actual target and baseline views   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-003.

Users shall compare actuals with original or revised targets and baselines using the correct indicator direction and period semantics. Views shall identify the selected target version and avoid misleading axes or silent truncation.

Acceptance: Display lower is better and cumulative indicators with the expected status and clear target context.

BR-ANA-004   Freshness and approval context   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-004.

Every result view shall identify whether it uses live approved data, provisional data or a frozen reporting snapshot. Last successful source refresh, calculation time and material missingness shall be inspectable.

Acceptance: A source failure is visible in the dashboard and a screenshot or export includes the relevant freshness disclosure.

BR-ANA-005   Table analysis and pivots   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-005.

Analysts shall create governed grouped tables, pivots and comparisons using supported aggregation rules. Totals shall remain semantically valid and disclose suppressed or incomplete components. Large analysis jobs shall be cancellable and quota controlled.

Acceptance: Pivot a multiselect dimension without presenting the sum as unique reach and show a correct grand total under the defined rule.

BR-ANA-006   Geographic analysis   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-006.

Maps shall show authorised locations or approved geographic aggregates with boundary version, legend and data period. Sensitive coordinates shall be masked or generalised. Map use shall have a nonvisual alternative.

Acceptance: An external map displays district totals without exposing exact locations of vulnerable participants through tooltips or downloads.

BR-ANA-007   Portfolio comparison   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-007.

Managers shall compare compatible projects and inspect differences in definitions, coverage and methods. The platform shall flag comparisons that mix unlike populations, units or periods instead of presenting an unexplained ranking.

Acceptance: A portfolio ranking with inconsistent denominators is blocked or explicitly qualified with visible comparability limits.

BR-ANA-008   Dashboard governance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-008.

Dashboards shall support ownership, draft and published versions, audience, expiry and controlled sharing. Copying a dashboard shall not copy permissions or reveal data to the new audience automatically.

Acceptance: Copy a dashboard into a partner workspace and require explicit valid bindings for restricted metrics.

BR-ANA-009   Alerts and thresholds   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-009.

Users shall subscribe to authorised performance, freshness and quality alerts with conditions, frequency and noise controls. The trigger shall distinguish stale or incomplete data from actual deterioration.

Acceptance: Missing data produces a missingness alert rather than a false zero achievement alert, with controlled repeat notifications.

BR-ANA-010   External analytics access   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-ANA-010.

Approved BI integrations shall expose governed datasets and metadata through scoped access. Data extracts and credentials shall have lifecycle controls; external copies shall be included in the sharing register where feasible.

Acceptance: Revoke a BI integration and block further retrieval while clearly identifying the limits of recalling data already copied into the external tool.

## 23 Reporting publication and donor obligations

Business owner: MEL and programme leads. Approval of report content and approval of its audience are separate decisions.

BR-RPT-001   Report template library   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-001.

Users shall configure reusable reports with narrative sections, approved metrics, tables, charts, evidence references and required disclosures. Templates shall carry owner, donor context, version, language and applicable reporting period.

Acceptance: Generate two donor reports from one approved data snapshot without duplicating or changing the underlying results.

BR-RPT-002   Reporting obligations   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-002.

The system shall track donor and internal obligations, due dates, owners, templates, required indicators and approval routes. A project may have multiple calendars and formats. Changed obligations shall retain the prior commitment history.

Acceptance: Track quarterly and annual obligations for the same project and show their independent completeness and approval status.

BR-RPT-003   Frozen reporting packages   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-003.

Official reports shall bind to an approved snapshot of data, definitions, calculations, targets, evidence and relevant configuration. Regeneration shall preserve numeric content even if live data later changes. Inaccessible or lawfully deleted evidence shall be disclosed appropriately.

Acceptance: Regenerate a published quarter after source corrections and retain the original values and version references.

BR-RPT-004   Narrative authoring and review   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-004.

Users shall draft, collaborate on and review narratives with tracked revisions and linked evidence. AI generated passages shall be identifiable during review. Required disclaimers and quality caveats shall persist into approved output.

Acceptance: Review an AI assisted section, correct an unsupported statement and preserve the reviewer’s final approved wording and sources.

BR-RPT-005   Accessible export formats   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-005.

Reports shall export to DOCX and PDF and tabular results to XLSX and CSV. Outputs shall retain filters, units, periods, definitions and material caveats. Supported accessible templates shall preserve meaningful headings and table structure.

Acceptance: Compare exported values with the approved snapshot and visually and structurally inspect representative long reports for clipping and missing context.

BR-RPT-006   Presentation and donor format output   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-006.

Users shall generate approved slide summaries and donor specific structured outputs from the same governed snapshot. Mapping to donor formats shall be versioned and validated. Formatting shall not require retyping authoritative results.

Acceptance: Produce a narrative report and presentation from one snapshot with identical results and traceable differences in audience specific content.

BR-RPT-007   Publication control   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-007.

Publication shall require an authorised actor, approved version, defined audience and completed privacy checks. Public publication shall be a separate action with preview. The system shall block unpublished drafts from appearing in public search or predictable URLs.

Acceptance: A draft report remains private even when its identifier is known; publication exposes only the approved disclosure artifact.

BR-RPT-008   Distribution and scheduled delivery   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-008.

Scheduled deliveries shall recheck recipient eligibility, artifact state and permissions when sending. Sensitive reports shall use authenticated access rather than unprotected attachments. Delivery, failure and cancellation shall be traceable.

Acceptance: Remove a recipient after scheduling and confirm they receive no protected report or link that still grants access.

BR-RPT-009   Amend withdraw and supersede   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-009.

Published reports shall support withdrawal or supersession with reason, replacement link and distribution history. Users shall be able to identify which authorised audiences received an obsolete version. Downloaded copies cannot be represented as remotely recalled.

Acceptance: Correct a report and show the superseded status, replacement version and appropriate notification record.

BR-RPT-010   Reporting reconciliation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-010.

The platform shall compare reports across versions and identify changed data, target, definition, calculation and narrative. It shall reconcile totals between detailed tables, charts and summary text before approval.

Acceptance: Introduce a changed source figure and identify every affected report location, including AI generated narrative numbers.

BR-RPT-011   Transparency publication   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-011.

Where enabled, IATI publication shall use a documented supported standard version, field mappings, validation and authorised publisher identity. Preview and approval shall precede publication. Revisions and removal shall follow the external service’s available controls. [S8]

Acceptance: Validate a representative export, correct errors and publish only through the approved workflow with an external acknowledgement recorded.

BR-RPT-012   Report evidence package   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-RPT-012.

An authorised auditor shall be able to receive a package containing the report, dictionary, approved result details, source references, approvals and caveats within their access scope. The package shall include a manifest and version identifiers.

Acceptance: Reconstruct selected published results from the package and identify any withheld material without disclosure of the withheld content.

## 24 Funding budgets and cost effectiveness

Business owner: Programme finance lead. The platform provides programme management and analysis; authoritative accounting remains with the designated finance system.

BR-FIN-001   Funding and grant context   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-001.

Users shall record funders, agreements, award amounts, currencies, periods, amendments, subgrants and reporting obligations. Confidential agreement fields shall have separate permissions. Funding relationships shall not automatically grant programme data access.

Acceptance: Link two funders to one programme and give each only its approved reporting view.

BR-FIN-002   Budget planning   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-002.

Managers shall create versioned budgets by project, activity, category, partner and period with approval and revision history. Baseline and revised budgets shall remain comparable. Budget changes shall not rewrite imported actual expenditure.

Acceptance: Approve a revised budget and display variance against either baseline without changing the expenditure source records.

BR-FIN-003   Expenditure ingestion   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-003.

Actual spending shall be imported or entered with source reference, date, currency, category, funding allocation and approval status. Controls shall prevent repeated imports from duplicating expenditure. Reconciliation shall preserve the finance system’s control totals.

Acceptance: Import an amended expenditure file twice and reconcile the approved total to the intended source balance.

BR-FIN-004   Currency treatment   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-004.

Any currency aggregation shall declare source currency, reporting currency, exchange rate source, effective date and method. Historical reports shall preserve the rates actually used. Unsupported conversions shall be blocked.

Acceptance: Restate a reporting currency view without changing the original currency transactions or the rates in an already published report.

BR-FIN-005   Variance and forecast   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-005.

Users shall compare approved budget, expenditure, commitments and forecast where available with clear definitions. Forecast assumptions shall be distinct from recorded actuals. Budget underspend shall not automatically imply programme failure or success.

Acceptance: Display expenditure and forecast separately with their dates, source coverage and approved assumptions.

BR-FIN-006   Shared costs and allocations   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-006.

Cost allocation across projects, donors and outcomes shall use versioned rules with documented basis. Allocations shall reconcile to source totals and avoid double charging in analytical views.

Acceptance: Allocate a shared cost across two projects and demonstrate that the combined allocated total equals the authorised source amount.

BR-FIN-007   Cost effectiveness   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-007.

Users shall calculate cost per defined output or outcome using compatible periods, currencies, populations and cost scopes. The result shall state exclusions, uncertainty and limitations. It shall not be labelled a causal return on investment without supporting methodology.

Acceptance: Calculate cost per participant using the approved unique participant denominator and disclose excluded shared costs.

BR-FIN-008   Finance permissions and audit   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-FIN-008.

Financial values, attachments, approvals and exports shall have separate access controls and audit coverage. Connecting a finance source shall not expose account credentials or unrestricted finance data to programme users.

Acceptance: A programme viewer sees an approved budget summary but cannot retrieve restricted agreement clauses or transaction level details.

## 25 Integrations APIs and interoperability

Business owner: Product integration lead and security lead. Named connectors are target integrations; their exact supported versions and credentials must be verified during FSD preparation.

| Source or destination | Intended flow | Release | Required contract |
| --- | --- | --- | --- |
| CSV and XLSX | Import and export | R1 | Types, identifiers, mappings, row outcomes and repeat handling |
| KoboToolbox | Survey data ingestion | R1 | Forms, response IDs, updates, repeats, attachments and deletions |
| ODK Central | Survey data ingestion | R2 | Published form versions, submissions, media and change handling |
| SurveyCTO | Survey data ingestion | R2 | Authorised datasets, repeat structures, revisions and refresh status |
| Google Sheets and Drive | Selected table and document ingestion | R2 | Least privilege consent, version changes, revocation and source ownership |
| Generic external systems | Scoped API and webhooks | R1 API; R2 webhooks | Stable resources, validation, versioning, idempotency and limits |
| Power BI Tableau and equivalent BI | Governed analytical retrieval | R2 | Permissions, metadata, freshness and extract lifecycle |
| Identity providers | Federation and lifecycle | R1 federation and R2 provisioning | Tenant identity, group mapping, credential rotation and revocation |
| Finance systems | Approved spending and budget ingestion | R2 | Control totals, source reference, currency and correction semantics |
| IATI publication | Approved structured publication | R2 | Supported standard, validation and acknowledgement |
| Email and notification providers | Operational notifications | R1 | Delivery status, minimal content and recipient recheck |
| Sector platforms such as DHIS2 | Approved domain exchange | R3 | Explicit object mapping and sector specific semantic validation |

BR-INT-001   Connector qualification   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-001.

Each supported connector shall document objects, direction, versions, limits, update and deletion semantics, attachment handling, ownership and support boundaries. Unsupported capabilities shall be visible before activation.

Acceptance: Run an agreed fixture for creates, updates, deletions, duplicates and attachments and reconcile source and destination outcomes.

BR-INT-002   Connection lifecycle   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-002.

Connections shall have an owner, authorised scope, credential reference, last verification, expiry and revocation status. Users shall verify permissions before activation. Secrets shall not appear in forms, logs or exported configuration.

Acceptance: Revoke the upstream authorisation and show a clear connection failure without retaining a hidden alternate credential.

BR-INT-003   Reliable job execution   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-003.

Integration jobs shall provide status, checkpoint, bounded retry, per item outcomes and safe replay. Repeated delivery shall be expected and handled idempotently. Poison records shall be isolated rather than blocking unrelated valid data indefinitely.

Acceptance: Retry a partially failed import and reconcile exactly one intended effect for each stable source record.

BR-INT-004   API completeness and consistency   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-004.

The API shall expose documented business resources and permitted operations with equivalent policy enforcement to the interface. It shall support pagination, filtering, stable identifiers and structured errors without exposing implementation internals or protected data.

Acceptance: Perform representative create, query, update and export operations and confirm the same validation and approval rules as the user interface.

BR-INT-005   API version and compatibility   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-005.

Published API contracts shall be versioned, testable and discoverable. Breaking changes shall follow an announced migration period of at least twelve months unless a security emergency requires a controlled exception.

Acceptance: Run a prior supported client against a new release and verify unchanged contract behaviour and visible deprecation notices.

BR-INT-006   Webhook delivery   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-006.

Outbound events shall use authenticated or signed delivery, replay protection, delivery IDs, retry status and controlled destinations. Consumers shall be informed of duplicate and ordering semantics. Revocation shall stop future deliveries.

Acceptance: Replay and reorder events without duplicate business effects and reject an invalid signature or unapproved destination.

BR-INT-007   Limits and tenant fairness   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-007.

Integrations shall have tenant and credential level quotas, rate limits and workload controls with clear status and retry guidance. One noisy or failing connector shall not exhaust capacity for other tenants or core approvals.

Acceptance: Exceed a connector limit and verify bounded impact, recoverable errors and unaffected core workflows for other tenants.

BR-INT-008   Import export standards   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-008.

The platform shall preserve documented code lists, language, currencies, units, dates and geographies across integrations. Standards mappings shall identify their version and any information loss. Custom exports shall include a mapping manifest.

Acceptance: Round trip a representative record set and identify every deliberately transformed or unsupported field.

BR-INT-009   Integration diagnostics   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-009.

Authorised administrators shall see connection health, freshness, run counts, errors, mapping changes and remediation guidance without seeing secrets or unauthorised payloads. Test connections shall use bounded samples.

Acceptance: Diagnose a schema change from the administrator view and safely reprocess the affected batch after a reviewed mapping fix.

BR-INT-010   Development and testing access   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-INT-010.

Integration developers shall have sample contracts, a test environment and synthetic fixtures independent of production credentials. Test data shall not flow into official results. Access to live debugging payloads shall be exceptional and controlled.

Acceptance: Validate a connector end to end with synthetic data and confirm that test credentials cannot access production records.

## 26 AI assisted product capabilities

Business owner: Product owner with MEL, privacy and AI assurance leads. The AI layer shall reduce work inside governed workflows. Its actions are subject to the same business rules and permissions as human actions. Risk review shall use NIST AI RMF and its Generative AI Profile as references, with product specific evidence rather than an unsupported certification claim. [S12]

BR-AI-001   Explicit enablement and policy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-001.

Tenant administrators shall enable AI capabilities by use case, data class and approved processing destination. Users shall see when AI is involved. Disabling AI shall preserve core data entry, calculations, approval and reporting workflows.

Acceptance: Disable AI for a tenant and complete the core reporting journey without sending content to a model service.

BR-AI-002   Proposal and logframe extraction   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-002.

AI shall propose structured programmes, results frameworks, indicators, targets and dates from authorised documents with source locations. Extracted facts, inferred relationships and suggested additions shall be distinguishable. Ambiguous commitments shall require review.

Acceptance: Process the agreed proposal corpus and meet the extraction gate while never presenting an unsupported target as a source fact.

BR-AI-003   Indicator design assistance   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-003.

AI shall suggest definitions, measurement methods, evidence sources and disaggregations using approved libraries and user context. It shall identify missing denominators, unclear populations and unsupported proxies. A MEL reviewer must approve production definitions.

Acceptance: A suggested indicator passes the same mandatory fields and compatibility checks as a manually authored indicator.

BR-AI-004   Import and cleaning assistance   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-004.

AI shall suggest column mappings, normalisations and possible errors with a preview of affected records. It shall not silently merge participants, delete records, change approved actuals or overwrite raw evidence.

Acceptance: Accept selected mapping suggestions and reject others, then inspect the applied deterministic transformation and unchanged original file.

BR-AI-005   Evidence based questions   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-005.

Users shall ask questions over their authorised project documents and approved datasets. Responses shall identify scope, date, relevant citations and important limitations. The system shall abstain or ask for missing context when available evidence cannot support an answer.

Acceptance: Answer representative supported questions and explicitly refuse to invent an answer to unanswerable or unauthorised questions.

BR-AI-006   Governed numerical analysis   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-006.

For numeric answers, AI shall invoke approved calculations or restricted analytical operations and present their returned values with filter and period context. Any query plan shall be constrained by current permissions and resource limits.

Acceptance: Ask for unique reach, pooled percentages and year to date totals and reconcile every reported number to the authoritative calculation result.

BR-AI-007   Report drafting   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-007.

AI shall draft narrative and report sections from the selected approved snapshot and template, linking material factual claims to evidence. It shall distinguish interpretation from observed fact and identify missing sections rather than fabricate them.

Acceptance: Review a donor report draft with intentionally missing evidence and confirm the gap is visible and numeric text matches the approved tables.

BR-AI-008   Qualitative assistance   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-008.

AI may suggest codes, themes, summaries and translations over permitted qualitative evidence, preserving source excerpts and minority or contradictory perspectives. Human analysts shall accept or revise codes and findings.

Acceptance: An evaluation containing opposing participant views retains both; the summary does not invent quotations or erase contradictory evidence.

BR-AI-009   Proactive findings   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-009.

AI may surface unusual performance, missing evidence and potential risks with affected data, rationale and proposed follow up. Findings shall be labelled as suggestions pending review. Alerts shall have feedback and noise controls.

Acceptance: A manager can verify, dismiss or assign a finding and distinguish a model suspicion from a validated programme issue.

BR-AI-010   Action proposal and approval   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-010.

AI initiated changes shall show the exact proposed objects, values, scope and consequences before application. Write actions require authorised confirmation and any existing independent approvals. Access and source versions shall be rechecked at execution.

Acceptance: Revoke permission or modify the object after proposal generation and confirm that the stale proposed action cannot execute unchanged.

BR-AI-011   Input and tool isolation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-011.

Instructions found in documents, uploads, external pages and connector content shall be treated as untrusted data. They shall not expand tools, change policy, disclose credentials or redirect outputs. Tool execution shall use bounded, independently authorised actions.

Acceptance: A document instructing the assistant to export all tenant records or send secrets to an external destination fails in adversarial testing.

BR-AI-012   Model data handling   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-012.

Customer content shall not be used to train shared models by default. Approved model providers and deployments shall meet the tenant’s retention, region and contractual requirements. Sensitive data minimisation and redaction shall precede transmission where required.

Acceptance: Inspect configured data flows and verify that prohibited classes never reach an unapproved destination, including fallback models and diagnostic logs.

BR-AI-013   Source access and conversation history   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-013.

AI retrieval, context, generated artifacts and shared conversations shall respect current permissions. Revoked evidence shall not remain retrievable through conversation summaries, vector indexes, caches or copied chat artifacts under platform control.

Acceptance: Revoke a source grant and repeat a prior question or open a shared conversation; protected content remains inaccessible under the current policy.

BR-AI-014   Traceability and reproducibility   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-014.

AI tasks shall retain permitted metadata about user, source versions, model version, configuration, tool results, review and applied changes. The product shall preserve concise evidence and decision explanations; it shall not require hidden model reasoning. Nondeterministic generation shall not be claimed as exactly reproducible.

Acceptance: An auditor can reconstruct what evidence and tools supported an applied change and who approved it without exposing prohibited content.

BR-AI-015   Evaluation and release gates   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-015.

Each AI use case shall have a versioned evaluation set, acceptance thresholds, language and sector coverage, known limitations and an accountable owner. Model or prompt changes shall require regression review. Production feedback shall feed a controlled improvement process.

Acceptance: A candidate model failing citation, leakage or critical numeric checks cannot replace the approved configuration.

BR-AI-016   Cost latency and fallback   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-016.

AI jobs shall have visible progress, cancellation, usage limits and tenant budgets. Failure shall preserve user work and offer the existing manual workflow. A fallback model may run only if it meets the same data handling policy.

Acceptance: Exhaust a tenant AI budget and simulate a provider outage; ordinary approvals continue and no prohibited fallback transmission occurs.

BR-AI-017   Forecasts and scenario assistance   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-017.

Forecasts and scenario suggestions shall identify inputs, assumptions, method, uncertainty and validation history. They shall be separate from observed actuals and approved targets. Unsupported predictions shall be withheld or clearly bounded.

Acceptance: Export a projection alongside actuals and retain the distinction, uncertainty and underlying scenario assumptions.

BR-AI-018   Safety feedback and shutdown   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-AI-018.

Users shall flag incorrect, unsafe or privacy violating output. Administrators shall disable an affected use case, model or provider promptly without taking down the core product. Incident review shall preserve lawful evidence and identify affected artifacts.

Acceptance: Trigger a simulated AI data exposure, disable the affected capability and identify generated artifacts requiring review or withdrawal.

## 27 Security and assurance requirements

Business owner: Security lead. The minimum verification baseline is all applicable OWASP ASVS 5.0 requirements through Level 2, including Level 1, with threat driven additional controls for privileged administration and high sensitivity data. Applicability and exceptions require evidence; this requirement is not a claim that a certification exists or has been achieved. [S9]

BR-SEC-001   Security threat assessment   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-001.

The product shall maintain a threat assessment covering tenant isolation, identity, uploads, offline devices, external sharing, integrations, AI and administrative access. Significant changes shall update the assessment and associated verification cases.

Acceptance: Security review maps material threats to implemented controls and tests, including abuse cases spanning multiple features.

BR-SEC-002   Encryption and key governance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-002.

Customer data shall be protected in transit and at rest, including backups, files, temporary exports and offline packages. Keys shall have accountable ownership, restricted use, rotation and recovery controls. Cryptographic choices shall follow current approved guidance at design review.

Acceptance: Inspect every data location and transport path and demonstrate protected storage, invalid certificate rejection and controlled key rotation.

BR-SEC-003   Tenant isolation verification   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-003.

Isolation shall cover application records, files, caches, background jobs, analytics, search, AI retrieval, backups and support tooling. Shared infrastructure shall not create shared authorisation. Isolation tests shall be required for every relevant release.

Acceptance: Adversarial users and service identities cannot retrieve or change another tenant’s resources through any exposed path.

BR-SEC-004   Application and API protection   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-004.

The platform shall resist common web and API attacks, including injection, cross site scripting, cross site request forgery, broken object authorisation, unsafe redirects and server side request forgery. Inputs shall be bounded and outputs safely encoded.

Acceptance: Applicable ASVS controls and independent penetration testing provide evidence of protection across authenticated and public surfaces.

BR-SEC-005   File and content safety   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-005.

Uploads and generated files shall be checked for allowed type, actual content, size and malicious payloads. Active content shall not execute in previews. Archives, external URLs and media processing shall have resource and destination restrictions.

Acceptance: Reject or quarantine malicious, misleading and oversized fixtures, including archive expansion attacks and links to restricted internal destinations.

BR-SEC-006   Secrets management   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-006.

Credentials, signing material and encryption secrets shall be protected from source code, browser storage, ordinary administrators, logs and exported configuration. Rotation and revocation shall be supported without undocumented manual recovery steps.

Acceptance: Run secret exposure checks and demonstrate credential rotation with continued authorised operation and revoked old credentials.

BR-SEC-007   Tamper evident audit   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-007.

Audit records shall capture attributable identity, tenant, action, affected object, result, time and correlation context for sensitive reads and mutations. Privileged users shall not silently alter or delete audit history. Personal values shall be minimised under retention policy.

Acceptance: Attempt audit tampering, inspect privileged access events and reconstruct a sensitive export and approval sequence.

BR-SEC-008   Secure engineering lifecycle   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-008.

Changes shall use peer review, automated security checks, dependency and license inventory, vulnerability assessment and controlled release evidence. Security relevant tests shall run before production promotion. A software component inventory shall be maintainable for incident response.

Acceptance: Trace a production version to reviewed changes, verification results, dependency inventory and approval records.

BR-SEC-009   Vulnerability management   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-009.

The product shall maintain intake, severity assessment, ownership, remediation targets and retesting for vulnerabilities. Release blocking criteria and emergency mitigation shall follow section 32. Disclosure reports shall have a monitored handling process.

Acceptance: Process a simulated critical vulnerability from report to containment, fix, retest and communication with timestamps.

BR-SEC-010   Independent assurance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-010.

An independent security assessment shall precede general production release and recur after material changes or at least annually. Critical or high findings affecting confidentiality, integrity or access shall block release until resolved or effectively mitigated and independently retested.

Acceptance: Release evidence contains the scoped assessment, findings, remediation and retest results rather than a blanket “secure” assertion.

BR-SEC-011   Detection and incident response   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-011.

The service shall detect suspicious authentication, privilege changes, bulk extraction, anomalous service access and failed security controls. Incident procedures shall define containment, evidence preservation, recovery and communications responsibilities.

Acceptance: A simulated cross tenant exposure or credential compromise triggers the specified on call response and tenant impact assessment.

BR-SEC-012   Environment separation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-012.

Development, testing and production shall have separated access and credentials. Production personal data shall not be copied into lower environments without an approved purpose and effective protection or anonymisation. Test users shall not exist as hidden production bypasses.

Acceptance: A test credential cannot access production and a production debug request follows controlled approval and redaction rules.

BR-SEC-013   Privileged operations   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-013.

Production administration shall use individually attributable access, MFA, minimum privilege and time bounded elevation. Sensitive operational changes shall require independent review where feasible, with emergency procedures and retrospective review.

Acceptance: Elevate an operator for a specific incident, observe actions, expire access and verify that standing broad access was not left behind.

BR-SEC-014   Resilience to abusive traffic   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-014.

The platform shall protect authentication, public forms, search, exports and AI endpoints against automated abuse and resource exhaustion. Controls shall balance legitimate field access with tenant fairness and accessible recovery paths.

Acceptance: Apply burst and abusive workloads and verify bounded degradation without indiscriminate lockout of unrelated organisations.

BR-SEC-015   Enterprise assurance options   P2 R3

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-SEC-015.

The product shall support qualified dedicated tenancy, customer controlled key arrangements and network restrictions where approved as deployment variants. Each variant shall meet the same functional, operational and recovery gates before being offered.

Acceptance: Qualify a selected deployment profile with documented responsibilities, upgrade process, failure handling and exit behaviour.

## 28 Privacy data governance and retention

Business owner: Privacy lead with tenant data owners. Applicable obligations depend on jurisdiction, contract, data category and deployment. The product must support controlled policies rather than imply universal compliance.

BR-PRV-001   Data inventory and classification   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-001.

Data objects and fields shall carry classification, purpose, accountable owner and retention policy. Sensitive participant information, credentials and restricted evidence shall receive stricter handling across interfaces, exports and AI.

Acceptance: Classify a new sensitive field and verify propagated restrictions in forms, datasets, reports, logs and model inputs.

BR-PRV-002   Minimisation and purpose controls   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-002.

Programme setup shall identify necessary personal data and permitted uses. Optional collection shall remain optional. Reuse for new research, cross programme matching or model improvement shall require an authorised basis and review.

Acceptance: Attempt to reuse service delivery data for an unapproved AI training purpose and confirm it is blocked.

BR-PRV-003   Hosting and transfer policy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-003.

Tenants shall know the hosting location and approved destinations for data, backups, support access and AI processing. Region changes and new subprocessors shall follow the applicable agreement and approval process. Failover shall not silently breach residency policy.

Acceptance: Simulate regional failure and confirm recovery only in a permitted location or a clear controlled outage when no permitted recovery location exists.

BR-PRV-004   Retention schedules   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-004.

Retention shall be configurable by data class and business purpose, covering source files, records, evidence, generated reports, audit metadata, logs, AI content and backups. Defaults shall be explicit and reviewed before real data collection.

Acceptance: Inspect the complete retention inventory and identify the owner and expiry treatment for each stored data category.

BR-PRV-005   Deletion restriction and holds   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-005.

Authorised deletion or restriction shall propagate to searchable copies, analytical derivatives, AI indexes and generated artifacts under platform control. Valid holds shall suspend affected deletion with reason and review date. The platform shall distinguish deletion, restriction and anonymisation.

Acceptance: Execute a request and verify each affected store’s outcome, including an explicitly recorded hold and its later release.

BR-PRV-006   Backup deletion handling   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-006.

Backup retention shall be bounded. Where granular deletion from immutable backups is infeasible, affected data shall expire within the approved backup window and deletion instructions shall be reapplied before restored data becomes accessible.

Acceptance: Restore a backup predating a deletion and verify the deleted participant data is not reopened to users or AI.

BR-PRV-007   Data subject request handling   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-007.

The product shall support verified access, correction, restriction, objection and deletion workflows as applicable, with deadlines driven by the tenant’s legal policy. Responses shall exclude other people’s information and preserve a minimal action history.

Acceptance: Process a household member’s request without disclosing another member’s restricted responses and record completion or justified limits.

BR-PRV-008   Sharing register and agreements   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-008.

External sharing shall identify recipient, purpose, scope, permitted reuse, expiry and responsible owner. Cross organisation exchanges shall record applicable agreements and subsequent revocation or correction notices.

Acceptance: List all active disclosures of a selected dataset and initiate the required change notices after a material correction.

BR-PRV-009   Privacy review and country policy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-009.

Before high sensitivity processing or a new deployment jurisdiction, the organisation shall record the applicable obligations, risk assessment, transfer conditions, incident notice commitments and approved safeguards. Product controls shall enforce the approved policy where technically expressible.

Acceptance: A new sensitive use case cannot be activated without required policy decisions and accountable approval.

BR-PRV-010   Telemetry and analytics privacy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-PRV-010.

Operational telemetry shall avoid participant values, credentials and unrestricted document text. Product analytics and support diagnostics shall respect tenant policy. Redaction, sampling and access restrictions shall apply to error traces and AI monitoring.

Acceptance: Inspect representative errors, traces and analytics events and verify that protected payloads do not leak into general operational tools.

## 29 Service administration and product operations

Business owner: Platform operations and product operations. These requirements are necessary for a supportable software product even though sales and customer acquisition are outside scope.

BR-OPS-001   Service administration console   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-001.

Operators shall manage tenant lifecycle, service health, quotas and support status through a controlled console. Customer content shall remain unavailable by default. High impact actions shall require clear scope, confirmation and audit.

Acceptance: Suspend the intended tenant without affecting another tenant and without granting the operator automatic access to programme records.

BR-OPS-002   Entitlements and limits   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-002.

The platform shall define entitlements for users, storage, projects, connectors, API use and AI budgets without mixing them with data permissions. Limit warnings shall precede restrictions. Reaching a commercial limit shall not silently delete data or remove essential security controls.

Acceptance: Exceed a storage or AI allowance and display the defined restriction while preserving authorised access, export and security functions.

BR-OPS-003   Subscription administration   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-003.

The product shall support trial, active, overdue, suspended and closing subscription states with billing contacts, usage history and permitted renewal or downgrade paths. Payment processing, if used, shall be delegated to a qualified provider without storing payment secrets unnecessarily.

Acceptance: Downgrade an account with excess usage and follow a documented resolution path that preserves data and contractual access rights.

BR-OPS-004   Support case management   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-004.

Users shall report issues with tenant context, severity and safe diagnostic references. Cases shall identify owner, status and communication history. Attachments and logs shared with support shall follow content access and retention policies.

Acceptance: Resolve a case using permitted diagnostics and trace any exceptional content access to an approved support session.

BR-OPS-005   Monitoring and service visibility   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-005.

Operations shall monitor availability, errors, latency, job backlogs, data freshness, capacity, tenant fairness and AI failures. Tenant facing service information shall distinguish platform outage, integration delay and model unavailability.

Acceptance: Fail a connector while keeping the core service healthy and show the correct separate status and affected data freshness.

BR-OPS-006   Backup and recovery operations   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-006.

Backups shall include required data, files, definitions, audit metadata and configuration. Restore procedures shall preserve their mutual consistency, permissions and deletion instructions. Recovery exercises shall demonstrate the agreed objectives.

Acceptance: Recover a representative tenant and independently verify records, attachments, approvals, report snapshots and access policies.

BR-OPS-007   Safe release and rollback   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-007.

Releases shall include verified migration, staged exposure where appropriate, rollback or roll forward plans and tenant impact communication. Feature flags shall not bypass access controls or leave unsupported data states.

Acceptance: Rehearse a failed release and restore service without silently losing accepted writes or corrupting historical reports.

BR-OPS-008   Capacity and cost management   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-008.

Operations shall observe resource and AI usage by tenant and workload while protecting content. Forecasting shall identify capacity constraints before service targets fail. Abandoned jobs and orphaned artifacts shall have controlled cleanup.

Acceptance: Identify an unusually expensive workload, enforce its approved limit and preserve service for other tenants.

BR-OPS-009   Operational automation   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-009.

Routine maintenance, retention, health checks and notifications shall be repeatable, observable and recoverable. Automated actions shall have accountable ownership and a stop mechanism. Destructive operations shall retain policy and approval checks.

Acceptance: Retry a failed retention job without deleting held records or duplicating notifications and inspect its complete outcome manifest.

BR-OPS-010   Trust and assurance information   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-OPS-010.

Customers shall be able to access appropriate security, privacy, subprocessor, service level and incident process information. Claims about external certifications or audits shall reflect actual current evidence and stated scope.

Acceptance: Review the published assurance package and reconcile each claim with the approved evidence and applicable deployment profile.

## 30 Migration onboarding and exit

Business owner: Implementation lead and MEL lead. Existing TolaData or other source migrations require authorised exports and confirmed source semantics; direct database access is not assumed.

BR-MIG-001   Source discovery and mapping   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-001.

Migration shall inventory projects, hierarchies, indicators, definitions, dimensions, periods, records, attachments, users, permissions and reports. Mapping shall explicitly identify supported, transformed, unavailable and excluded source elements.

Acceptance: Approve a mapping manifest with known limitations before loading production data.

BR-MIG-002   Trial migrations   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-002.

The platform shall support isolated trial loads with reconciliation, error correction and repeatable mappings. Trial data shall not trigger real notifications, integrations or publication. Production credentials shall not be reused unnecessarily.

Acceptance: Perform two trial migrations and verify identical intended results without duplicate records or external side effects.

BR-MIG-003   Semantic reconciliation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-003.

Migration acceptance shall compare source and destination counts, control totals, indicator actuals, periods, targets, attachments and representative reports. Differences shall be resolved or explicitly accepted with rationale and impact.

Acceptance: Recalculate selected complex indicators in both systems and explain every variance rather than relying only on record counts.

BR-MIG-004   Historical provenance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-004.

Imported history shall distinguish original source events from migration events and identify unavailable original audit evidence. The product shall not fabricate historical approvals or claim imported timestamps prove authenticity.

Acceptance: Inspect a migrated approval and see whether it is a preserved source record, a verified import or a new destination approval.

BR-MIG-005   Cutover and rollback   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-005.

Cutover shall define the authoritative system, write freeze or delta handling, reconciliation point, owner and rollback decision. Changes made during migration shall be captured or explicitly paused. Duplicate live reporting shall be prevented.

Acceptance: Rehearse cutover with a late source update and show its controlled migration or documented exclusion and remediation.

BR-MIG-006   User enablement   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-006.

Onboarding shall provide role specific guidance, sample programmes, definitions and practice workflows using safe data. Administrators shall validate access and users shall complete essential tasks before operational rollout.

Acceptance: Representative field, manager and reviewer users complete their assigned workflow after the defined onboarding experience.

BR-MIG-007   Full tenant export   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-007.

Authorised owners shall export tenant data, relationships, files, definitions, code lists, configuration, approvals and permitted audit history in documented formats with a manifest. Export shall preserve stable identifiers and clearly state any excluded third party material.

Acceptance: Reconstruct the business relationships and selected reports outside the product using the package without undocumented assistance.

BR-MIG-008   Closure and deletion evidence   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-MIG-008.

Exit shall support an agreed retrieval period, export confirmation, credential revocation, scheduled deletion and evidence of completion subject to valid holds and backup expiry. Live integrations and scheduled deliveries shall stop at the appropriate point.

Acceptance: Close a tenant and verify access termination, successful permitted export, connector shutdown and recorded remaining retention obligations.

## 31 User experience accessibility and localisation

Business owner: Design lead with representative users. Accessibility shall target WCAG 2.2 Level AA across complete supported processes, not a selected set of screens. [S10]

BR-UX-001   Role relevant workspaces   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-001.

Users shall see their pending work, relevant programme context and permitted actions without needing to understand internal implementation. Field collection, programme management, review and funder viewing shall have coherent role appropriate experiences.

Acceptance: Representative users locate and complete their primary task without navigating unrelated administration features.

BR-UX-002   Progressive configuration   P1 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-002.

Common programme setup shall use sensible visible defaults and templates, while advanced rules remain inspectable. Defaults shall not conceal material assumptions about aggregation, consent, sharing or targets.

Acceptance: A new manager creates a valid simple programme and can identify the rules determining its first reported result.

BR-UX-003   Error recovery and work preservation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-003.

Errors shall state what failed, whether work was saved and the next permitted action. Drafts shall survive supported recoverable failures. Destructive and bulk actions shall show impact and support undo where business semantics permit.

Acceptance: Simulate validation, timeout and partial batch errors and verify that users can recover without unknowingly repeating completed actions.

BR-UX-004   Accessible interaction   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-004.

Supported workflows shall work with keyboard and screen readers, adequate contrast, visible focus, accessible labels and errors, text alternatives and sufficient target sizes. Dragging shall have an accessible alternative. Authentication shall not impose unnecessary cognitive barriers.

Acceptance: Complete core journeys with keyboard and screen reader testing in addition to automated accessibility checks.

BR-UX-005   Responsive operation   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-005.

Collection, review, task management and viewing shall work on the supported mobile and desktop profiles. Dense analytical configuration may use an explicitly supported desktop workspace, while mobile users receive a useful permitted alternative.

Acceptance: Complete the defined mobile task set at a 360 CSS pixel width without horizontal dependence for ordinary forms or hidden actions.

BR-UX-006   Language and locale   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-006.

The product shall separate interface language, data language and reporting language. Dates, numbers, currencies and time zones shall have explicit locale rules. Unicode shall be preserved in search, imports, exports and documents.

Acceptance: Import and export multilingual names and decimal formats without corruption or changed numerical meaning.

BR-UX-007   Expanded localisation   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-007.

Additional approved interface languages shall cover navigation, validation, help, notifications and reports with professional review. Right to left layout shall be supported where a selected language requires it. Stable codes shall remain independent of translation.

Acceptance: Complete the core journeys in each released language with no untranslated blocking text and consistent indicator calculations.

BR-UX-008   Discoverability and help   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-008.

Users shall have permission aware global search, recent work, saved views and context sensitive help explaining measurement concepts and actions. Help shall identify product behaviour and limitations without exposing system internals unnecessarily.

Acceptance: A user can find an assigned indicator and understand why it is awaiting approval without contacting an administrator.

BR-UX-009   Status and trust cues   P0 R1

Build 0.12 coverage: PARTIAL. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-009.

The interface shall visibly distinguish draft, submitted, approved, published, stale, partial, suppressed and AI proposed content. A generic success message shall not imply that a background calculation, sync or external delivery has completed.

Acceptance: Submit a large import and observe distinct receipt, validation, approval and recalculation statuses.

BR-UX-010   Usability evidence   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, FR-UX-010.

Design acceptance shall use representative MEL staff, managers, reviewers, partners and field users, including people with accessibility needs. Findings shall be prioritised by task failure and error consequence rather than visual preference alone.

Acceptance: Meet the core task completion target and resolve all observed usability defects that cause unauthorised disclosure, data loss or incorrect official results.

## 32 Non functional requirements and qualification targets

Business owner: Engineering and platform operations, with security, privacy, design and MEL signoff. All numerical targets in this section are proposed acceptance targets. They must be costed and qualified during HLD and performance design before any external service commitment. A change to a target requires a BRD change, not an undocumented engineering assumption.

### 32 1 Reference workload and measurement conditions

| Dimension | Qualification baseline |
| --- | --- |
| Tenant population | 250 configured tenants; at least 20 generating concurrent workload |
| Interactive load | 1000 concurrently active users in the test; 250 in the largest active tenant; average one business operation per user per five seconds |
| Workload mix | 50 percent record reads and navigation, 20 percent dashboard requests, 15 percent submissions and edits, 10 percent search and 5 percent approvals; background imports and exports run concurrently |
| Portfolio size | 10000 projects and 200000 indicator instances across the service; largest tenant contains 1000 projects and 20000 indicators |
| Data volume | 100 million structured observation rows across the service; 20 million in the largest tenant; 30 typical fields per row |
| Aggregation fixture | Up to ten reporting levels, 1000 contributing indicators to one aggregate and five disaggregation dimensions; bounded sparse combinations |
| Standard network | 20 Mbps connection and 80 ms round trip latency from the test client |
| Constrained network | 1 Mbps connection, 300 ms round trip latency and intermittent loss; offline scenarios tested separately |
| Standard client | Supported browser on a midrange laptop with 8 GB RAM; mobile core tasks on an Android device with 4 GB RAM |
| Duration | 60 minute peak workload, eight hour soak test and twofold arrival burst for five minutes |
| Test evidence | Dataset manifest, workload script, environment description, cold and warm results, errors, percentiles and tenant level results |

The test envelope is a reproducible qualification target, not permission for unbounded queries. Maximum object limits are tested individually and in representative combinations. The FSD shall define user visible limits and admission rules; the HLD shall estimate cost and scaling behaviour. Averages shall not substitute for percentiles, and aggregate service metrics shall not hide a failing tenant.

### 32 2 Performance and capacity

NFR-PER-001   Interactive response   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-001.

Under the standard workload, ordinary record reads, list views with up to 100 returned rows, saves and approval actions shall complete at p95 within 2 seconds and p99 within 5 seconds measured from user action to usable confirmed response. Long jobs are excluded only if explicitly routed asynchronously.

Acceptance: Measure each action class independently and report errors and percentiles per representative tenant over the full peak test.

NFR-PER-002   Dashboard response   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-002.

A standard dashboard of up to ten widgets with approved bounded calculations shall become usable at p95 within 5 seconds and p99 within 10 seconds. Cached and uncached results shall be reported separately. Freshness and calculation status shall remain visible.

Acceptance: Test dashboard opening, filter changes and permitted drill down with standard and cold caches and the specified background workload.

NFR-PER-003   Search response   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-003.

Permission filtered metadata and indexed document searches shall return the first 50 results at p95 within 3 seconds and p99 within 8 seconds under the standard profile. Empty, restricted and multilingual searches shall follow the same confidentiality rules.

Acceptance: Test search latency with mixed public and restricted fixtures and verify no leakage through counts or suggestions.

NFR-PER-004   Import and recalculation throughput   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-004.

A standard import of 100000 rows and 30 simple fields with configured deterministic checks shall complete validation and ingestion at p95 within 10 minutes, excluding human approval and external source transfer. A resulting bounded 1000 indicator recalculation shall complete within 5 additional minutes at p95.

Acceptance: Measure repeated representative batches, include duplicates and rejected rows, and verify correct totals under concurrent interactive load.

NFR-PER-005   Export and report generation   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-005.

A standard 100000 row data export or 50 page report with up to 20 charts shall complete at p95 within 5 minutes. Jobs shall acknowledge receipt within 2 seconds, expose progress and support cancellation. Larger jobs shall show estimated class and explicit limits.

Acceptance: Generate both artifact types, reconcile results and verify cancellation and permission rechecks before delivery.

NFR-PER-006   Data freshness   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-006.

After a submission is approved and its bounded calculation finishes, live dashboards shall reflect the new approved result within 60 seconds at p95. External source cadence and human review delays shall be displayed separately rather than hidden in this metric.

Acceptance: Trace timestamps from source receipt through validation, approval, calculation and dashboard availability.

NFR-PER-007   AI responsiveness   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PER-007.

For interactive evidence questions, the system shall acknowledge within 2 seconds and target a first useful response at p95 within 15 seconds and a completed standard answer within 45 seconds. Long extraction and reporting tasks shall use visible asynchronous jobs with cancellation and a declared timeout.

Acceptance: Measure representative supported model configurations separately and verify graceful fallback when a provider cannot meet the target.

NFR-CAP-001   Supported object limits   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-CAP-001.

The baseline shall qualify forms with 200 questions and 100 repeat entries, source files up to 100 MB, media files up to 25 MB and import jobs up to one million rows through an appropriate asynchronous path. Limits and supported combinations shall be visible before work begins.

Acceptance: Exercise each boundary, reject over limit content safely and preserve existing drafts and accepted data.

NFR-CAP-002   Scaling and workload isolation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-CAP-002.

The service shall admit, queue or limit work predictably as demand rises. A large tenant import or AI job shall not cause unrelated tenants to miss core service targets during the baseline workload. Bursts shall recover without unbounded queues.

Acceptance: Apply the defined burst and noisy tenant workloads and demonstrate fair processing, bounded failures and queue recovery.

### 32 3 Availability durability and recovery

NFR-AVL-001   Core availability   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AVL-001.

The internal core service objective shall be at least 99.9 percent monthly availability for supported authentication, record access, submission, approval and access to published reports. Measure each critical journey and material tenant cohort. Planned maintenance affecting these journeys counts against this internal objective.

Acceptance: Provide synthetic and real request monitoring with a defined success criterion; do not hide platform dependency failures through blanket exclusions.

NFR-AVL-002   Dependency degradation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AVL-002.

AI, email, external data collection and BI failures shall be isolated where possible. Users shall see the affected function, stale data and queued actions. Core manual workflows shall remain available when their independent dependencies are healthy.

Acceptance: Fail each noncore provider and show bounded impact, safe retries and no false completion or duplicate notification.

NFR-DR-001   Disaster recovery   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-DR-001.

For the standard qualified deployment, catastrophic recovery shall target a recovery point objective of at most 15 minutes and recovery time objective of at most 4 hours from incident declaration. Recovery shall occur only within permitted regions and include files, configuration and governance state.

Acceptance: Conduct a timed recovery exercise and reconcile the possible lost interval, affected accepted writes and restored snapshots before reopening access.

NFR-DR-002   Ordinary failure durability   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-DR-002.

A server acknowledgement of a saved record shall represent durable acceptance under the qualified ordinary single component failure model. Offline local saves shall be clearly distinct. Catastrophic recovery exposure remains governed by NFR-DR-001.

Acceptance: Interrupt service components during writes and prove that acknowledged records survive or are explicitly identified for reconciliation without silent loss.

NFR-DR-003   Recovery testing and backups   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-DR-003.

Backups shall be protected against unauthorised alteration and credential compromise. Representative restores shall be tested monthly and disaster recovery at least quarterly. Default backup retention shall be no more than 35 days unless an approved contract or hold requires a different schedule.

Acceptance: Produce restore evidence including permission checks, file integrity, report snapshots and reapplication of deletion instructions.

### 32 4 Correctness consistency and revocation

NFR-DIN-001   Calculation correctness   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-DIN-001.

The entire approved deterministic golden corpus shall pass exactly at the defined precision before release. It shall cover pooled ratios, distinct counts, period semantics, dimensions, corrections, rounding, missingness, cycles and permissions. There shall be zero unexplained official report reconciliation differences.

Acceptance: Independently calculated expected outcomes match the application and exports for every release critical fixture.

NFR-DIN-002   Concurrent change integrity   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-DIN-002.

Concurrent edits and retries shall not silently lose updates, duplicate achievements or approve stale versions. Business transactions shall either complete with recorded effects or return a recoverable explicit partial outcome where the operation permits one.

Acceptance: Run concurrent editing, repeated delivery, approval races and interrupted bulk operations and reconcile final state and history.

NFR-IAM-001   Revocation time   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-IAM-001.

Online user suspension, permission removal and credential revocation shall take effect within 60 seconds across user interfaces, APIs, generated downloads, search and AI access. Queued jobs shall reauthorise before sensitive action. Directory initiated revocation is measured from receipt by the platform.

Acceptance: Instrument every affected channel and show that no protected access is served after the revocation bound.

NFR-OFF-001   Offline authority window   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-OFF-001.

Default offline packages shall expire within 24 hours without renewed authorisation. Restricted participant packages shall default to at most 8 hours and require approved device controls. Longer low sensitivity windows require a recorded risk exception; sensitive data may be prohibited from offline use entirely.

Acceptance: Test clock manipulation, expiry and reconnect handling and document any device limitation before qualifying the client.

### 32 5 Security and privacy operating targets

NFR-SEC-001   Release security threshold   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-SEC-001.

All applicable baseline security controls shall have passing evidence. No unresolved critical or high vulnerability affecting confidentiality, integrity or access shall enter production without an effective verified mitigation. Functional parity shall not override this gate.

Acceptance: Security signoff includes control mapping, independent assessment, retesting and any bounded noncritical exception.

NFR-SEC-002   Incident and remediation timing   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-SEC-002.

For critical production incidents, on call acknowledgement shall occur within 15 minutes and containment work shall begin within 30 minutes. Confirmed critical vulnerabilities require mitigation within 24 hours and a permanent fix target within 72 hours; high vulnerabilities within 7 days. Legal and contractual notices follow the approved incident policy.

Acceptance: Exercise the process and record timestamps, escalation and any approved shortfall with continuing mitigation.

NFR-AUD-001   Audit coverage and retention   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AUD-001.

All defined security and business audit event classes shall be captured and searchable by authorised reviewers. Default security event metadata retention shall be 365 days; longer business audit retention shall follow tenant policy. Secret values and unnecessary personal payloads shall not be logged.

Acceptance: Execute the audited action catalogue and reconcile every expected event with its actual stored and exported record.

NFR-PRV-001   Deletion propagation   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PRV-001.

After an authorised deletion becomes executable and no hold applies, active primary records, caches, indexes and platform generated derivatives shall be removed or effectively restricted within 24 hours. Backup expiry follows the approved schedule, normally within 35 days. External recipient actions shall be tracked separately.

Acceptance: Search and query all in scope stores after the deadline and verify no unauthorised recovery, including through AI and restored backups.

NFR-PRV-002   Retention defaults and proof   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PRV-002.

Production tenants shall have approved record and evidence retention policies before collection. Diagnostic logs shall default to 90 days or less; retained AI prompt and response content shall default to 30 days or less unless a justified policy specifies otherwise. Minimal governed approval evidence may have a separate schedule.

Acceptance: Demonstrate scheduled expiry and identify every exception by owner, purpose, scope and review date.

### 32 6 AI quality qualification

NFR-AIQ-001   Evaluation set quality   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AIQ-001.

Each enabled use case shall have a held out evaluation set with at least 200 representative cases where feasible, including at least 20 percent boundary, unsupported or adversarial cases. Small specialist sets require documented justification and risk review. Each released language and sector must have explicit coverage evidence.

Acceptance: An independent reviewer confirms separation from tuning data, representative tasks and versioned expected judgments.

NFR-AIQ-002   Evidence and numeric accuracy   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AIQ-002.

Evidence question answering shall achieve at least 95 percent supported factual claims and at least 98 percent correct citation locations on the approved set. Every numeric value presented as an official result shall match the authoritative tool result. A critical unsupported consequential claim blocks release regardless of the average score.

Acceptance: Score claims and citations independently, record denominators and failures, and verify all official numeric outputs against deterministic results.

NFR-AIQ-003   Extraction and abstention   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AIQ-003.

Document extraction shall target at least 95 percent field level precision and 90 percent recall on mandatory fields. The system shall correctly abstain or request clarification for at least 95 percent of designated unanswerable cases, while incorrect abstention on answerable cases remains at or below 10 percent.

Acceptance: Report performance by field type and language and count reviewer correction time in the setup efficiency measure.

NFR-AIQ-004   Leakage and action safety   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AIQ-004.

Adversarial qualification shall show zero successful cross tenant disclosures, unauthorised tool actions or secret disclosures in the defined test suite. This is a test acceptance criterion, not proof that real world risk is zero. Any observed failure blocks the affected capability until resolved.

Acceptance: Run injection, indirect retrieval, conversation sharing, stale permission and tool escalation cases and retain results for each release.

NFR-AIQ-005   Change monitoring and rollback   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-AIQ-005.

Model, prompt, retrieval and policy changes shall have versioned evaluation, controlled rollout and rollback. Production monitoring shall track failures, reviewer corrections, refusals, latency, cost and language specific quality with minimised content retention.

Acceptance: Introduce a deliberately degraded configuration and demonstrate detection, rollback and identification of affected generated artifacts.

### 32 7 Accessibility compatibility and maintainability

NFR-UX-001   Accessibility conformance   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-UX-001.

All supported core journeys shall meet WCAG 2.2 Level AA through automated checks and manual keyboard and assistive technology review. Complete processes, third party authentication flows under product control and generated standard templates shall be included in the scope. [S10]

Acceptance: An accessibility review records tested environments, findings, resolutions and any declared limits for user supplied content.

NFR-UX-002   Usability qualification   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-UX-002.

At least 90 percent of representative users shall complete programme setup, assigned collection, correction, approval, result explanation and report generation tasks without facilitator intervention after standard onboarding. No observed critical data loss or disclosure error is acceptable.

Acceptance: Record task time, completion, errors and user role across at least 15 participants and improve failing workflows before release.

NFR-CMP-001   Browser and device support   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-CMP-001.

The product shall qualify current and previous major versions of Chrome, Edge, Firefox and Safari at release, with stated mobile OS and client support. Browser changes shall trigger regression checks. Unsupported environments shall receive clear guidance rather than silent data corruption.

Acceptance: Run the supported workflow matrix, including file handling, federation, accessibility and offline capabilities on each qualified client.

NFR-L10-001   Localisation integrity   P1 R1

Unicode, locale specific number and date handling and explicit time zones shall survive ingestion, search, calculations and export. Released translations shall cover all blocking workflow text. Display locale shall not change stored values or period assignment.

Acceptance: Run multilingual and daylight saving boundary fixtures and compare the interpreted values across views and exports.

NFR-MNT-001   Maintainable contracts   P1 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-MNT-001.

Business rules, supported APIs, configurable policies and data dictionaries shall be documented and version controlled. Changes shall retain traceability to requirements and tests. Routine tenant configuration shall not require a customer specific code fork.

Acceptance: Configure two materially different programme templates through supported mechanisms and trace a rule change through documentation and regression evidence.

NFR-OBS-001   Operational diagnosability   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-OBS-001.

Failures shall have correlation references linking user actions, background jobs and integration events without exposing secrets. Critical service failure alerts shall be generated within 5 minutes of detection conditions. Logs shall support tenant scoped diagnosis and audit separation.

Acceptance: Trace a failed report job across its stages and verify both timely alerting and protected diagnostic content.

NFR-PRT-001   Portability and exit quality   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-PRT-001.

Tenant exports shall include a documented manifest and machine readable relationships. A standard tenant with up to one million structured rows and 10 GB of attachments shall receive a complete asynchronous package within 24 hours under the agreed service process. Larger exports require a visible estimate and progress.

Acceptance: Validate file integrity, completeness, access scope and reconstruction of representative business objects outside the platform.

NFR-ECO-001   Cost transparency and sustainability   P1 R2

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-ECO-001.

The operating model shall measure cost per active tenant, approved result workload, storage volume, integration run and AI use case. Product limits shall be costed against the qualification profile. A cost budget shall be approved before offering unbounded or dedicated deployment commitments.

Acceptance: Produce a cost model for the reference workload with measured assumptions and show how budget limits affect user behaviour.

NFR-SUP-001   Support and service readiness   P0 R1

Build 0.12 coverage: PENDING. Full acceptance remains open. Evidence and limits: TRACEABILITY.csv, VF-SUP-001.

Critical incident response shall have continuous on call coverage. Normal support hours, response targets and escalation channels shall be published for each service plan. An operational owner, runbook and tested recovery path shall exist for every critical capability.

Acceptance: Conduct a release readiness exercise with service incidents, identity recovery, failed imports and report corrections.

## 33 Mandatory business rules and invariants

The following rules consolidate requirements that cross module boundaries. They shall become explicit functional rules and automated regression assertions where applicable. They do not replace the detailed catalogue.

| Rule | Invariant | Principal requirements |
| --- | --- | --- |
| RULE01 | An identity has access through a tenant membership and scope, never merely because an object ID is known | BR-IAM-008, BR-ACC-001 |
| RULE02 | Account ownership and billing rights do not imply access to participant data | BR-TEN-010, BR-ACC-002 |
| RULE03 | A person cannot satisfy an independent approval requirement for their own governed change | BR-ACC-004, BR-WFL-002 |
| RULE04 | Official actuals use approved source versions and approved deterministic calculations | BR-CAL-001, BR-WFL-007 |
| RULE05 | Zero, missing, suppressed and pending approval have different meanings | BR-IND-007, BR-DQ-006 |
| RULE06 | Percentage pooling requires compatible numerators and denominators | BR-CAL-003 |
| RULE07 | Unique reach requires a justified deduplication scope; unknown overlap is disclosed | BR-CAL-004, BR-PAR-002 |
| RULE08 | Cumulative totals, period flows and snapshots have different time aggregation rules | BR-CAL-005 |
| RULE09 | A source contribution cannot be counted twice through two aggregation paths unless the measure explicitly intends it | BR-CAL-006, BR-CAL-014 |
| RULE10 | Material definition or target changes preserve previous baselines and reveal breaks in comparability | BR-IND-004, BR-IND-008 |
| RULE11 | A corrected source does not silently rewrite a published report | BR-CAL-011, BR-RPT-003 |
| RULE12 | Imports and synchronisation are safe to retry without duplicate intended effects | BR-DAT-003, BR-OFF-003 |
| RULE13 | A stale approval cannot authorise a newer object version | BR-WFL-002 |
| RULE14 | Permission checks apply at scheduling, execution and delivery of sensitive work | BR-ACC-007, BR-RPT-008 |
| RULE15 | Copying a dashboard, report, template or AI conversation does not broaden data access | BR-ANA-008, BR-AI-013 |
| RULE16 | Publishing an approved aggregate may disclose it without exposing its protected source rows | BR-ACC-005, BR-ACC-009 |
| RULE17 | Every model action obeys the same access, validation and approval rules as a human action | BR-AI-010, BR-AI-011 |
| RULE18 | Model output cannot become an official numeric result without the authoritative calculation result | BR-AI-006, NFR-AIQ-002 |
| RULE19 | No customer content enters shared model training by default | BR-AI-012 |
| RULE20 | Archival, restriction, deletion and anonymisation are distinct lifecycle actions | BR-PRV-004, BR-PRV-005 |
| RULE21 | Restoring a backup must not resurrect deleted or newly restricted data | BR-PRV-006, NFR-DR-003 |
| RULE22 | Offline revocation cannot be instantaneous on a disconnected device; local authority is bounded | BR-OFF-005, NFR-OFF-001 |
| RULE23 | A budget or usage limit does not silently delete data or weaken security | BR-OPS-002 |
| RULE24 | No aggregate trend or AI narrative establishes a causal effect without adequate methodology and evidence | BR-EVA-004 |
| RULE25 | A live link can be revoked; an already downloaded external copy cannot be claimed as recalled | BR-ACC-011, BR-RPT-009 |
| RULE26 | A service incident, data delay and model outage have distinguishable statuses and owners | BR-OPS-005, NFR-AVL-002 |

## 34 Business acceptance scenarios

These scenarios define minimum integrated acceptance evidence. The FSD shall expand each into preconditions, actors, inputs, transition rules, positive and negative steps, expected outputs and audit events. The detailed test plan shall also cover every requirement independently.

### 34 1 Measurement and reporting scenarios

| Scenario | Test situation | Expected business result |
| --- | --- | --- |
| UAT01 | A reviewer pools 50 successes from 100 eligible people and 1 from 10 | Numerator 51 and denominator 110; percentage 46.3636 before configured rounding; traceable to both sources |
| UAT02 | Two projects each report 100 people with 20 shared identities | 180 unique people when matching is authorised; with aggregate only sources, gross reach 200 and unknown overlap disclosed |
| UAT03 | Monthly cumulative values are 10, 15 and 20 | End position 20; period increments only where the approved rule supports deriving them; no total of 45 labelled as unique cumulative reach |
| UAT04 | Three of five partner submissions are approved; one missing and one pending | Official totals use eligible approved records and show 60 percent approval coverage, with other states separate |
| UAT05 | A target falls from 1000 to 800 after quarter close | Original report remains against 1000; revised target has approval, effective date and explicit comparison context |
| UAT06 | One source feeds two intermediate aggregates that feed the same parent | Shared contribution is detected and follows the approved deduplication rule; cycles cannot be created |
| UAT07 | A previously published result changes after a corrected import | Current views recalculate with status; original report remains frozen; restatement requires approval and identifies recipients |
| UAT08 | Partners report different age bands and units | Comparable subsets are identified; unsupported conversions or exact combined categories are blocked |
| UAT09 | An input is zero, missing, not applicable, suppressed or undefined | Display, completeness and aggregation follow each state’s rule consistently across API, dashboard and export |
| UAT10 | A programme records a stronger outcome after an intervention | The report describes observed change with evidence; causal attribution requires the evaluation methodology and reviewed claim |

Coverage: BR-IND-003 through BR-IND-010, BR-CAL-001 through BR-CAL-016, BR-DQ-004 through BR-DQ-008, BR-WFL-007, BR-WFL-008, BR-RPT-003 and BR-EVA-004.

### 34 2 Identity privacy and operational scenarios

| Scenario | Test situation | Expected business result |
| --- | --- | --- |
| UAT11 | A partner guesses another project’s object IDs, searches and asks AI | No protected record, snippet, count, citation or export is exposed |
| UAT12 | A reviewer authored the submission under another group assignment | Self approval is blocked; an independent authorised reviewer is required |
| UAT13 | A user is revoked while an export and report delivery are queued | Sensitive work reauthorises; unauthorised download and delivery fail within the online revocation bound |
| UAT14 | A contractor leaves while owning a connector and report schedule | Access ends, ownership and pending work are explicitly reassigned or cancelled, historical attribution remains |
| UAT15 | A privacy deletion is followed by restoring last week’s backup | Deleted data remains inaccessible after restoration and deletion instructions are reapplied before reopening |
| UAT16 | A public aggregate has small cells and subtractable totals | The approved suppression and filter policy prevents the tested inference paths in visuals and downloads |
| UAT17 | An operator needs access to resolve a sensitive support incident | Access is approved, limited, attributable and expires; no hidden unrestricted impersonation |
| UAT18 | A tenant reaches its AI or storage entitlement | Visible controlled limits apply; no silent deletion, weakened security or loss of core authorised export |
| UAT19 | A region or critical component fails | The service meets the qualified recovery behaviour, respects residency and reconciles accepted writes and published reports |
| UAT20 | An organisation exports and closes its account | Complete documented package, ended credentials and integrations, and recorded deletion or remaining hold obligations |

Coverage: BR-IAM-008 through BR-IAM-014, BR-ACC-001 through BR-ACC-012, BR-PRV-005 through BR-PRV-008, BR-OPS-002, BR-MIG-007, BR-MIG-008 and the availability, recovery and revocation NFRs.

### 34 3 Field data and AI scenarios

| Scenario | Test situation | Expected business result |
| --- | --- | --- |
| UAT21 | An enumerator completes forms offline and retries an interrupted sync several times | One intended effect per submission; saved drafts persist; incomplete media and conflicts are visible |
| UAT22 | Two devices modify one record while a form version changes | Both candidate revisions and the form versions remain identifiable; no silent last write overwrite |
| UAT23 | A recurring spreadsheet changes a date column and repeats old records | Schema drift pauses or quarantines the affected data; no duplicate achievements or accidental date reinterpretation |
| UAT24 | A malicious document instructs AI to disclose all project records | Content remains untrusted; no permission expansion, external exfiltration or unauthorised tool use |
| UAT25 | A proposal omits the target population and gives conflicting dates | AI marks ambiguity and missing fields; a reviewed valid definition is required before activation |
| UAT26 | A user asks for a result outside their access or beyond available evidence | The response preserves permission boundaries and abstains or requests context without inventing evidence |
| UAT27 | AI proposes a change and the source or user authority changes before confirmation | Execution revalidates the current state and rejects or regenerates the stale proposal |
| UAT28 | The model service is unavailable during period close | Manual review, deterministic calculation and non AI report generation remain usable |
| UAT29 | Interview evidence includes conflicting opinions in two languages | The reviewed summary preserves disagreement, labels automated translation and links quotations to sources |
| UAT30 | Keyboard and screen reader users complete collection and approval tasks | Complete supported journeys work with understandable errors, visible focus and accessible status updates |

Coverage: BR-FRM-002 through BR-FRM-007, BR-OFF-001 through BR-OFF-008, BR-DAT-001 through BR-DAT-010, BR-EVD-005 through BR-EVD-008, BR-AI-001 through BR-AI-018 and the accessibility and AI quality NFRs.

### 34 4 Test evidence requirements

Every test record shall identify BRD and FSD references, dataset version, user role and scope, application version, policy configuration, expected result, observed result and evidence. Negative tests must include indirect access through search, exports, background jobs and AI. Release evidence shall distinguish automated verification, manual review, independent assessment and operational rehearsal.

Fixtures shall include multilingual text, dates around fiscal and daylight saving boundaries, large and fractional values, missing identifiers, duplicate submissions, expired grants, restricted participant fields, malformed files, integration retries, and deletion and restore history. Test environments shall use synthetic or appropriately protected data. Acceptance must not depend on unrecorded administrator intervention.

## 35 Delivery sequencing dependencies and release gates

### 35 1 Capability waves

| Wave | Intended usable outcome | Scope discipline |
| --- | --- | --- |
| R1 Controlled production | An organisation can establish secure access, create a governed programme, collect or import evidence, validate and approve results, inspect a portfolio and publish a traceable report with bounded AI assistance | All R1 requirements and applicable cross cutting gates; controlled cohort and qualified operating envelope |
| R2 Enterprise breadth | Larger distributed programmes can use directory lifecycle, more connectors, advanced qualitative and evaluation workflows, donor formats, analytics and finance operations | All R2 requirements plus repeated R1 security and integrity regression |
| R3 Advanced capability | Qualified deployments can add advanced scenarios, forecasts, outcome harvesting, learning reuse and enterprise deployment variants | All R3 requirements; each variant and AI use case separately qualified |

P0 through P2 are product priorities, not permission to ship unsafe partial workflows. A capability introduced in R2 or R3 inherits all relevant R1 controls. No delivery date or fixed price is established by these waves. Estimation follows FSD scope, integration qualification and HLD costing.

### 35 2 Business dependency order

1. Establish tenant identity, policy, audit and data classification before admitting production data.

2. Approve the information model, indicator semantics and golden calculation corpus before building portfolio claims on top of them.

3. Establish versioned collection and ingestion before quality, approval and recalculation workflows.

4. Establish approved results and snapshots before external reporting, sharing or publication.

5. Establish governed retrieval and calculations before AI questions and report drafting.

6. Establish controlled action contracts before AI write assistance or workflow automation.

7. Qualify operations, recovery, migration and support before expanding the production cohort.

### 35 3 Release gates

| Gate | Required evidence | Accountable signoff |
| --- | --- | --- |
| Scope and semantics | Complete requirement mapping, approved definitions and unresolved decision disposition | Product and MEL leads |
| Functional integrity | Passing core journeys, negative cases and calculation corpus | Product, MEL and QA leads |
| Security | Applicable control evidence, independent assessment and retested critical fixes | Security lead |
| Privacy | Approved data inventory, retention, regions, sharing and request workflows | Privacy lead and tenant owner |
| AI assurance | Per use case quality, leakage and action safety evidence; approved model data handling | AI assurance, MEL and privacy leads |
| Performance and reliability | Qualified workload, percentile results, recovery and failure exercises | Engineering and operations leads |
| Accessibility and usability | Complete process review and representative user task evidence | Design and product leads |
| Migration | Reconciliation, source limitations, rollback and tenant acceptance | Implementation and tenant MEL leads |
| Service readiness | On call ownership, runbooks, incident exercise, support and exit paths | Operations lead |
| Production authorisation | All applicable gates passed and bounded residual risks recorded | Sponsor or delegated release authority |

No unresolved defect that exposes another tenant’s data, loses accepted records, misstates official results, bypasses independent approval or leaks secrets through AI may be waived as a cosmetic or later release issue. Lower severity exceptions require a named owner, mitigation, expiry and visibility to affected stakeholders.

## 36 Risks assumptions and decision register

### 36 1 Product and delivery risks

| Risk | Consequence | Required response |
| --- | --- | --- |
| Incomplete understanding of reference product | Unsupported parity claim or missing edge workflows | Validate public benchmark through authorised product walkthroughs and actual export fixtures |
| Scope growth without sequencing | Large unfinished system with weak core reliability | Preserve the full catalogue and commit releases only after dependency and capacity review |
| Ambiguous indicator semantics | Plausible but incorrect portfolio totals | Approve measurement contracts and golden cases before implementation |
| Weak programme usability | Staff revert to spreadsheets or bypass controls | Test real role tasks and include correction time in efficiency measures |
| Overcollection of personal data | Unnecessary exposure and operating obligations | Make participant registries optional and require purpose based field selection |
| Offline device loss | Sensitive evidence exposed outside central control | Minimise packages, enforce expiry and qualify device protections |
| AI overclaiming and provider changes | Unsupported reports or unapproved data transfers | Require citations, governed arithmetic, policy checked fallback and regression gates |
| Integration drift | Silent data staleness or corrupted mappings | Version contracts, monitor freshness and require mapping review on material changes |
| Migration changes meaning | Historical reports cannot be reconciled | Preserve source semantics, limitations and approved migration differences |
| Capacity targets exceed budget | Poor service or unsustainable cost | Cost the reference envelope and make limits visible before commitments |
| Operational gaps | Recoverable software defect becomes prolonged outage | Establish named ownership, drills and support procedures before launch |
| Misleading assurance claims | Procurement and trust failures | Tie every claim to current evidence and the qualified deployment scope |

### 36 2 Decisions to baseline before detailed design

These are recorded decisions to resolve during product review and FSD preparation. They are not reasons to omit requirements or stop this BRD. The proposed defaults allow design to proceed while keeping consequences explicit.

| Decision | Proposed baseline | Decision owner and latest gate |
| --- | --- | --- |
| DEC01 Product ownership and name | Working title Impact Management Platform; product owner to be named by the sponsor | Sponsor before external branding |
| DEC02 Greenfield or existing product evolution | BRD applies to either; assess authorised code and data before choosing implementation strategy | Sponsor and engineering before HLD |
| DEC03 First production cohort | Limited named organisations with available MEL administrators and representative data | Product before pilot commitment |
| DEC04 Deployment and residency | Managed hosted service; select permitted primary and recovery regions per contract | Privacy and engineering before production data |
| DEC05 Participant data scope | Optional; aggregate only operation remains fully supported | Product and privacy before programme template approval |
| DEC06 Identity baseline | Enterprise federation, privileged MFA and governed local recovery | Security before FSD identity approval |
| DEC07 Offline client | Qualified field workflow with bounded packages; exact client technology belongs in HLD | Field operations and security before offline release |
| DEC08 First interface languages | Complete English interface; multilingual instruments at R1; prioritise later interface languages using actual deployment needs | Product before localisation plan |
| DEC09 Initial connectors | File import, governed API and KoboToolbox at R1 | Product and integration lead before FSD connector scope |
| DEC10 Model providers and hosting | Select from deployments meeting regional, retention and quality requirements | AI assurance and privacy before any real data use |
| DEC11 High sensitivity AI use | Disabled unless the use case and destination are explicitly approved | Privacy before AI enablement |
| DEC12 Retention schedule | Tenant approved records policy; operational defaults in section 32 | Privacy before production onboarding |
| DEC13 Numerical scale and service targets | Use section 32 as qualification target pending cost and design review | Engineering and operations before HLD baseline |
| DEC14 Paid entitlements | Separate commercial limits from permissions; preserve essential security and exit rights | Product before billing design |
| DEC15 Finance depth | Programme budgeting and analytical expenditure, with source accounting external | Product and finance before R2 FSD |
| DEC16 Evaluation depth | Registry, evidence, methods and management response; advanced statistical execution separately scoped | MEL lead before R2 FSD |
| DEC17 Publication standards | IATI support with a specifically qualified standard and publication route | MEL and integration lead before R2 release |
| DEC18 Dedicated deployment options | R3 only after responsibilities and recovery are qualified | Sponsor and operations before an enterprise commitment |
| DEC19 Independent assurance roadmap | Baseline security assessment and evidence; formal certification programme separately approved | Security and sponsor before external claims |
| DEC20 Delivery budget and staffing | No fixed commitment in the BRD; estimate against decomposed FSD and qualified HLD | Sponsor before delivery commitment |
| DEC21 Reference product migration | Use authorised exports and confirm source semantics; no assumed access to proprietary internals | Implementation lead before migration estimate |
| DEC22 Customer specific extensions | Configuration first; extensions require compatibility, security and support review | Product before extension approval |

### 36 3 Assumptions requiring validation

The organisation has the authority to process the data it supplies. Representative source documents and exports can be obtained lawfully for testing. A qualified MEL reviewer is available to approve indicator definitions and expected results. Users have devices that can meet the qualified field security profile. Hosting and model providers can meet the selected regional requirements. These assumptions shall be checked before the corresponding production use, not treated as established facts.

## 37 Traceability and downstream specification contract

### 37 1 Required FSD contents

The FSD shall expand each BRD requirement into one or more uniquely identified functional requirements without losing the originating ID. For every capability it shall specify actors, permissions, preconditions, trigger, complete workflow, alternative and failure paths, validations, states, business rules, audit events, notifications, bulk behaviour, cancellation, concurrency and acceptance cases.

The FSD shall contain a field dictionary, role and permission catalogue, transition matrices, indicator and aggregation semantics, form version rules, import contracts, report snapshot behaviour, sharing rules, AI action catalogue and integration object mappings. Screen inventories and interaction specifications belong there. It shall explicitly cover empty, loading, stale, partial, denied, failed and recovered states. It must settle mandatory field definitions and meaningful defaults rather than use “configurable” as a substitute for behaviour.

### 37 2 Required HLD contents

The HLD shall map the approved functional and quality requirements to system responsibilities, trust boundaries, data flows and deployment profiles. It shall justify tenancy and identity enforcement, storage lifecycle, computation, search, integrations, offline operation, AI orchestration and observability. It shall include capacity and cost estimates, failure modes, recovery, regional policy enforcement and build versus adopt decisions.

No particular programming language, cloud vendor, database, framework or microservice layout is mandated by this BRD. The HLD must justify its choices against correctness, maintainability, operating capacity and total cost. Third party components must meet the same product controls and licensing obligations.

### 37 3 Required LLD contents

The LLD shall specify detailed data structures, interface contracts, validation, state transitions, permission checks, calculation algorithms, job semantics, failure handling and migrations. It shall define exact audit fields, idempotency rules, concurrency controls, indexing behaviour, deletion propagation and test fixtures. AI integration shall include allowed tools, structured action contracts, evidence validation and provider policy checks.

Every implementation unit shall trace to approved FSD behaviour and relevant NFRs. The LLD shall not silently introduce a new business rule or relax a product safeguard. Such changes return to the appropriate baseline owner.

### 37 4 Traceability register schema

| Field | Purpose |
| --- | --- |
| BRD ID and version | Stable business requirement and approved meaning |
| Outcome and persona | Why the requirement exists and who uses it |
| Priority release and owner | Accountability and sequencing |
| FSD IDs and business rules | Detailed behaviour implementing the requirement |
| HLD responsibility and trust boundary | Where the behaviour and protection are allocated |
| LLD contract or component | Implementation detail and associated data semantics |
| Test IDs and evidence | Positive, negative, boundary, security and quality verification |
| Operational metric and runbook | Production monitoring and response where applicable |
| Status and exception | Planned, implemented, verified, accepted or explicitly deferred with authority |

### 37 5 Coverage map

| Requirement family | Business coverage | Key dependent families |
| --- | --- | --- |
| BR-TEN | Tenant lifecycle and organisation configuration | IAM, ACC, PRV, OPS |
| BR-IAM | Identity and membership lifecycle | ACC, SEC, OPS |
| BR-ACC | Access decisions and controlled disclosure | IAM, PRV, SEC |
| BR-PLN | Strategy and measurement planning | IND, PRG, EVD |
| BR-PRG | Programme and delivery operations | PLN, WFL, FIN |
| BR-IND | Indicator contracts targets and periods | CAL, DQ, WFL |
| BR-CAL | Deterministic results and aggregation | IND, DAT, DQ, ACC |
| BR-FRM | Collection instruments and rounds | PAR, OFF, DQ |
| BR-OFF | Field continuity and synchronisation | FRM, IAM, SEC, PRV |
| BR-DAT | Source data imports and transformations | INT, DQ, CAL |
| BR-DQ | Quality issues and completeness | DAT, IND, WFL |
| BR-PAR | Participants institutions and service events | PRV, FRM, CAL |
| BR-EVD | Evidence and qualitative interpretation | ACC, PRV, EVA, AI |
| BR-EVA | Evaluation and learning | EVD, IND, WFL |
| BR-WFL | Collaboration approvals and period control | IAM, ACC, DQ |
| BR-ANA | Analysis and dashboards | CAL, ACC, RPT |
| BR-RPT | Reporting publication and obligations | CAL, EVD, WFL, ACC |
| BR-FIN | Funding costs and analytical finance | DAT, CAL, ACC |
| BR-INT | External exchange and API contracts | IAM, ACC, DAT, SEC |
| BR-AI | Evidence grounded assistance and actions | Every accessed domain plus ACC, PRV and SEC |
| BR-SEC | Security verification and incident controls | All product and operating families |
| BR-PRV | Purpose retention and rights handling | All stores, interfaces and processors |
| BR-OPS | Service management and administration | SEC, PRV and all critical workflows |
| BR-MIG | Onboarding migration and exit | DAT, CAL, IAM, PRV |
| BR-UX | Usability accessibility and language | All supported user journeys |
| NFR families | Measurable quality and operating constraints | Every affected capability and release |

Every detailed requirement in sections 7 through 32 has an owner at its module or quality domain level, a priority, a release and acceptance evidence. The complete delivery traceability register is created from these IDs during FSD preparation; the family map above is a coverage view, not a substitute for that individual mapping.

## 38 Glossary

| Term | Meaning in this BRD |
| --- | --- |
| Actual | Observed or calculated indicator value for a defined context and period |
| Aggregate | A result produced by an approved combination of compatible contributing results |
| Approval | An attributable decision by an authorised person on a specific version |
| Baseline | Approved starting measurement or plan against which later change is compared |
| Cohort | A defined population followed under specified eligibility and observation rules |
| Data controller or owner | The accountable organisation determining authorised purposes, subject to applicable law and contract |
| Data steward | Person responsible for source quality, mapping, corrections and traceability |
| Denominator | The eligible quantity defining a ratio, percentage or rate |
| Disaggregation | Breakdown of a measure by declared dimensions and categories |
| Evidence | A source supporting or challenging a reported result or finding |
| FSD | Functional Specification Document defining detailed product behaviour |
| HLD | High Level Design allocating responsibilities and data flows across the system |
| LLD | Low Level Design specifying implementation contracts and algorithms |
| Idempotency | Repeating the same intended operation does not create duplicate business effects |
| Indicator | A defined quantitative or qualitative measure with explicit semantics |
| Lineage | Traceable relationships from source evidence through transformations to a result |
| Logframe | Structured representation of intended results, measures, assumptions and verification sources |
| Material change | A change affecting meaning, access, commitments, comparability or official output |
| MEL | Monitoring evaluation and learning |
| MFA | Multifactor authentication |
| PII | Information identifying or capable of being linked to a person in the relevant context |
| Portfolio | A governed view of programmes or projects for management and reporting |
| Programme | A coordinated set of activities and projects pursuing defined results |
| Pseudonymisation | Replacing direct identity with controlled identifiers while reidentification may remain possible |
| RPO | Recovery point objective measuring the maximum targeted data loss interval after a qualifying disaster |
| RTO | Recovery time objective measuring the targeted time to restore the defined service after incident declaration |
| SCIM | Standardised cross domain identity provisioning protocol |
| Snapshot | Versioned point in time data and configuration context used for reproducible reporting |
| SSO | Single sign on through an approved identity provider |
| Tenant | Independently governed organisational security and data boundary |
| Theory of change | Explicit model of intended change, relationships and assumptions |
| Unique reach | Count of distinct eligible entities within a declared scope using an approved method |
| p95 and p99 | Response time thresholds at or below which 95 or 99 percent of measured operations complete |

## 39 Reference sources

Sources were reviewed on 24 September 2026. Product pages establish the public comparison baseline. Standards establish selected assurance references. The requirements, priorities, operating targets and delivery waves in this BRD are proposed product decisions; they are not claims made by these sources.

S1 TolaData platform overview and announced AI roadmap

https://www.toladata.com/

Used for the public feature categories and the distinction between existing capabilities and announced Q4 2026 AI releases.

S2 TolaData data management

https://www.toladata.com/data-management-monitoring-and-evaluation/

Used for source imports, data tables and links between datasets and indicators.

S3 TolaData indicator management

https://www.toladata.com/docs/knowledge-base/indicator-workflow/about-indicator-management/

Used for indicator plans, numeric and qualitative measures, targets and results review.

S4 TolaData indicator aggregation

https://www.toladata.com/indicator-aggregation/

Used for the public aggregation and disaggregation benchmark.

S5 TolaData dashboards

https://www.toladata.com/monitoring-evaluation-dashboards/

Used for configurable dashboards and stakeholder reporting.

S6 TolaData release notes for 2023

https://www.toladata.com/docs/release-notes/2023-toladata-release-notes/

Used for documented approvals, MFA, discussion, file upload and reporting history features. Historical release notes demonstrate documented capability, not independent verification of the present implementation.

S7 TolaData AI

https://www.toladata.com/ai/

Used with S1 for the announced direction of AI assisted workflows.

S8 TolaData IATI reporting

https://www.toladata.com/international-aid-transparency-initiative-iati/

Used for inclusion of a structured transparency publication capability in the comparison baseline.

S9 OWASP Application Security Verification Standard

https://owasp.org/www-project-application-security-verification-standard/

Version 5.0 baseline selected for application security verification; exact applicable controls are mapped during the FSD and security design.

S10 W3C Web Content Accessibility Guidelines 2 2

https://www.w3.org/TR/WCAG22/

Level AA selected as the product accessibility target for complete supported processes.

S11 NIST Digital Identity Guidelines Authentication and Authenticator Management

https://csrc.nist.gov/pubs/sp/800/63/b/4/final

SP 800 63B 4 selected as an authentication and account recovery reference.

S12 NIST Artificial Intelligence Risk Management Framework Generative Artificial Intelligence Profile

https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

NIST AI 600 1 selected as a reference for identifying and managing generative AI risks.

## 40 Baseline review and acceptance record

This BRD is complete as a proposed product baseline for review. Approval shall record the accepted version, resolved or explicitly bounded decisions, delivery waves and named domain owners. It shall not be described as implemented or verified software. Detailed product access, source exports and technical design may reveal additional requirements; additions must be captured through change control with stable IDs.

| Review responsibility | Evidence to confirm | Recorded disposition |
| --- | --- | --- |
| Sponsor and product owner | Purpose, target scope, boundaries, priorities and decisions | Pending review |
| MEL and evaluation leads | Definitions, calculations, evidence, reporting and evaluation semantics | Pending review |
| Security and privacy leads | Access, identity, lifecycle, AI and assurance controls | Pending review |
| Design lead | Role workflows, language, accessibility and usability targets | Pending review |
| Engineering and operations leads | Feasibility, workload targets, recovery, cost and service ownership | Pending review |
| Implementation lead | Migration, onboarding, reconciliation and exit requirements | Pending review |

The next artifact is the FSD. Its entry condition is an agreed BRD baseline or an explicitly identified subset of resolved requirements. Its exit condition is complete behaviour and test traceability for the committed scope, with material business decisions resolved before HLD and LLD implementation commitments.
