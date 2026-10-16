# Release 1.23 coding candidate — disclosure-safe geographic analysis

FR-ANA-006 / APL-616 adds persisted MAP widget configuration bound to one exact currently readable calculated-result revision. Configuration pins the period, geographic dimension, governed boundary revision, authorised aggregate or point-reference layer, permitted granularity, legend and missingness treatment. External point maps are refused; authorised point views carry provider-side references only.

One disclosure-filtered, coordinate-free projection supplies both the map request and sortable equivalent table. Its closed feature and tooltip contracts have no latitude, longitude, geometry or coordinate fields. District aggregate payloads therefore cannot hide household coordinates in tooltips, downloads or external map requests. Suppressed values remain suppressed. Every source boundary revision is returned and a mismatch with the selected version is visibly labelled `MISMATCH`.

This release adds no migration or privilege change.

## Positive journey evidence

The synthetic HTTP journey
`qualification/test_dashboard_geography_live.py::test_analyst_previews_one_coordinate_free_map_and_equivalent_table`
passed on 16 October 2026. It creates and independently approves three district-coded observations,
calculates their exact result, saves a version-bound aggregate map through the API, and reads the
geographic preview. The selected and source boundary versions match, the North and South values are
12 and 3, and the map request is byte-equivalent to the accessible table. The returned structure has
no latitude, longitude, geometry or hidden coordinate member; it declares
`NO_COORDINATES_IN_PLATFORM_PAYLOAD`.

CI, independent review, merge, staging deployment and product acceptance remain separate gates.

## Integration notes

- Story: APL-616 / FR-ANA-006.
- Positive user journey: locally passed; no acceptance, CI or deployment movement.
