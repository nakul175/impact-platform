# Release 1.18 coding candidate — governed dashboard authoring

FR-ANA-001 / APL-610 activates saved Dashboard drafts and constrains each draft to one through ten permitted metric, table, trend, target, narrative or evidence widgets. Every widget pins one exact CalculatedResult or Evidence revision, view mode, period, dimensions, disclosure classification, layout position and mandatory quality-context flag. Duplicate widget identities or positions and any attempt to hide quality context are refused.

Dashboard creation and editing use the existing audited, tenant-fenced revision command path. Copy is an idempotent audited command and always creates an INTERNAL `PRIVATE_DRAFT`; it grants no new access. Desktop, mobile and table previews use the same server response. Calculated-result chart values and labelled table rows are built from the same stored value. Coverage, freshness, limitations and mode remain visible alongside the widget.

Preview rechecks current object access and the exact revision pin under the tenant transaction. If a binding is revoked, restricted, removed or superseded, the response contains `UNAVAILABLE`, empty chart values, empty table rows and no cached quality payload. The React authoring view creates drafts, adds permitted result widgets up to ten, copies privately and switches among desktop, mobile and table previews.

This release adds no migration or database privilege change; the existing `dashboard_current` projection is used. The story-specific live journey proves a ten-widget mobile preview with chart/table parity, visible quality context and an idempotent private copy; CI, deployment and acceptance remain separate gates.
