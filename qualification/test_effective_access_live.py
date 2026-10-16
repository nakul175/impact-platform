"""Positive live journey for FR-ACC-003 / APL-350 effective-access explanations."""

from uuid import uuid4

from impact_api.contracts import validate
from test_live_application import expect


def test_current_grants_explain_permitted_and_sanitized_denied_access(live):
    programme_id = live.records["programme_a"]["object_id"]
    permitted = expect(
        live.request(
            live.path("access/effective/self"),
            method="POST",
            body={"operation_id": "get_programmes", "object_id": programme_id},
        ),
        200,
    )
    validate("OwnEffectiveAccess", permitted)
    assert permitted["decision"] == "PERMITTED"
    assert permitted["capability"] == "programmes.read"
    assert permitted["grant_paths"]
    assert all("scope_id" not in path for path in permitted["grant_paths"])

    unavailable_id = str(uuid4())
    denied = expect(
        live.request(
            live.path("access/effective/self"),
            method="POST",
            body={"operation_id": "get_programmes", "object_id": unavailable_id},
        ),
        200,
    )
    validate("OwnEffectiveAccess", denied)
    assert denied["decision"] == "DENIED"
    assert denied["restrictions"] == ["RESOURCE_UNAVAILABLE"]
    assert unavailable_id not in str(denied)

    simulated = expect(
        live.request(
            live.path("access/effective/simulations"),
            actor="admin",
            method="POST",
            body={
                "operation_id": "get_programmes",
                "object_id": programme_id,
                "subject_principal_id": live.fixture["actors"]["author"]["principal_id"],
            },
        ),
        200,
    )
    validate("SimulatedEffectiveAccess", simulated)
    assert simulated["decision"] == "PERMITTED"
    assert live.fixture["actors"]["author"]["principal_id"] not in str(simulated)


def test_simulation_refuses_non_administrator_and_cross_tenant_subject(live):
    body = {
        "operation_id": "get_programmes",
        "object_id": live.records["programme_a"]["object_id"],
        "subject_principal_id": live.fixture["actors"]["author"]["principal_id"],
    }
    refused = expect(
        live.request(
            live.path("access/effective/simulations"),
            actor="author",
            method="POST",
            body=body,
        ),
        403,
    )
    assert refused["code"] == "POLICY_DENIED"

    body["subject_principal_id"] = live.fixture["actors"]["other_tenant"]["principal_id"]
    hidden = expect(
        live.request(
            live.path("access/effective/simulations"),
            actor="admin",
            method="POST",
            body=body,
        ),
        404,
    )
    assert hidden["code"] == "RESOURCE_UNAVAILABLE"
