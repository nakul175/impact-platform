"""Actual saved0.33 HTTP tenant ->40 reviewed exporter ceiling upgrade.

This separately operated gate uses a git-archive0.33 API and its retained native
database. Ordinary fresh full suites skip it rather than invent old authority.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import pytest

from test_access_upgrade import action, preview, propose
from test_administration import command, expect, expiry
from test_ai_plan_exports_live import issue, request_body


@pytest.mark.skipif(
    not os.environ.get("IMPACT_EXPORT_HISTORICAL_UPGRADE"),
    reason="Separate actual historical HTTP/native database gate",
)
def test_actual_old_http_ceiling_requires_three_party_review_and_keeps_revocations(live):
    state = json.loads(Path(os.environ["IMPACT_EXPORT_UPGRADE_STATE"]).read_text())
    revoked = json.loads(Path(os.environ["IMPACT_EXPORT_PREUPGRADE_REVOCATION"]).read_text())
    tenant, row = state["tenant"], state["saved_plan"]
    tenant_id = tenant["tenant_id"]

    def path(route):
        return live.path(route, tenant=tenant_id)

    def access():
        return expect(live.request(path("me/access"), actor="reviewer"), 200)

    def private_state():
        with live.db() as c:
            authorities = c.execute(
                "SELECT authority_id,principal_id,capability,scope_id,expires_at FROM impact.grant_authority "
                "WHERE tenant_id=%s ORDER BY authority_id",
                (tenant_id,),
            ).fetchall()
            original_ids = [grant["object_id"] for grant in state["original_grants"]]
            grants = c.execute(
                "SELECT g.*,r.lifecycle_state FROM impact.grant_current g JOIN impact.object_registry r "
                "ON r.tenant_id=g.tenant_id AND r.object_id=g.object_id "
                "WHERE g.tenant_id=%s AND g.object_id=ANY(%s::uuid[]) ORDER BY g.object_id",
                (tenant_id, original_ids),
            ).fetchall()
            revoked_rows = c.execute(
                "SELECT r.object_id,r.head_revision,r.lifecycle_state,v.payload,v.payload_sha256 "
                "FROM impact.object_registry r JOIN impact.object_revision v "
                "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
                "WHERE r.tenant_id=%s AND r.object_id=ANY(%s::uuid[]) ORDER BY r.object_id",
                (tenant_id, [g["object_id"] for g in revoked["revoked_grants"]]),
            ).fetchall()
            ledger = c.execute(
                "SELECT version,sha256 FROM impact.schema_migration ORDER BY version"
            ).fetchall()
        return json.loads(
            json.dumps(
                dict(authorities=authorities, grants=grants, revoked=revoked_rows, ledger=ledger), default=str
            )
        )

    before = private_state()
    assert len(before["ledger"]) == 40
    assert before["authorities"] == state["original_authorities"]
    assert before["revoked"] == revoked["exact_revoked_current_rows"]
    assert "ai.enablement.read" in access()["capabilities"]
    assert "ai.enablement.manage" not in access()["capabilities"]
    assert "ai.enablement.export" not in access()["capabilities"]
    old_roles = expect(live.request(path("role-templates"), actor="reviewer"), 200)["items"]
    manager = next(r for r in old_roles if r["object_id"] == state["manager_role_id"])
    assert "ai.enablement.export" not in manager["capabilities"]
    issue(live, tenant, row, status=404)
    described = preview(live, tenant)
    assert described["new_capabilities"] == ["ai.enablement.export"]
    requested, _, request = propose(live, tenant)
    assert private_state() == before
    issue(live, tenant, row, status=404)
    action(live, requested, "approve", "admin", status=409)
    action(live, requested, "accept", "author", status=404)
    accepted = action(live, requested, "accept", "reviewer")
    assert private_state() == before
    issue(live, tenant, row, status=404)
    approved = action(live, accepted, "approve", "admin")
    assert approved["state"] == "Applied"
    after = private_state()
    assert after["grants"] == before["grants"]
    assert after["revoked"] == before["revoked"]
    original_authorities = {r["authority_id"]: r for r in before["authorities"]}
    final_authorities = {r["authority_id"]: r for r in after["authorities"]}
    assert all(final_authorities[key] == value for key, value in original_authorities.items())
    additions = [r for key, r in final_authorities.items() if key not in original_authorities]
    assert len(additions) == 2 and {r["capability"] for r in additions} == {"ai.enablement.export"}
    capabilities = access()["capabilities"]
    assert {"ai.enablement.read", "ai.enablement.export"} <= set(capabilities)
    assert "ai.enablement.manage" not in capabilities
    body = request_body()
    export = issue(live, tenant, row, body)
    document = json.loads(export["content"])
    assert document["plan"]["data"] == state["saved_plan_public_data"]
    assert document["guidance"] == state["saved_guidance"]
    assert issue(live, tenant, row, body) == export
    assert (
        expect(
            live.request(
                "/v1/platform/tenants/" + tenant_id + "/access-upgrade", method="POST", body=request
            ),
            200,
        )
        == requested
    )
    # A later deliberate ordinary role request is independently approved. Only
    # this explicit action may restore previously revoked manager capability.
    roles = expect(live.request(path("role-templates"), actor="reviewer"), 200)["items"]
    manager = next(r for r in roles if r["object_id"] == state["manager_role_id"])
    assert "ai.enablement.export" in manager["capabilities"]
    members = expect(live.request(path("membership-directory"), actor="reviewer"), 200)["items"]
    member = next(m for m in members if m["object_id"] == state["bootstrap"]["second_membership_id"])
    ordinary = expect(
        live.request(
            path("access-requests"),
            actor="reviewer",
            method="POST",
            body=command(
                {
                    "membership_id": member["object_id"],
                    "expected_membership_revision": member["revision_id"],
                    "role_template_id": manager["object_id"],
                    "scope_ids": [state["bootstrap"]["scope_id"]],
                    "expires_at": expiry(20),
                    "reason": "Explicit current-profile manager role review after export upgrade",
                }
            ),
        ),
        200,
    )
    decision = path("access-requests") + "/" + ordinary["object_id"] + "/actions/approve"
    expect(
        live.request(
            decision,
            actor="reviewer",
            method="POST",
            body=command({"reason": "Self approval still refused"}, ordinary["revision_id"]),
        ),
        403,
    )
    role_approval = expect(
        live.request(
            decision,
            actor="author",
            method="POST",
            body=command({"reason": "Independent deliberate role reissue"}, ordinary["revision_id"]),
        ),
        200,
    )
    assert {"ai.enablement.read", "ai.enablement.manage", "ai.enablement.export"} <= set(
        access()["capabilities"]
    )
    assert private_state()["revoked"] == before["revoked"]
    result = dict(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        scope="Actual saved0.33 HTTP/native39->40 migration and current three-party ceiling review; local only",
        original_snapshot_commit="861c2a807e774ec6bb53ef05c1ee25f853591085",
        before=before,
        after_review=after,
        reviewed_upgrade=approved,
        ordinary_role_request=ordinary,
        ordinary_role_approval=role_approval,
        export_manifest=export["manifest"],
        export_receipt=export["receipt"],
        export_utf8_sha256=hashlib.sha256(export["content"].encode()).hexdigest(),
        old_saved_plan_and_guidance_unchanged=True,
        revoked_heads_and_payloads_unchanged=True,
        implicit_old_grant_widening=False,
        profile_or_authority_row_rewrite=False,
        provider_calls="NOT_RUN",
    )
    Path(os.environ["IMPACT_EXPORT_HISTORICAL_RESULT"]).write_text(
        json.dumps(result, indent=2, default=str) + "\n"
    )
