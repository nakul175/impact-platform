"""Smoke check of a deployed Impact Platform from outside, over its public URLs.

    .venv/bin/python scripts/smoke.py https://168-144-78-191.sslip.io
    .venv/bin/python scripts/smoke.py https://impact.test --cacert caddy-root.crt   # internal CA
    .venv/bin/python scripts/smoke.py https://impact.test --insecure                # no TLS check

Checks, each reported as pass, fail or skip in one JSON document (exit 1 when any fails):

    tls              the certificate chain and host name verify (skipped with --insecure or http)
    https_redirect   plain HTTP on port 80 redirects to HTTPS (skipped for an http:// base)
    live, ready      /health/live and /health/ready answer 200 (ready: schema, database logins)
    headers          HSTS, CSP, nosniff, no-store, no-referrer on the application's responses
    web_client       / serves the compiled web client
    ai_walkthrough   the separate fictional walkthrough is packaged with restrictive headers
                     and bounded same-origin compiled script/style assets (static smoke only)
    live_provider    /auth/mode reports development sign-in off
    login_redirect   /auth/login redirects to the provider's authorization endpoint with S256 PKCE,
                     the web client, the callback on this origin and the required ACR
    provider         the realm's discovery document names the same issuer and endpoints, and the
                     authorization page answers
    provider_admin_hidden   the provider's administration console is not published
    deploy_status    /deploy-status.json answers with a commit and no secret-looking field

--issuer defaults to https://auth.<host>/realms/impact. --no-provider and --no-deploy-status skip
the provider and status checks (for a local stack without them).
"""

import argparse
import json
import re
import socket
import ssl
import sys
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

import httpx

REQUIRED_HEADERS = {
    "strict-transport-security": lambda v: "max-age=" in v,
    "content-security-policy": lambda v: "default-src 'self'" in v and "frame-ancestors 'none'" in v,
    "x-content-type-options": lambda v: v.lower() == "nosniff",
    "cache-control": lambda v: "no-store" in v,
    "referrer-policy": lambda v: v.lower() == "no-referrer",
}
SECRET_WORDS = ("password", "passwd", "secret", "token", "dsn", "key", "credential")
WALKTHROUGH_HTML_LIMIT = 128 * 1024
WALKTHROUGH_ASSET_LIMIT = 8 * 1024 * 1024
WALKTHROUGH_REFERENCE_LIMIT = 16


