# Imprana Commons backlog: Access control
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Access control

  Rule: FR-ACC-001 Deny by default
    As a Platform Operator, I want every read and write to be authorised against each resource and related reference by default, so that a supplied tenant or record ID can never be used to reach data the user is not permitted to access.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-001 @R1-Pilot @Must
    Scenario: Authorise every resource and reference
      When a request reads or writes a resource
      Then the resource and each related reference are authorised before access
      And a client supplied tenant or object ID is treated only as a selector

    @FR-ACC-001 @R1-Pilot @Must
    Scenario: Check batch items individually
      When a batch request is submitted
      Then each item is checked
      And only permitted item outcomes are exposed

    @FR-ACC-001 @R1-Pilot @Must
    Scenario: Reject a cross tenant reference
      Given a valid form submission
      When the participant ID is replaced with one from another tenant
      Then the reference is rejected
      And no cross tenant relationship is recorded

    @FR-ACC-001 @R1-Pilot @Must
    Scenario: Reject leaky responses and failing open
      When a protected unknown ID is requested or policy cannot be resolved
      Then RESOURCE_UNAVAILABLE is returned without record names or counts
      And the action is denied rather than using a cached broad role

  Rule: FR-ACC-002 Fine grained scope
    As an Organisation Administrator, I want to grant access by action, project or partner scope, record condition and field category separately, so that people can see and do exactly what their role needs and nothing more.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-002 @R1-Pilot @Must
    Scenario: Define a fine grained grant
      When the Organisation Administrator creates a grant
      Then they select action, project or partner scope, record condition and permitted field categories separately
      And sensitive view, download, approval and publication are granted independently from ordinary read

    @FR-ACC-002 @R1-Pilot @Must
    Scenario: Apply row and field policy first
      When a member reads records
      Then row and field policy is applied before filters, sorting, aggregation or export

    @FR-ACC-002 @R1-Pilot @Must
    Scenario: Leave omitted hidden fields unchanged
      Given a field is hidden from a member
      When they save an editable row without that field
      Then the omitted field is not cleared

    @FR-ACC-002 @R1-Pilot @Must
    Scenario: Reject actions outside a narrow grant
      Given a Reviewer is granted access to one candidate and its necessary evidence
      When they attempt to edit the source or export the registry
      Then both attempts fail

    @FR-ACC-002 @R1-Pilot @Must
    Scenario: Reject writing a hidden field
      Given a row is editable but a field is hidden from the member
      When they attempt to write the hidden field
      Then the write is denied

  Rule: FR-ACC-003 Effective permissions
    As an Organisation Administrator, I want to inspect effective access for an action, including grant paths, restrictions and missing assurance, and simulate members within my scope, so that I can explain and fix access without exposing hidden information.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-003 @R1-Pilot @Must
    Scenario: Inspect effective access
      When the Organisation Administrator inspects effective access for a selected action and a subject within their administration scope
      Then each permitted grant path, restriction and missing assurance is shown

    @FR-ACC-003 @R1-Pilot @Must
    Scenario: Explain a normal user's own access
      When a normal user inspects their own access
      Then they see explanations only about their own permitted context

    @FR-ACC-003 @R1-Pilot @Must
    Scenario: Resolve conflicting roles
      Given a person has both analyst and partner templates
      And a restriction applies to another partner's rows
      When their access is inspected
      Then the restriction remains effective
      And the explanation identifies the scope rule safely

    @FR-ACC-003 @R1-Pilot @Must
    Scenario: Reject leaking hidden information
      When a denial is explained or the Organisation Administrator attempts to simulate a subject outside their administration scope
      Then names of hidden projects and sensitive field values are not exposed
      And the out of scope simulation is refused

  Rule: FR-ACC-004 Separation of duties
    As a MEL Manager, I want approvals to be accepted only from reviewers who are genuinely independent of the candidate's authors, so that four-eyes review cannot be bypassed through roles, groups, delegation or aliases.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-004 @R1-Pilot @Must
    Scenario: Accept an independent approval
      Given a candidate's author set, verified identity aliases, delegated authorisation and current reviewer assignment have been calculated
      When a Reviewer who is not a material author approves it
      Then the approval is accepted

    @FR-ACC-004 @R1-Pilot @Must
    Scenario: Invalidate decisions when the candidate is edited
      Given a candidate has existing decisions
      When the candidate is edited
      Then it returns to draft
      And the old candidate decisions are invalidated

    @FR-ACC-004 @R1-Pilot @Must
    Scenario: Reject self approval through a second group
      Given the author of a candidate becomes a Reviewer through a second group
      When they attempt to approve the candidate
      Then the approval is rejected
      And a different eligible person is still required

    @FR-ACC-004 @R1-Pilot @Must
    Scenario: Reject other routes to false independence
      Given the approver overlaps the material authors through a role switch, group change, delegated task, service identity or verified alias
      When approval is attempted
      Then it is not counted as independent
      And an emergency exception requires a separately approved policy and cannot silently count self approval as independent

  Rule: FR-ACC-005 Permission safe derivation
    As an Analyst, I want dashboards, search results, saved analyses and AI answers to carry the restrictions of their sources, so that derived or copied content never reveals restricted data to people who could not see the sources.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-005 @R1-Pilot @Must
    Scenario: Recheck source restrictions on read
      Given a private derivative records its source restriction dependencies
      When a dashboard, search result, saved analysis or AI answer is read
      Then those dependencies are rechecked for the reader

    @FR-ACC-005 @R1-Pilot @Must
    Scenario: Serve an approved public aggregate
      Given an approved public aggregate
      When it is viewed
      Then it is served from a separate disclosure artifact with fixed approved content
      And no private drill down is available

    @FR-ACC-005 @R1-Pilot @Must
    Scenario: Reject leaking a restricted metric through a copy
      Given a restricted dashboard
      When an Analyst copies it to a partner workspace
      Then a new governed object is created that preserves the restrictions
      And the restricted metric remains unavailable until a valid substitute or disclosure is approved

    @FR-ACC-005 @R1-Pilot @Must
    Scenario: Reject treating mixed sources as public
      Given a result combines one public and one restricted source
      When its visibility is determined
      Then the result is not treated as public

  Rule: FR-ACC-006 External access lifecycle
    As a MEL Manager, I want to share a specific artifact version with a defined audience, permitted actions, owner, reason and expiry, previewed as the recipient will see it, so that external sharing is deliberate and stops when it should.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-006 @R1-Pilot @Must
    Scenario: Create a share
      When the MEL Manager shares an artifact
      Then they must specify the artifact version, audience, permitted actions, owner, reason and expiry
      And the preview uses the intended recipient's effective view
      And authenticated external access is the default

    @FR-ACC-006 @R1-Pilot @Must
    Scenario: Limit public links
      When a public link is requested
      Then it is allowed only for approved public artifacts

    @FR-ACC-006 @R1-Pilot @Must
    Scenario: Revalidate on classification change
      Given an artifact has existing disclosures
      When its classification changes
      Then existing disclosures are revoked or revalidated

    @FR-ACC-006 @R1-Pilot @Must
    Scenario: Reject access after revocation
      Given a seven day report link has been issued
      When the MEL Manager revokes it after one day
      Then old URLs and generated download references cease serving the artifact

    @FR-ACC-006 @R1-Pilot @Must
    Scenario: Reject link possession as authorisation
      Given a link to sensitive data or an expired link
      When someone opens it
      Then link possession alone does not authorise the sensitive data
      And an expired link shows unavailable without an artifact preview

  Rule: FR-ACC-011 Access changes and existing artifacts
    As an Organisation Administrator, I want a grant change to take effect across sessions, caches, queued jobs, generated artifacts and AI content, so that removed access is actually removed everywhere the platform controls.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-ACC-011 @R1-Pilot @Must
    Scenario: Propagate a grant change
      When the Organisation Administrator changes a grant
      Then a revocation event covers active sessions, cached reads, queued jobs, generated artifacts and AI dependencies
      And new sensitive actions evaluate current policy immediately
      And online presentation converges within 60 seconds

    @FR-ACC-011 @R1-Pilot @Must
    Scenario: Report previously downloaded copies
      Given copies were downloaded before the grant change
      When the revocation is processed
      Then those copies are reported as external disclosures rather than remotely erased

    @FR-ACC-011 @R1-Pilot @Must
    Scenario: Reject revoked source text in saved AI answers
      Given an AI answer citing a source has been saved
      When access to that source is removed and the conversation is reopened
      Then the revoked source text is not revealed, including through its summary

    @FR-ACC-011 @R1-Pilot @Must
    Scenario: Reject stale presentation beyond the bound
      Given a grant has been removed
      When more than 60 seconds have passed
      Then no online presentation under platform control still shows the revoked content

  Rule: FR-ACC-007 Export and bulk access
    As an Analyst, I want to preview exports and receive downloads that stay tied to current authorisation, so that I can extract the data I am entitled to while exports stop working once access is revoked.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-ACC-007 @R2-Scale @Must
    Scenario: Preview an export
      When an Analyst prepares an export
      Then the preview lists selected fields, filters, classification, row estimate and intended format

    @FR-ACC-007 @R2-Scale @Must
    Scenario: Authorise at each stage
      When the export is requested, starts execution, generates sensitive output and is downloaded
      Then authorisation is checked at each of those points
      And the receipt identifies the export owner and expiry

    @FR-ACC-007 @R2-Scale @Must
    Scenario: Reject download after revocation
      Given an export has been generated
      When the requester is revoked before download
      And retrieval is attempted from the original URL
      Then no bytes are served after the revocation bound

    @FR-ACC-007 @R2-Scale @Must
    Scenario: Reject reliance on an old signature
      Given a generated download link
      When it is used after the policy grant has ended
      Then access is refused because downloads must be authenticated or bound to a current approved disclosure

  Rule: FR-ACC-008 Privileged support access
    As a Support Agent, I want time-bound, case-scoped elevated access under my own identity, so that I can diagnose a tenant's problem with their consent while every action is attributable and the tenant can end access at any time.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-ACC-008 @R2-Scale @Must
    Scenario: Open a support session
      Given a support case tied to the tenant consent policy, requested objects, purpose and duration
      When the Support Agent accesses the tenant using their real identity and an active elevation grant
      Then every sensitive read and mutation is attributed to them

    @FR-ACC-008 @R2-Scale @Must
    Scenario: Tenant ends support access
      Given an active support session
      When the Organisation Administrator ends access
      Then the Support Agent's access ends immediately

    @FR-ACC-008 @R2-Scale @Must
    Scenario: Reject operations outside the approved scope
      Given a support session approved for one failed import
      When the Support Agent reads the import diagnostics and then attempts an owner transfer
      Then the diagnostic read succeeds
      And the owner transfer is denied

    @FR-ACC-008 @R2-Scale @Must
    Scenario: Reject hidden or excessive support access
      Given a support session without explicit download or participant identity scope
      When the Support Agent attempts to download data, view participant identities, impersonate a user or use a universal support account
      Then each attempt is refused

  Rule: FR-ACC-009 Privacy preserving aggregates
    As a Privacy Officer, I want to configure and test suppression rules for published aggregates, so that totals, cross tables and filters cannot be combined to reveal small groups.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-ACC-009 @R2-Scale @Must
    Scenario: Configure and test disclosure rules
      When the Privacy Officer selects a minimum cell threshold, complementary suppression and allowed fixed slices
      Then the preview tests totals, cross tables and filter combinations for reconstruction
      And the default threshold of five is applied as a minimum rule

    @FR-ACC-009 @R2-Scale @Must
    Scenario: Return the same suppressed output everywhere
      When the aggregate is retrieved through public APIs or downloads
      Then the same suppressed representation is returned without hidden raw values

    @FR-ACC-009 @R2-Scale @Must
    Scenario: Reject reconstruction by differencing
      Given groups of two and eight with a total of ten
      When the aggregate is published
      Then the eight and ten combination is not exposed if it reveals the suppressed two

    @FR-ACC-009 @R2-Scale @Must
    Scenario: Reject slices that cannot be bounded
      Given complementary suppression or differencing cannot be bounded for a slice
      When publication is attempted
      Then the affected slice is withheld or only a reviewed fixed artifact is exposed

  Rule: FR-ACC-010 Partner limited collaboration
    As a Programme Manager, I want partner organisations to see only the obligations and artifacts assigned to them across every list, search and preview, so that partners can collaborate without learning anything about other partners' data.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-ACC-010 @R2-Scale @Must
    Scenario: Apply partner scope everywhere
      Given a partner organisation is assigned to specified obligations and shared artifacts
      When a Partner Organisation User views lists, comments, mentions, lookup suggestions, task counts or previews
      Then only items within that scope are shown

    @FR-ACC-010 @R2-Scale @Must
    Scenario: Provide funder access through approved views
      When a Funder Portfolio Manager views partner results
      Then access is through separately approved result views

    @FR-ACC-010 @R2-Scale @Must
    Scenario: Reject leaks through search and guessed URLs
      Given a Partner Organisation User
      When they search for another partner's participant name or request a guessed report URL
      Then neither reveals existence, snippet or count

    @FR-ACC-010 @R2-Scale @Must
    Scenario: Reject access through author identity or unapproved summaries
      Given a Partner Organisation User authored content in a shared programme
      When they attempt to open another partner's contributor record or view shared summary status without an approved definition
      Then access is denied

  Rule: FR-ACC-012 Administrative review and simulation
    As an Organisation Administrator, I want to draft an access change and simulate its effect on representative people before applying it, so that I understand gained and lost access and sensitive expansions get a second review.
    Release: R3 Ecosystem · Priority: Should · Built today: Partial

    @FR-ACC-012 @R3-Ecosystem @Should
    Scenario: Simulate an access change
      Given an Organisation Administrator drafts an access change and chooses representative subjects
      When they preview it
      Then gained and lost capabilities, affected restricted classes, links and schedules are calculated

    @FR-ACC-012 @R3-Ecosystem @Should
    Scenario: Approve a sensitive expansion
      Given the change expands sensitive access
      When it is executed
      Then a second eligible Reviewer must approve it
      And a current policy comparison is made at execution

    @FR-ACC-012 @R3-Ecosystem @Should
    Scenario: Reject execution on a stale preview
      Given an Organisation Administrator previewed expanding a group to a new programme
      When the group's membership changes before execution
      Then execution requires a fresh preview

    @FR-ACC-012 @R3-Ecosystem @Should
    Scenario: Reject simulation side effects or overexposure
      When the Organisation Administrator runs a simulation
      Then nothing is changed
      And no data beyond their review scope is revealed, with counts or redacted scope labels used only when permitted
