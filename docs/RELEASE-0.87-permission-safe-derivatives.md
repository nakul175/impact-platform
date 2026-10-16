# 0.87 permission-safe derivatives

FR-ACC-005 / APL-352 adds immutable source-revision manifests for dashboards, searches, analyses and AI artifacts. Reads recheck every source through current authority; a mixed-source derivative cannot be marked public, while the separately typed approved aggregate remains explicit.

`qualification/test_permission_safe_derivatives_live.py` exercises the real HTTP flow on a disposable database. It records and returns the exact immutable Evidence revision, then revokes the reader's current Evidence authority and observes an opaque unavailable response on the same derivative. It also refuses an ordinary analysis that attempts to claim approved-aggregate disclosure. Independent review, CI, merge and deployment remain separate gates.
