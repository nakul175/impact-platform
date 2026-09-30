"""The owner's first sign-in on a deployed stack, driven without a browser (CI and rehearsal only).

    .venv/bin/python scripts/staging_first_login.py https://impact.test --email owner@example.org \
        --cacert caddy-root.crt            # temporary password from IMPACT_TEMP_PASSWORD

Follows exactly what deploy/first-admin.sh tells the owner to do: open the application, sign in at
the identity provider with the temporary password, choose a new password, enrol an authenticator
(the TOTP secret is read from the enrolment form and codes are computed here), and return to the
platform. Then it checks, over HTTP only, that the platform session exists, that the account is the
platform operator, and that the session carries the MFA assurance class (a fresh-assurance
control-plane request passes the assurance gate and stops at the missing qualification, 404,
writing nothing). Prints one JSON report; exit 1 on any failure. Never prints a password or secret.
"""

import argparse
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import struct
import sys
import time
from urllib.parse import urljoin
from uuid import uuid4

import httpx


HIDDEN = re.compile(r'<input[^>]*type="hidden"[^>]*>', re.I)


def attribute(tag, name):
    found = re.search(r"\b" + name + r'="([^"]*)"', tag)
    return html.unescape(found.group(1)) if found else None


def form(page, marker=None):
    """(action URL, hidden fields) of the form on the page (the one whose tag holds `marker`)."""
    for match in re.finditer(r"<form[^>]*>", page, re.I):
        tag = match.group(0)
        if marker and marker not in tag:
            continue
        action = attribute(tag, "action")
        end = page.find("</form>", match.end())
        hidden = {}
        for field in HIDDEN.findall(page[match.end() : end if end > 0 else None]):
            if attribute(field, "name"):
                hidden[attribute(field, "name")] = attribute(field, "value") or ""
        return action, hidden
    raise AssertionError("no form" + (" " + marker if marker else "") + " on the page")


def totp(key, at=None, period=30, digits=6):
    """RFC 6238 code for the raw key bytes (Keycloak's enrolment form carries the raw secret in its
    hidden `totpSecret` field; the Base32 text shown to people encodes the same bytes)."""
    counter = int((at or time.time()) // period)
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    return str((struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF) % 10**digits).zfill(digits)


def follow(client, response, limit=10):
    for _ in range(limit):
        if response.status_code not in {301, 302, 303, 307, 308}:
            return response
        response = client.get(urljoin(str(response.url), response.headers["location"]))
    raise AssertionError("too many redirects")


def first_login(base, email, password, verify):
    base = base.rstrip("/")
    steps = []
    with httpx.Client(verify=verify, timeout=20, follow_redirects=False) as client:
        page = follow(client, client.get(base + "/auth/login"))
        assert page.status_code == 200, "login page " + str(page.status_code)
        action, hidden = form(page.text, 'id="kc-form-login"')
        page = follow(client, client.post(action, data={**hidden, "username": email, "password": password}))
        steps.append("password")
        new_password = "Ci-" + secrets.token_urlsafe(18)
        secret = None
        # The provider chooses the order of its required actions; answer whichever page it shows.
        for _ in range(6):
            if str(page.url).startswith(base + "/"):
                break
            if 'id="kc-passwd-update-form"' in page.text:
                action, hidden = form(page.text, 'id="kc-passwd-update-form"')
                data = {**hidden, "password-new": new_password, "password-confirm": new_password}
                step = "update-password"
            elif 'name="totpSecret"' in page.text:
                action, hidden = form(page.text, 'id="kc-totp-settings-form"')
                secret = hidden["totpSecret"]
                data = {**hidden, "totp": totp(secret.encode()), "userLabel": "first-login check"}
                step = "configure-totp"
            elif 'id="kc-update-profile-form"' in page.text:
                # The account was created without a name; the provider asks for one.
                action, hidden = form(page.text, 'id="kc-update-profile-form"')
                data = {**hidden, "email": email, "firstName": "Deployment", "lastName": "Owner"}
                step = "update-profile"
            elif 'id="kc-otp-login-form"' in page.text:
                assert secret, "an authenticator code is asked for but none was enrolled here"
                action, hidden = form(page.text, 'id="kc-otp-login-form"')
                data = {**hidden, "otp": totp(secret.encode())}
                step = "otp"
            else:
                found = re.search(
                    r'kc-feedback-text">([^<]*)<|id="input-error[^"]*"[^>]*>([^<]*)<', page.text
                )
                raise AssertionError(
                    "unexpected provider page: " + str(found.groups() if found else page.url)[:200]
                )
            assert steps.count(step) < 2, step + " was refused"
            page = follow(client, client.post(action, data=data))
            steps.append(step)
        assert str(page.url).startswith(base + "/"), "did not return to the platform: " + str(page.url)[:120]
        me = client.get(base + "/auth/me")
        assert me.status_code == 200, "/auth/me " + str(me.status_code)
        csrf = me.json()["csrf_token"]
        directory = client.get(base + "/v1/platform/tenants")
        assert directory.status_code == 200, "platform directory " + str(directory.status_code)
        operator = directory.json()["operator"]
        qualifications = directory.json()["qualifications"]
        probe = client.post(
            base + "/v1/platform/tenants",
            headers={"Origin": base, "X-CSRF-Token": csrf, "Content-Type": "application/json"},
            content=json.dumps(
                {
                    "operation_id": str(uuid4()),
                    "data": {
                        "owner_identity_id": str(uuid4()),
                        "qualification_id": str(uuid4()),
                        "operating_name": "Assurance probe (never created)",
                        "reporting_zone": "Asia/Kolkata",
                        "retention_days": 30,
                        "privacy_reference": "probe",
                        "reason": "First-login check: fresh MFA assurance reaches the qualification lookup",
                    },
                }
            ),
        )
        reason = (
            probe.json().get("reason_code")
            if probe.headers.get("content-type", "").startswith("application/json")
            else None
        )
    return {
        "steps": steps,
        "identity_id": me.json()["identity_id"],
        "operator": operator,
        "qualifications": len(qualifications),
        "assurance_probe": {"status": probe.status_code, "reason_code": reason},
        "passed": bool(operator) and probe.status_code == 404 and "configure-totp" in steps,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("base_url")
    p.add_argument("--email", required=True)
    tls = p.add_mutually_exclusive_group()
    tls.add_argument("--cacert")
    tls.add_argument("--insecure", action="store_true")
    args = p.parse_args(argv)
    password = os.environ.get("IMPACT_TEMP_PASSWORD", "")
    if not password:
        raise SystemExit("IMPACT_TEMP_PASSWORD is required")
    try:
        report = first_login(
            args.base_url, args.email, password, False if args.insecure else (args.cacert or True)
        )
    except (AssertionError, httpx.HTTPError, KeyError, ValueError) as e:
        report = {"passed": False, "error": type(e).__name__ + ": " + str(e)[:300]}
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
