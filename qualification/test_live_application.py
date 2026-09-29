import json
import uuid
import httpx
import jwt
import pytest
import psycopg


def cmd(data, revision=None, operation=None):
    return {
        "operation_id": operation or str(uuid.uuid4()),
        **({"expected_revision": revision} if revision else {}),
        "data": data,
    }


def draft(live, key=None, **override):
    indicator = expect(
        live.request(live.path("indicator-instances", live.records["indicator_a"]["object_id"])), 200
    )["object_id"]
    return {
        "source_namespace": "MANUAL",
        "source_key": key or str(uuid.uuid4()),
        "indicator_id": indicator,
        "event_at": "2026-08-15T12:00:00Z",
        "captured_at": "2026-09-25T10:00:00Z",
        "capture_zone": "UTC",
        "value_state": "PRESENT",
        "value": "80",
        "numerator": "8",
        "denominator": "10",
        "source_version": "1",
        "dimension_values": {},
        **override,
    }


def expect(response, status):
    assert response.status_code == status, response.text
    return response.json()


def test_observation_review_calculation_freshness(live):
    saved = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    submitted = expect(
        live.request(
            live.path("observations", saved["object_id"]) + "/actions/submit",
            method="POST",
            body=cmd(
                {"workflow_version": live.records["workflow_template"]["revision_id"]}, saved["revision_id"]
            ),
        ),
        200,
    )
    workflow = expect(live.request(live.path("workflows", submitted["object_id"])), 200)
    decision = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Checked evidence"},
        submitted["revision_id"],
    )
    denied = expect(
        live.request(
            live.path("workflows", submitted["object_id"]) + "/actions/approve", method="POST", body=decision
        ),
        403,
    )
    assert denied["reason_code"] == "INDEPENDENCE_REQUIRED"
    expect(
        live.request(
            live.path("workflows", submitted["object_id"]) + "/actions/approve",
            actor="reviewer",
            method="POST",
            body=cmd(decision["data"], submitted["revision_id"]),
        ),
        200,
    )
    indicator = expect(
        live.request(live.path("indicator-instances", live.records["indicator_a"]["object_id"])), 200
    )
    period = live.records["period"]
    result = expect(
        live.request(
            live.path("indicator-instances", indicator["object_id"]) + "/actions/calculate",
            method="POST",
            body=cmd({"period_id": period["object_id"]}, indicator["revision_id"]),
        ),
        200,
    )
    data = expect(live.request(live.path("calculated-results", result["object_id"])), 200)["data"]
    assert data["displayed_value"] == "49.17" and data["mode"] == "PROVISIONAL"
    assert data["coverage"]["complete"] is False
    lineage = expect(live.request(live.path("lineage-manifests", data["lineage_manifest_id"])), 200)
    assert lineage["data"]["source_revisions"]
    expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    assert (
        expect(live.request(live.path("calculated-results", result["object_id"])), 200)["data"]["freshness"][
            "stale"
        ]
        is True
    )


def test_cross_tenant_reference_is_atomic(live):
    body = cmd({"programme_id": live.fixture["programme_b"]})
    expect(live.request(live.path("indicator-instances"), method="POST", body=body), 404)
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.operation_receipt WHERE operation_id=%s", (body["operation_id"],)
        ).fetchone()


def test_retry_has_one_revision_audit_outbox_receipt(live):
    body = cmd({"title": "Atomic " + str(uuid.uuid4()), "code": "ATOMIC"})
    p = live.path("programmes")
    one = expect(live.request(p, method="POST", body=body), 201)
    two = expect(live.request(p, method="POST", body=body), 201)
    assert one == two
    with live.db() as c:
        for query, args in [
            ("SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s", (one["object_id"],)),
            (
                "SELECT count(*) AS n FROM impact.audit_event_current WHERE object_reference=%s",
                (one["object_id"],),
            ),
            (
                "SELECT count(*) AS n FROM impact.outbox_event WHERE payload->>'aggregate_id'=%s",
                (one["object_id"],),
            ),
            (
                "SELECT count(*) AS n FROM impact.operation_receipt WHERE operation_id=%s",
                (body["operation_id"],),
            ),
        ]:
            assert c.execute(query, args).fetchone()["n"] == 1


def test_duplicate_source_key(live):
    data = draft(live)
    expect(live.request(live.path("observations"), method="POST", body=cmd(data)), 201)
    expect(live.request(live.path("observations"), method="POST", body=cmd(data)), 409)


