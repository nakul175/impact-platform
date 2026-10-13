# Release 1.31 coding candidate — frozen analysis packages

FR-EVA-003 / APL-632 freezes approved observation and official calculated-result revisions into integrity-bound analysis packages. Each package records the exact reviewed evaluation methodology, selected safe variables, declarative filters, dictionary, approved source digests and optional Evidence revisions for reviewed scripts or notebooks.

Uploaded code is retained as evidence with execution prohibited. Results reference the exact package, package integrity digest and methodology revision. Later source corrections cannot rewrite the frozen package, and export requires the separate `report.export` capability and an integrity recheck.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
