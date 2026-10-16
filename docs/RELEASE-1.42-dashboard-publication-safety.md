# Release 1.42 — Dashboard publication safety checkpoint

## Delivered

- Registers `DashboardPublication` as an allowed immutable registry kind through additive migration 0099.
- Keeps publication registry and revision rows unavailable to the background worker, which has no duty for publication manifests.
- Adds visible recipient-binding previews and publication status controls to the dashboard UI.
- Requires the exact dashboard revision when publishing and registers the sharing, publish and status operations in the generated access policy.
- Fails closed for anonymous public publication until independently reviewed dashboard disclosure artifacts and a safe retrieval boundary are implemented.

## Contract and persistence

The API contract is unchanged. Migration 0099 repairs the missing registry-kind declaration required by the existing internal publication API. Migrations 0001–0098 remain byte-exact.

## Limits

APL-614 is not coding-complete. Cross-workspace funder copying, approved public disclosure artifacts, governed owner transfer, durable suspension/revalidation, publication content retrieval and story-level qualification remain open. No testing, acceptance, merge or deployment is claimed by this checkpoint.

## Reproduction

Regenerate contracts and run the repository formatting/type checks. The focused application and native PostgreSQL qualification packs must be added before this story can be promoted.

## Integration notes

- Active story: FR-ANA-008 / APL-614.
- This is a traceable partial checkpoint, not a completed-story increment.
- Risk: treating a generic public-classified evidence row as independently approved disclosure material could disclose data incorrectly; the candidate now refuses PUBLIC publication until that workflow exists.
