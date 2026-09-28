import json
import os
import time
from pathlib import Path
import httpx
import jwt
import pytest
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
# A fresh-assurance operation needs auth_time within 300 s. Tokens are minted per actor on demand
# and reused for at most this long, so no test depends on how long the suite has been running.
TOKEN_REUSE_SECONDS = 60


def signed(config, local, identity, **overrides):
    """One RS256 fixture token with the claims scripts/run.py mints; overrides replace claims."""
    claims = {
        "iss": config["issuer"],
        "sub": identity,
        "aud": config["audience"],
        "azp": config["client_id"],
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        # Sub-second precision: a token minted right after an authentication cutoff must sort
        # after it, exactly as the earlier per-test helper minted it.
        "auth_time": time.time(),
        **overrides,
    }
    return jwt.encode(claims, (local / "private.pem").read_bytes(), algorithm="RS256")


@pytest.fixture(scope="session")
def live():
    if not os.environ.get("IMPACT_TEST_LOCAL"):
        pytest.skip("Use scripts/run.py test for provisioned live tests")
    local = Path(os.environ["IMPACT_TEST_LOCAL"])
    fixture = json.loads((ROOT / "specification/fixtures/api-fixture.json").read_text())
    records = {r["key"]: r for r in json.loads((ROOT / "specification/fixtures/records.json").read_text())}
    config = json.loads((local / "config.json").read_text())

    class Client:
        def __init__(self):
            self.client = httpx.Client(base_url=os.environ["IMPACT_BASE_URL"], trust_env=False, timeout=20)
            self.tokens = {}

        def signed(self, identity, **overrides):
            return signed(config, local, identity, **overrides)

        def token(self, actor):
            minted, token = self.tokens.get(actor, (0, None))
            if time.time() - minted >= TOKEN_REUSE_SECONDS:
                minted, token = time.time(), self.signed(fixture["actors"][actor]["identity_id"])
                self.tokens[actor] = (minted, token)
            return token

        def request(self, path, actor="author", method="GET", body=None, **kwargs):
            headers = {"Authorization": "Bearer " + self.token(actor)} if actor else {}
            headers.update(kwargs.pop("headers", {}))
            return self.client.request(method, path, json=body, headers=headers, **kwargs)

        def path(self, route, obj=None, tenant=None):
            return "/v1/tenants/" + (tenant or fixture["tenant_a"]) + "/" + route + ("/" + obj if obj else "")

        def db(self):
            return psycopg.connect(
                os.environ.get("IMPACT_FIXTURE_DSN", config["app_dsn"]),
                row_factory=dict_row,
                prepare_threshold=None,
            )

    api = Client()
    api.fixture = fixture
    api.records = records
    api.config = config
    api.local = local
    yield api
    api.client.close()
