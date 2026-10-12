# Release 0.76 candidate — fixed-fee packages on the subscription invoice

Coding-only candidate for **US-CM-06 / APL-598**.

The bounded service catalogue offers only code-reviewed packages carrying a nonblank scope, positive fixed INR price and stable code. A current subscription administrator selects only the package code; scope, title, currency and price remain server-owned.

Purchase requires an explicitly active, in-window subscription. The service creates or reuses that subscription's single open commercial invoice and appends one immutable fixed-fee line. The request cannot supply another invoice and the response fixes `separate_invoice_created=false`. Exact retries return the original invoice/item receipt; changed payload reuse is refused.

Invoice issuance, tax calculation and payment remain later stories. Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
