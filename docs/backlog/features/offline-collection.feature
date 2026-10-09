# Imprana Commons backlog: Offline collection
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Offline collection

  Rule: FR-OFF-001 Offline task packages
    As a Field Data Collector, I want to download a package containing only my assigned work, after previewing its forms, reference fields, media size and expiry, so that I can collect offline without carrying unnecessary participant data.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-001 @R2-Scale @Must
    Scenario: Package assigned work for offline use
      Given an authenticated Field Data Collector with three assigned households
      When they preview and download the package
      Then the preview lists form versions, minimal reference fields, media size and expiry
      And the package is bound to the actor, tenant, device workspace and policy version
      And successful local preparation is confirmed before field departure

    @FR-OFF-001 @R2-Scale @Must
    Scenario: Complete assigned forms offline
      Given the package is downloaded and the device is offline
      When the collector opens their work
      Then they can complete forms for the three assigned households

    @FR-OFF-001 @R2-Scale @Must
    Scenario: Reject access beyond assigned work
      Given the collector is offline with a package of three assigned households
      When they try to browse a fourth unassigned household
      Then it is not available
      And no full project registry was downloaded by default

    @FR-OFF-001 @R2-Scale @Must
    Scenario: Reject expired assignments and offline renewal
      Given an assignment has expired but is still visible in an old task list
      When a package is prepared or renewed
      Then the expired assignment is excluded
      And renewal requires online policy verification

  Rule: FR-OFF-002 Durable local capture
    As a Field Data Collector, I want every local save confirmed with a device receipt and recovered after a restart, with warnings before storage becomes unsafe, so that I do not lose captured data or mistake a local save for server receipt.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-002 @R2-Scale @Must
    Scenario: Local save returns a device receipt
      Given a collector capturing data offline
      When they save
      Then a device receipt and safe status are shown
      And drafts, stable IDs and attachment references persist

    @FR-OFF-002 @R2-Scale @Must
    Scenario: Restart during an attachment save
      Given the device restarts during an attachment save
      When the app reopens
      Then the saved answers survive and recovered work is listed
      And the incomplete file is flagged
      And no false server received status appears

    @FR-OFF-002 @R2-Scale @Must
    Scenario: Storage warning before capture becomes unsafe
      Given device storage is running low
      When capture continues
      Then a storage warning appears before capture becomes unsafe

    @FR-OFF-002 @R2-Scale @Must
    Scenario: Reject sensitive offline capture without qualified secure storage
      Given secure durable storage cannot be qualified on a client
      When sensitive offline collection is attempted
      Then it is disabled and the supported alternative is shown
      And a local acknowledgement is never presented as server durability

  Rule: FR-OFF-003 Idempotent synchronisation
    As a Field Data Collector, I want synchronisation to resume after interruptions and report each item's outcome, so that every intended submission is stored exactly once and incomplete media stays visible.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-003 @R2-Scale @Must
    Scenario: Per-item sync outcomes
      Given a batch of submissions with identity, base revision, form version, grant context and media manifest
      When it is synchronised
      Then the server returns accepted, duplicate, conflict, quarantined or rejected for each item

    @FR-OFF-003 @R2-Scale @Must
    Scenario: Interrupted batch resolves to one identity per submission
      Given the same batch is interrupted five times
      When synchronisation completes
      Then each intended submission has one identity
      And media chunks resume independently
      And missing media remains visibly incomplete

    @FR-OFF-003 @R2-Scale @Must
    Scenario: Reject duplicate server objects or premature completion
      Given an identical submission is repeated after ordinary interactive operation receipts have expired
      When it is synchronised
      Then it resolves to the same server object
      And the local receipt is retained until server reconciliation completes
      And the submission is not marked complete until required files and checks finish

  Rule: FR-OFF-004 Conflict handling
    As a Data Steward, I want concurrent offline edits preserved as candidate revisions that can be compared and resolved with a reason, so that no field data or approved data is silently overwritten.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-004 @R2-Scale @Must
    Scenario: Both candidates are visible to the resolver
      Given two devices alter the same visit
      And one of them used an obsolete form
      When the edits are synchronised
      Then the common base is identified
      And both candidate revisions remain visible to the resolver with their distinct versions

    @FR-OFF-004 @R2-Scale @Must
    Scenario: Resolve and resubmit
      Given an authorised resolver comparing permitted fields
      When they choose values or create a merged revision and supply a reason
      Then the resolution is resubmitted through validation and approval

    @FR-OFF-004 @R2-Scale @Must
    Scenario: Reject last-device-wins and overwrites
      Given conflicting edits from two devices
      When they are synchronised
      Then neither is applied automatically as last device wins
      And identity duplicates, reassigned tasks and obsolete forms receive specific conflict categories
      And existing approved data is not overwritten

  Rule: FR-OFF-005 Device protection and expiry
    As an Organisation Administrator, I want offline access to require local authentication, expire with its grant and apply revocation on reconnect, so that revoked or expired collectors cannot keep viewing or submitting protected data.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-005 @R2-Scale @Must
    Scenario: Offline unlock and expiry
      Given a collector with an offline grant
      When they unlock the device offline and later the grant expires
      Then unlocking requires the qualified local authentication policy
      And after expiry further protected viewing or capture under that grant is prevented

    @FR-OFF-005 @R2-Scale @Must
    Scenario: Removal and wipe outcomes are reported
      Given a package removal or remote wipe request
      When its status is viewed
      Then it reports requested, confirmed or unknown

    @FR-OFF-005 @R2-Scale @Must
    Scenario: Reject a revoked collector after expiry
      Given a disconnected collector is revoked
      And time advances beyond the grant expiry
      When the collector reconnects
      Then viewing is blocked locally
      And uploads are rejected or explicitly quarantined
      But quarantined uploads never become approved data automatically

    @FR-OFF-005 @R2-Scale @Must
    Scenario: Reject clock rollback
      Given the device clock is rolled back
      When the collector tries to continue offline work
      Then the verified authority window is not extended

  Rule: FR-OFF-006 Shared device operation
    As a Field Data Collector, I want my own protected workspace on a shared device, so that the next collector cannot see my unsynchronised answers or take over my authorship.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-006 @R2-Scale @Must
    Scenario: Switching accounts protects the previous workspace
      Given collector A leaves two unsynchronised forms on a shared device
      When collector B signs in
      Then A's workspace is closed and its unsynchronised count is shown without content
      And B sees neither the answers nor participant names
      And A's authorship remains unchanged

    @FR-OFF-006 @R2-Scale @Must
    Scenario: Handover requires eligible actors
      Given pending work needs to be handed over
      When the handover is performed
      Then both eligible actors are online or a separately qualified secure supervisor procedure is used

    @FR-OFF-006 @R2-Scale @Must
    Scenario: Reject authorship transfer or silent deletion
      Given collector A has pending work on the device
      When collector B continues on the device or A logs out
      Then author identity is never transferred to B
      And pending work may be locked for later recovery
      But it is deleted only after an explicit loss warning and permitted confirmation

  Rule: FR-OFF-007 Sync and quality supervisor view
    As a Programme Manager, I want a sync and quality view showing each device's last reported status with timestamps, so that I can follow up or reassign work without assuming knowledge of unseen offline activity.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @FR-OFF-007 @R2-Scale @Should
    Scenario: Timestamped device status
      Given devices within the Programme Manager's scope
      When the supervisor view is opened
      Then it shows last contact, last reported pending count, package version, expiry, known failures and unresolved conflicts
      And each value is timestamped

    @FR-OFF-007 @R2-Scale @Should
    Scenario: Disconnected device shows last-known state
      Given a device reported two pending forms and then disconnected
      When the Programme Manager views it
      Then the view shows two pending at last contact and current state unknown
      And no live count is shown

    @FR-OFF-007 @R2-Scale @Should
    Scenario: Request follow up or reassignment
      Given a device with unknown current progress
      When the Programme Manager requests follow up or reassignment
      Then the request is recorded without claiming knowledge of unseen offline activity

    @FR-OFF-007 @R2-Scale @Should
    Scenario: Reject treating unknown progress as zero or wiped
      Given a disconnected device
      When its status is shown
      Then it is not recorded as zero completed or guaranteed wiped
      And counts and locations outside the supervisor's scope are not shown

  Rule: FR-OFF-008 Constrained connectivity
    As a Field Data Collector, I want to prepare languages, reference lists and form logic before departure and sync text first over weak connections, so that I can complete work reliably in low-bandwidth areas without false completion.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-OFF-008 @R2-Scale @Must
    Scenario: Complete a form on a weak connection
      Given approved languages, reference lists and form logic were downloaded before departure
      And the connection is under 1 Mbps with intermittent loss
      When the collector completes a form
      Then the answers persist
      And permitted delayed media upload does not create a false complete submission

    @FR-OFF-008 @R2-Scale @Must
    Scenario: Manual text-first sync
      Given policy permits deferred media transfer
      When the collector syncs manually
      Then text is uploaded first and media transfer is deferred

    @FR-OFF-008 @R2-Scale @Must
    Scenario: Reject automatic large downloads on constrained connections
      Given a constrained connection and large media available for download
      When the client prepares downloads
      Then large media is not downloaded automatically
      And large downloads require size disclosure and user control

    @FR-OFF-008 @R2-Scale @Must
    Scenario: Reject online-only logic shown as offline capable
      Given form logic that requires a live external lookup
      When the form is packaged for offline use
      Then it is labelled online only and not presented as offline capable

  Rule: VF-OFF-001 Offline authority window
    As a Privacy Officer, I want offline data packages to expire within set authority windows unless reauthorised, so that participant data on field devices is not usable indefinitely.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @VF-OFF-001 @R2-Scale @Must
    Scenario: Default offline package expires within 24 hours
      Given a default offline package on a device
      When 24 hours pass without renewed authorisation
      Then the package expires
      And expiry holds across restart, clock rollback, account switching, prolonged disconnection and revoked reconnect

    @VF-OFF-001 @R2-Scale @Must
    Scenario: Restricted participant package expires within 8 hours by default
      Given a restricted participant package on a device with approved device controls
      When 8 hours pass without renewed authorisation
      Then the package expires

    @VF-OFF-001 @R2-Scale @Must
    Scenario: Longer windows need a recorded risk exception
      Given a low sensitivity package
      When a window longer than the default is configured
      Then a recorded risk exception is required
      But sensitive data may be prohibited from offline use entirely

    @VF-OFF-001 @R2-Scale @Must
    Scenario: Reject sensitive offline use on a device that cannot enforce the window
      Given a device that cannot reliably enforce the authority window
      When sensitive offline use is assessed for that device
      Then sensitive offline use is not qualified
      And remote wipe is recorded as best effort only
