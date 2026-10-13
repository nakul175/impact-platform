# Release 1.25 coding candidate — governed dashboard publication

FR-ANA-008 / APL-614 adds an authority-checked recipient sharing preview that reports unavailable bindings without creating grants. Private copy remains a new draft and preserves no additional access.

Publication pins the exact dashboard revision, layout, bindings, audience, owner and expiry. Public publication refuses calculated results and any source that is not a public Evidence artifact. Publication status rechecks every pinned source revision and classification, returning `SUSPENDED` after expiry or any source authority/sensitivity change. Publish retries use the exact operation identity and payload fingerprint.

This release adds no migration or privilege change. Tests and CI remain deferred by owner request.
