"""Supplemental native restart/restored-API diagnosis checks; actual outcomes are separate.

Synthetic fixture only. Existing two-phase restart or explicit disposable restored
API mode is required; PGlite skips are not recovery evidence. The private state
contains an existing synthetic session and must never be committed.
"""

from copy import deepcopy
import json
import os

import pytest

from test_ai_diagnosis_live import action, action_body, diagnosis, get, save
from test_live_application import cmd, expect


def owned_counts(live, checkpoint):
    tenant, object_id = live.fixture["tenant_a"], checkpoint["object_id"]
    with live.db() as c:
        return {
            "revisions": c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
                (tenant, object_id),
            ).fetchone()["n"],
            "receipts": c.execute(
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE tenant_id=%s "
                "AND operation_id=ANY(%s::uuid[])",
                (tenant, [item["body"]["operation_id"] for item in checkpoint["commands"]]),
            ).fetchone()["n"],
            "audit": c.execute(
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE tenant_id=%s AND object_reference=%s",
                (tenant, object_id),
            ).fetchone()["n"],
        }


def capture_diagnosis(live):
    creation = cmd(diagnosis())
    draft = save(live, body=creation)
    path = live.path("ai-enablement/diagnoses", draft["object_id"])
    completion = action_body(draft)
    completed = action(live, draft, "complete", completion)
    correction = action_body(completed, reason="Synthetic correction must survive recovery")
    corrected = action(live, completed, "revise", correction)
    checkpoint = {
        "object_id": draft["object_id"],
        "commands": [
            {"path": live.path("ai-enablement/diagnoses"), "body": creation, "receipt": draft, "status": 201},
            {"path": path + "/actions/complete", "body": completion, "receipt": completed, "status": 200},
            {"path": path + "/actions/revise", "body": correction, "receipt": corrected, "status": 200},
        ],
        "current": get(live, corrected),
        "history": expect(live.request(path + "/revisions", actor="admin"), 200),
        "versions": [
            expect(live.request(path + "/revisions/" + row["revision_id"], actor="admin"), 200)
            for row in (draft, completed, corrected)
        ],
    }
    assert checkpoint["current"]["business_state"] == "Draft"
    assert [row["business_state"] for row in checkpoint["versions"]] == ["Draft", "Completed", "Draft"]
    assert len(checkpoint["history"]["items"]) == 3 and checkpoint["history"]["next_cursor"] is None
    checkpoint["counts"] = owned_counts(live, checkpoint)
    assert checkpoint["counts"] == {"revisions": 3, "receipts": 3, "audit": 3}
    return checkpoint


def verify_diagnosis(live, checkpoint):
    path = live.path("ai-enablement/diagnoses", checkpoint["object_id"])
    assert expect(live.request(path, actor="admin"), 200) == checkpoint["current"]
    assert expect(live.request(path + "/revisions", actor="admin"), 200) == checkpoint["history"]
    for version in checkpoint["versions"]:
        assert (
            expect(live.request(path + "/revisions/" + version["revision_id"], actor="admin"), 200) == version
        )
    assert owned_counts(live, checkpoint) == checkpoint["counts"]
    for item in checkpoint["commands"]:
        assert (
            expect(
                live.request(item["path"], actor="admin", method="POST", body=item["body"]), item["status"]
            )
            == item["receipt"]
        )
    changed = deepcopy(checkpoint["commands"][0]["body"])
    changed["data"]["title"] = "Synthetic changed replay remains refused after recovery"
    refused = expect(
        live.request(live.path("ai-enablement/diagnoses"), actor="admin", method="POST", body=changed), 409
    )
    assert refused["code"] == "CONFLICT_OPERATION"
    assert owned_counts(live, checkpoint) == checkpoint["counts"]
    assert expect(live.request(path, actor="admin"), 200) == checkpoint["current"]


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1" or os.environ.get("IMPACT_DIAGNOSIS_RESTORED_CHECK") != "1",
    reason="Requires an actual private native pg_dump/pg_restore copy and replacement unprivileged API",
)
def test_exact_diagnosis_history_and_receipts_on_restored_api(live):
    state = json.loads((live.local / "restart-state.json").read_text())
    verify_diagnosis(live, state["diagnosis"])