class WalkthroughDocument(HTMLParser):
    """Inspect the static production entry without executing scripts or authenticating."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.roots, self.scripts, self.assets = 0, [], {}
        self.title, self.notice = [], []
        self.capture = None
        self.doctype = False

    def handle_decl(self, decl):
        self.doctype = decl.lower() == "doctype html"

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        assert len(values) == len(attrs), "duplicate static entry attribute"
        assert not any(name.startswith("on") for name in values), "inline static event handler"
        if values.get("id") == "root":
            assert tag == "div", "unexpected static root"
            self.roots += 1
        if tag in {"title", "noscript", "script"}:
            self.capture = tag
        for name in {
            "src",
            "href",
            "xlink:href",
            "srcset",
            "srcdoc",
            "action",
            "formaction",
            "poster",
            "data",
        } & values.keys():
            path = values[name] or ""
            assert re.fullmatch(r"/assets/[A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:js|css)", path), (
                "static reference is not a bounded same-origin compiled asset"
            )
            assert ".." not in path, "static asset traversal"
            if tag == "script" and name == "src":
                assert values.get("type") == "module" and path.endswith(".js"), (
                    "walkthrough entry is not a compiled module"
                )
                assert re.fullmatch(r"/assets/walkthrough-[A-Za-z0-9_-]+\.js", path), (
                    "unexpected walkthrough script entry"
                )
                self.scripts.append(path)
                kind = "script"
            elif tag == "link" and name == "href":
                rel = values.get("rel", "").lower()
                assert rel in {"stylesheet", "modulepreload"}, "unexpected static asset relation"
                kind = "style" if rel == "stylesheet" else "script"
                assert path.endswith(".css" if kind == "style" else ".js"), (
                    "static asset extension does not match its relation"
                )
            else:
                raise AssertionError("unexpected static resource reference")
            assert path not in self.assets, "duplicate static resource reference"
            self.assets[path] = kind
            assert len(self.assets) <= WALKTHROUGH_REFERENCE_LIMIT, "too many static assets"
        if tag == "script":
            assert values.get("src"), "inline/source-only walkthrough script"
        assert tag not in {"base", "iframe", "object", "embed", "form"}, (
            "unexpected static document navigation or embedded content"
        )
        assert not (tag == "meta" and values.get("http-equiv", "").lower() == "refresh"), (
            "unexpected static document redirect"
        )

    def handle_endtag(self, tag):
        if tag == self.capture:
            self.capture = None

    def handle_data(self, data):
        if self.capture == "title":
            self.title.append(data)
        elif self.capture == "noscript":
            self.notice.append(data)
        elif self.capture == "script":
            assert not data.strip(), "inline walkthrough script body"


def walkthrough_csp(value):
    directives = {}
    for item in value.split(";"):
        words = item.strip().split()
        if not words:
            continue
        name = words[0].lower()
        assert name not in directives, "duplicate walkthrough CSP directive"
        directives[name] = words[1:]
    for name in (
        "default-src",
        "connect-src",
        "img-src",
        "object-src",
        "base-uri",
        "form-action",
        "frame-ancestors",
    ):
        assert directives.get(name) == ["'none'"], "weak walkthrough CSP: " + name
    for name in ("script-src", "style-src"):
        assert directives.get(name) == ["'self'"], "weak walkthrough CSP: " + name
    for name in ("script-src-elem", "style-src-elem"):
        assert name not in directives or directives[name] == ["'self'"], "weak walkthrough CSP: " + name
    for name in ("script-src-attr", "frame-src", "child-src", "worker-src", "font-src", "media-src"):
        assert name not in directives or directives[name] == ["'none'"], "weak walkthrough CSP: " + name
    assert "style-src-attr" not in directives or directives["style-src-attr"] in (
        ["'none'"],
        ["'unsafe-inline'"],
    ), "weak walkthrough CSP: style-src-attr"


def bounded_static_get(client, url, limit):
    """Bound downloaded bytes and do not follow a redirect to another origin."""
    with client.stream("GET", url, follow_redirects=False) as response:
        assert response.status_code == 200, "static status " + str(response.status_code)
        assert "set-cookie" not in response.headers, "static response sets a cookie"
        chunks, size = [], 0
        for chunk in response.iter_bytes():
            size += len(chunk)
            assert size <= limit, "static response exceeds byte limit"
            chunks.append(chunk)
        return response.headers, b"".join(chunks)


def secret_looking(name):
    """True when a word of a field name names a secret: ``db_password``, ``signingKey``, ``api-key``,
    ``apikey``, ``signing_keys``. Matching is per word (a word ending in a secret word, plural or
    not), so the service name ``keycloak`` in the status file's ``services`` is not taken for a key."""
    words = re.split(r"[^a-z0-9]+", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(name)).lower())
    stems = {w for word in words if word for w in (word, word[:-1] if word.endswith("s") else word)}
    return any(stem.endswith(secret) for stem in stems for secret in SECRET_WORDS)


