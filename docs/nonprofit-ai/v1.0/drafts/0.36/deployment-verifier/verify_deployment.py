"""Root-gated, read-only public deployment verification. Default: no network."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit

import httpx

JOBS = {"local-reference-and-browser", "live-identity-provider", "native-postgresql-gate", "container-stack"}
SERVICES = {"postgres", "keycloak", "api", "worker", "mailsink", "caddy", "backup", "executor"}
SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
ASSET = re.compile(r"/assets/[A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:js|css)")
SECRET_VALUE = re.compile(
    r"(?i)(?:bearer\s+\S+|postgres(?:ql)?://[^\s]+|-----BEGIN [^-]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|(?:password|passwd|secret|token|credential)\s*[=:]\s*(?!\[redacted\]|redacted\b)[^\s,;}]+)"
)


class NotRun(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def private_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        json.dump(value, handle, indent=2)
        handle.write("\n")


def clean_origin(value):
    p = urlsplit(value)
    require(p.scheme == "https" and p.hostname and not p.username and not p.password, "HTTPS origin required")
    require(
        p.path in {"", "/"} and not p.query and not p.fragment,
        "Origin cannot include a path, query or fragment",
    )
    require(p.port in {None, 443}, "Only standard public HTTPS port allowed")
    require(not any(c.isspace() for c in value), "Invalid origin")
    return "https://" + p.netloc.lower()


def gate_record(record, expected, git_run):
    """Validate root-supplied evidence references, without contacting GitHub or approving spend."""
    if not SHA.fullmatch(expected):
        raise NotRun("Expected main merge commit is not a full lowercase SHA")
    if record.get("financial_approval") is not True or not record.get("financial_approval_reference"):
        raise NotRun("Financial approval evidence is missing")
    if record.get("merge_authorized") is not True or record.get("main_merge_commit") != expected:
        raise NotRun("Main merge authorization/commit evidence is missing")
    ci = record.get("ci", {})
    if set(ci.get("jobs", {})) != JOBS or any(v != "success" for v in ci.get("jobs", {}).values()):
        raise NotRun("All four exact-head CI jobs have not succeeded")
    head = ci.get("head_sha", "")
    if not SHA.fullmatch(head) or not ci.get("run_url"):
        raise NotRun("CI head and run evidence are missing")
    # A merge SHA differs from its tested branch head. Require an actual local
    # ancestor and identical full tree, rather than assuming the merge was safe.
    if head != expected:
        if git_run(["merge-base", "--is-ancestor", head, expected], check=False).returncode:
            raise NotRun("Tested CI commit is not an ancestor of the merge commit")
        if (
            git_run(["rev-parse", head + "^{tree}"]).stdout
            != git_run(["rev-parse", expected + "^{tree}"]).stdout
        ):
            raise NotRun("Main merge tree differs from the exact CI-tested tree")
    return {
        "main_merge_commit": expected,
        "ci_head_sha": head,
        "ci_run_url": ci["run_url"],
        "jobs": ci["jobs"],
        "financial_approval_reference": record["financial_approval_reference"],
        "evidence_boundary": "Root-supplied approval/CI record; this verifier does not approve spending or query CI",
    }


def safe_relative(name):
    p = Path(name)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in name, "Unsafe proof path")
    return p


def validate_build(repo, proof, expected, git_run):
    sources = proof.get("source_sha256_start")
    require(
        isinstance(sources, dict) and sources and sources == proof.get("source_sha256_end"),
        "Build sources changed or are missing",
    )
    require(
        {
            "VERSION.json",
            "scripts/smoke.py",
            "apps/api/impact_api/main.py",
            "apps/web/index.html",
            "apps/web/ai-walkthrough.html",
            "apps/web/src/ai-walkthrough-main.tsx",
            "apps/web/src/AIFictionalWalkthrough.tsx",
            "apps/web/src/AIFictionalWalkthroughAdapter.ts",
            "apps/web/src/walkthrough-guidance.json",
            "apps/web/vite.config.ts",
        }.issubset(sources),
        "Incomplete frozen source proof",
    )
    require(
        proof.get("exit_codes") == [0, 0] and proof.get("source_changed_during_run", []) == [],
        "Build did not pass unchanged",
    )
    assets = proof.get("built_assets_sha256", {})
    require(
        isinstance(assets, dict)
        and len(assets) == 8
        and {"index.html", "ai-walkthrough.html"}.issubset(assets),
        "Expected exact dual-entry eight-file build proof",
    )
    for name, expected_hash in sources.items():
        safe_relative(name)
        require(DIGEST.fullmatch(expected_hash), "Malformed source digest")
        require(digest((repo / name).read_bytes()) == expected_hash, "Local frozen source mismatch: " + name)
        # Binds the qualified source bytes to the actual merged commit as well.
        result = git_run(["show", expected + ":" + name], binary=True)
        require(digest(result.stdout) == expected_hash, "Merged source differs from build proof: " + name)
    for name, expected_hash in assets.items():
        safe_relative(name)
        require(
            name in {"index.html", "ai-walkthrough.html"} or ASSET.fullmatch("/" + name),
            "Unexpected build asset",
        )
        require(".." not in name and DIGEST.fullmatch(expected_hash), "Malformed asset proof")
        require(
            digest((repo / "apps/web/dist" / name).read_bytes()) == expected_hash,
            "Local built asset mismatch: " + name,
        )
    return {"sources": sources, "assets": assets}


def no_secrets(value, secret_looking):
    if isinstance(value, dict):
        for key, item in value.items():
            require(not secret_looking(key), "Public status contains a secret-looking field")
            no_secrets(item, secret_looking)
    elif isinstance(value, list):
        for item in value:
            no_secrets(item, secret_looking)
    elif isinstance(value, str):
        require(not SECRET_VALUE.search(value), "Public status contains a recognizable secret value")


def validate_status(document, expected, origin, secret_looking):
    no_secrets(document, secret_looking)
    if document.get("commit") != expected or str(document.get("schema_version")) != "40":
        raise NotRun("Public deployment is an older/different commit or schema; new-release scopes not run")
    require(document.get("result") == "ok", "Deployment result is not ok")
    require(document.get("alerts") == [], "Deployment has alerts or missing alert status")
    require(
        document.get("urls", {}).get("application") == origin + "/", "Deployment application hostname differs"
    )
    require(document.get("tls") == "acme", "Deployment does not report public TLS")
    services = document.get("services", {})
    require(SERVICES.issubset(services), "Expected deployment services missing")
    for name in SERVICES:
        row = services[name]
        require(
            row.get("state") == "running" and row.get("health") in {None, "healthy"},
            "Deployment service unhealthy: " + name,
        )
    # Retain only public status projections. Never persist log_tail or full body.
    return {
        "commit": expected,
        "schema_version": "40",
        "result": "ok",
        "tls": "acme",
        "alerts": [],
        "services": {
            name: {"state": services[name]["state"], "health": services[name].get("health")}
            for name in sorted(SERVICES)
        },
        "secret_scan": "No secret-looking keys or recognized credential/JWT/DSN/PEM patterns; not proof against arbitrary unknown secrets",
    }


class RootDocument(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets, self.roots, self.scripts = {}, 0, 0

    def handle_starttag(self, tag, attrs):
        v = dict(attrs)
        require(len(v) == len(attrs), "Duplicate root document attribute")
        require(not any(k.startswith("on") for k in v), "Inline root handler")
        if v.get("id") == "root":
            self.roots += 1
        for key in {"src", "href", "srcset", "srcdoc", "action", "poster", "data"} & v.keys():
            name = v[key] or ""
            require(ASSET.fullmatch(name) and ".." not in name, "External/dev/unsafe root asset")
            if tag == "script" and key == "src":
                require(
                    v.get("type") == "module" and name.endswith(".js"), "Root script is not compiled module"
                )
                self.scripts += 1
                kind = "script"
            elif tag == "link" and key == "href" and v.get("rel") in {"stylesheet", "modulepreload"}:
                kind = "style" if v["rel"] == "stylesheet" else "script"
            else:
                raise ValueError("Unexpected root resource reference")
            require(name not in self.assets and len(self.assets) < 16, "Repeated/excess root references")
            self.assets[name] = kind
        require(
            tag not in {"iframe", "object", "embed", "form", "base"},
            "Unexpected root embedded/navigation tag",
        )
        if tag == "script":
            require(v.get("src"), "Inline root script")


def observe_asset(client, origin, route, expected, observations, limit=8 * 1024 * 1024):
    with client.stream("GET", origin + route, follow_redirects=False) as response:
        chunks, size = [], 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            require(size <= limit, "Response byte limit exceeded")
            chunks.append(chunk)
        body = b"".join(chunks)
        actual = digest(body)
        row = {
            "path": route,
            "status": response.status_code,
            "bytes": size,
            "sha256": actual,
            "expected_sha256": expected,
            "matches": actual == expected,
            "sets_cookie": "set-cookie" in response.headers,
            "content_type": response.headers.get("content-type", "").split(";", 1)[0],
        }
        observations.append(row)  # Preserve mismatches before refusing this scope.
        require(
            response.status_code == 200 and not row["sets_cookie"] and row["matches"],
            "Served static status/cookie/hash mismatch: " + route,
        )
        require(body.strip(), "Empty built asset")
        return response.headers, body


def minimal_env():
    return {
        k: v
        for k, v in os.environ.items()
        if k in {"HOME", "PATH", "TMPDIR", "TEMP", "TMP", "LANG", "LC_ALL", "SYSTEMROOT"}
    }


def bounded_json_get(client, url, limit):
    """Read-only JSON GET with no redirect/cookie and a bound before decoding."""
    with client.stream("GET", url, follow_redirects=False) as response:
        require(response.status_code == 200, "Public JSON endpoint unavailable")
        require("set-cookie" not in response.headers, "Public JSON endpoint sets cookie")
        require(
            response.headers.get("content-type", "").split(";", 1)[0].lower() == "application/json",
            "Public endpoint is not JSON",
        )
        chunks, size = [], 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            require(size <= limit, "Public JSON response exceeds byte limit")
            chunks.append(chunk)
        body = b"".join(chunks)
        return json.loads(body), {
            "status": response.status_code,
            "bytes": size,
            "sha256": digest(body),
            "sets_cookie": False,
        }


def load_smoke(repo):
    spec = importlib.util.spec_from_file_location("frozen_smoke", repo / "scripts/smoke.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(args, report, output):
    repo = args.repo.resolve()
    origin = clean_origin(args.origin)

    def git_run(command, check=True, binary=False):
        return subprocess.run(
            ["git", *command],
            cwd=repo,
            check=check,
            capture_output=True,
            text=not binary,
            env=minimal_env(),
            timeout=30,
        )

    try:
        record = json.loads(args.gate.read_text())
        require(isinstance(record, dict), "Gate record is not an object")
    except (OSError, ValueError):
        raise NotRun("Root approval/CI/merge evidence record is missing or invalid") from None
    report["authorization_gate"] = gate_record(record, args.expected_commit, git_run)
    proof = json.loads(args.build_proof.read_text())
    frozen = validate_build(repo, proof, args.expected_commit, git_run)
    report["frozen_build_proof_sha256"] = digest(args.build_proof.read_bytes())
    report["origin"] = origin
    smoke = load_smoke(repo)
    observations = report.setdefault("served_static_observations", [])
    # No bearer credentials, ambient proxies, cookies, redirects or auth endpoints.
    with httpx.Client(
        verify=True, trust_env=False, timeout=15, follow_redirects=False, cookies=None
    ) as client:
        document, observation = bounded_json_get(client, origin + "/deploy-status.json", 128 * 1024)
        report["deploy_status_http"] = observation
        report["public_deployment"] = validate_status(
            document, args.expected_commit, origin, smoke.secret_looking
        )
        for name, expected_value in (("live", "live"), ("ready", "ready")):
            document, observation = bounded_json_get(client, origin + "/health/" + name, 4096)
            require(
                document == {"status": expected_value},
                "Health does not report " + expected_value,
            )
            report[name] = {**observation, "body_status": expected_value}
        all_assets = set()
        tour_assets = set()
        for route, local_name in (("/", "index.html"), ("/ai-walkthrough.html", "ai-walkthrough.html")):
            headers, body = observe_asset(
                client, origin, route, frozen["assets"][local_name], observations, 128 * 1024
            )
            require(
                headers.get("content-type", "").split(";", 1)[0] == "text/html", "Static entry is not HTML"
            )
            if local_name == "ai-walkthrough.html":
                smoke.walkthrough_csp(headers.get("content-security-policy", ""))
                document = smoke.WalkthroughDocument()
            else:
                document = RootDocument()
            document.feed(body.decode("utf-8"))
            document.close()
            require(document.roots == 1, "No unique static root")
            all_assets.update(document.assets)
            if local_name == "ai-walkthrough.html":
                tour_assets.update(document.assets)
        require(
            all_assets == {"/" + p for p in frozen["assets"] if p.startswith("assets/")},
            "Built and served entry graphs differ",
        )
        for route in sorted(all_assets):
            headers, _ = observe_asset(client, origin, route, frozen["assets"][route[1:]], observations)
            mime = headers.get("content-type", "").split(";", 1)[0]
            require(
                mime
                in (
                    {"text/css"} if route.endswith(".css") else {"text/javascript", "application/javascript"}
                ),
                "Wrong built asset MIME type",
            )
    # Runs the existing default non-provider smoke, including TLS/HTTP redirect,
    # root, readiness, tour and deploy-status. All auth/provider checks are skipped.
    result = subprocess.run(
        [str(repo / ".venv/bin/python"), str(repo / "scripts/smoke.py"), origin, "--no-provider"],
        cwd=repo,
        env=minimal_env(),
        capture_output=True,
        text=True,
        timeout=240,
    )
    try:
        smoke_report = json.loads(result.stdout)
    except ValueError:
        raise ValueError("Existing static smoke did not return JSON; raw output withheld") from None
    no_secrets(smoke_report, lambda _: False)
    report["existing_default_smoke"] = smoke_report
    require(
        result.returncode == 0 and smoke_report.get("passed") is True, "Existing default static smoke failed"
    )
    expected_checks = {
        "tls",
        "https_redirect",
        "live",
        "ready",
        "headers",
        "web_client",
        "ai_walkthrough",
        "deploy_status",
    }
    require(
        all(row["status"] == "pass" for row in smoke_report["checks"] if row["check"] in expected_checks),
        "A required static smoke scope did not pass",
    )
    require(
        expected_checks.issubset({row["check"] for row in smoke_report["checks"]}),
        "A required static smoke scope is missing",
    )
    browser_manifest = {
        "origin": origin,
        "repo": str(repo),
        "expected_commit": args.expected_commit,
        "build_proof": str(args.build_proof.resolve()),
        "build_proof_sha256": report["frozen_build_proof_sha256"],
        "assets": frozen["assets"],
        "sources": frozen["sources"],
        "output": str(output),
        "browser_source_sha256": digest(Path(__file__).with_name("verify_walkthrough.mjs").read_bytes()),
        "browser_executable": str(args.browser_executable.resolve()),
        "root_gate_passed": True,
        "tour_asset_paths": sorted(tour_assets),
    }
    private_json(output / "browser-manifest.json", browser_manifest)
    browser = subprocess.run(
        [
            str(args.node.resolve()),
            str(Path(__file__).with_name("verify_walkthrough.mjs")),
            str(output / "browser-manifest.json"),
        ],
        cwd=repo,
        env=minimal_env(),
        capture_output=True,
        text=True,
        timeout=360,
    )
    report["browser_process"] = {
        "exit_code": browser.returncode,
        "diagnostic": SECRET_VALUE.sub("[redacted]", browser.stderr[-4000:]),
    }
    require((output / "walkthrough-browser.json").exists(), "Browser scope did not produce its named report")
    browser_report = json.loads((output / "walkthrough-browser.json").read_text())
    report["public_browser"] = {
        "report": "walkthrough-browser.json",
        "status": browser_report["status"],
        "groups": len(browser_report["results"]),
    }
    require(
        browser.returncode == 0 and browser_report["status"] == "PASS",
        "Public anonymous browser scope failed; inspect named report",
    )
    # Recheck local source/build equality after remote scopes, and public status
    # again to refuse a deployment that changed during verification.
    validate_build(repo, proof, args.expected_commit, git_run)
    with httpx.Client(verify=True, trust_env=False, timeout=15, follow_redirects=False) as client:
        document, observation = bounded_json_get(client, origin + "/deploy-status.json", 128 * 1024)
        report["final_deploy_status_http"] = observation
        validate_status(document, args.expected_commit, origin, smoke.secret_looking)
    report["status"] = "PASS"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--origin", required=True)
    p.add_argument("--expected-commit", required=True)
    p.add_argument("--build-proof", type=Path, required=True)
    p.add_argument("--gate", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--node", type=Path, required=True)
    p.add_argument("--browser-executable", type=Path, required=True)
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    output = args.output.resolve()
    require(str(output).startswith("/private/tmp/"), "Private tmp output required")
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    report = {
        "status": "NOT_RUN",
        "expected_commit": args.expected_commit,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Read-only public release identity, TLS, readiness, static asset packaging and anonymous fictional walkthrough. No sign-in, API/business command, DB observation, provider or acceptance proof.",
        "limitations": [
            "Approval and CI references are supplied by the root integrator; not independently queried by this helper",
            "Schema40 is public deployment status plus readiness, not a privileged live migration ledger",
            "Anonymous cookie-free context does not prove ambient cookies are absent in an existing user browser",
            "Automated axe plus keyboard/viewport checks do not certify accessibility; incompletes retained",
            "No real organisation onboarding, authentication, procurement, official impact or AI-provider check",
            "Static GETs can update normal server access logs/metrics; no domain writes are requested",
        ],
    }
    try:
        if not args.execute:
            raise NotRun("Explicit root --execute gate not supplied; no network contacted")
        execute(args, report, output)
    except NotRun as error:
        report["reason"] = str(error)
    except Exception as error:
        report["status"] = "FAIL"
        report["reason"] = type(error).__name__ + ": " + str(error)[:400]
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    private_json(output / "deployment-verification.json", report)
    print(json.dumps({"status": report["status"], "report": str(output / "deployment-verification.json")}))
    return 0 if report["status"] == "PASS" else 2 if report["status"] == "NOT_RUN" else 1


if __name__ == "__main__":
    sys.exit(main())
