# Imprana Commons backlog: NFR compatibility
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR compatibility

  Rule: VF-CMP-001 Browser and device support
    As a Field Data Collector, I want the product to work on qualified browsers and devices and to warn me clearly on unsupported ones, so that my work is never silently lost or corrupted.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-CMP-001 @R2-Scale @Should
    Scenario: Current and previous browser versions are qualified
      Given the current and previous major versions of Chrome, Edge, Firefox and Safari at release and the stated mobile OS and client profiles
      When federation, file handling, accessibility, capture and recovery are tested in each declared supported combination
      Then each combination passes
      And the actual browser versions and qualified desktop, mobile and offline profiles are recorded

    @VF-CMP-001 @R2-Scale @Should
    Scenario: Browser changes trigger regression checks
      Given a supported browser releases a change
      When the change is identified
      Then regression checks are run

    @VF-CMP-001 @R2-Scale @Should
    Scenario: Reject silent acceptance of work on unsupported clients
      Given an unsupported browser or device
      When a Field Data Collector tries to work on it
      Then clear guidance is shown
      But the client does not silently accept work it cannot preserve
      And offline support is not promised for a browser merely because online viewing works
