# Release 0.47 coding candidate: published vetting criteria and listing state

This coding candidate implements US-DC-03 / APL-369. A public read-only endpoint explains what the product means by “vetted,” identifies the criteria edition, and publishes the status and last-review date for every current catalogue listing. The adoption workspace shows the same criteria and listing metadata beside each shortlisted option.

Publication fails closed unless listing metadata covers exactly the current catalogue IDs and every entry has a supported status plus a valid calendar review date. The initial status is provisionally `EDITORIAL_REVIEW_PENDING`, reviewed on the existing source-check date. This deliberately avoids claiming human confirmation, endorsement, warranty, purchase approval or measured performance.

The criteria are a provisional editorial definition: source evidence, explicit use-case mapping, data-review questions and commercial disclosure. Owner/editorial review of the wording and state transitions remains pending. Existing frozen catalogue and archived guidance editions are unchanged; the criteria publication is a separate document joined by stable solution ID.

Status: coding complete as a candidate. Tests, CI, independent review, merge, deployment and owner acceptance have not been run or claimed, following the owner's request to batch those gates later.
