# Release 1.26 coding candidate — alerts and thresholds

FR-ANA-009 / APL-618 adds governed alert rules that pin a measure, threshold condition, minimum approved coverage, maximum freshness, evaluation cadence, recipients and cooldown. Evaluation classifies missingness, stale input and threshold breach separately. Missing values never enter threshold arithmetic, and only official present results can trigger a threshold incident.

Every threshold or stale incident pins the exact evaluated result revision. A missed result creates a missingness incident without inventing a value. Repeated evaluations of the same alert type inside the cooldown update the existing incident occurrence count instead of creating a separate incident. Create and evaluate operations retain exact-payload idempotency receipts.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