def test_database_tenant_fence_and_immutable_revisions(live):
    with live.db() as c:
        c.execute("SET LOCAL ROLE impact_app")
        assert c.execute("SELECT count(*) AS n FROM impact.object_registry").fetchone()["n"] == 0
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (live.fixture["tenant_a"],))
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_registry WHERE tenant_id=%s",
                (live.fixture["tenant_b"],),
            ).fetchone()["n"]
            == 0
        )
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            c.execute(
                "UPDATE impact.object_revision SET payload=payload WHERE tenant_id=%s",
                (live.fixture["tenant_a"],),
            )


def token(live, actor="author", **claims):
    return live.signed(live.fixture["actors"][actor]["identity_id"], **claims)


@pytest.mark.parametrize(
    "override",
    [
        {"aud": "other"},
        {"iss": "https://evil.test"},
        {"exp": 1},
        {"azp": "other"},
        {"auth_time": "yesterday"},
        {"auth_time": 999999999999},
    ],
)
def test_invalid_signed_tokens(live, override):
    expect(
        live.request(
            live.path("programmes"),
            actor=None,
            headers={"Authorization": "Bearer " + token(live, **override)},
        ),
        401,
    )


def test_claimed_roles_do_not_grant_access(live):
    expect(
        live.request(
            live.path("memberships"),
            actor=None,
            headers={"Authorization": "Bearer " + token(live, "partner", roles=["OWNER", "MEL_ADMIN"])},
        ),
        403,
    )


def test_unsigned_jwt(live):
    unsigned = jwt.encode({"sub": live.fixture["actors"]["author"]["identity_id"]}, "", algorithm="none")
    expect(
        live.request(live.path("programmes"), actor=None, headers={"Authorization": "Bearer " + unsigned}),
        401,
    )


def test_duplicate_json_and_body_limit(live):
    p = live.path("programmes")
    expect(
        live.request(
            p, method="POST", headers={"Content-Type": "application/json"}, content='{"data":{},"data":{}}'
        ),
        400,
    )
    expect(
        live.request(p, method="POST", headers={"Content-Type": "application/json"}, content="x" * 262145),
        413,
    )


def test_cursor_integrity(live):
    page = expect(live.request(live.path("programmes") + "?limit=1"), 200)
    cursor = page["next_cursor"]
    assert cursor
    expect(
        live.request(
            live.path("programmes") + "?cursor=" + cursor[:-1] + ("0" if cursor[-1] != "0" else "1")
        ),
        400,
    )


def test_browser_session_csrf_logout(live):
    with httpx.Client(base_url=live.config["public_origin"], trust_env=False) as browser:
        password = json.loads((live.local / "passwords.json").read_text())["author"]
        origin = {"Origin": live.config["public_origin"]}
        response = browser.post(
            "/auth/development-login", headers=origin, json={"username": "author", "password": password}
        )
        expect(response, 200)
        assert "HttpOnly" in response.headers["set-cookie"]
        me = expect(browser.get("/auth/me"), 200)
        expect(browser.post(live.path("programmes"), headers=origin, json=cmd({"title": "CSRF denied"})), 403)
        expect(browser.post("/auth/logout", headers={**origin, "X-CSRF-Token": me["csrf_token"]}), 200)
        expect(browser.get("/auth/me"), 401)


def test_disaggregation_is_explicitly_refused(live):
    expect(
        live.request(
            live.path("observations"),
            method="POST",
            body=cmd(draft(live, dimension_values={"sex": "female"})),
        ),
        422,
    )


def test_template_contract(live):
    from impact_api.contracts import validate

    validate("WorkflowTemplateList", expect(live.request(live.path("workflow-templates")), 200))


def test_revocation_prevents_receipt_replay(live):
    body = cmd({"title": "Revocable record"})
    path = live.path("programmes")
    receipt = expect(live.request(path, method="POST", body=body), 201)
    actor = live.fixture["actors"]["author"]
    try:
        with live.db() as c:
            c.execute(
                "UPDATE impact.tenant_principal SET active=false,subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (actor["tenant_id"], actor["principal_id"]),
            )
        expect(live.request(path, method="POST", body=body), 404)
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.tenant_principal SET active=true,subject_epoch=subject_epoch+1 WHERE tenant_id=%s AND principal_id=%s",
                (actor["tenant_id"], actor["principal_id"]),
            )
    assert expect(live.request(path, method="POST", body=body), 201) == receipt


