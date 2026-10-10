# Imprana Commons backlog: Identity and accounts
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Identity and accounts

  Rule: FR-IAM-001 Invitations and onboarding
    As an Organisation Administrator, I want to invite people with a chosen role, scopes, expiry and intended identity and see their effective capabilities before sending, so that only the intended person gains exactly the intended membership.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-001 @R1-Pilot @Must
    Scenario: Preview and send an invitation
      Given an Organisation Administrator selects tenant, role template, explicit scopes, expiry and the intended verified identity
      When they preview the invitation
      Then the effective capabilities are shown before sending
      And the invitation expires in seven days by default

    @FR-IAM-001 @R1-Pilot @Must
    Scenario: Accept an invitation
      Given a valid invitation token and an inviter who still has authority
      When the invitee proves control of the nominated identity and accepts
      Then exactly one membership is created

    @FR-IAM-001 @R1-Pilot @Must
    Scenario: Report bulk invitation outcomes
      When the Organisation Administrator sends invitations in bulk
      Then outcomes are reported separately as created, duplicate, invalid and delivery failed
      And receiving the email alone is not treated as membership activation

    @FR-IAM-001 @R1-Pilot @Must
    Scenario: Reject forwarded, replayed or superseded invitations
      Given an invitation forwarded to a different signed in account, a token that has already been consumed, or a token invalidated by a resend
      When the token is used to accept
      Then acceptance fails
      And no protected tenant content is revealed

  Rule: FR-IAM-002 Enterprise federation
    As an Organisation Administrator, I want to configure, test and enforce sign-in through our identity provider with safe certificate rotation, so that members sign in through our provider and no weaker path can bypass it.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-002 @R1-Pilot @Must
    Scenario: Configure and test federation before enforcing it
      Given an Organisation Administrator configures provider metadata, tenant binding and subject mapping
      When they test sign in with designated accounts
      Then federation can be enforced
      And login binds the issuer and stable subject to the intended tenant membership

    @FR-IAM-002 @R1-Pilot @Must
    Scenario: Rotate the provider certificate
      Given federation is enforced and the certificate expiry is shown
      When the Organisation Administrator performs a tested overlapping certificate rotation
      Then sign in continues under the new certificate

    @FR-IAM-002 @R1-Pilot @Must
    Scenario: Reject email-only linking and invalid assertions
      Given two different federation identities share a matching email
      When either signs in
      Then the matching email alone never joins the identities
      And an invalid assertion, wrong audience or missing assurance fails safely

    @FR-IAM-002 @R1-Pilot @Must
    Scenario: Reject local password bypass
      Given federation is enforced, the old certificate has expired and the provider is interrupted
      When a member attempts to sign in with an ordinary local password
      Then the sign in is refused
      And only separately enrolled, restricted and audited emergency local recovery remains available

  Rule: FR-IAM-003 Multifactor and passkeys
    As an Organisation Administrator, I want to enrol a passkey or approved additional factor and confirm privileged and sensitive actions with a short-lived step-up challenge, so that my account and organisation stay protected even if a signed-in session is misused.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-003 @R1-Pilot @Must
    Scenario: Enrol a passkey
      Given an Organisation Administrator has verified their existing identity
      When they enrol a passkey or approved additional factor
      Then the factor is added to their enrolled assurance
      And the chosen authenticator discloses its device synchronisation behaviour

    @FR-IAM-003 @R1-Pilot @Must
    Scenario: Step up for a sensitive action
      Given an Organisation Administrator has signed in but not stepped up
      And a reviewed public publication is pending
      When they attempt the publication
      Then a step up challenge bound to them and to that action is required
      When they complete a valid challenge within the five minute freshness window
      Then only the reviewed pending action becomes eligible

    @FR-IAM-003 @R1-Pilot @Must
    Scenario: Reject removing the last privileged factor
      Given a privileged account with one qualifying factor
      When the member attempts to remove it without verified recovery replacing it
      Then the removal is blocked

    @FR-IAM-003 @R1-Pilot @Must
    Scenario: Reject weak or stale assurance
      Given a privileged role activation or sensitive action
      When the only factor presented is SMS, or the step up challenge has expired or is bound to a different action
      Then the activation or action is refused

  Rule: FR-IAM-006 Session control
    As a Data Author, I want to see my active sessions and revoke one or all of them, with safe expiry and logout, so that a lost or shared device cannot keep access to protected data.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-006 @R1-Pilot @Must
    Scenario: View sessions
      When a Data Author views their sessions
      Then each shows a device label, approximate activity, creation and last use without unnecessary location detail

    @FR-IAM-006 @R1-Pilot @Must
    Scenario: Revoke sessions
      Given a Data Author has verified their identity
      When they revoke one session or all sessions
      Then the revoked sessions lose server authority even if a browser retains a stale screen image

    @FR-IAM-006 @R1-Pilot @Must
    Scenario: Warn before expiry
      Given a session approaching idle or absolute expiry as defined in FD04
      When the warning is shown
      Then permitted drafts are preserved before reauthentication

    @FR-IAM-006 @R1-Pilot @Must
    Scenario: Reject use of a revoked session
      Given a Data Author has two open sessions and revokes one
      When the revoked session uses browser back navigation or a queued export
      Then neither returns protected data

    @FR-IAM-006 @R1-Pilot @Must
    Scenario: Reject protected state after logout or on a shared device
      Given a Data Author has logged out or is using shared device mode
      When the browser is used to return to protected content
      Then sensitive in memory state and protected cached navigation have been cleared
      And no persistent unrestricted session is available

  Rule: FR-IAM-008 Membership status and expiry
    As an Organisation Administrator, I want each tenant membership to have its own active, suspended, expired or revoked status with scheduled expiry, so that access ends precisely in the right tenant without affecting other tenants or historical attribution.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-008 @R1-Pilot @Must
    Scenario: Show upcoming expiry
      Given a membership with a scheduled expiry at an absolute instant
      When the member or owner views the membership
      Then they see the upcoming expiry

    @FR-IAM-008 @R1-Pilot @Must
    Scenario: Expire a membership in one tenant only
      Given a Reviewer has memberships in tenants A and B
      When their tenant A membership expires
      Then their approvals in tenant A fail
      And their authorised work in tenant B continues
      And their account is not deleted

    @FR-IAM-008 @R1-Pilot @Must
    Scenario: Suspend a membership
      When the Organisation Administrator suspends a membership
      Then online revocation starts immediately
      And pending work is identified
      And historical attribution is unchanged

    @FR-IAM-008 @R1-Pilot @Must
    Scenario: Reject reactivation without review or revival of revoked items
      Given a suspended or expired membership
      When the Organisation Administrator reactivates it
      Then a current grant review and a new expiry where relevant are required
      But revoked links, old service secrets and independently expired delegations are not revived

  Rule: FR-IAM-009 Delegated user administration
    As an Organisation Administrator, I want to delegate member administration within a defined envelope with previews and independent approval for sensitive expansion, so that local administrators can manage their people without escalating privileges directly or indirectly.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-009 @R1-Pilot @Must
    Scenario: Invite or modify members within the delegation envelope
      Given a delegated administrator with a delegation envelope
      When they invite or modify a member within that envelope
      Then the grant preview shows the effective capability difference
      And any sensitive expansion is flagged for independent approval

    @FR-IAM-009 @R1-Pilot @Must
    Scenario: Recheck authority at approval
      Given a flagged grant awaiting independent approval
      When it is approved
      Then the issuer's current delegation authority is rechecked before the grant applies

    @FR-IAM-009 @R1-Pilot @Must
    Scenario: Reject indirect escalation through a group
      Given a project administrator
      When they create a group and attempt to add tenant administration through it
      Then the indirect escalation fails

    @FR-IAM-009 @R1-Pilot @Must
    Scenario: Reject delegating non-delegable rights and self elevation
      Given an administrator holds a right that is not delegable
      When they attempt to delegate it, elevate themselves, grant a role through a new group or expand scope through an import
      Then identical checks apply and the action is refused

  Rule: FR-IAM-014 Departure and work reassignment
    As an Organisation Administrator, I want an offboarding process that revokes a leaver's access first and then reassigns, cancels or holds each item they owned, so that work continues under accountable successors without misusing the leaver's authority.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-IAM-014 @R1-Pilot @Must
    Scenario: Offboard a departing member
      When the Organisation Administrator runs the offboarding wizard for a departing member
      Then access is revoked first
      And owned sources, schedules, drafts, credentials and approval tasks are listed for an authorised successor
      And each item is reassigned, cancelled or held with an owner

    @FR-IAM-014 @R1-Pilot @Must
    Scenario: Remove a schedule owner with an export in progress
      Given a report schedule owner has an export in progress
      When they are removed
      Then receipts are preserved
      And export and delivery jobs reauthorise before any sensitive action
      And the successor decision is recorded

    @FR-IAM-014 @R1-Pilot @Must
    Scenario: Reject unapproved delivery and impersonation
      Given work from a departed member has been reassigned
      When the work continues
      Then it does not run under the departed person's orphaned human session
      And the departed person's approval decision is not transferred
      And content visibility follows the successor's explicit grants
      And unapproved delivery is prevented

  Rule: VF-IAM-001 Revocation time
    As an Organisation Administrator, I want suspensions, permission removals and credential revocations to take effect everywhere promptly, so that removed users and services lose access before they can misuse it.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @VF-IAM-001 @R1-Pilot @Must
    Scenario: Revocation takes effect within 60 seconds across all channels
      Given an online user, grant or service credential
      When the Organisation Administrator suspends the user, removes the permission or revokes the credential
      Then access is blocked within 60 seconds across user interfaces, APIs, generated downloads, search and AI access

    @VF-IAM-001 @R1-Pilot @Must
    Scenario: Directory-initiated revocation is measured from platform receipt
      Given a revocation initiated from a directory
      When the platform receives it
      Then the 60-second bound is measured from that receipt

    @VF-IAM-001 @R1-Pilot @Must
    Scenario: Queued jobs reauthorise before sensitive actions
      Given a queued job pending a sensitive action for a revoked user or credential
      When the job is about to execute
      Then it reauthorises and does not perform the action

    @VF-IAM-001 @R1-Pilot @Must
    Scenario: Reject any protected access after 60 seconds
      Given a revocation was received by the platform more than 60 seconds ago
      When the revoked user or credential attempts protected access through any channel
      Then the access is refused
      And any successful protected access fails the gate, because 60 seconds is a maximum, not a percentile

  Rule: FR-IAM-004 Local account security
    As a Data Author with a local account, I want clear password rules that work with password managers and a safe single-use reset, so that I can secure and recover my account without exposing my password or whether an address is registered.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-IAM-004 @R2-Scale @Must
    Scenario: Set a local password
      Given a Data Author is setting up a local account
      When they paste a password from a password manager
      Then the paste is accepted
      And the effective password policy is displayed
      And the password is checked against known compromised values

    @FR-IAM-004 @R2-Scale @Must
    Scenario: Reset a password
      When a Data Author requests a password reset
      Then a neutral acknowledgement is returned
      And a single use recovery link with a 30 minute expiry is issued
      When they complete a successful reset
      Then prior recovery tokens and sessions are revoked according to policy

    @FR-IAM-004 @R2-Scale @Must
    Scenario: Reject token replay and secret leakage
      Given a reset token has already been used
      When the same token is submitted again
      Then the replay fails
      And after a failed password attempt neither the password nor the token is recoverable from logs or diagnostics

    @FR-IAM-004 @R2-Scale @Must
    Scenario: Reject account enumeration and unbounded retries
      When a reset is requested for an address that is not registered
      Then the response does not reveal whether the address is registered
      And repeated attempts are subject to bounded retry and abuse controls
      And password text is never exposed to telemetry or normal administrators

  Rule: FR-IAM-007 Recovery and identity changes
    As a Data Author, I want changes to my sign-in identity and recovery of lost factors to require strong verification and notify me, so that someone with a stolen session or a persuasive story cannot take over my account.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-IAM-007 @R2-Scale @Must
    Scenario: Change identity after step up
      Given a Data Author has completed a recent step up
      When they change their identity contact and verify the new channel
      Then the change is applied
      And both permitted old and new contacts are notified without disclosing secrets

    @FR-IAM-007 @R2-Scale @Must
    Scenario: Recover a lost factor
      Given a Data Author has lost a factor
      When they verify enrolled recovery evidence
      Then one recovery code is consumed
      And a security notice is triggered

    @FR-IAM-007 @R2-Scale @Must
    Scenario: Reject identity change from a stolen session
      Given an attacker holds a stolen ordinary session
      When they attempt to replace the recovery email
      Then the change is blocked until stronger verification succeeds

    @FR-IAM-007 @R2-Scale @Must
    Scenario: Reject support resets based on conversation alone
      Given a Support Agent receives an identity reset request
      When the only evidence is a conversation or knowledge questions
      Then the Support Agent cannot reset the identity
      And a disputed change enters a restricted recovery case where existing broad privileges are not restored until verification completes

  Rule: FR-IAM-010 Group management
    As an Organisation Administrator, I want to manage groups with dated, scoped and owned grants and inspect the effective permissions they produce, so that group access is clear and removing someone reliably removes everything they derived from the group.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-IAM-010 @R2-Scale @Should
    Scenario: Maintain groups and inspect effective permissions
      Given a group editor maintains members and scoped grants with effective dates and ownership
      When effective permissions are inspected for a member
      Then all valid grant paths are expanded

    @FR-IAM-010 @R2-Scale @Should
    Scenario: Remove a member from a group
      Given an Analyst is a member of a reporting group
      When they are removed from the group
      Then their existing report links, AI citations and scheduled exports are denied within the defined bound

    @FR-IAM-010 @R2-Scale @Should
    Scenario: Delete a group
      When a group is deleted
      Then its future grants are retired
      And its audit history is retained

    @FR-IAM-010 @R2-Scale @Should
    Scenario: Reject group permissions overriding restrictive policy
      Given an explicit restrictive policy applies to a member
      When a group grants a conflicting permission
      Then the restrictive policy still applies

    @FR-IAM-010 @R2-Scale @Should
    Scenario: Reject unqualified nested groups
      Given cycle detection, visible ancestry and identical revocation behaviour have not been qualified for nested groups
      When an administrator attempts to nest one group inside another
      Then nesting is not available and groups remain flat

  Rule: FR-IAM-012 Service identities
    As an Integration Developer, I want to create scoped, expiring service identities with show-once secrets and overlapping rotation, so that integrations run securely without human logins or broader access than the integration needs.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-IAM-012 @R2-Scale @Must
    Scenario: Create a service identity
      When an Integration Developer creates a machine identity with purpose, allowed resources, operations and expiry
      Then the secret is shown once at issue
      And afterwards only a safe reference to it is shown

    @FR-IAM-012 @R2-Scale @Must
    Scenario: Rotate during a retried connector run
      Given a connector run is being retried
      When the Integration Developer rotates the secret
      Then the previous credential remains valid only for the bounded overlap
      And one intended row effect is recorded
      And the expired secret fails on its next request

    @FR-IAM-012 @R2-Scale @Must
    Scenario: Flag on owner departure
      Given the owner of a service identity departs
      When the departure is recorded
      Then the credential is flagged for reassignment or suspension

    @FR-IAM-012 @R2-Scale @Must
    Scenario: Reject human use and scope broadening
      Given a service identity
      When it is used for an ordinary login or a human approval, or to act beyond the scope of the owning integration
      Then the request is refused

  Rule: FR-IAM-013 User profile and preferences
    As a Data Author, I want to set my display name, language, reporting preferences, time zone and accessibility choices, so that the platform suits how I work without changing stored data or who is recorded as having acted.
    Release: R2 Scale · Priority: Should · Built today: Partial

    @FR-IAM-013 @R2-Scale @Should
    Scenario: Change profile preferences
      When a Data Author changes their display name, interface language, reporting preferences, time zone or accessibility choices
      Then a preview shows the resulting date and number display
      And stored values are not changed

    @FR-IAM-013 @R2-Scale @Should
    Scenario: Show directory-controlled fields as read only
      Given a profile field controlled by the directory
      When the Data Author views their profile
      Then the field is read only and labelled with its source

    @FR-IAM-013 @R2-Scale @Should
    Scenario: Keep attribution stable
      Given a member recorded an approval
      When they change their display name and time zone
      Then the approval still resolves to the same actor and original absolute timestamp

    @FR-IAM-013 @R2-Scale @Should
    Scenario: Reject preferences that suppress notices or override calendars
      When a Data Author sets a preference that would suppress mandatory security notices or override the organisation reporting calendar
      Then the preference does not take effect

  Rule: FR-IAM-005 Provisioning and deprovisioning
    As an Organisation Administrator, I want our directory to provision and deprovision memberships within a configured scope and show reconciliation differences, so that joiners get the right access and leavers lose it promptly without orphaning their work.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-IAM-005 @R3-Ecosystem @Should
    Scenario: Provision from the directory
      Given a directory connection that declares authoritative attributes and groups
      When a directory user is provisioned
      Then a pending or active membership is created only within the configured scope

    @FR-IAM-005 @R3-Ecosystem @Should
    Scenario: Deactivate a user who owns a job
      Given a directory user owns a job
      When the user is deactivated in the directory
      Then derived access is removed, sessions are revoked and ownership reassignment tasks are opened
      And within the BRD revocation bound further access fails
      And the job is cancelled or explicitly reassigned

    @FR-IAM-005 @R3-Ecosystem @Should
    Scenario: Reconcile directory and platform
      When the Organisation Administrator views reconciliation
      Then differences between the directory and the platform are shown

    @FR-IAM-005 @R3-Ecosystem @Should
    Scenario: Reject manual override of directory-controlled attributes
      Given an attribute controlled by the directory
      When an administrator manually overrides it without a recorded bounded exception
      Then the override is rejected
      And a manual grant may add only separately authorised scope and is removed if policy forbids local supplements

  Rule: FR-IAM-011 Access certification
    As an Organisation Administrator, I want to run access reviews where each grant is retained, narrowed or revoked with a reason, so that access stays justified and stale or orphaned grants are found and fixed.
    Release: R3 Ecosystem · Priority: Should · Built today: Absent

    @FR-IAM-011 @R3-Ecosystem @Should
    Scenario: Start an access review
      When the Organisation Administrator starts an access review for selected scopes and a snapshot date
      Then reviewers see each grant's subject, source of grant, sensitive capabilities, expiry, owner and last relevant activity

    @FR-IAM-011 @R3-Ecosystem @Should
    Scenario: Decide each grant
      When a reviewer retains, narrows or revokes a grant
      Then a reason is recorded
      And unreviewed grants remain flagged overdue

    @FR-IAM-011 @R3-Ecosystem @Should
    Scenario: Review a service identity whose owner has left
      Given a service identity whose owner has left
      When the reviewer assigns a new owner or revokes it
      Then the review decision and execution receipt are retained

    @FR-IAM-011 @R3-Ecosystem @Should
    Scenario: Reject exposure of protected record content
      Given a reviewer is performing an access review
      When they inspect a grant
      Then they see entitlement metadata only and no protected record content

    @FR-IAM-011 @R3-Ecosystem @Should
    Scenario: Reject stale review execution
      Given a grant was replaced after the review decision was made
      When the revocation decision is executed
      Then the current grant revision is rechecked
      And the unrelated replacement grant is not revoked
