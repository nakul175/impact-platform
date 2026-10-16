"""A real loopback API with explicit local activation and real versioned tenant policy.

No policy/safety function is substituted. No provider key or live model is configured.
"""

from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from uuid import uuid4

import httpx

from impact_api.ai_runtime_activation import REVIEWABLE_USE_CASES
from test_live_application import expect

PURPOSES = dict(
    zip(
        REVIEWABLE_USE_CASES,
        (
            "INDICATOR_DESIGN_ASSISTANCE",
            "IMPORT_MAPPING_ASSISTANCE",
            "EVIDENCE_BASED_QUESTION",
            "GOVERNED_NUMERIC_ANALYSIS",
            "QUALITATIVE_SUGGESTION",
            "PROACTIVE_FINDING_SUGGESTION",
            "ACTION_PROPOSAL_GENERATION",
        ),
        strict=True,
    )
)


@contextmanager
def runtime(live, directory, cases=REVIEWABLE_USE_CASES):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    config = {
        **live.config,
        "environment": "test",
        "public_origin": f"http://127.0.0.1:{port}",
        "ai_reviewed_use_cases": ",".join(cases),
        "ai_enabled": False,
        "ai_api_key": "",
    }
    path = directory / "runtime.json"
    path.write_text(json.dumps(config))
    path.chmod(0o600)
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("IMPACT_", "PG")) and key != "OPENAI_API_KEY"
    }
    env.update(IMPACT_CONFIG_FILE=str(path), PYTHONPATH=str(Path(__file__).resolve().parents[1] / "apps/api"))
    with (directory / "api.log").open("w") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "impact_api.main:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--no-access-log",
            ],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        client = httpx.Client(base_url=config["public_origin"], trust_env=False, timeout=30)

        class Proxy:
            def __getattr__(self, key):
                return getattr(live, key)

            def request(self, route, actor="author", method="GET", body=None, **kwargs):
                headers = {"Authorization": "Bearer " + live.token(actor)} if actor else {}
                headers.update(kwargs.pop("headers", {}))
                response = client.request(method, route, json=body, headers=headers, **kwargs)
                self.requests.append((route, actor, method, deepcopy(body), response.status_code))
                return response

        proxy = Proxy()
        proxy.requests = []
        try:
            for _ in range(150):
                if process.poll() is not None:
                    raise AssertionError("Reviewed synthetic API exited; inspect its private api.log")
                try:
                    if client.get("/health/live").status_code in {200, 404}:
                        break
                except httpx.TransportError:
                    pass
                time.sleep(0.1)
            else:
                raise AssertionError("Reviewed synthetic API did not start")
            yield proxy
        finally:
            client.close()
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def save_policy(live, rules):
    path = live.path("ai-enablement/policy")
    current = expect(live.request(path, actor="admin"), 200)
    body = {
        "operation_id": str(uuid4()),
        "expected_version": current["policy_version"],
        "data": {"use_cases": rules},
    }
    result = expect(live.request(path, actor="admin", method="PUT", body=body), 200)
    return result["policy_version"]


def rules():
    return [
        {
            "use_case": case,
            "enabled": True,
            "data_classes": ["CONFIDENTIAL"],
            "destinations": ["openai-us"],
            "purposes": [PURPOSES[case]],
            "languages": ["en", "es"],
            "review_mode": "HUMAN_REVIEW",
            "budget_units": 100,
            "tools": ["governed.pool_ratio.v1"] if case == "NUMERIC_ANALYSIS" else [],
        }
        for case in REVIEWABLE_USE_CASES
    ]