def test_restricted_record_hidden_from_get_and_list(live):
    saved = expect(
        live.request(live.path("programmes"), method="POST", body=cmd({"title": "Restricted test"})), 201
    )
    with live.db() as c:
        c.execute(
            "UPDATE impact.object_registry SET classification='RESTRICTED' WHERE tenant_id=%s AND object_id=%s",
            (live.fixture["tenant_a"], saved["object_id"]),
        )
    expect(live.request(live.path("programmes", saved["object_id"])), 404)
    assert saved["object_id"] not in [
        r["object_id"] for r in expect(live.request(live.path("programmes") + "?limit=100"), 200)["items"]
    ]


def test_source_key_patch_conflict_rolls_back(live):
    first = expect(live.request(live.path("observations"), method="POST", body=cmd(draft(live))), 201)
    other_data = draft(live)
    expect(live.request(live.path("observations"), method="POST", body=cmd(other_data)), 201)
    expect(
        live.request(
            live.path("observations", first["object_id"]),
            method="PATCH",
            body=cmd({"source_key": other_data["source_key"]}, first["revision_id"]),
        ),
        409,
    )
    assert (
        expect(live.request(live.path("observations", first["object_id"])), 200)["revision_id"]
        == first["revision_id"]
    )


def test_explicit_object_scope_filters_read_and_list(live):
    tenant = live.fixture["tenant_a"]
    partner = live.fixture["actors"]["partner"]
    scope = str(uuid.uuid4())
    with live.db() as c:
        grant = c.execute(
            "SELECT g.* FROM impact.grant_current g WHERE tenant_id=%s AND subject_id=%s AND capability='programmes.read' AND purpose IS NULL LIMIT 1",
            (tenant, partner["principal_id"]),
        ).fetchone()
        template = c.execute(
            "SELECT * FROM impact.scope_definition WHERE tenant_id=%s AND scope_id=%s",
            (tenant, grant["scope_id"]),
        ).fetchone()
        c.execute(
            "INSERT INTO impact.scope_definition(tenant_id,scope_id,scope_type,predicate_version) VALUES(%s,%s,'OBJECT_SET',%s)",
            (tenant, scope, template["predicate_version"]),
        )
        c.execute(
            "INSERT INTO impact.scope_member VALUES(%s,%s,%s)", (tenant, scope, live.fixture["programme_a"])
        )
        c.execute(
            "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
            (scope, tenant, grant["object_id"]),
        )
    try:
        expect(live.request(live.path("programmes", live.fixture["programme_a"]), actor="partner"), 200)
        expect(live.request(live.path("programmes", live.fixture["mutable_programme"]), actor="partner"), 404)
        page = expect(live.request(live.path("programmes"), actor="partner"), 200)
        assert [r["object_id"] for r in page["items"]] == [live.fixture["programme_a"]]
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.grant_current SET scope_id=%s WHERE tenant_id=%s AND object_id=%s",
                (grant["scope_id"], tenant, grant["object_id"]),
            )


def test_purpose_restricted_grant_does_not_authorize_general_reads(live):
    actor = live.fixture["actors"]["partner"]
    tenant = actor["tenant_id"]
    with live.db() as c:
        grant = c.execute(
            "SELECT * FROM impact.grant_current WHERE tenant_id=%s AND subject_id=%s AND capability='programmes.read' LIMIT 1",
            (tenant, actor["principal_id"]),
        ).fetchone()
        c.execute(
            "UPDATE impact.grant_current SET purpose='QUALIFICATION' WHERE tenant_id=%s AND object_id=%s",
            (tenant, grant["object_id"]),
        )
    try:
        expect(live.request(live.path("programmes"), actor="partner"), 403)
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.grant_current SET purpose=%s WHERE tenant_id=%s AND object_id=%s",
                (grant["purpose"], tenant, grant["object_id"]),
            )


def test_backchannel_logout_absent_with_development_login(live):
    """Without a live provider the back-channel logout route does not exist and never reads a body."""
    response = live.request(
        "/auth/backchannel-logout",
        actor=None,
        method="POST",
        content=b"logout_token=x",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 404


def test_logout_without_a_live_session_clears_the_cookie(live):
    """L5 with the development login: a dead or unknown session cookie is deleted, no provider URL."""
    response = live.client.post(
        "/auth/logout",
        headers={"Origin": live.config["public_origin"]},
        cookies={"impact_dev_session": "gone"},
    )
    assert response.status_code == 200 and response.json() == {"authenticated": False, "logout_url": None}
    assert 'impact_dev_session=""' in response.headers["set-cookie"]
    assert live.client.post("/auth/logout", headers={"Authorization": "Bearer x"}).status_code == 401
