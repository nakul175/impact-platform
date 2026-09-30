BEGIN;
SET LOCAL ROLE impact_owner;
-- Live identity provider (v0.15). A browser session created from an OIDC sign-in records the
-- provider's session identifier (the ID token's sid claim) so that a verified back-channel logout
-- token revokes exactly the platform sessions of that provider session, and a sealed logout hint:
-- the ID token encrypted (AES-256-GCM) under a key derived from the session cookie value, which
-- the database never stores, so the hint is usable only by a request that presents the session.
-- No provider access or refresh token is stored anywhere. Development sign-in leaves both NULL.
ALTER TABLE impact.web_session ADD COLUMN provider_sid varchar(255);
ALTER TABLE impact.web_session ADD COLUMN provider_logout_hint bytea
 CHECK(octet_length(provider_logout_hint) BETWEEN 29 AND 16412);
CREATE INDEX web_session_provider_sid ON impact.web_session(provider_sid) WHERE provider_sid IS NOT NULL;
-- Back-channel logout tokens already accepted, per issuer and jti, until the token expires: a
-- replayed token is refused. Insert-once (no UPDATE grant); expired rows are purged by the
-- identity role in bounded batches. Identity table: no tenant_id, reached only via impact_identity.
CREATE TABLE impact.oidc_logout_token(
 issuer varchar(512) NOT NULL, jti varchar(255) NOT NULL, expires_at timestamptz NOT NULL,
 accepted_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(issuer,jti)
);
CREATE INDEX oidc_logout_token_expiry ON impact.oidc_logout_token(expires_at);
GRANT SELECT,INSERT,DELETE ON impact.oidc_logout_token TO impact_identity;
COMMIT;
