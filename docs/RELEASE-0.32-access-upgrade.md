# Reviewed tenant access upgrades — development slice

No slice version bump; schema +1 (assigned migration 0036); domain API +0 operations; platform API +8 operations; no requirement acceptance or ledger movement proposed. This is an integration candidate for the unified Tola and nonprofit AI platform.

## Delivered

An existing organisation can request the current registered deployment access profile through its current owner, obtain the exact named second administrator's consent, and receive approval from a current platform operator who represents a different natural person from both administrators. Each consent is tied to the current tenant revision, reviewed profile and current authority snapshot. A changed membership, ceiling, grant, managed role, custody owner, authentication cutoff or deployment profile requires a new request.

The application adds only capabilities introduced since the last applied profile. It preserves existing ceiling and grant expiry dates. A previously removed capability or a capability omitted from an existing managed role stays removed. New authority expires at the earliest existing ceiling for each administrator. Existing custom roles are never rewritten; a conflicting custom role name makes the profile unavailable for this request.

Owners, the exact second administrator and current platform operators have a bounded review inbox. Historical nomination alone gives no access after current authority is revoked. Global and tenant directories use signed cursors with a 15-minute lifetime, bound to identity, route, tenant and current visibility. Current membership heads, status and expiry, principal state and epochs, identity cutoffs, platform operator state and live ceiling holdings participate in the visibility binding.

The upgrade and authority-renewal flows exclude one another while a request is pending. Exact retries return the original receipt only after current actor authority is checked. Changed payloads under the same operation identifier fail closed. Approval, ceiling marker, managed role revisions, grants, principal epochs, platform event and receipt commit atomically.

## Contract and persistence

The closed request selects the second identity, expected tenant revision, current authority hash and registered profile hash, and includes a reason. It cannot supply capabilities, authentication times, consent, approval identities or waiver flags. Accept, approve, reject and cancel actions select the expected request revision and include a reason. Unknown fields and duplicate JSON keys are rejected.

Platform operations are:

- `GET /v1/platform/access-upgrades`
- `GET /v1/platform/tenants/{tenant_id}/access-upgrades`
- `GET /v1/platform/tenants/{tenant_id}/access-upgrade-preview`
- `POST /v1/platform/tenants/{tenant_id}/access-upgrade`
- `POST /v1/platform/tenants/{tenant_id}/access-upgrades/{request_id}/actions/{accept|approve|reject|cancel}`

Migration `0036_reviewed_ceiling_widening.sql` is additive. Its SHA-256 is `4e4bf01ebee650fb5c910c944e9ee6344f66c540d178f8c673bd54116710a464`. It adds the forced-RLS tenant tables `tenant_access_upgrade` and `tenant_access_upgrade_applied`, tenant-qualified bootstrap references, one pending request per tenant, immutable applied markers and controlled state transitions. The existing platform role's restrictive domain-object lists are unchanged.

The global `platform_access_profile` registry is deployment metadata. Runtime platform access is read-only; inserts require owner authority from a reviewed additive migration, and registered entries cannot be updated or deleted. Migration 0036 registers the exact generated profile with hash `48e75c64f1ea2ddceeadce089d1c3f2b056254f236060f1c7d4a18ff439183b0`. A future generated profile requires a new reviewed registry migration. Preview fails closed while the current generated profile is unregistered.

`apply_access_upgrade(uuid,uuid,uuid,timestamptz)` is a narrowly granted owner definer for the platform role. It independently validates the exact registered target, latest applied source manifest, monotonic per-role capability bundles, purpose-bound capability inclusion, exact target-minus-source delta, pinned authority and revisions, live memberships, current operator, recent authentication and three distinct natural persons. It cannot reset the source baseline to an older or narrower registered profile. Application, identity and worker roles cannot invoke it or create ceilings. The directory definers return bounded references and the viewer's own visibility metadata, without granting runtime access across tenant fences.

## Limits

This slice is implemented and qualified locally. It has not been deployed and has not changed any live tenant's access. It does not make the platform production-ready or mark any original requirement accepted. Current implementation evidence is distinct from the retained target design.

PGlite exercises application behaviour and bounded `SET ROLE` checks, not PostgreSQL concurrency or provisioned-login deployment evidence. Four native-only tests await the integrator's real PostgreSQL run: registered role narrowing, registered purpose-bound relocation, an unregistered forged profile, and actual login isolation for app, identity and worker roles. Hosted identity, container and full deployment gates remain outside this focused run.

The exact existing second administrator must still hold current authority and membership. Replacing that administrator, renewing expired authority, owner recovery and tenancy readiness changes retain their separate governed flows. Existing retired or missing managed roles are not recreated as part of an upgrade. This flow does not grant ordinary customer data access merely because a person has custody or control-plane review authority.

## Reproduction

Focused reports preserved on 5 October 2026:

- `docs/evidence/sprint-0.32-access-upgrade-unit.xml`: 20 passed pure contract/profile checks.
- `docs/evidence/sprint-0.32-access-upgrade-local-tests.xml`: 62 passed, 4 native-only skips. The new upgrade file contributes 33 passed and 4 skipped; the existing renewal file contributes 29 passed. No failures.
- `docs/evidence/sprint-0.32-access-upgrade-evidence.json`: source hashes and focused evidence scope.

The generic historical `application-tests.xml` was restored after the focused run. These named reports do not replace the historical full-suite evidence.

```sh
.venv/bin/pytest qualification/test_access_upgrade_unit.py -q
IMPACT_PORT=8181 .venv/bin/python scripts/run.py test \
  --pytest-path qualification/test_access_upgrade.py \
  --pytest-path qualification/test_authority_renewal.py
```

## Integration notes

Backend-owned files are `access_upgrade.py`, `access_upgrade_contracts.py`, migration 0036 and the two access-upgrade test files. The narrowly approved existing-file edits are the pending-upgrade guard in `authority_renewal.py` and its reason in `renewal_contracts.py`. The integrator owns main routes, `tenant_contracts.py`, generated contracts, frontend wiring, versions, SQL dictionary and shared documentation.

Add the pure qualification file to the unit target. Regenerate contracts after integrating all slices and expose the `ACCESS_PROFILE_NOT_REGISTERED` and `ACCESS_PROFILE_ROLE_CONFLICT` reasons in the UI. The current generated profile must match the registry seed byte-for-byte as decoded JSON; the pure seed-equality regression protects this boundary. The source migration hash above is ready for the shared data dictionary.

Record the implemented owner → exact second administrator → independent current operator flow in implementation and API inventories, with eight platform operations and no new domain capabilities. Record focused local counts separately from subsequent native, browser and full-suite counts. Keep the original requirement ledger unchanged until the integrator proposes a specific requirement movement supported by final-tree evidence.

Security regressions include `test_direct_platform_cannot_reset_baseline_to_a_registered_but_narrower_profile`, `test_direct_platform_proposal_cannot_apply_a_forged_unregistered_target`, `test_signed_cursors_bind_identity_route_tenant_visibility_and_expiry`, the existing managed-role omission and assigned-principal denial check, stale consent, current-authority-before-receipt checks, independent-person aliases, cross-tenant RLS, and an injected failure that rolls back the entire approval transaction. The native variants use provisioned runtime login DSNs and never print credentials.
