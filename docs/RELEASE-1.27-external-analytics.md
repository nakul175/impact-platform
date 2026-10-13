# Release 1.27 coding candidate — governed external analytics access

FR-ANA-010 / APL-620 adds revocable service identities scoped to exact currently authorised dataset revisions and an explicit field allowlist. Creation records the destination and reuse terms and returns a bounded credential; it does not expose a database connection.

Each refresh rechecks the credential, connection state, exact object revision, restriction state and classification before returning a package with definitions, units, value states and freshness context. Successful extracts are registered with their destination and exact revision set. Revocation blocks new refreshes while retaining the last successful extract and stating that external copies remain tracked, not remotely erased. Create, refresh and revoke use exact-payload idempotency receipts.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
