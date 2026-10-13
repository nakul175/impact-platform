# Release 1.19 coding candidate — permission-safe filters and drill down

FR-ANA-002 / APL-434 extends authored dashboards with visible current filter values, per-widget compatible-filter declarations, approved disclosure-slice bindings and a closed drill hierarchy of portfolio, partner and programme. Participant-level drill is absent from the contract and refused as invalid.

A filter affects only widgets that declare its field. Other widgets explicitly return `NOT_APPLICABLE` and list the ignored field. An applicable filter displays a value only when the widget carries an approved slice that matches the selected field and single value and pins an exact currently-readable result revision. Otherwise it returns `UNAVAILABLE` with empty chart and table arrays. Multi-value or multiple applicable filters likewise fail closed until an approved combined slice exists, so a partner selection cannot reuse a cross-partner total or reveal a hidden source count.

Saved views continue to pin an exact indicator-definition revision. When the current definition changes, reads report `PINNED_REVISION` and the exact revision in use; they never silently rebind. If the definition or pin is no longer currently readable, the view is withheld.

The dashboard UI displays current filter values, visibly names non-applicable filters, exposes only the permitted drill levels and sends filter changes through the ordinary audited revision command. This release adds no migration or database privilege change. Tests and CI remain deferred by owner request; source checks only are recorded for this unmerged, undeployed coding candidate.
