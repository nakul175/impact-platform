# Release 1.23 coding candidate — disclosure-safe geographic analysis

FR-ANA-006 / APL-616 adds persisted MAP widget configuration bound to one exact currently readable calculated-result revision. Configuration pins the period, geographic dimension, governed boundary revision, authorised aggregate or point-reference layer, permitted granularity, legend and missingness treatment. External point maps are refused; authorised point views carry provider-side references only.

One disclosure-filtered, coordinate-free projection supplies both the map request and sortable equivalent table. Its closed feature and tooltip contracts have no latitude, longitude, geometry or coordinate fields. District aggregate payloads therefore cannot hide household coordinates in tooltips, downloads or external map requests. Suppressed values remain suppressed. Every source boundary revision is returned and a mismatch with the selected version is visibly labelled `MISMATCH`.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
