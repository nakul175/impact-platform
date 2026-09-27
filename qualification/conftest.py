import json
import os
from pathlib import Path
import httpx
import pytest
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]


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

        def request(self, path, actor="author", method="GET", body=None, **kwargs):
            headers = (
                {"Authorization": "Bearer " + os.environ[fixture["actors"][actor]["token_env"]]}
                if actor
                else {}
            )
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
