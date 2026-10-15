# Release 1.42 — Effective access coding completion

## Delivered

FR-ACC-003 / APL-350 now provides an actor-facing effective-access inspector for every active member and a tenant-administrator member simulation. The explanation evaluates current direct and group grant paths, purpose requirements, record restrictions, scope membership, field-category restrictions and session assurance.

Explicit record and field facets narrow the subject's effective capability across conflicting roles. A wider second role cannot erase a current attached restriction. The same precedence is applied by request authorization, field checks and list visibility so the explanation does not disagree with runtime enforcement.

Results expose only safe path labels, scope types, category codes, decisions and requirement codes. They do not expose scope IDs, selected object IDs, protected resource names, record values or the simulated principal identifier. Unknown or unavailable records produce a sanitized denial.

## Contract and UI

- Own explanation remains available through `POST /v1/tenants/{tenant_id}/access/effective/self` to every role that holds the common member notification capability.
- Tenant administrators use `POST /v1/tenants/{tenant_id}/access/effective/simulations` and may select only a current member returned by the governed directory.
- Both requests accept an optional stated purpose and a paired field-category/access-mode context.
- The account page provides the self inspector. People & access provides the administrator simulation when `grants.read` is current.

## Security limits

Simulation remains tenant-wide because the delivered administrator authority is tenant-wide `grants.read`; narrower delegated administration is not claimed. The operation picker is a bounded catalogue of common read actions and never searches protected resources. Explicit deny records outside the existing immutable grant facets are not invented.

## Reproduction

Run:

```text
.venv/bin/python -m pytest qualification/test_effective_access_unit.py
make lint
make unit
```

Full exact-candidate CI, independent review, merge and staging verification remain separate delivery gates.

## Integration notes

- Story: FR-ACC-003 / APL-350.
- The focused tests cover conflicting-role restriction precedence, sanitized unavailable resources, purpose requirements, closed request validation and list-visibility alignment.
- APL-614 remains a separate partial candidate in the same integration build and is not promoted by this note.
