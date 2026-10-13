"""Actual diagnosis HTTP confidentiality headers across success and refusals.

Synthetic loopback authentication only. This does not prove browser cache eviction,
TLS/HSTS, actual provider login, human acceptance or deployed headers.
"""

from copy import deepcopy
from uuid import UUID, uuid4

from test_ai_diagnosis_live import ROUTE, diagnosis, domain_counts, narrowed
from test_live_application import cmd, expect


def private_headers(response, correlation=None):
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
    observed = response.headers["x-correlation-id"]
    assert str(UUID(observed)) == observed
    if correlation is not None:
        assert observed == correlation
    policy = response.headers["content-security-policy"]
    for directive in ("default-src 'self'", "object-src 'none'", "frame-ancestors 'none'"):
        assert directive in policy.split("; ")
    assert "unsafe-inline" not in policy


def test_diagnosis_private_headers_cover_saved_data_and_current_authority_refusals(live):
    body = cmd(diagnosis())
    correlation = str(uuid4())
    create = live.request(
        live.path(ROUTE),
        actor="admin",
        method="POST",
        body=body,
        headers={"X-Correlation-ID": correlation},
    )
    row = expect(create, 201)
    private_headers(create, correlation)
    current = live.path(ROUTE, row["object_id"])
    paths = (
        current,
        live.path(ROUTE),
        current + "/revisions",
        current + "/revisions/" + row["revision_id"],
    )
    before = domain_counts(live)
    for path in paths:
        response = live.request(path, actor="admin", headers={"X-Correlation-ID": "invalid"})
        expect(response, 200)
        private_headers(response)
    replay = live.request(live.path(ROUTE), actor="admin", method="POST", body=body)
    assert expect(replay, 201) == row
    private_headers(replay)

    changed = deepcopy(body)
    changed["data"]["title"] = "Different synthetic title under the same operation"
    conflict = live.request(live.path(ROUTE), actor="admin", method="POST", body=changed)
    assert expect(conflict, 409)["code"] == "CONFLICT_OPERATION"
    private_headers(conflict)

    with narrowed(live, "ai.diagnosis.read"):
        responses = [live.request(path, actor="admin") for path in paths]
        responses.append(live.request(live.path(ROUTE), actor="admin", method="POST", body=body))
        for response in responses:
            assert expect(response, 404)["code"] == "RESOURCE_UNAVAILABLE"
            private_headers(response)
            assert body["data"]["title"] not in response.text
            assert body["data"]["problems"][0]["supporting_evidence"] not in response.text

    unauthenticated = live.request(current, actor=None)
    assert expect(unauthenticated, 401)["code"] == "AUTH_REQUIRED"
    private_headers(unauthenticated)
    hidden = live.request(live.path(ROUTE, str(uuid4())), actor="admin")
    assert expect(hidden, 404)["code"] == "RESOURCE_UNAVAILABLE"
    private_headers(hidden)
    assert domain_counts(live) == before
