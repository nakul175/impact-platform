"""Actual HTTP diagnosis receipts after independently executed privacy erasure.

Only the NEW diagnosis receives explicit synthetic fixture ownership attribution
to the subject. This is not a governed transfer or acceptance claim. The active
admin remains its original HTTP author, so denial exercises removed-content guards
rather than a revoked identity. No grants, approvals, receipts or ledger rows are
fabricated. This test does not claim backup/restored API or TH27 qualification.
"""

from copy import deepcopy
import json
import os

import pytest
import test_privacy_requests as privacy

from test_ai_diagnosis_linkage_candidate_native import linkage  # noqa: F401
from test_ai_diagnosis_privacy_candidate_native import diagnosis_privacy_scope, stored  # noqa: F401
from test_ai_diagnosis_recovery import capture_diagnosis, owned_counts, verify_diagnosis
from test_live_application import expect

pytestmark = pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="Actual registered native storage and independent erasure required",
)


def original_receipts(live, checkpoint):
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        return c.execute(
            "SELECT to_jsonb(r) AS row FROM impact.operation_receipt r WHERE tenant_id=%s "
            "AND actor_id=%s AND operation_id=ANY(%s::uuid[]) ORDER BY command_type,operation_id",
            (
                live.fixture["tenant_a"],
                live.fixture["actors"]["admin"]["principal_id"],
                [command["body"]["operation_id"] for command in checkpoint["commands"]],
            ),
        ).fetchall()


@pytest.mark.usefixtures("diagnosis_privacy_scope")
def test_active_original_author_exact_receipts_and_lists_refuse_after_independent_erasure(live):
    checkpoint = capture_diagnosis(live)
    verify_diagnosis(live, checkpoint)
    subject = privacy.member(live)
    obj = checkpoint["object_id"]
    tenant = live.fixture["tenant_a"]
    before = stored(live, obj)
    private_receipts = original_receipts(live, checkpoint)
    assert len(private_receipts) == 3
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
        registry = c.execute(
            "SELECT to_jsonb(r) AS row FROM impact.object_registry r WHERE tenant_id=%s AND object_id=%s",
            (tenant, obj),
        ).fetchone()["row"]
        assert registry["created_by"] == live.fixture["actors"]["admin"]["principal_id"]
        changed = c.execute(
            "UPDATE impact.object_registry SET owner_id=%s WHERE tenant_id=%s AND object_id=%s AND owner_id=%s AND created_by=%s",
            (subject.principal, tenant, obj, registry["owner_id"], registry["created_by"]),
        ).rowcount
        assert changed == 1
        attributed = c.execute(
            "SELECT to_jsonb(r) AS row FROM impact.object_registry r WHERE tenant_id=%s AND object_id=%s",
            (tenant, obj),
        ).fetchone()["row"]
        assert {k: v for k, v in attributed.items() if k != "owner_id"} == {
            k: v for k, v in registry.items() if k != "owner_id"
        }
    assert stored(live, obj) == before
    verify_diagnosis(live, checkpoint)
    privacy.revoke(live, subject)
    created = privacy.create_case(live, subject, "ERASURE", diagnosis_ids=[obj])
    privacy.approve(live, created["object_id"])
    privacy.execute(live, created["object_id"])
    after = stored(live, obj)
    assert len(after) == len(before) == 3
    for old, removed in zip(before, after, strict=True):
        assert removed["row"]["payload"] is None and removed["row"]["restriction_state"] == "REMOVED"
        assert {k: v for k, v in old["row"].items() if k not in {"payload", "restriction_state"}} == {
            k: v for k, v in removed["row"].items() if k not in {"payload", "restriction_state"}
        }
    counts = owned_counts(live, checkpoint)
    assert counts == checkpoint["counts"]
    for command, kind in zip(
        checkpoint["commands"],
        ["create_ai_diagnosis", "complete_ai_diagnosis", "revise_ai_diagnosis"],
        strict=True,
    ):
        refused = expect(
            live.request(command["path"], actor="admin", method="POST", body=command["body"]), 404
        )
        assert refused["code"] == "RESOURCE_UNAVAILABLE"
        expect(
            live.request(
                live.path("operations", command["body"]["operation_id"]),
                actor="admin",
                params={"command_type": kind},
            ),
            404,
        )
    changed = deepcopy(checkpoint["commands"][0]["body"])
    changed["data"]["title"] = "Changed operation bytes stay a conflict after erasure"
    assert (
        expect(
            live.request(checkpoint["commands"][0]["path"], actor="admin", method="POST", body=changed), 409
        )["code"]
        == "CONFLICT_OPERATION"
    )
    path = live.path("ai-enablement/diagnoses", obj)
    for suffix in ["", "/revisions", *["/revisions/" + row["revision_id"] for row in checkpoint["versions"]]]:
        assert expect(live.request(path + suffix, actor="admin"), 404)["code"] == "RESOURCE_UNAVAILABLE"
    cursor = None
    seen = set()
    while True:
        page = expect(
            live.request(
                live.path("ai-enablement/diagnoses"),
                actor="admin",
                params={"limit": 2, **({"cursor": cursor} if cursor else {})},
            ),
            200,
        )
        assert "total_rows" not in page
        ids = {item["object_id"] for item in page["items"]}
        assert obj not in ids and not ids.intersection(seen)
        seen.update(ids)
        cursor = page["next_cursor"]
        if cursor is None:
            break
    assert owned_counts(live, checkpoint) == counts
    assert original_receipts(live, checkpoint) == private_receipts
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.diagnosis_evidence_binding WHERE tenant_id=%s AND object_id=%s",
                (tenant, obj),
            ).fetchone()["n"]
            == 0
        )
    (live.local / "diagnosis-erasure-receipts.json").write_text(
        json.dumps(
            {
                "fixture_attribution": "NEW diagnosis owner_id only; not governed ownership transfer",
                "actual_independent_erasure": True,
                "original_author_active": True,
                "exact_receipt_retries": "three404",
                "generic_lookups": "three404",
                "changed_body": "409CONFLICT_OPERATION",
                "list_filtered": True,
                "private_receipts_unchanged": True,
                "diagnosis_counts": counts,
                "backup_recovery_claim": False,
            },
            indent=2,
        )
        + "\n"
    )
