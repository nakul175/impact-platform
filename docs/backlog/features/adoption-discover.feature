# Imprana Commons backlog: Adoption: Discover
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Adoption: Discover

  Rule: US-DC-01 At most 2-3 vetted options per opportunity
    As an Executive Director, I want to see no more than 2-3 vetted options per opportunity, so that I am not overwhelmed.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DC-01 @R1-Pilot @Must
    Scenario: Default view shows at most 3 options
      Given an opportunity with more than 3 vetted options
      When the Executive Director opens the opportunity
      Then at most 3 options are shown

    @US-DC-01 @R1-Pilot @Must
    Scenario: More options only on request
      Given the default view of an opportunity with more than 3 vetted options
      When the Executive Director asks to see more options
      Then the remaining vetted options are shown

    @US-DC-01 @R1-Pilot @Must
    Scenario: Reject more than 3 options by default
      Given an opportunity with more than 3 vetted options
      When the default view loads without a request for more
      Then no more than 3 options are shown
      And no unvetted option is shown

  Rule: US-DC-02 Fit score per option (advisor-scored in pilot)
    As an Executive Director, I want to see how well each option fits us, so that I can choose with confidence.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-DC-02 @R1-Pilot @Must
    Scenario: Fit score shown for each option
      Given a vetted option for an opportunity
      When the Executive Director views the option
      Then a fit score is shown covering size, budget, context, language, data sensitivity and existing systems

    @US-DC-02 @R1-Pilot @Must
    Scenario: Fit score set by an advisor in the pilot
      Given the pilot release
      When an option's fit score is produced
      Then it is scored by an Imprana Advisor

    @US-DC-02 @R1-Pilot @Must
    Scenario: Reject an incomplete fit score
      Given an option's fit score
      When any of size, budget, context, language, data sensitivity or existing systems is not assessed
      Then the fit score is not shown as complete

  Rule: US-DC-03 Published vetting criteria and status
    As an Executive Director, I want to see the vetting criteria and each solution's status, so that I know what vetted means.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-DC-03 @R1-Pilot @Must
    Scenario: Public vetting criteria page
      Given the published vetting criteria
      When anyone opens the criteria page
      Then the vetting criteria are shown

    @US-DC-03 @R1-Pilot @Must
    Scenario: Status and last-review date on every listing
      Given the solution catalogue
      When the Executive Director views any listing
      Then the listing shows its vetting status and last-review date

    @US-DC-03 @R1-Pilot @Must
    Scenario: Reject a listing without status or review date
      Given a solution listing with no vetting status or no last-review date
      When it is published to the catalogue
      Then publication is refused

  Rule: US-DC-04 Disclose commercial relationships
    As an Executive Director, I want any commercial relationship with a listed solution disclosed, so that I can judge neutrality.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-DC-04 @R1-Pilot @Must
    Scenario: Disclosure label on every listing
      Given any solution listing
      When the Executive Director views it
      Then it carries a disclosure label stating any commercial relationship with the solution

    @US-DC-04 @R1-Pilot @Must
    Scenario: Reject a listing without a disclosure label
      Given a solution listing with no disclosure label
      When it is published to the catalogue
      Then publication is refused
