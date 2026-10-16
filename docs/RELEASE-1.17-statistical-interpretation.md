# Release 1.17 coding candidate — governed statistical interpretation

FR-CAL-016 / APL-611 makes statistical interpretation part of the independently approved indicator-definition revision. The closed configuration names the sample basis, weighting, uncertainty method and level, sample or population interpretation, and any reviewed population-expansion method. Existing definitions retain conservative defaults: raw values, no weighting, no uncertainty estimate and sample interpretation.

A pooled median is admitted only from approved eligible raw values. The frozen formula labels it `POOLED_MEDIAN`; the source example 1, 2, 100, 3 and 4 therefore produces 3. Subgroup medians cannot request a pooled median. Their supported alternative is a `MEAN` explicitly labelled `MEAN_OF_MEDIANS` with a limitation stating that it is not a pooled median. Frequency-weighted means and medians require positive weights, with median frequency weights restricted to whole counts.

A sample statistic remains labelled `SAMPLE` and carries a `SAMPLE_NOT_POPULATION` limitation. A population count is refused unless the approved definition contains a named, explained, positive expansion factor; expansion is limited to count measurements and is disclosed in the result and lineage formula. Eligible observation revisions remain pinned in lineage, and reproduction now retains the exact statistical weight used for arithmetic.

The configuration form exposes these choices and the result view names pooled medians and means of medians directly. This release adds no migration or database privilege change.

The focused disposable live positive journey passed locally on 16 October 2026: an independently approved definition and five independently approved raw values `1, 2, 100, 3, 4` produced the exact pooled median `3`, carried the `POOLED_MEDIAN`, `SAMPLE_NOT_POPULATION` and `UNCERTAINTY_NOT_ESTIMATED` disclosures, and reproduced from the exact five pinned source revisions. CI, independent final review, merge, staging deployment and owner acceptance remain separate gates.
