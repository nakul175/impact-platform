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
COMMIT;
