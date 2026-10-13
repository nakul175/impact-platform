# Release 0.77 candidate — partner revenue-share statements

Coding-only candidate for **US-CM-07 / APL-604**.

Freshly assured platform operators can attribute one exact tenant invoice to one partner and month only when recorded amount and currency equal the invoice's current immutable line total. A partner/month statement includes every recorded entry, one currency and the exact summed amount. Generation rechecks every invoice and records whether the statement reconciles.

Settlement is a separate platform command. It refuses an unreconciled or already settled statement and rechecks every underlying invoice immediately before settlement. Exact command retries are receipt-backed and changed operation reuse is refused. Tenant roles have no access to these platform tables or functions.

Partner payout execution remains outside this candidate. Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
