# Imprana Commons backlog: Funder portfolio
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Funder portfolio

  Rule: US-FP-01 Enrol and manage a cohort
    As a Funder Portfolio Manager, I want to enrol and manage a cohort, so that I can support many grantees at once.
    Release: R1 Pilot · Priority: Must · Built today: Absent

    @US-FP-01 @R1-Pilot @Must
    Scenario: Bulk invite grantees to a cohort
      Given a Funder Portfolio Manager with a list of grantee organisations
      When they invite them to a cohort in one bulk action
      Then each organisation receives an invitation

    @US-FP-01 @R1-Pilot @Must
    Scenario: Cohort status view
      Given a cohort with invited grantees
      When the Funder Portfolio Manager opens the cohort status view
      Then the status of each grantee in the cohort is shown

    @US-FP-01 @R1-Pilot @Must
    Scenario: Reject organisations outside the cohort
      Given an organisation not enrolled in the Funder Portfolio Manager's cohort
      When they open the cohort status view
      Then that organisation is not shown

  Rule: US-FP-03 Portfolio impact report
    As a Funder Portfolio Manager, I want a portfolio impact report, so that I can report to my board.
    Release: R1 Pilot · Priority: Must · Built today: Partial

    @US-FP-03 @R1-Pilot @Must
    Scenario: Export a portfolio impact report
      Given a portfolio with shared grantee data
      When the Funder Portfolio Manager exports the impact report
      Then the report includes its methodology and data sources

    @US-FP-03 @R1-Pilot @Must
    Scenario: Reject a report without methodology or sources
      Given a portfolio impact report
      When its methodology or data sources are missing
      Then the report is not accepted

  Rule: US-FP-02 Portfolio progress, adoption and ROI across grantees
    As a Funder Portfolio Manager, I want to see portfolio progress, adoption and ROI, so that I know the capacity investment is working.
    Release: R2 Scale · Priority: Must · Built today: Absent

    @US-FP-02 @R2-Scale @Must
    Scenario: Portfolio view aggregated by default
      Given a cohort of grantees who share metrics
      When the Funder Portfolio Manager opens the portfolio view
      Then progress, adoption and ROI are shown aggregated across grantees by default

    @US-FP-02 @R2-Scale @Must
    Scenario: Reject metrics grantees have not agreed to share
      Given a grantee who has not agreed to share a metric
      When the Funder Portfolio Manager views the portfolio
      Then that metric is not shown for that grantee
      And it is not included in any aggregate

  Rule: US-FP-04 Grantee controls what the funder sees
    As an Executive Director, I want to control exactly what my funder sees, so that I can trust the platform.
    Release: R2 Scale · Priority: Must · Built today: Partial

    @US-FP-04 @R2-Scale @Must
    Scenario: Set sharing per metric
      Given an Executive Director of a grantee organisation
      When they set sharing on or off for each metric
      Then the funder sees only the metrics set to shared

    @US-FP-04 @R2-Scale @Must
    Scenario: Log of what was shared and when
      Given metrics have been shared with the funder
      When the Executive Director opens the sharing log
      Then it shows each metric that was shared and when

    @US-FP-04 @R2-Scale @Must
    Scenario: Reject showing a metric that is not shared
      Given a metric set to not shared
      When the funder views the grantee's data
      Then the metric is not visible
