# Release 1.33 coding candidate — management responses

FR-EVA-007 / APL-639 records an accountable accept, partial-accept or reject response against an exact evaluation recommendation revision. Accepted scope creates an owned, dated action with required completion evidence; rejected recommendations remain visible with their reason.

Completing an action requires exact current Evidence revisions and keeps outcome improvement pending follow-up measurement. Overdue open actions escalate without closing automatically.

Migration `0112_management_response_kinds.sql` registers the three versioned record kinds and
denies the generic worker role access with restrictive row policies. Explicit access-policy
operations expose only recommendation creation/read, response, action read/history, completion,
and overdue escalation through existing evaluation capabilities. Recommendation creation pins a
current Evidence revision; completion also requires exact current Evidence revisions.

`qualification/test_management_responses_live.py` exercises the positive HTTP journey against a
disposable database: issue a recommendation from exact evidence, partially accept it, create an
owned and dated action, complete it using the same exact evidence, retry the operation exactly,
and read its two immutable revisions. Outcome improvement remains pending follow-up measurement.
