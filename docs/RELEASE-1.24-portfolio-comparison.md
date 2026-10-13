# Release 1.24 coding candidate — fair portfolio comparison

FR-ANA-007 / APL-612 extends the existing permission-filtered portfolio view with a selectable approved-coverage threshold and exact compatibility groups. Definition revisions and observation periods stay separate. The service refuses a raw cross-group ranking and labels every within-group ordering as qualified pending comparability review.

Rows without an official value or below the chosen coverage threshold are explicitly excluded. Ratio denominators remain visible beside ranked values so equal displayed percentages cannot conceal different eligible populations. A partial permission scope is stated without revealing a hidden member count, identity or inferred total.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
