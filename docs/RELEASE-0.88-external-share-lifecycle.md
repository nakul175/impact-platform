# 0.88 external share lifecycle

FR-ACC-006 / APL-353 adds authenticated shares pinned to an exact derivative revision, named audience, actions, owner, reason and a maximum seven-day expiry. Link possession is insufficient; reads revalidate audience, expiry, revocation and all source permissions and disclose no preview on failure.

`qualification/test_external_share_lifecycle_live.py` exercises the real HTTP flow on a disposable database. A private exact derivative is shared with one named authenticated principal for one declared action and expiry; an unrelated principal receives no preview. The audience can read until owner revocation, a synthetically advanced expiry, or loss of current source authority, after which the same share is uniformly unavailable. Independent review, CI, merge and deployment remain separate gates.
