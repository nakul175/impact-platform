"""Synthetic diagnosis qualification through real local Keycloak sessions.

Uses the existing provider fixtures, never development-minted bearer tokens.
Source assertions do not constitute a run, human acceptance or deployed evidence.
"""

from copy import deepcopy

import httpx

from impact_api.contracts import validate
from test_ai_diagnosis_live import action_body, diagnosis
from test_live_application import cmd, expect
from test_live_idp import browser as browser
from test_live_idp import db
from test_live_idp import idp as idp
from test_live_idp import pytestmark as pytestmark
from test_live_idp import tenant_path


def test_diagnosis_provider_session_history_replay_and_logout(idp, browser):
    admin = browser()
    admin.sign_in("admin")
    route = tenant_path(idp, "ai-enablement/diagnoses")
    body = cmd(diagnosis())
    draft = expect(admin.post(route, body), 201)
    validate("AIDiagnosisReceipt", draft)
    path = route + "/" + draft["object_id"]
    original = expect(admin.get(path), 200)
    validate("AIDiagnosis", original)
    assert original["business_state"] == "Draft"
    assert original["data"]["priority_order"] == body["data"]["priority_order"]
    assert expect(admin.post(route, body), 201) == draft
    changed = deepcopy(body)
    changed["data"]["title"] = "Synthetic changed operation through live sign-in"
    assert expect(admin.post(route, changed), 409)["code"] == "CONFLICT_OPERATION"
    completed = expect(admin.post(path + "/actions/complete", action_body(draft)), 200)
    validate("AIDiagnosisReceipt", completed)
    current = expect(admin.get(path), 200)
    assert current["business_state"] == "Completed"
    assert current["data"]["completed_by"] == idp["fixture"]["actors"]["admin"]["principal_id"]
    assert expect(admin.get(path + "/revisions/" + draft["revision_id"]), 200) == original
    history = expect(admin.get(path + "/revisions"), 200)
    assert len(history["items"]) == 2 and history["next_cursor"] is None

    # Provider roles never replace the tenant's actual diagnosis capability.
    author = browser()
    # This fixture has provider role claims but no configured MFA credential.
    # Use the existing password-only flow; it still must not gain diagnosis access.
    author.sign_in("author", strip=("acr_values",))
    expect(author.get(path), 404)
    expect(author.post(route, cmd(diagnosis())), 404)
    foreign = path.replace(idp["fixture"]["tenant_a"], idp["fixture"]["tenant_b"])
    expect(admin.get(foreign), 404)

    cookie = admin.session
    expect(admin.post("/auth/logout"), 200)
    assert admin.session is None
    replay = httpx.post(
        idp["origin"] + route,
        json=body,
        cookies={idp["config"].get("cookie_name", "impact_dev_session"): cookie},
        headers={"Origin": idp["origin"], "X-CSRF-Token": admin.csrf},
        trust_env=False,
    )
    expect(replay, 401)
    with db() as connection:
        count = connection.execute(
            "SELECT count(*) AS n FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s",
            (idp["fixture"]["tenant_a"], draft["object_id"]),
        ).fetchone()["n"]
    assert count == 2
