# Imprana Commons backlog: Tenancy and organisation
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Tenancy and organisation

  Rule: FR-TEN-001 Tenant lifecycle
    As a Platform Operator, I want to create, activate, suspend, reactivate and close tenants through a controlled lifecycle, so that each organisation's workspace is set up safely and can be paused or exited without losing recorded data or affecting other tenants.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-TEN-001 @R1-Pilot @Must
    Scenario: Create and activate a requested tenant
      Given a requested tenant with an owner invitation and a selected policy profile
      When the Platform Operator activates the tenant
      Then activation checks for a verified owner, recovery contact, region, retention and identity settings
      And the tenant becomes active only when those checks pass

    @FR-TEN-001 @R1-Pilot @Must
    Scenario: Suspend a tenant with work in progress
      Given tenant A has a running import and a report schedule
      And tenant B is active
      When the Platform Operator reviews the preview of scheduled writes and suspends tenant A
      Then rows already accepted by the import remain recorded
      And future writes stop at the cancellation boundary
      And policy permitted support and exit access is preserved
      And tenant B continues normally

    @FR-TEN-001 @R1-Pilot @Must
    Scenario: Reject automatic replay of queued writes on reactivation
      Given tenant A was suspended with queued writes
      When the Platform Operator reactivates tenant A
      Then expired grants and source credentials are rechecked
      But the queued writes are not replayed automatically

    @FR-TEN-001 @R1-Pilot @Must
    Scenario: Reject closure that skips holds
      Given tenant A is subject to a hold
      When the Platform Operator attempts to close tenant A outside the exit workflow or without resolving the hold
      Then the closure is refused

  Rule: FR-TEN-002 Organisation structures
    As an Organisation Administrator, I want to create organisational units and move units or projects with a preview of the effects and an effective date, so that our structure stays accurate without silently changing access or rewriting historical reports.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-TEN-002 @R1-Pilot @Must
    Scenario: Create a unit
      Given an Organisation Administrator
      When they create a unit with a stable code and an optional parent
      Then the unit is created with that code and parent

    @FR-TEN-002 @R1-Pilot @Must
    Scenario: Move a project with a preview and effective date
      Given project P belongs to office East
      When the Organisation Administrator previews moving project P to office West effective 1 July
      Then the preview shows the reporting membership, every explicit access grant that would change and future obligations
      When they confirm the move
      Then the change applies from 1 July and the old parent East is recorded
      And June reporting retains East as its organisational context

    @FR-TEN-002 @R1-Pilot @Must
    Scenario: Reject self parenting and descendant cycles
      Given unit U has a descendant unit D
      When the Organisation Administrator sets U as its own parent or sets D as the parent of U
      Then the change is rejected

    @FR-TEN-002 @R1-Pilot @Must
    Scenario: Reject implicit changes to existing grants
      Given a confirmed move would affect existing access grants
      When the move is applied
      Then existing grants change only through an explicit reviewed access change
      And historical reports retain their original organisational context

  Rule: FR-TEN-003 Multiple memberships
    As a Reviewer with memberships in more than one tenant, I want to switch between tenants with each tab staying bound to its own tenant, so that my rights and data in one organisation can never be used or exposed in another.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-TEN-003 @R1-Pilot @Must
    Scenario: List memberships and open a second tenant
      Given a Reviewer with active memberships in tenants A and B
      When they open the tenant selector
      Then it lists their active memberships and display identities
      When they open tenant B in a new tab
      Then existing tabs remain bound to tenant A

    @FR-TEN-003 @R1-Pilot @Must
    Scenario: Switch tenant in the same tab
      Given a Reviewer is working in tenant A in a tab
      When they switch that tab to tenant B
      Then tenant A scoped recent items and unsent AI context are cleared

    @FR-TEN-003 @R1-Pilot @Must
    Scenario: Reject reuse of a permission from another tenant
      Given a Reviewer holds reviewer rights in tenant A and collector rights in tenant B
      And they approve an item from a tenant A tab
      When the tenant B tab attempts to reuse that permission or source reference
      Then the command is rejected because the resource belongs to another tenant

    @FR-TEN-003 @R1-Pilot @Must
    Scenario: Reject restoring protected cached content on back navigation
      Given a Reviewer has left a protected page
      When they use browser back navigation to return to it
      Then the historic page is reauthorised
      And protected cached content is not restored without reauthorisation

  Rule: FR-TEN-010 Ownership continuity
    As an Executive Director, I want to hand over workspace ownership to a verified successor and have a controlled recovery path if the last owner is unavailable, so that the organisation never loses custody of its workspace and every transfer is traceable.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-TEN-010 @R1-Pilot @Must
    Scenario: Transfer ownership between two actors
      Given the Executive Director is the current owner
      When they nominate an active eligible successor
      Then the system previews the commercial and administrative responsibilities
      When the successor verifies identity and accepts custody after step up
      Then ownership transfers and both actors are recorded in a complete custody history

    @FR-TEN-010 @R1-Pilot @Must
    Scenario: Recover an unavailable last owner
      Given the last owner is unavailable
      When recovery of ownership is requested
      Then it proceeds only through a verified case with distinct approval

    @FR-TEN-010 @R1-Pilot @Must
    Scenario: Reject removing the sole owner
      Given the Executive Director is the final eligible owner
      When someone attempts to revoke or suspend them through ordinary member administration without a successor or approved closure path
      Then the action fails

    @FR-TEN-010 @R1-Pilot @Must
    Scenario: Reject automatic participant identity access
      Given an ownership transfer has completed
      When the new owner attempts to view participant identities
      Then access is not granted by the transfer itself

  Rule: FR-TEN-004 Configuration and terminology
    As an Organisation Administrator, I want to propose dated changes to labels, code lists, reporting calendar, time zone or units with a preview of affected schedules and drafts, so that changes apply going forward while historical data keeps the configuration it used.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-TEN-004 @R2-Scale @Should
    Scenario: Preview and approve a configuration change
      Given an Organisation Administrator proposes a label, code list, reporting calendar, time zone or unit change with an effective date
      When they preview the change
      Then the preview lists dependent schedules and drafts
      And once approved the new version applies prospectively

    @FR-TEN-004 @R2-Scale @Should
    Scenario: Historical objects keep their configuration version
      Given an output label has been renamed and the next fiscal year start changed
      When a prior snapshot is opened
      Then its original labels and period membership remain reconstructable

    @FR-TEN-004 @R2-Scale @Should
    Scenario: Reject a label edit that changes a stable code
      Given a code list entry with a stable code
      When the Organisation Administrator edits its display label
      Then the stable code is not changed

    @FR-TEN-004 @R2-Scale @Should
    Scenario: Reject an unsafe fiscal boundary change
      Given an Organisation Administrator changes the fiscal year boundary
      When they attempt to apply it without a new calendar and explicit regeneration of future obligations
      Then the change is rejected
      And a calendar that creates overlapping official periods is also rejected

  Rule: FR-TEN-005 Custom fields and templates
    As an Organisation Administrator, I want to define and publish versioned custom fields with type, code, applicable objects, required condition, validation and classification, so that teams capture the extra data they need while access restrictions and history are preserved.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-TEN-005 @R2-Scale @Should
    Scenario: Preview and publish a custom field
      Given an Organisation Administrator selects a field type, stable code, permitted object types, required condition, validation and classification
      When they preview the field
      Then the preview shows its availability in forms, imports, search and reports
      And publishing creates a field definition version that templates reference

    @FR-TEN-005 @R2-Scale @Should
    Scenario: Use a restricted conditional field
      Given a published restricted decimal field required only for active grants
      When an authorised import supplies values for the field
      Then the import succeeds
      And an external viewer sees neither the value nor a search facet for the field

    @FR-TEN-005 @R2-Scale @Should
    Scenario: Retire a field
      Given a field with historical values
      When the Organisation Administrator retires it
      Then new entry is no longer possible
      And historical values and their restricted visibility are preserved

    @FR-TEN-005 @R2-Scale @Should
    Scenario: Reject a type change without a migration mapping
      Given a field that already has values
      When the Organisation Administrator changes its type without an explicit migration mapping
      Then the change is rejected
      And they must supply a migration mapping or create a new field

  Rule: FR-TEN-006 Partner and consortium boundaries
    As a Programme Manager, I want to set up partner agreements that define shared projects, artifacts, allowed actions, purpose, dates and owner, so that I can collaborate with partners while every exchange is explicit, recorded and limited to what was agreed.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-TEN-006 @R2-Scale @Must
    Scenario: Create a partner agreement
      Given a Programme Manager
      When they create a partner agreement naming projects, shared artifacts, allowed actions, purpose, dates and owner
      Then the agreement is recorded
      But it grants no tenant membership by itself

    @FR-TEN-006 @R2-Scale @Must
    Scenario: Exchange an artifact across tenants
      Given an active partner agreement
      When an artifact is exchanged across tenants under it
      Then an explicit destination copy is created with the source version and agreement reference
      And the transfer is recorded in the sharing register

    @FR-TEN-006 @R2-Scale @Must
    Scenario: Share one indicator definition with two partners
      Given an approved indicator definition shared with partners X and Y
      When each partner submits data against it
      Then each partner sees only its own submissions
      And neither receives the other's completion statistics unless explicitly disclosed

    @FR-TEN-006 @R2-Scale @Must
    Scenario: Reject transfers after the agreement expires
      Given a partner agreement has expired
      When a new transfer is attempted under it
      Then the transfer is refused
      And live access is revoked
      And the agreed restriction or deletion process for retained copies starts, with external completion tracked separately

  Rule: FR-TEN-007 Policy inheritance and exceptions
    As an Organisation Administrator, I want to see effective tenant and project policies with the source of each restriction and manage tightening and time-bound exceptions, so that stricter rules apply reliably and any relaxation is justified, independently approved and expires.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-TEN-007 @R2-Scale @Must
    Scenario: Inspect effective policy
      Given a project that inherits tenant policies
      When the Organisation Administrator opens the policy editor
      Then it shows the effective tenant and project rules with the source of each restriction

    @FR-TEN-007 @R2-Scale @Must
    Scenario: Tighten a policy
      Given the Organisation Administrator tightens a rule
      When the impact is shown and they confirm it
      Then the tighter rule is applied

    @FR-TEN-007 @R2-Scale @Must
    Scenario: Request a permitted relaxation
      Given a relaxation that policy permits
      When the Organisation Administrator requests it
      Then an exception request is opened specifying scope, reason, compensating control, independent approver and expiry
      And when the exception expires the stricter rule is restored and dependent jobs are rechecked

    @FR-TEN-007 @R2-Scale @Must
    Scenario: Reject overriding a tenant prohibition
      Given the tenant prohibits public raw participant exports
      And a project administrator owns the dataset
      When an attempt is made to enable public raw participant exports for that dataset
      Then the platform rejects it

    @FR-TEN-007 @R2-Scale @Must
    Scenario: Reject forbidden exceptions and unresolved policy
      Given an exception that would permit cross tenant access, self approval or unsupported arithmetic, or a policy that is unknown, or an exception that has expired
      When sensitive work is attempted under it
      Then the work is denied

  Rule: FR-TEN-008 Configuration promotion
    As an Organisation Administrator, I want to test configuration in an isolated workspace and promote a reviewed package to production with rollback, so that configuration changes are safe and never expose production credentials or personal data.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-TEN-008 @R3-Ecosystem @Should
    Scenario: Copy configuration to a test workspace
      Given an Organisation Administrator
      When they copy configuration and synthetic fixtures into an isolated test workspace
      Then production credentials and personal records are not copied by default

    @FR-TEN-008 @R3-Ecosystem @Should
    Scenario: Promote an approved package
      Given a configuration package in the test workspace
      When promotion compares versions, dependencies and validation results
      And an eligible Reviewer approves the complete package
      Then the production application records the exact promoted versions and affected future objects

    @FR-TEN-008 @R3-Ecosystem @Should
    Scenario: Roll back a promoted collection rule
      Given a new collection rule was promoted and production submissions were accepted under it
      When the Organisation Administrator rolls it back
      Then compatible configuration references are restored
      And sample records never appear in production
      And accepted production submissions keep their original rule references

    @FR-TEN-008 @R3-Ecosystem @Should
    Scenario: Reject rollback that erases intervening writes
      Given writes were made under an intervening configuration version
      When a rollback is attempted without an explicit migration
      Then those writes are not erased or altered

  Rule: FR-TEN-009 Branding and external identity
    As an Organisation Administrator, I want to apply approved, accessible branding and a verified external domain to our workspace and reports, including white-labelling under a funder's brand, so that stakeholders see the right brand without hiding caveats, approval status or the actual organisation.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-TEN-009 @R3-Ecosystem @Should
    Scenario: Preview and publish a theme
      Given approved logos, accessible colours, tenant name and report styles
      When the Organisation Administrator previews and publishes the theme
      Then only presentation changes

    @FR-TEN-009 @R3-Ecosystem @Should
    Scenario: Activate an external domain
      Given an external domain has been added
      When verified control and an active renewal or revocation owner are recorded
      Then the domain becomes active
      But until then it remains pending

    @FR-TEN-009 @R3-Ecosystem @Should
    Scenario: Reject an inaccessible theme
      Given reports are served with an accessible theme
      When the Organisation Administrator attempts to publish a theme with a low contrast colour palette
      Then publication of the failing theme is blocked
      And the prior accessible theme continues to serve reports

    @FR-TEN-009 @R3-Ecosystem @Should
    Scenario: Reject unsafe assets and branding that hides mandatory content
      Given the Organisation Administrator is editing branding
      When they upload an asset that fails file safety checks or configure branding that hides mandatory caveats, approval status or the actual organisation
      Then the asset or branding is rejected

    @FR-TEN-009 @R3-Ecosystem @Should
    Scenario: Reject fallback when domain verification expires
      Given an external domain whose verification has expired
      When the domain is requested
      Then the domain is disabled
      And no fallback tenant is opened