class Smoke:
    def __init__(self, base, issuer=None, verify=True, timeout=15, required_acr=None):
        parsed = urlparse(base)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.path not in {"", "/"}:
            raise ValueError("The base URL must be an origin such as https://example.org")
        self.base = parsed.scheme + "://" + parsed.netloc
        self.host, self.https = parsed.hostname, parsed.scheme == "https"
        self.port = parsed.port or (443 if self.https else 80)
        self.issuer = (issuer or "https://auth." + self.host + "/realms/impact").rstrip("/")
        self.verify, self.required_acr = verify, required_acr
        self.client = httpx.Client(verify=verify, timeout=timeout, follow_redirects=False)
        self.results = []

    def check(self, name, function):
        try:
            outcome = function()
            status, detail = outcome if isinstance(outcome, tuple) else ("pass", outcome)
        except AssertionError as e:
            status, detail = "fail", str(e) or "assertion failed"
        except (httpx.HTTPError, OSError, ssl.SSLError, ValueError, KeyError) as e:
            status, detail = "fail", type(e).__name__ + ": " + str(e)[:300]
        self.results.append({"check": name, "status": status, "detail": detail})

    def get(self, path, **kwargs):
        return self.client.get(self.base + path, **kwargs)

    def tls(self):
        if not self.https:
            return "skip", "plain HTTP base URL"
        if self.verify is False:
            return "skip", "--insecure"
        context = ssl.create_default_context(cafile=self.verify if isinstance(self.verify, str) else None)
        with socket.create_connection((self.host, self.port), timeout=10) as raw:
            with context.wrap_socket(raw, server_hostname=self.host) as tls:
                cert = tls.getpeercert()
                version = tls.version()
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        return "pass", {
            "protocol": version,
            "issuer": issuer.get("organizationName") or issuer.get("commonName"),
            "not_after": cert.get("notAfter"),
        }

    def https_redirect(self):
        if not self.https:
            return "skip", "plain HTTP base URL"
        response = httpx.get("http://" + self.host + "/health/live", timeout=10, follow_redirects=False)
        location = response.headers.get("location", "")
        assert response.status_code in {301, 302, 307, 308}, "HTTP answered " + str(response.status_code)
        assert location.startswith("https://" + self.host), "HTTP redirects to " + location
        return "pass", {"status": response.status_code}

    def live(self):
        response = self.get("/health/live")
        assert response.status_code == 200, "status " + str(response.status_code)
        return response.json()

    def ready(self):
        response = self.get("/health/ready")
        body = (
            response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        )
        assert response.status_code == 200, (
            "status " + str(response.status_code) + " " + str(body.get("reason_code", ""))
        )
        assert body.get("status") == "ready", "body " + json.dumps(body)[:200]
        return body

    def headers(self):
        response = self.get("/health/live")
        missing = {}
        for name, valid in REQUIRED_HEADERS.items():
            value = response.headers.get(name)
            if name == "strict-transport-security" and not self.https:
                continue
            if value is None or not valid(value):
                missing[name] = value
        assert not missing, "missing or weak: " + json.dumps(missing)
        return "pass", sorted(
            REQUIRED_HEADERS if self.https else set(REQUIRED_HEADERS) - {"strict-transport-security"}
        )

    def web_client(self):
        response = self.get("/")
        assert response.status_code == 200, "status " + str(response.status_code)
        assert "<script" in response.text and 'id="root"' in response.text, "no compiled web client"
        return {"bytes": len(response.content)}

    def ai_walkthrough(self):
        headers, body = bounded_static_get(
            self.client, self.base + "/ai-walkthrough.html", WALKTHROUGH_HTML_LIMIT
        )
        assert headers.get("content-type", "").split(";", 1)[0].lower() == "text/html", (
            "walkthrough is not HTML"
        )
        for name, expected in (("x-content-type-options", "nosniff"), ("referrer-policy", "no-referrer")):
            assert headers.get(name, "").lower() == expected, "weak static header: " + name
        cache = [item.strip().lower() for item in headers.get("cache-control", "").split(",")]
        assert "no-store" in cache, "walkthrough response is not no-store"
        walkthrough_csp(headers.get("content-security-policy", ""))
        document = WalkthroughDocument()
        document.feed(body.decode("utf-8"))
        document.close()
        assert document.doctype and document.roots == 1, "no unique production walkthrough root"
        assert " ".join("".join(document.title).split()) == (
            "Fictional AI walkthrough · Tola / Impact Platform"
        ), "missing fictional walkthrough title"
        notice = " ".join("".join(document.notice).split()).lower()
        assert notice == (
            "this fictional walkthrough needs javascript. it has no sign-in, network actions or persistence."
        ), "missing static fictional/no-persistence notice"
        assert len(document.scripts) == 1 and "style" in document.assets.values(), (
            "missing compiled walkthrough entry or style"
        )
        for path, kind in document.assets.items():
            asset_headers, asset_body = bounded_static_get(
                self.client, self.base + path, WALKTHROUGH_ASSET_LIMIT
            )
            content_type = asset_headers.get("content-type", "").split(";", 1)[0].lower()
            permitted = {"text/css"} if kind == "style" else {"text/javascript", "application/javascript"}
            assert content_type in permitted and asset_body.strip(), "missing/wrong-type compiled asset"
        return {
            "scope": "static packaging/header smoke only; no script execution, authentication or persistence",
            "document_bytes": len(body),
            "asset_count": len(document.assets),
        }

    def live_provider(self):
        response = self.get("/auth/mode")
        assert response.status_code == 200 and response.json() == {"development": False}, response.text[:200]
        return response.json()

    def login_redirect(self):
        response = self.get("/auth/login")
        assert response.status_code in {302, 303}, "status " + str(response.status_code)
        location = urlparse(response.headers["location"])
        query = {k: v[0] for k, v in parse_qs(location.query).items()}
        expected = self.issuer + "/protocol/openid-connect/auth"
        actual = location.scheme + "://" + location.netloc + location.path
        assert actual == expected, "redirects to " + actual
        assert query.get("code_challenge_method") == "S256" and query.get("code_challenge"), "no S256 PKCE"
        assert query.get("response_type") == "code", "not the authorization-code flow"
        assert query.get("redirect_uri") == self.base + "/auth/callback", "callback " + str(
            query.get("redirect_uri")
        )
        assert query.get("state") and query.get("nonce"), "no state or nonce"
        if self.required_acr:
            assert query.get("acr_values") == self.required_acr, "acr_values " + str(query.get("acr_values"))
        else:
            assert query.get("acr_values"), "no acr_values"
        self.authorization = response.headers["location"]
        return {"client_id": query.get("client_id"), "acr_values": query.get("acr_values")}

    def provider(self):
        discovery = self.client.get(self.issuer + "/.well-known/openid-configuration")
        assert discovery.status_code == 200, "discovery status " + str(discovery.status_code)
        document = discovery.json()
        assert document["issuer"] == self.issuer, "issuer " + document["issuer"]
        assert "S256" in document.get("code_challenge_methods_supported", []), "S256 not supported"
        assert document.get("backchannel_logout_supported") is True, "no back-channel logout"
        page = self.client.get(getattr(self, "authorization", document["authorization_endpoint"]))
        assert page.status_code == 200 and "<form" in page.text, "authorization page " + str(page.status_code)
        return {"issuer": document["issuer"], "authorization_page": page.status_code}

    def provider_admin_hidden(self):
        origin = urlparse(self.issuer)
        response = self.client.get(origin.scheme + "://" + origin.netloc + "/admin/master/console/")
        assert response.status_code in {403, 404}, "console answers " + str(response.status_code)
        return {"status": response.status_code}

    def deploy_status(self):
        response = self.get("/deploy-status.json")
        assert response.status_code == 200, "status " + str(response.status_code)
        document = response.json()
        assert document.get("commit"), "no commit"

        def keys(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    yield k
                    yield from keys(v)
            elif isinstance(value, list):
                for v in value:
                    yield from keys(v)

        suspicious = [k for k in keys(document) if secret_looking(k)]
        assert not suspicious, "secret-looking fields: " + ", ".join(suspicious)
        return {
            "commit": document.get("commit"),
            "result": document.get("result"),
            "alerts": [a.get("code") for a in document.get("alerts") or [] if isinstance(a, dict)],
        }

    def run(self, provider=True, status=True):
        self.check("tls", self.tls)
        self.check("https_redirect", self.https_redirect)
        self.check("live", self.live)
        self.check("ready", self.ready)
        self.check("headers", self.headers)
        self.check("web_client", self.web_client)
        self.check("ai_walkthrough", self.ai_walkthrough)
        for name in ("live_provider", "login_redirect", "provider", "provider_admin_hidden"):
            self.check(name, getattr(self, name) if provider else lambda: ("skip", "--no-provider"))
        self.check("deploy_status", self.deploy_status if status else lambda: ("skip", "--no-deploy-status"))
        return {
            "base_url": self.base,
            "issuer": self.issuer,
            "passed": all(r["status"] != "fail" for r in self.results),
            "checks": self.results,
        }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("base_url")
    p.add_argument("--issuer")
    p.add_argument("--required-acr", default="urn:impact:acr:mfa")
    tls = p.add_mutually_exclusive_group()
    tls.add_argument("--insecure", action="store_true", help="Do not verify TLS certificates")
    tls.add_argument("--cacert", help="Verify TLS against this CA file (for an internal CA)")
    p.add_argument("--no-provider", action="store_true")
    p.add_argument("--no-deploy-status", action="store_true")
    args = p.parse_args(argv)
    verify = False if args.insecure else (args.cacert or True)
    report = Smoke(args.base_url, args.issuer, verify, required_acr=args.required_acr).run(
        provider=not args.no_provider, status=not args.no_deploy_status
    )
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
