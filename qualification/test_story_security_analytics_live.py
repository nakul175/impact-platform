"""Cross-tenant security controls for the completed analytics/evaluation/finance slice.

These checks complement each story's positive journey, current-authority refusal
test and error/recovery test.  They exercise both request-boundary isolation and
forced row-level isolation using a real object owned by tenant A.
"""

from uuid import uuid4

import pytest

from test_story_error_recovery_analytics_live import COMMAND_CASES


OBJECT_ID = "10000000-0000-4000-8000-000000000001"


READ_CASES = [
    pytest.param("APL-610", f"dashboards/{OBJECT_ID}", id="APL-610-dashboard-authoring"),
    pytest.param(
        "APL-434",
        f"dashboards/{OBJECT_ID}/preview?viewport=TABLE&drill_level=PROGRAMME",
        id="APL-434-filtered-drilldown",
    ),
    pytest.param(
        "APL-616",
        f"dashboards/{OBJECT_ID}/geographic-preview?widget_id={OBJECT_ID}",
        id="APL-616-geographic-analysis",
    ),
    pytest.param(
        "APL-618",
        f"dashboard-alert-rules/{OBJECT_ID}/incidents",
        id="APL-618-dashboard-alerts",
    ),
    pytest.param(
        "APL-620",
        f"external-analytics-connections/{OBJECT_ID}/extracts",
        id="APL-620-external-analytics",
    ),
    pytest.param("APL-625", f"evaluations/{OBJECT_ID}", id="APL-625-evaluation-registry"),
    pytest.param(
        "APL-630",
        f"evaluation-methodologies/{OBJECT_ID}/history",
        id="APL-630-evaluation-methodology",
    ),
    pytest.param(
        "APL-632",
        f"analysis-packages/{OBJECT_ID}/export",
        id="APL-632-analysis-packages",
    ),
    pytest.param(
        "APL-634",
        f"learning-questions/{OBJECT_ID}/summary",
        id="APL-634-learning-agenda",
    ),
    pytest.param(
        "APL-639",
        f"management-actions/{OBJECT_ID}/history",
        id="APL-639-management-responses",
    ),
]


def _path(live, suffix, tenant):
    route, separator, remainder = suffix.partition("/")
    return live.path(route, tenant=tenant) + (separator + remainder if separator else "")


def _tenant_counts(live):
    with live.db() as connection:
        return {
            tenant: connection.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s", (tenant,)
            ).fetchone()["n"]
            for tenant in (live.fixture["tenant_a"], live.fixture["tenant_b"])
        }


@pytest.mark.parametrize(("story_id", "suffix"), READ_CASES)
def test_tenant_a_identity_cannot_read_story_route_in_tenant_b(live, story_id, suffix):
    """The requested tenant is current authority, not a client-controlled selector."""

    before = _tenant_counts(live)
    response = live.request(_path(live, suffix, live.fixture["tenant_b"]), actor="author")
    assert response.status_code in {401, 404}, (story_id, response.status_code, response.text)
    assert response.json()["code"] in {"AUTH_REQUIRED", "RESOURCE_UNAVAILABLE"}, story_id
    assert _tenant_counts(live) == before, story_id


@pytest.mark.parametrize(("story_id", "suffix", "data"), COMMAND_CASES)
def test_tenant_a_identity_cannot_execute_story_command_in_tenant_b(live, story_id, suffix, data):
    """Cross-tenant commands fail before a receipt, audit event or domain write."""

    operation_id = str(uuid4())
    before = _tenant_counts(live)
    response = live.request(
        _path(live, suffix, live.fixture["tenant_b"]),
        actor="author",
        method="POST",
        body={"operation_id": operation_id, "data": data},
    )
    assert response.status_code in {401, 404}, (story_id, response.status_code, response.text)
    assert response.json()["code"] in {"AUTH_REQUIRED", "RESOURCE_UNAVAILABLE"}, story_id
    assert _tenant_counts(live) == before, story_id
    with live.db() as connection:
        assert (
            connection.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE operation_id=%s",
                (operation_id,),
            ).fetchone()["n"]
            == 0
        ), story_id
