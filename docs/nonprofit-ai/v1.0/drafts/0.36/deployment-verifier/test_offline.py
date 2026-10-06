"""Offline sanity checks only: no sockets, HTTP server, browser or hosting calls."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import httpx

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("verifier", ROOT / "verify_deployment.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
REPO = Path(
    "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform"
)
smoke = v.load_smoke(REPO)
COMMIT = "a" * 40


def gate():
    return {
        "financial_approval": True,
        "financial_approval_reference": "Synthetic offline approval record",
        "merge_authorized": True,
        "main_merge_commit": COMMIT,
        "ci": {
            "head_sha": COMMIT,
            "run_url": "https://example.test/ci/1",
            "jobs": dict.fromkeys(v.JOBS, "success"),
        },
    }


def status():
    return {
        "commit": COMMIT,
        "schema_version": "40",
        "result": "ok",
        "tls": "acme",
        "alerts": [],
        "urls": {"application": "https://example.test/"},
        "services": {name: {"state": "running", "health": "healthy"} for name in v.SERVICES},
        "log_tail": ["ready", "password=[redacted]"],
        "operations": None,
    }


class Offline(unittest.TestCase):
    def test_final_status_cookie_refused_before_decoding(self):
        response = httpx.Response(
            200,
            headers={"content-type": "application/json", "set-cookie": "fictional=1"},
            content=b"not even JSON",
        )
        with httpx.Client(transport=httpx.MockTransport(lambda request: response)) as client:
            with self.assertRaisesRegex(ValueError, "sets cookie"):
                v.bounded_json_get(client, "https://example.test/deploy-status.json", 128 * 1024)

    def test_final_status_oversize_refused_before_decoding(self):
        response = httpx.Response(
            200, headers={"content-type": "application/json"}, content=b" " * (128 * 1024 + 1)
        )
        with httpx.Client(transport=httpx.MockTransport(lambda request: response)) as client:
            with self.assertRaisesRegex(ValueError, "byte limit"):
                v.bounded_json_get(client, "https://example.test/deploy-status.json", 128 * 1024)

    def test_health_oversize_refused_before_decoding(self):
        response = httpx.Response(200, headers={"content-type": "application/json"}, content=b" " * 4097)
        with httpx.Client(transport=httpx.MockTransport(lambda request: response)) as client:
            with self.assertRaisesRegex(ValueError, "byte limit"):
                v.bounded_json_get(client, "https://example.test/health/ready", 4096)

    def test_default_command_reports_not_run_with_no_network_or_subprocess(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as folder:
            out = Path(folder) / "not-run"
            argv = [
                "verify_deployment.py",
                "--repo",
                str(REPO),
                "--origin",
                "https://example.test",
                "--expected-commit",
                COMMIT,
                "--build-proof",
                "does-not-exist",
                "--gate",
                "does-not-exist",
                "--output",
                str(out),
                "--node",
                "does-not-exist",
                "--browser-executable",
                "does-not-exist",
            ]
            with (
                patch("sys.argv", argv),
                patch.object(httpx, "Client", side_effect=AssertionError("Network forbidden")),
                patch.object(subprocess, "run", side_effect=AssertionError("No subprocess allowed")),
            ):
                self.assertEqual(v.main(), 2)
            self.assertEqual(
                json.loads((out / "deployment-verification.json").read_text())["status"], "NOT_RUN"
            )

    def test_missing_financial_approval_refuses_before_any_git_or_network(self):
        r = gate()
        r["financial_approval"] = False
        with patch.object(httpx, "Client", side_effect=AssertionError("Network forbidden")):
            with self.assertRaises(v.NotRun):
                v.gate_record(r, COMMIT, lambda _: self.fail("git should not run"))

    def test_missing_approval_reference_refuses(self):
        r = gate()
        r.pop("financial_approval_reference")
        with self.assertRaises(v.NotRun):
            v.gate_record(r, COMMIT, None)

    def test_missing_merge_refuses(self):
        r = gate()
        r["main_merge_commit"] = "b" * 40
        with self.assertRaises(v.NotRun):
            v.gate_record(r, COMMIT, None)

    def test_incomplete_or_non_success_ci_refuses(self):
        for change in [
            lambda r: r["ci"]["jobs"].pop("container-stack"),
            lambda r: r["ci"]["jobs"].update({"container-stack": "skipped"}),
        ]:
            r = gate()
            change(r)
            with self.assertRaises(v.NotRun):
                v.gate_record(r, COMMIT, None)

    def test_branch_ci_head_requires_ancestry_and_identical_merged_tree(self):
        r = gate()
        r["ci"]["head_sha"] = "b" * 40

        def changed(command, **kwargs):
            return subprocess.CompletedProcess(
                command, 0, stdout="old" if command[-1].startswith("b") else "new"
            )

        with self.assertRaises(v.NotRun):
            v.gate_record(r, COMMIT, changed)

        def same(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, stdout="same")

        self.assertEqual(v.gate_record(r, COMMIT, same)["main_merge_commit"], COMMIT)

        def no_ancestor(command, **kwargs):
            return subprocess.CompletedProcess(command, 1, stdout="same")

        with self.assertRaises(v.NotRun):
            v.gate_record(r, COMMIT, no_ancestor)

    def test_exact_success_gate_is_evidence_record_not_ci_fetch(self):
        with patch.object(httpx, "Client", side_effect=AssertionError("Network forbidden")):
            self.assertEqual(v.gate_record(gate(), COMMIT, None)["jobs"], dict.fromkeys(v.JOBS, "success"))

    def test_origin_forbids_non_tls_auth_query_fragment_and_nondefault_port(self):
        for origin in [
            "http://example.test",
            "https://user:pass@example.test",
            "https://example.test/v1",
            "https://example.test/?x=y",
            "https://example.test/#a",
            "https://example.test:8443",
        ]:
            with self.assertRaises(ValueError):
                v.clean_origin(origin)
        self.assertEqual(v.clean_origin("https://example.test/"), "https://example.test")

    def test_old_deployment_is_not_run_never_success(self):
        for field, value in [("commit", "b" * 40), ("schema_version", "33")]:
            r = status()
            r[field] = value
            with self.assertRaises(v.NotRun):
                v.validate_status(r, COMMIT, "https://example.test", smoke.secret_looking)

    def test_health_and_service_problems_fail(self):
        for mutate in [
            lambda r: r.update(result="failed"),
            lambda r: r.update(alerts=[{"code": "DOWN"}]),
            lambda r: r["services"]["api"].update(health="unhealthy"),
            lambda r: r["services"].pop("worker"),
            lambda r: r.update(tls="internal"),
        ]:
            r = status()
            mutate(r)
            with self.assertRaises(ValueError):
                v.validate_status(r, COMMIT, "https://example.test", smoke.secret_looking)

    def test_status_secret_keys_and_recognized_values_fail(self):
        for field, value in [
            ("db_password", "synthetic"),
            ("note", "Bearer synthetic-value"),
            ("note", "postgresql://fixture:invented@example.test/db"),
        ]:
            r = status()
            r[field] = value
            with self.assertRaises(ValueError):
                v.validate_status(r, COMMIT, "https://example.test", smoke.secret_looking)

    def test_status_projection_omits_log_tail_and_config(self):
        r = status()
        r["log_tail"] = ["purely synthetic harmless line"]
        result = v.validate_status(r, COMMIT, "https://example.test", smoke.secret_looking)
        self.assertNotIn("log_tail", result)
        self.assertNotIn("urls", result)
        self.assertEqual(result["schema_version"], "40")

    def test_root_graph_rejects_dev_external_traversal_and_query(self):
        for source in ["/src/main.tsx", "https://other.test/x.js", "/assets/../x.js", "/assets/x.js?x=1"]:
            with self.assertRaises(ValueError):
                v.RootDocument().feed(f'<div id="root"></div><script type="module" src="{source}"></script>')

    def test_actual_local_entry_graph_exact_union_matches_eight_file_proof(self):
        proof = json.loads((REPO / "docs/evidence/sprint-0.35-web-build-source-proof.json").read_text())
        root, tour = v.RootDocument(), smoke.WalkthroughDocument()
        root.feed((REPO / "apps/web/dist/index.html").read_text())
        tour.feed((REPO / "apps/web/dist/ai-walkthrough.html").read_text())
        self.assertEqual(
            set(root.assets) | set(tour.assets),
            {"/" + p for p in proof["built_assets_sha256"] if p.startswith("assets/")},
        )
        self.assertEqual(len(tour.assets), 4)

    def test_remote_hash_mismatch_is_retained_before_refusal(self):
        observations = []
        with httpx.Client(
            transport=httpx.MockTransport(lambda r: httpx.Response(200, content=b"older asset"))
        ) as client:
            with self.assertRaises(ValueError):
                v.observe_asset(
                    client, "https://example.test", "/assets/x.js", v.digest(b"newer asset"), observations
                )
        self.assertEqual(len(observations), 1)
        self.assertFalse(observations[0]["matches"])
        self.assertEqual(observations[0]["sha256"], v.digest(b"older asset"))

    def test_static_cookie_redirect_and_oversize_fail_without_following(self):
        for response in [
            httpx.Response(302, headers={"location": "https://other.test/"}),
            httpx.Response(200, headers={"set-cookie": "synthetic=1"}, content=b"x"),
            httpx.Response(200, content=b"longer"),
        ]:
            observations, calls = [], []

            def handle(request):
                calls.append(request.url)
                return response

            with httpx.Client(transport=httpx.MockTransport(handle)) as client:
                with self.assertRaises(ValueError):
                    v.observe_asset(
                        client, "https://example.test", "/assets/x.js", v.digest(b"x"), observations, limit=2
                    )
            self.assertEqual(len(calls), 1)

    def test_build_source_changed_or_wrong_compiled_bytes_fail(self):
        proof = json.loads((REPO / "docs/evidence/sprint-0.35-web-build-source-proof.json").read_text())

        def git_read(command, **kwargs):
            name = command[-1].split(":", 1)[1]
            return subprocess.CompletedProcess(command, 0, stdout=(REPO / name).read_bytes())

        self.assertEqual(len(v.validate_build(REPO, proof, COMMIT, git_read)["assets"]), 8)
        wrong = copy.deepcopy(proof)
        wrong["built_assets_sha256"]["index.html"] = "0" * 64
        with self.assertRaises(ValueError):
            v.validate_build(REPO, wrong, COMMIT, git_read)
        wrong = copy.deepcopy(proof)
        wrong["source_sha256_end"]["VERSION.json"] = "0" * 64
        with self.assertRaises(ValueError):
            v.validate_build(REPO, wrong, COMMIT, git_read)

    def test_wrong_merged_source_fails_even_local_build_matches(self):
        proof = json.loads((REPO / "docs/evidence/sprint-0.35-web-build-source-proof.json").read_text())
        with self.assertRaises(ValueError):
            v.validate_build(
                REPO,
                proof,
                COMMIT,
                lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=b"older merged source"),
            )

    def test_private_output_is_insert_once_and_0600(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as folder:
            p = Path(folder) / "report.json"
            v.private_json(p, {"status": "NOT_RUN"})
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                v.private_json(p, {})

    def test_browser_is_static_only_and_retains_incompletes(self):
        js = (ROOT / "verify_walkthrough.mjs").read_text()
        self.assertIn("ignoreHTTPSErrors: false", js)
        self.assertIn('serviceWorkers: "block"', js)
        self.assertIn("incomplete: a.incomplete.map", js)
        self.assertIn("has_authorization", js)
        self.assertNotIn("IMPACT_LOGIN_DSN", js)
        self.assertNotIn("applicationSnapshot", js)
        self.assertIn('"localStorage", "sessionStorage", "indexedDB"', js)
        self.assertIn("served_asset_mismatches", js)
        self.assertIn('new Set(["/ai-walkthrough.html", ...m.tour_asset_paths])', js)


if __name__ == "__main__":
    unittest.main(verbosity=2)
