"""Read failures leave the durable store untouched and a permitted retry usable."""

from test_live_application import expect
from test_story_error_recovery_analytics_live import _durable_counts


def assert_read_recovery(live, route, object_id, suffix="", expected=None):
    path = live.path(route, object_id) + suffix
    original = expect(live.request(path), 200)
    if expected is not None:
        assert original == expected
    before = _durable_counts(live)
    malformed = live.path(route, "malformed-selector") + suffix
    refused = expect(live.request(malformed), 404)
    assert refused["code"] == "RESOURCE_UNAVAILABLE"
    assert _durable_counts(live) == before
    assert expect(live.request(path), 200) == original
    # Successful reproduction/explanation reads legitimately append audit events.
    # Their returned exact revision and arithmetic must remain unchanged.
