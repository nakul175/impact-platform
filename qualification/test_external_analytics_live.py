"""Positive user journey for FR-ANA-010 / APL-620 governed analytics extracts."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from impact_api.contracts import validate
from test_dashboards import calculate, measure, ratio_source
from test_forms import temporary_grants
from test_live_application import expect


def test_author_exports_an_exact_result_then_revokes_the_connection(live):
    _, indicator, period, keys = measure(live, keys=1)
    ratio_source(live, indicator, keys[0], "3", "4")
    result = calculate(live, indicator, period)
    revoke_grants = temporary_grants(
        live, "author", ["dashboards.draft.create", "dashboards.draft.edit", "dashboards.read"]
    )
    path = live.path("external-analytics-connections")
    body = {
        "operation_id": str(uuid4()),
        "data": {
            "datasets": [
                {
                    "kind": "CalculatedResult",
                    "object_id": result["object_id"],
                    "revision_id": result["revision_id"],
                    "fields": ["value_state", "value", "displayed_value", "numerator", "denominator"],
                }
            ],
            "destination": "Synthetic board workbook",
            "reuse_terms": "Internal synthetic evaluation only",
            "backup_owner_id": live.fixture["actors"]["reviewer"]["principal_id"],
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        },
    }

    created = expect(live.request(path, actor="author", method="POST", body=body), 201)
    validate("ExternalAnalyticsConnectionReceipt", created)
    credential = created["credential"]
    connection_path = path + "/" + created["object_id"]

    current = expect(live.request(connection_path, actor="author"), 200)
    validate("ExternalAnalyticsConnection", current)
    assert current["data"]["status"] == "ACTIVE"
    assert "credential" not in current["data"] and "credential_sha256" not in current["data"]

    extracted = expect(
        live.request(
            connection_path + "/actions/refresh",
            actor="author",
            method="POST",
            body={"operation_id": str(uuid4()), "credential": credential},
        ),
        200,
    )
    validate("ExternalAnalyticsExtract", extracted)
    assert len(extracted["package"]) == 1
    item = extracted["package"][0]
    assert item["object_id"] == result["object_id"]
    assert item["revision_id"] == result["revision_id"]
    assert item["fields"]["value_state"] == "PRESENT"
    assert item["fields"]["numerator"] == "3"
    assert item["fields"]["denominator"] == "4"

    history = expect(live.request(connection_path + "/extracts", actor="author"), 200)
    validate("ExternalAnalyticsExtractList", history)
    assert len(history["items"]) == 1
    assert history["items"][0]["object_id"] == extracted["extract_id"]
    assert history["items"][0]["data"]["dataset_revisions"] == [result["revision_id"]]

    revoked = expect(
        live.request(
            connection_path + "/actions/revoke",
            actor="author",
            method="POST",
            body={"operation_id": str(uuid4())},
        ),
        200,
    )
    validate("ExternalAnalyticsRevocation", revoked)
    assert revoked["remote_copy_status"] == "TRACKED_NOT_REMOTELY_ERASED"
    assert revoked["last_successful_extract"]["dataset_revisions"] == [result["revision_id"]]

    refused = live.request(
        connection_path + "/actions/refresh",
        actor="author",
        method="POST",
        body={"operation_id": str(uuid4()), "credential": credential},
    )
    assert expect(refused, 403)["code"] == "POLICY_DENIED"
    revoke_grants()
