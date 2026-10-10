# Imprana Commons backlog: Data quality
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Data quality

  Rule: FR-DQ-003 Duplicate detection
    As a Data Steward, I want exact and fuzzy duplicate detection with reviewed decisions to keep records distinct, merge them or investigate further, so that duplicates are resolved without wrongly combining different people or losing provenance.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DQ-003 @R1-Pilot @Must
    Scenario: Detect exact duplicates by declared business keys
      Given business keys are declared for a record type
      When two records share the same business key values
      Then they are flagged as exact duplicates

    @FR-DQ-003 @R1-Pilot @Must
    Scenario: Same-name participants stay separate until reviewed evidence supports a merge
      Given two participants both named Asha
      When fuzzy matching proposes them as a candidate pair with permitted evidence and match rationale
      Then they remain separate until a Reviewer chooses distinct, merge or further investigation
      And a merge happens only when reviewed evidence supports identity equivalence
      And the merge maps both source identities to a canonical record, preserving provenance and source confidentiality

    @FR-DQ-003 @R1-Pilot @Must
    Scenario: Unmerge restores relationships and counts
      Given two records were merged into a canonical record
      When a Data Steward performs an unmerge or corrective split
      Then the affected relationships are restored
      And affected counts are recalculated

    @FR-DQ-003 @R1-Pilot @Must
    Scenario: Reject a merge based solely on a shared name
      Given two participants named Asha with no other supporting evidence
      When a merge is attempted solely on the shared name
      Then the merge is refused

    @FR-DQ-003 @R1-Pilot @Must
    Scenario: Reject silent reappearance of a rejected match
      Given a Reviewer has rejected a candidate match
      When duplicate detection runs again
      Then the rejected match does not silently reappear as confirmed

  Rule: FR-DQ-006 Completeness and timeliness
    As a MEL Manager, I want a completeness and timeliness view based on each period's obligation snapshot that distinguishes expected, received, valid, approved, late and excepted submissions, so that I see reliable reporting coverage with transparent numerators and denominators.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @FR-DQ-006 @R1-Pilot @Must
    Scenario: Completeness view distinguishes submission states
      Given a period with an obligation snapshot
      When a MEL Manager opens the completeness view
      Then it distinguishes expected, received, valid, approved, late and excepted submissions
      And each percentage shows its numerator and denominator
      And lateness uses first valid receipt or approval according to the declared metric

    @FR-DQ-006 @R1-Pilot @Must
    Scenario: Retired partner keeps its historic obligations
      Given a partner with a missing June submission
      When the partner is retired in July
      Then the missing June submission remains counted
      And no August obligation is created for that partner

    @FR-DQ-006 @R1-Pilot @Must
    Scenario: Reject rewriting older obligation denominators
      Given past periods with obligation snapshots
      When current partner membership changes
      Then the older obligation denominators are not rewritten

    @FR-DQ-006 @R1-Pilot @Must
    Scenario: Reject an unapproved obligation cancellation
      Given an obligation in a period
      When it is cancelled without approved effective dates and a reason
      Then the cancellation is refused

  Rule: FR-DQ-001 Quality rule catalogue
    As a Data Steward, I want to define quality rules with a rule type, target fields, scope, severity, owner and effective version and preview their failures on a permitted sample before activation, so that data checks are consistent, traceable and safe to switch on.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DQ-001 @R2-Scale @Must
    Scenario: Define and preview a quality rule before activation
      Given a Data Steward in the quality editor
      When they define a rule with rule type, target fields, scope, severity, owner and effective version
      And they preview it against a permitted sample
      Then the preview reports the failures the rule would raise before the rule is activated

    @FR-DQ-001 @R2-Scale @Must
    Scenario: Inspect a failing record for a date cross-field check
      Given a Data Steward has activated a "visit date after birth date" check
      When a record has a visit date that is not after its birth date
      Then the failing record shows the exact rule version that failed
      And it shows a safe field message

    @FR-DQ-001 @R2-Scale @Must
    Scenario: Rule updates apply prospectively
      Given an active quality rule
      When the Data Steward updates the rule without requesting a reviewed revalidation job
      Then the updated rule applies prospectively only
      And existing records are revalidated only when a reviewed revalidation job is requested

    @FR-DQ-001 @R2-Scale @Must
    Scenario: Reject a rule reading a field outside its authorised scope
      Given a Data Steward defining a quality rule
      When the rule targets a field outside its authorised processing scope
      Then the system refuses to let the rule read that field

  Rule: FR-DQ-002 Blocking and warning behaviour
    As a Data Steward, I want blocking errors to prevent progression, review warnings to require an explicit disposition and informational findings not to block, with correction, revalidation and exception kept as separate actions, so that quality issues are handled according to their severity.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DQ-002 @R2-Scale @Must
    Scenario: Blocking error stays blocked until corrected
      Given a submission with a blocking duplicate event
      When a Reviewer attempts to approve it
      Then the approval is blocked
      And it stays blocked until the duplicate is corrected

    @FR-DQ-002 @R2-Scale @Must
    Scenario: Permitted warning proceeds only with its recorded exception
      Given a submission with a review warning that policy permits to be excepted
      When an exception request is recorded with the rule, affected revision, reason, authority and expiry
      Then the submission can proceed with that exception recorded
      But it cannot proceed without an explicit disposition of the warning

    @FR-DQ-002 @R2-Scale @Must
    Scenario: Informational findings do not block
      Given a submission with only informational findings
      When it is progressed
      Then the findings do not block progression

    @FR-DQ-002 @R2-Scale @Must
    Scenario: Reject dismissing a notification as a resolution
      Given a submission with a blocking error or review warning
      When a user dismisses the notification about it
      Then the underlying issue remains unresolved

    @FR-DQ-002 @R2-Scale @Must
    Scenario: Reject waiving non-waivable conditions
      Given a finding caused by a security restriction, an impossible calculation or self approval
      When an exception is requested for it
      Then the exception is refused

  Rule: FR-DQ-004 Reconciliation checks
    As a Data Steward, I want reconciliation rules that declare the expected equation and category semantics, so that totals are checked correctly for both exclusive and overlapping breakdowns.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DQ-004 @R2-Scale @Must
    Scenario: Exclusive components reconcile to the total
      Given a reconciliation rule for an exclusive exhaustive breakdown
      And a total of ten with components six and four
      When the check compares the component sum to the total at the stated precision
      Then the check passes

    @FR-DQ-004 @R2-Scale @Must
    Scenario: Overlapping categories are not forced to sum to the total
      Given a reconciliation rule for overlapping service categories
      And a total of ten with two overlapping service categories of six and seven
      When the check runs
      Then the categories are not required to sum to ten
      And the check compares distinct entities or uses a labelled nonadditive check

    @FR-DQ-004 @R2-Scale @Must
    Scenario: Missing components make the check incomplete
      Given an exclusive breakdown with a missing component
      When the check runs
      Then the check is marked incomplete
      But it is not automatically marked failed or passed

    @FR-DQ-004 @R2-Scale @Must
    Scenario: Reject exposing suppressed values in public reconciliation detail
      Given a reconciliation that involves suppressed values
      When the reconciliation detail is published
      Then the suppressed values may have been evaluated privately
      But they are never exposed in the public reconciliation detail

  Rule: FR-DQ-005 Quality issue workflow
    As a Data Steward, I want each quality issue to track the failing revision, rule, severity, owner and due time through correction, revalidation and evidenced closure, so that issues are resolved traceably and unresolved material issues stay visible on dependent results.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DQ-005 @R2-Scale @Must
    Scenario: Trace a malformed date from import rejection to accepted revision
      Given an imported record is rejected for a malformed date
      And a quality issue binds the failing revision, rule, severity, owner and due time
      When a correction opens a linked revision
      And revalidation confirms the new outcome
      Then closure records its evidence
      And the reporting delay and final accepted revision remain traceable

    @FR-DQ-005 @R2-Scale @Must
    Scenario: Unresolved material issue stays attached to dependent results
      Given an unresolved material quality issue
      When a dependent result is viewed
      Then the issue remains attached to that result

    @FR-DQ-005 @R2-Scale @Must
    Scenario: Recurrence links to prior history
      Given a quality issue that was previously fixed
      When the issue recurs
      Then the new recurrence links to the prior history
      And the earlier fix is not erased

    @FR-DQ-005 @R2-Scale @Must
    Scenario: Reject closing an issue by changing owner or resolving a comment
      Given an open quality issue
      When its owner is changed or a comment on it is marked resolved
      Then the issue remains open

  Rule: FR-DQ-008 Quality disclosure
    As a MEL Manager, I want every result to carry its required quality disclosures through dashboards, report templates, exports and AI drafting, so that readers always see material caveats such as partial coverage.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @FR-DQ-008 @R2-Scale @Must
    Scenario: Partial coverage disclosed in chart and narrative exports
      Given a report generated from three of five approved submissions
      When the chart and the narrative are exported
      Then both exports retain the partial coverage disclosure
      And both show 60 percent approval completeness

    @FR-DQ-008 @R2-Scale @Must
    Scenario: Shortened disclosure uses approved wording
      Given a result with a required quality disclosure
      When an author shortens the disclosure
      Then only an approved equivalent wording template can be used

    @FR-DQ-008 @R2-Scale @Must
    Scenario: Restricted detail withheld while the limitation stays visible
      Given a disclosure that references restricted detail
      When the result is shown to a user without access to that detail
      Then the restricted detail is withheld
      And the material limitation remains visible

    @FR-DQ-008 @R2-Scale @Must
    Scenario: Reject hiding partial coverage
      Given a result with a partial coverage disclosure
      When an author removes a widget, exports a bare number, or applies dashboard styling, a report template or AI drafting
      Then the material partial coverage caveat is still preserved with the result

  Rule: FR-DQ-007 Anomaly assistance
    As a Data Steward, I want anomaly runs to suggest possible issues with their method, data, comparison window and explanation for me to confirm, dismiss with a reason or defer, so that unusual data is reviewed without being changed automatically.
    Release: R3 Ecosystem · Priority: Should · Built today: Partial

    @FR-DQ-007 @R3-Ecosystem @Should
    Scenario: Anomaly run records its context and suggests findings
      Given eligible data for an anomaly run
      When the anomaly run executes
      Then it records the method version, eligible data, comparison window and explanation
      And its findings enter a suggested state with severity and owner

    @FR-DQ-007 @R3-Ecosystem @Should
    Scenario: Seasonal spike reviewed as expected
      Given an anomaly run flags a seasonal spike
      When a Data Steward reviews it as expected and dismisses it with a reason
      Then the underlying data is retained unchanged
      And the dismissed suggestion remains distinct from a confirmed quality defect
      And the false positive evidence is retained under the minimised policy to inform later evaluated model changes

    @FR-DQ-007 @R3-Ecosystem @Should
    Scenario: Reject a flag that changes data or labels a person
      Given an anomaly finding has been raised
      When it is suggested, confirmed, dismissed or deferred
      Then it never modifies the underlying data
      And it never labels a person as fraudulent
