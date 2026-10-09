# Imprana Commons backlog: Transition
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: Transition

  Rule: US-RT-01 Written licence from Nakul Jain to Athena
    As Athena Leadership, I want a written licence from Nakul Jain to use, host and modify the Impact Platform code, so that Athena's use is legally clear.
    Release: Foundation · Priority: Must · Built today: Absent

    @US-RT-01 @Foundation @Must
    Scenario: Signed licence before pilot work starts
      Given pilot work has not started
      When Athena Leadership checks the licence
      Then a written licence signed by Nakul Jain grants rights to use, host and modify the Impact Platform code
      And it covers Athena and its contractors

    @US-RT-01 @Foundation @Must
    Scenario: Repository stays in Nakul's GitHub account
      Given the licence is in place
      When Athena uses the code
      Then the repository stays in Nakul's GitHub account

    @US-RT-01 @Foundation @Must
    Scenario: Reject pilot work without a signed licence
      Given no signed licence covering Athena and its contractors
      When pilot work is due to start
      Then pilot work does not start

  Rule: US-RT-02 Tag, rename and rebrand as Imprana Commons
    As the Product Owner, I want the current state tagged and the repository renamed and rebranded as Imprana Commons, so that it represents one product.
    Release: Foundation · Priority: Must · Built today: Absent

    @US-RT-02 @Foundation @Must
    Scenario: Tag the current state
      Given the last Impact Platform commit
      When the Product Owner checks the repository tags
      Then a tag marks that commit

    @US-RT-02 @Foundation @Must
    Scenario: Rename and rebrand as Imprana Commons
      Given the repository has been renamed
      When someone opens the old repository URL
      Then they are redirected to the renamed repository
      And the interface, README and docs say Imprana Commons

    @US-RT-02 @Foundation @Must
    Scenario: Reject an incomplete rebrand
      Given the rename and rebrand are done
      When the old URL does not redirect, or the interface, README or docs still present the product as Impact Platform
      Then the rebrand is not accepted

  Rule: US-RT-03 Archive evidence and agent logs out of main
    As a Platform Operator, I want saved test evidence, failed-run folders and agent logs archived out of main, so that the repository is lean and easy to navigate.
    Release: Foundation · Priority: Must · Built today: Absent

    @US-RT-03 @Foundation @Must
    Scenario: Archive evidence and agent logs out of main
      Given the tag on the last Impact Platform commit
      When the archive change is merged to main
      Then docs/evidence and dated agent logs are no longer in main
      And they are still available at the tag

    @US-RT-03 @Foundation @Must
    Scenario: Keep governance templates and current guides
      Given the archive change has been merged
      When the Platform Operator browses main
      Then governance templates and current guides are still present

    @US-RT-03 @Foundation @Must
    Scenario: Reject lost evidence or removed current material
      Given the archive change
      When evidence or agent logs are missing from the tag, or governance templates or current guides are removed from main
      Then the change is rejected

  Rule: US-RT-05 One GitHub backlog for all requirements
    As the Product Owner, I want Impact Platform's 307 requirements and these stories in one GitHub backlog, so that there is one source of truth.
    Release: Foundation · Priority: Must · Built today: Absent

    @US-RT-05 @Foundation @Must
    Scenario: Import requirements as issues with their IDs
      Given Impact Platform's 307 requirements and these stories
      When they are imported into the GitHub backlog
      Then each requirement becomes an issue carrying its ID

    @US-RT-05 @Foundation @Must
    Scenario: Duplicates handled and acceptance refined
      Given imported issues that duplicate each other
      When the Product Owner triages them
      Then each duplicate is linked or closed
      And when a story is refined its prose acceptance is converted to Gherkin

    @US-RT-05 @Foundation @Must
    Scenario: Reject an incomplete backlog
      Given the import is complete
      When any requirement is missing or lacks its ID, or a duplicate is neither linked nor closed
      Then the backlog is not accepted as the single source of truth
