# Release 0.75 candidate — combined entitlement view

Coding-only candidate for **US-CM-03 / APL-595**.

The effective-entitlement read combines explicitly `ACTIVE` direct subscriptions and accepted, unexpired sponsored access for the organisation. Every contributing source is visible with its type, stable identifier, source tenant and plan or terms reference. Invited or expired sponsorships and inactive, unresolved or out-of-window subscriptions contribute nothing.

All current sources reduce to one `PLATFORM_ACCESS` entitlement. At most one direct subscription is marked chargeable and `charge_count` is bounded to zero or one; additional direct sources remain visible but cannot create a duplicate charge. Sponsored sources are always non-chargeable. This view records billing intent only; invoice issuance remains a separate later story.

Tests, CI, merge, staging deployment, acceptance and human certification remain pending under the owner's coding-first instruction.
