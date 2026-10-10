# Imprana Commons backlog: Security
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Security

  Rule: FR-SEC-008 Secure engineering lifecycle
    As a Platform Operator, I want each release record to link requirement changes, reviewed code, dependency and licence inventory, security checks, migrations and approvers, so that every production change is traceable and promoted only with its required gate evidence.
    Release: Foundation · Priority: Must · Built today: Absent

    @FR-SEC-008 @Foundation @Must
    Scenario: Release record links its evidence
      Given a release
      When its record is created
      Then it links requirement and specification changes, reviewed code, dependency and licence inventory, security checks, migration results and approvers
      And security relevant changes identify their affected threat and regression cases

    @FR-SEC-008 @Foundation @Must
    Scenario: Trace a changed rule in production
      Given a production version with a changed export rule
      When the Platform Operator traces it
      Then they reach its FSD parent, reviewed change, negative tests and release approval

    @FR-SEC-008 @Foundation @Must
    Scenario: Reject promotion without gate evidence
      Given a release missing declared gate evidence
      When production promotion is attempted
      Then promotion is blocked
      And a feature flag is not accepted as a security exemption
      And an unsupported dependency requires an owned risk and resolution decision

  Rule: FR-SEC-010 Independent assurance
    As a Platform Operator, I want an assurance record for each independent assessment and a release gate tied to it, so that general production releases proceed only after independent assessment and verified mitigation of critical and high findings.
    Release: Foundation · Priority: Must · Built today: Absent

    @FR-SEC-010 @Foundation @Must
    Scenario: Assurance record is complete
      Given an independent assessment
      When it is recorded
      Then the record names assessment scope, deployment profile, assessor independence, dates, findings and retest evidence

    @FR-SEC-010 @Foundation @Must
    Scenario: New assessment obligations are created
      Given a material change or the annual recurrence date
      When it occurs
      Then another independent assessment obligation is created

    @FR-SEC-010 @Foundation @Must
    Scenario: Reject release with an unretired high finding
      Given an unretired high object-authorisation finding
      When general production release is attempted
      Then the gate remains blocked until independently retested mitigation is recorded

    @FR-SEC-010 @Foundation @Must
    Scenario: Reject overstated certification
      Given a partial review
      When assurance is reported
      Then it is not labelled as whole product certification

  Rule: FR-SEC-001 Security threat assessment
    As a Platform Operator, I want each release review to record threat scenarios linked to controls, owners, tests and residual decisions, so that critical attack paths across modules are verified rather than hidden under a general security sign-off.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-SEC-001 @R1-Pilot @Must
    Scenario: Threats are recorded and linked
      Given a release review
      When threats are recorded
      Then they cover identity, tenant boundaries, source data, files, offline devices, publication, AI and support
      And each links to a functional control, owner, test and residual decision

    @FR-SEC-001 @R1-Pilot @Must
    Scenario: Chained abuse paths are verified
      Given a document injection leading to export and a support access escalation
      When the review assesses them
      Then independent controls and verification evidence are identified for both paths

    @FR-SEC-001 @R1-Pilot @Must
    Scenario: Material changes trigger an impact review
      Given a material feature change
      When it is proposed
      Then an impact review is triggered

    @FR-SEC-001 @R1-Pilot @Must
    Scenario: Reject hidden critical paths
      Given an unresolved critical threat path
      When a general security signoff is given
      Then the critical path is not hidden or treated as resolved
      And tests that cover only isolated input checks without chained abuse across modules are insufficient

  Rule: FR-SEC-002 Encryption and key governance
    As a Platform Operator, I want an encryption inventory covering every data location and transport, with visible key ownership, status, expiry and rotation evidence, so that keys can be governed and rotated without exposing key material or losing authorised access.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-002 @R1-Pilot @Must
    Scenario: Inventory covers every location
      Given the security inventory
      When it is reviewed
      Then it covers every permitted data location and transport, including temporary artifacts, backups and offline packages

    @FR-SEC-002 @R1-Pilot @Must
    Scenario: Key status is visible without key material
      Given operational interfaces for keys
      When the Platform Operator views a key
      Then its ownership, status, expiry and rotation evidence are shown
      And no key material is displayed

    @FR-SEC-002 @R1-Pilot @Must
    Scenario: Key rotation preserves authorised access
      Given a test data protection key
      When it is rotated
      Then approved records and backups remain accessible only through authorised paths
      And no key values are exposed

    @FR-SEC-002 @R1-Pilot @Must
    Scenario: Reject plaintext fallback on key loss
      Given a required key is lost or revoked
      When data protected by it is requested
      Then a controlled unavailable state is returned
      But no plaintext fallback is used

  Rule: FR-SEC-003 Tenant isolation verification
    As a Platform Operator, I want every release affecting tenancy to run isolation fixtures across records, attachments, jobs, caches, search, AI and support, so that no tenant's data can reach another tenant through any path.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-003 @R1-Pilot @Must
    Scenario: Isolation fixtures run for tenancy changes
      Given a release affecting tenancy
      When release checks run
      Then isolation fixtures cover records, attachments, async jobs, caches, search, AI and support
      And each fixture uses distinct synthetic tenant markers and principals with differing roles

    @FR-SEC-003 @R1-Pilot @Must
    Scenario: Cross tenant access attempts return nothing
      Given another tenant's artifact carrying a synthetic marker
      When a user guesses its reference, requests it through a background job and asks AI for its contents
      Then no path returns the synthetic marker

    @FR-SEC-003 @R1-Pilot @Must
    Scenario: Reject release on isolation failure
      Given an isolation fixture that exposes another tenant's data
      When the release is evaluated
      Then the finding records the specific exposed path
      And the affected release is blocked even if ordinary workflows succeed
      And shared infrastructure or reused cache entries do not imply shared authorisation

  Rule: FR-SEC-004 Application and API protection
    As a Platform Operator, I want the application and API to validate input, render text safely, protect mutations and verify outbound destinations under one authorisation model, so that common attacks are refused at the right boundary with evidence mapped to ASVS 5.0.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-004 @R1-Pilot @Must
    Scenario: Hostile inputs are handled at the boundary
      Given script-like text, a cross tenant object reference and an internal network URL
      When each is submitted
      Then each is safely rendered or rejected at the relevant boundary

    @FR-SEC-004 @R1-Pilot @Must
    Scenario: Shared authorisation and error contracts
      Given public and authenticated surfaces
      When a request is processed
      Then both use the same domain authorisation and safe error contracts
      And authenticated mutations are protected and outbound destinations are verified

    @FR-SEC-004 @R1-Pilot @Must
    Scenario: Verification maps to ASVS
      Given security verification for a release
      When it is reviewed
      Then applicable ASVS 5.0 controls through Level 2, including Level 1, are mapped
      And tests cover uploads, rich text, links, filtering, exports and API references

    @FR-SEC-004 @R1-Pilot @Must
    Scenario: Reject assertions in place of evidence
      Given a release that asserts broad immunity without passing test evidence and independent review
      When it is assessed
      Then the assertion is not accepted as security verification

  Rule: FR-SEC-005 File and content safety
    As a Platform Operator, I want uploaded files identified by actual content type, held in quarantine until checked and previewed without active content, so that malicious or misleading files never reach users or count as evidence.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-005 @R1-Pilot @Must
    Scenario: Files are quarantined until checks complete
      Given a received file
      When it is processed
      Then its actual content type, size, expansion limits and permitted processing are identified
      And it remains quarantined until checks complete
      And previews execute no active content

    @FR-SEC-005 @R1-Pilot @Must
    Scenario: Hostile uploads are blocked
      Given a misleading extension, a malicious document and an archive expansion fixture
      When each is uploaded
      Then none reaches normal preview
      And none satisfies mandatory evidence requirements

    @FR-SEC-005 @R1-Pilot @Must
    Scenario: External fetches are validated
      Given an external fetch
      When it is requested
      Then the destination is validated before the request and after redirects

    @FR-SEC-005 @R1-Pilot @Must
    Scenario: Reject excluded and unscannable files
      Given an executable, a macro enabled document or a password protected unscannable file in R1
      When it is uploaded
      Then executables and macro enabled documents are rejected
      And password protected unscannable files remain quarantined or are rejected
      And archives are accepted only under a specifically qualified bounded profile

  Rule: FR-SEC-006 Secrets management
    As an Organisation Administrator, I want secrets stored as credential references with explicit, audited rotation and revocation, so that credentials never appear in views, reports, diagnostics or exported configuration.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-006 @R1-Pilot @Must
    Scenario: Secret entry returns only a reference
      Given an Organisation Administrator entering a connector secret
      When it is saved
      Then only a credential reference and safe fingerprint are returned

    @FR-SEC-006 @R1-Pilot @Must
    Scenario: Rotation and revocation are audited operations
      Given a stored connector credential
      When it is rotated or revoked
      Then the operation records owner, scope and audit
      And the old credential is rejected after rotation

    @FR-SEC-006 @R1-Pilot @Must
    Scenario: Configuration export omits secrets
      Given a connection configuration
      When it is exported and then imported
      Then secret values are omitted from the export
      And the import marks required reconfiguration

    @FR-SEC-006 @R1-Pilot @Must
    Scenario: Reject secret exposure
      Given a rotated connector credential
      When its configuration export and permitted logs are inspected
      Then neither the old nor the new secret is present
      And secrets do not appear in ordinary admin views, client storage, generated reports or diagnostics

  Rule: FR-SEC-007 Tamper evident audit
    As an Executive Director, I want audit events that record who did what, in which capacity, on which version and with what outcome, and that cannot be edited or erased, so that approvals and privileged actions remain attributable.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-007 @R1-Pilot @Must
    Scenario: Audit events are complete
      Given an action covered by the event catalogue, including privileged reads and decisions
      When it occurs
      Then an audit event records real actor, delegated capacity, tenant, action, object version, outcome, time and correlation

    @FR-SEC-007 @R1-Pilot @Must
    Scenario: Audit access is scoped
      Given a user searching or exporting audit events
      When they run the search or export
      Then results are restricted to their authorised audit scopes

    @FR-SEC-007 @R1-Pilot @Must
    Scenario: Corrections are additional events
      Given an audit event that needs correction
      When it is corrected
      Then the correction is recorded as an additional event
      And the original event is unchanged

    @FR-SEC-007 @R1-Pilot @Must
    Scenario: Reject editing past audit history
      Given an approval event
      When an administrator attempts to change or erase it through ordinary administration
      Then the attempt fails
      And both the attempt and the original decision remain attributable

  Rule: FR-SEC-009 Vulnerability management
    As a Platform Operator, I want each reported vulnerability tracked as a restricted case with severity, affected versions, owner and timing targets through separate mitigation, fix, retest and closure milestones, so that serious exposures are contained on time.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-SEC-009 @R1-Pilot @Must
    Scenario: Intake creates a restricted case
      Given a vulnerability report
      When it is received
      Then a restricted case records reported scope, severity, affected versions, owner and timing targets
      And triage distinguishes confirmed exposure from suspected risk

    @FR-SEC-009 @R1-Pilot @Must
    Scenario: Milestones are recorded against targets
      Given a simulated credential exposure
      When it is handled
      Then report, acknowledgement, containment, rotation, fix and retest times are recorded against the applicable targets
      And mitigation, fix, independent retest and closure are separate milestones

    @FR-SEC-009 @R1-Pilot @Must
    Scenario: Reject silent downgrade and missed release block
      Given a critical or high finding affecting confidentiality, integrity or access
      When an exception is requested or a release is attempted
      Then the BRD release block and timing targets still apply
      And the severity is not silently downgraded

  Rule: FR-SEC-011 Detection and incident response
    As a Platform Operator, I want detection rules to raise restricted incident records for suspicious activity and track containment and recovery, so that compromises are contained quickly without spreading sensitive payloads.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-SEC-011 @R1-Pilot @Must
    Scenario: Detection raises a restricted incident
      Given detection rules for suspicious identity changes, bulk extraction, service misuse and failed controls
      When a rule fires
      Then a restricted incident record is created
      And on call receives safe context and correlation references

    @FR-SEC-011 @R1-Pilot @Must
    Scenario: Compromised service identity is handled
      Given a simulated compromised service identity
      When detection triggers
      Then the identity is revoked
      And the incident identifies affected jobs and potential disclosures
      And general alerts contain no payloads

    @FR-SEC-011 @R1-Pilot @Must
    Scenario: Incident handling is recorded
      Given an open incident
      When it is handled
      Then containment, affected tenants, evidence preservation, recovery and communications decisions are recorded

    @FR-SEC-011 @R1-Pilot @Must
    Scenario: Reject invented deadlines and uncontrolled access
      Given an incident requiring notification or investigation
      When notifications are sent or investigators access data
      Then notifications follow the approved legal and contractual policy, not an invented universal deadline
      And investigation access follows exceptional support controls

  Rule: FR-SEC-012 Environment separation
    As a Platform Operator, I want clearly identified environments with distinct credentials and synthetic data by default, so that test activity can never reach production and copied configurations cannot trigger real actions.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-SEC-012 @R1-Pilot @Must
    Scenario: Environment identity is visible
      Given a Platform Operator or Integration Developer
      When they work in any environment
      Then the environment identity is visible

    @FR-SEC-012 @R1-Pilot @Must
    Scenario: Lower environments use synthetic data
      Given a lower environment
      When it is provisioned
      Then synthetic data is the default
      And any exceptional production sample requires approved minimisation and expiry

    @FR-SEC-012 @R1-Pilot @Must
    Scenario: Reject cross environment credentials and copied schedules
      Given a test credential and a sandbox with copied configuration
      When the credential is used against production and copied report schedules are activated in the sandbox
      Then both are prevented
      And the copied configuration omits production secrets, external recipients and active schedules

    @FR-SEC-012 @R1-Pilot @Must
    Scenario: Reject hidden bypasses
      Given the production environment
      When its accounts and roles are reviewed
      Then no hidden production test users or bypass roles exist

  Rule: FR-SEC-013 Privileged operations
    As a Platform Operator, I want to request time-limited elevation scoped to a named task and exact capability, so that I can perform privileged work without standing broad access to customer content.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-SEC-013 @R1-Pilot @Must
    Scenario: Request scoped elevation
      Given a Platform Operator with a named incident or maintenance task
      When they request elevation
      Then the request states the exact capability scope and duration
      And a distinct reviewer approves where required

    @FR-SEC-013 @R1-Pilot @Must
    Scenario: Emergency activation is reviewed afterwards
      Given an emergency elevation
      When it is activated
      Then a mandatory retrospective review is created

    @FR-SEC-013 @R1-Pilot @Must
    Scenario: Sessions keep the real actor and expire
      Given an elevated session
      When it is used
      Then the real actor is retained
      And the session expires automatically

    @FR-SEC-013 @R1-Pilot @Must
    Scenario: Reject actions after expiry
      Given an operator elevated for recovery diagnostics whose grant has expired
      When they attempt further reads or a queued sensitive operation runs
      Then all are denied
      And no expired job credential can continue a privileged operation

  Rule: FR-SEC-014 Resilience to abusive traffic
    As a Data Author, I want abuse controls on login, public collection, search, exports and AI applied by tenant and credential, so that an abusive source elsewhere cannot lock my organisation out and I always get a safe wait or recovery route.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @FR-SEC-014 @R1-Pilot @Must
    Scenario: Separate controls with safe recovery
      Given abuse controls for login, public collection, search, exports and AI
      When a user is limited
      Then they see a safe wait or recovery route
      And accessible challenges and assisted recovery are available where needed

    @FR-SEC-014 @R1-Pilot @Must
    Scenario: Burst on one form is contained
      Given a burst of traffic on one public form
      When limits apply
      Then rejection is bounded to that form
      And other tenants continue collecting and approving records

    @FR-SEC-014 @R1-Pilot @Must
    Scenario: Reject indiscriminate lockout and disclosure
      Given an abusive source
      When denial controls respond
      Then unrelated organisations are not locked out
      And responses do not expose account existence or participant lookup results

  Rule: VF-SEC-001 Release security threshold
    As a Platform Operator, I want releases blocked until baseline security controls pass and no unmitigated critical or high vulnerability remains, so that production never ships known exposures.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-SEC-001 @R1-Pilot @Must
    Scenario: Release proceeds with complete security evidence
      Given passing evidence for all applicable baseline security controls
      And independent assessment, retest evidence and scoped mitigation records
      When the release gate is evaluated
      Then the release may proceed

    @VF-SEC-001 @R1-Pilot @Must
    Scenario: Finding with an effective verified mitigation does not block release
      Given a critical or high vulnerability with an effective verified mitigation
      When the release gate is evaluated
      Then that finding does not block the release

    @VF-SEC-001 @R1-Pilot @Must
    Scenario: Reject release with an unmitigated exposure
      Given an unresolved critical or high vulnerability affecting confidentiality, integrity or access without an effective verified mitigation
      When the release gate is evaluated
      Then the release is blocked
      And neither a product priority waiver nor functional parity can override the gate

  Rule: VF-SEC-002 Incident and remediation timing
    As a Platform Operator, I want critical incidents and vulnerabilities acknowledged, contained and fixed within set times, so that exposure is limited and organisations stay protected.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-SEC-002 @R1-Pilot @Must
    Scenario: Critical incident is acknowledged and contained on time
      Given a simulated critical production incident is detected
      When on call is alerted
      Then an accountable responder acknowledges within 15 minutes
      And containment work begins within 30 minutes
      And legal and contractual notices follow the approved incident policy

    @VF-SEC-002 @R1-Pilot @Must
    Scenario: Confirmed vulnerabilities are remediated on time
      Given a confirmed vulnerability
      When remediation is timed from confirmation
      Then a critical vulnerability is mitigated within 24 hours with a permanent fix targeted within 72 hours
      And a high vulnerability is addressed within 7 days

    @VF-SEC-002 @R1-Pilot @Must
    Scenario: Reject acknowledgement without an accountable responder
      Given a notification has been sent for a critical incident
      When no accountable responder has acknowledged it
      Then the acknowledgement target is not satisfied
      And missed targets, escalation and continuing protection are recorded

  Rule: FR-SEC-015 Enterprise assurance options
    As an Executive Director, I want each enterprise deployment variant to have a qualified profile showing its capabilities, region, recovery, responsibilities, key custody and exit process, so that I know what is supported before choosing it.
    Release: Later · Priority: Could · Built today: Absent

    @FR-SEC-015 @Later @Could
    Scenario: Variant profile is defined
      Given an enterprise deployment variant
      When it is offered
      Then it has a named capability profile, region and recovery constraints, responsibilities, upgrade process, key custody and exit process
      And product screens show supported and unsupported features for that profile

    @FR-SEC-015 @Later @Could
    Scenario: Customer key loss behaves as documented
      Given a qualified dedicated profile with a customer controlled key
      When the key is lost
      Then the documented unavailable and recovery behaviour occurs
      And data is not silently moved elsewhere

    @FR-SEC-015 @Later @Could
    Scenario: Reject unqualified variants
      Given a dedicated deployment or customer controlled key option
      When it is selected through a commercial checkbox without passing equivalent functional, isolation and recovery gates
      Then it is not made available
