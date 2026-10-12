# Release 0.45 coding candidate: bounded solution shortlist

This coding candidate implements US-DC-01 / APL-367. For an opportunity with more than three matching options, the default server response and workspace view show at most three. A person must explicitly request expansion before further matching options are returned.

The shortlist is derived only from the current validated, source-backed editorial catalogue and exact use-case mappings. In this candidate, **vetted** means present in that validated catalogue edition with its required source and commercial-disclosure fields. It does not mean that an advisor, the owner, or a release reviewer has endorsed the product or approved a purchase.

The read is tenant-authorised through the existing `ai.enablement.read` capability. Invalid requests and invalid catalogue editions fail closed. The response reports the catalogue content version and whether expansion was requested.

Status: coding complete as a candidate. Tests, CI, independent review, merge, deployment and owner acceptance have not been run or claimed, following the owner's request to batch those gates later.
