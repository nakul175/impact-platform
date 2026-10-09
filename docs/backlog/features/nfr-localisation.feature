# Imprana Commons backlog: NFR localisation
# Generated 2026-10-09 from the unified backlog. Refine each story at sprint planning.

Feature: NFR localisation

  Rule: VF-L10-001 Localisation integrity
    As a Data Steward, I want text, numbers, dates and time zones handled correctly in every locale, so that stored values and period assignments stay accurate whatever language people use.
    Release: R2 Scale · Priority: Should · Built today: Absent

    @VF-L10-001 @R2-Scale @Should
    Scenario: Locale-sensitive data survives the full data path
      Given Unicode, decimal-comma, decimal-point, ambiguous date, daylight-saving and right-to-left fixtures where released
      When they are ingested, searched, calculated and exported
      Then stored values, period membership, filters and exported text are preserved correctly

    @VF-L10-001 @R2-Scale @Should
    Scenario: Released translations cover blocking workflow text
      Given a released language
      When its workflows are reviewed
      Then translations cover all blocking workflow text

    @VF-L10-001 @R2-Scale @Should
    Scenario: Reject a display locale that changes results
      Given a stored value and its event period assignment
      When the display locale is changed
      Then any change to the stored value, arithmetic or event assignment fails the check

    @VF-L10-001 @R2-Scale @Should
    Scenario: Reject a language release with missing blocking translations
      Given a language release
      When any blocking workflow text is untranslated
      Then that language release fails
