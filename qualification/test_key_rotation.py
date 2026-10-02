"""Key governance and rotation of the application's own secrets (v0.25 part A).

Pure checks of the keyring, the sealed formats and scripts/rotate_secrets.py, then live checks: values
made by the running API before a rotation (a browser session's CSRF token, a signed cursor, a fixture
bearer token, sealed delivery recipients and invitation links) keep working on an API started with the
rotated configuration while the old secrets are in grace, new values carry the new key id, and every
old value fails once its secret is retired. The rotated APIs run in-process on a copy of the run
directory; the suite's API keeps its own configuration."""

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets as random
import shutil
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from conftest import signed as mint
from impact_api.auth import Auth
from impact_api.config import Settings
from impact_api.delivery import (
    channel_code,
    channel_code_hash,
    code_secret,
    seal_recipient,
    unseal_recipient,
)
from impact_api.keyring import Keyring, KeyringError, key_id, ring, rsa_key_id, sealed_kid, validate
from impact_api.worker import ConfigurationError, WorkerSettings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import rotate_secrets  # noqa: E402

OLD, NEW, OTHER = "o" * 64, "n" * 64, "x" * 64


# ------------------------------------------------------------------------------------- keyring


def test_kids_are_derived_per_family_and_reveal_no_value():
    assert key_id("cookie", OLD) != key_id("delivery", OLD)
    assert len(key_id("cookie", OLD)) == 12 and OLD[:12] not in key_id("cookie", OLD)
    keys = Keyring("cookie", NEW, [OLD])
    assert keys.ids() == [key_id("cookie", NEW), key_id("cookie", OLD)]
    assert NEW not in repr(keys) and OLD not in str(keys)


def test_hmac_tokens_verify_during_grace_and_fail_after_retirement():
    token = Keyring("cookie", OLD).sign(b"csrf:session")
    assert token.startswith(key_id("cookie", OLD) + ".")
    assert Keyring("cookie", NEW, [OLD]).verify(b"csrf:session", token)
    assert not Keyring("cookie", NEW).verify(b"csrf:session", token)
    # A legacy bare-hex token (made before kids existed) verifies with any non-retired secret.
    legacy = hmac.new(OLD.encode(), b"csrf:session", hashlib.sha256).hexdigest()
    assert Keyring("cookie", NEW, [OLD]).verify(b"csrf:session", legacy)
    assert not Keyring("cookie", NEW).verify(b"csrf:session", legacy)
    # A kid that names the wrong key, a malformed kid and another message all fail.
    forged = key_id("cookie", NEW) + "." + token.split(".")[1]
    assert not Keyring("cookie", NEW, [OLD]).verify(b"csrf:session", forged)
    assert not Keyring("cookie", NEW, [OLD]).verify(b"csrf:session", "zz." + token.split(".")[1])
    assert not Keyring("cookie", NEW, [OLD]).verify(b"csrf:other", token)


def test_sealed_recipients_carry_the_kid_and_legacy_values_still_open():
    sealed = seal_recipient(OLD, "t", "MEMBER_INVITATION", "r", "Person@Example.test")
    assert sealed_kid(sealed) == key_id("delivery", OLD) and len(sealed) <= 300
    rotated = Keyring("delivery", NEW, [OLD])
    assert unseal_recipient(rotated, "t", "MEMBER_INVITATION", "r", sealed) == "person@example.test"
    with pytest.raises(InvalidTag):
        unseal_recipient(Keyring("delivery", NEW), "t", "MEMBER_INVITATION", "r", sealed)
    with pytest.raises(InvalidTag):
        unseal_recipient(rotated, "t", "MEMBER_INVITATION", "other", sealed)
    assert sealed_kid(seal_recipient(rotated, "t", "MEMBER_INVITATION", "r", "a@b.test")) == key_id(
        "delivery", NEW
    )
    # The pre-rotation format: nonce + AES-GCM ciphertext without a header.
    nonce = random.token_bytes(12)
    key = hmac.new(OLD.encode(), b"impact-delivery-recipient-v1", hashlib.sha256).digest()
    legacy = nonce + AESGCM(key).encrypt(
        nonce, b"legacy@example.test", b"impact-delivery-v1:t:MEMBER_INVITATION:r"
    )
    assert unseal_recipient(rotated, "t", "MEMBER_INVITATION", "r", legacy) == "legacy@example.test"
    with pytest.raises(InvalidTag):
        unseal_recipient(Keyring("delivery", NEW), "t", "MEMBER_INVITATION", "r", legacy)


def test_recovery_codes_issued_before_a_rotation_are_found_during_grace():
    stored = channel_code_hash(OLD, "challenge", channel_code(OLD, "challenge"))
    assert code_secret(Keyring("delivery", NEW, [OLD]), "challenge", stored) == OLD
    assert code_secret(Keyring("delivery", NEW), "challenge", stored) is None


def test_logout_hints_rotate_and_an_oversized_token_is_not_sealed():
    session = "session-cookie-value"
    before = Auth(SimpleNamespace(cookie_secret=OLD, jwks_url=""), None)
    hint = before.seal_hint(session, "id.token.value")
    assert sealed_kid(hint) == key_id("cookie", OLD)
    during = Auth(SimpleNamespace(cookie_secret=NEW, cookie_secret_previous=OLD, jwks_url=""), None)
    assert during.open_hint(session, hint) == "id.token.value"
    assert during.open_hint("another-session", hint) is None
    after = Auth(SimpleNamespace(cookie_secret=NEW, cookie_secret_previous="", jwks_url=""), None)
    assert after.open_hint(session, hint) is None
    # migration 0017 caps the column at 16412 bytes: header 7 + nonce 12 + tag 16 + token.
    assert len(during.seal_hint(session, "t" * 16377)) == 16412
    assert during.seal_hint(session, "t" * 16378) is None


def test_settings_validate_keyrings_and_never_print_secrets(tmp_path, monkeypatch):
    config = {
        "environment": "development",
        "app_dsn": "postgresql://app:app-password-value@127.0.0.1/impact",
        "identity_dsn": "postgresql://identity:identity-password-value@127.0.0.1/impact",
        "public_origin": "http://127.0.0.1:8000",
        "issuer": "http://127.0.0.1:8080/realms/impact-dev",
        "client_id": "web",
        "audience": "api",
        "jwks_url": "",
        "authorization_url": "",
        "token_url": "",
        "cookie_secret": NEW,
        "cookie_secret_previous": OLD,
        "invitation_secret": "i" * 64,
        "delivery_secret": "d" * 64,
        "delivery_secret_previous": "e" * 64 + ",  " + "f" * 64,
        "dev_auth": True,
    }
    for name in [n for n in os.environ if n.startswith("IMPACT_")]:
        monkeypatch.delenv(name)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
    s = Settings.load()
    assert ring(s, "delivery").ids() == [key_id("delivery", x * 64) for x in "def"]
    text = repr(s)
    for value in [NEW, OLD, "i" * 64, "d" * 64, "e" * 64, "app-password-value", "identity-password-value"]:
        assert value not in text
    for change, message in [
        ({"cookie_secret_previous": "short"}, "at least 48"),
        ({"cookie_secret_previous": NEW}, "repeats the current"),
        ({"delivery_secret_previous": "i" * 64}, "share a secret"),
    ]:
        path.write_text(json.dumps({**config, **change}))
        with pytest.raises(ValueError, match=message):
            Settings.load()
    with pytest.raises(KeyringError, match="need a current"):
        validate(SimpleNamespace(delivery_secret="", delivery_secret_previous=OLD), families=("delivery",))
    worker = WorkerSettings(
        environment="test",
        worker_dsn="postgresql://w:worker-password-value@h/db",
        public_origin="http://127.0.0.1:8000",
        invitation_secret="i" * 64,
        invitation_secret_previous=OLD,
        delivery_secret="d" * 64,
        delivery_secret_previous="j" * 64,
        synthetic_sink=str(tmp_path / "sink"),
    )
    worker.validate()
    assert not {"i" * 64, OLD, "d" * 64, "j" * 64, "worker-password-value"} & {
        part for part in repr(worker).replace("'", " ").replace(",", " ").split()
    }
    shared = WorkerSettings(**{**worker.__dict__, "delivery_secret_previous": OLD})
    with pytest.raises(ConfigurationError, match="INVALID_KEYRING"):
        shared.validate()


# ------------------------------------------------------------------------------ rotation script


def run_script(capsys, *argv):
    code = rotate_secrets.main(list(argv))
    out, err = capsys.readouterr()
    return code, (json.loads(out) if out.strip() else None), err


def env_secrets(path):
    return dict(line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)


def test_env_file_rotation_is_atomic_private_and_prints_kids_only(tmp_path, capsys):
    env = tmp_path / "secrets.env"
    compose = tmp_path / "compose.env"
    original = {
        "POSTGRES_PASSWORD": "p" * 64,
        "IMPACT_COOKIE_SECRET": "c" * 96,
        "IMPACT_INVITATION_SECRET": "i" * 96,
        "IMPACT_DELIVERY_SECRET": "d" * 96,
    }
    env.write_text("".join(k + "=" + v + "\n" for k, v in original.items()))
    env.chmod(0o600)
    compose.write_text("IMPACT_TAG=abc\nIMPACT_COOKIE_SECRET=" + "c" * 96 + "\n")
    # A dry run reports the plan and writes nothing.
    code, out, _ = run_script(capsys, "--env-file", str(env), "--dry-run", "rotate", "--family", "all")
    assert code == 0 and out["dry_run"] and env_secrets(env) == original
    assert not (tmp_path / "secrets.env.keys.json").exists()
    code, out, _ = run_script(
        capsys,
        "--env-file",
        str(env),
        "--sync-to",
        str(compose),
        "rotate",
        "--family",
        "all",
        "--reason",
        "drill",
    )
    assert code == 0 and out["restart_required"] == ["api", "worker"]
    rotated = env_secrets(env)
    assert oct(env.stat().st_mode & 0o777) == "0o600" and rotated["POSTGRES_PASSWORD"] == "p" * 64
    for family in ["cookie", "invitation", "delivery"]:
        name = "IMPACT_" + family.upper() + "_SECRET"
        assert rotated[name] != original[name] and len(rotated[name]) >= 48
        assert rotated[name + "_PREVIOUS"] == original[name]
        result = next(r for r in out["results"] if r["family"] == family)
        assert result["grace_kid"] == key_id(family, original[name])
        assert result["new_kid"] == key_id(family, rotated[name])
    synced = env_secrets(compose)
    assert synced["IMPACT_TAG"] == "abc" and synced["IMPACT_COOKIE_SECRET"] == rotated["IMPACT_COOKIE_SECRET"]
    assert synced["IMPACT_DELIVERY_SECRET_PREVIOUS"] == original["IMPACT_DELIVERY_SECRET"]
    register = json.loads((tmp_path / "secrets.env.keys.json").read_text())
    assert [e["event"] for e in register["events"]] == ["rotate"] * 3
    # status names kids and grace dates, never a value.
    code, status, _ = run_script(capsys, "--env-file", str(env), "status")
    assert status["families"]["cookie"]["grace"][0]["kid"] == key_id(
        "cookie", original["IMPACT_COOKIE_SECRET"]
    )
    printed = json.dumps([out, status, register])
    for value in list(original.values()) + list(rotated.values()):
        for part in value.split(","):
            assert part not in printed
    # Retire one kid, then nothing is left in grace for that family; an unknown kid is refused.
    kid = key_id("cookie", original["IMPACT_COOKIE_SECRET"])
    code, out, _ = run_script(capsys, "--env-file", str(env), "retire", "--family", "cookie", "--kid", kid)
    assert code == 0 and out["results"] == [{"family": "cookie", "retired": [kid]}]
    assert env_secrets(env)["IMPACT_COOKIE_SECRET_PREVIOUS"] == ""
    code, _, err = run_script(capsys, "--env-file", str(env), "retire", "--family", "cookie", "--kid", kid)
    assert code == 2 and "not a grace key" in err
    # --expired retires only keys whose recorded grace has ended.
    code, out, _ = run_script(capsys, "--env-file", str(env), "retire", "--family", "all", "--expired")
    assert all(r["retired"] == [] for r in out["results"])
    register = json.loads((tmp_path / "secrets.env.keys.json").read_text())
    for family in ["invitation", "delivery"]:
        register["keys"][family + ":" + key_id(family, original["IMPACT_" + family.upper() + "_SECRET"])][
            "grace_until"
        ] = "2000-01-01T00:00:00Z"
    (tmp_path / "secrets.env.keys.json").write_text(json.dumps(register))
    code, out, _ = run_script(capsys, "--env-file", str(env), "retire", "--family", "all", "--expired")
    assert sorted(r["family"] for r in out["results"] if r["retired"]) == ["delivery", "invitation"]
    assert env_secrets(env)["IMPACT_DELIVERY_SECRET_PREVIOUS"] == ""


def test_provisioner_family_rotates_without_grace_and_asks_for_the_provider_realignment(tmp_path, capsys):
    """v0.27: the identity provider's client secret is one value on each side. A rotation writes the
    new value to the env file only (the wrapper re-aligns Keycloak and recreates the api), keeps no
    previous value, cannot be retired, exists only in env-file mode, and prints kids only."""
    env = tmp_path / "secrets.env"
    env.write_text("IMPACT_COOKIE_SECRET=" + "c" * 96 + "\nIMPACT_PROVISIONER_SECRET=" + "p" * 48 + "\n")
    env.chmod(0o600)
    code, status, _ = run_script(capsys, "--env-file", str(env), "status")
    assert code == 0 and status["families"]["provisioner"]["grace"] == []
    assert status["families"]["provisioner"]["current"]["kid"] == key_id("provisioner", "p" * 48)
    code, out, _ = run_script(
        capsys, "--env-file", str(env), "--dry-run", "rotate", "--family", "provisioner"
    )
    assert code == 0 and out["dry_run"] and env_secrets(env)["IMPACT_PROVISIONER_SECRET"] == "p" * 48
    assert out["provider_realign"] == ["provisioner"] and out["restart_required"] == []
    code, out, _ = run_script(
        capsys, "--env-file", str(env), "rotate", "--family", "provisioner", "--reason", "drill"
    )
    rotated = env_secrets(env)
    assert code == 0 and rotated["IMPACT_PROVISIONER_SECRET"] != "p" * 48
    assert (
        len(rotated["IMPACT_PROVISIONER_SECRET"]) >= 48
        and "IMPACT_PROVISIONER_SECRET_PREVIOUS" not in rotated
    )
    assert rotated["IMPACT_COOKIE_SECRET"] == "c" * 96
    assert out["restart_required"] == ["api"] and out["provider_realign"] == ["provisioner"]
    (result,) = out["results"]
    assert result["grace_kid"] is None and result["new_kid"] == key_id(
        "provisioner", rotated["IMPACT_PROVISIONER_SECRET"]
    )
    register = json.loads((tmp_path / "secrets.env.keys.json").read_text())
    assert register["keys"]["provisioner:" + key_id("provisioner", "p" * 48)]["retired_at"]
    assert register["events"][-1]["replaced"] == key_id("provisioner", "p" * 48)
    printed = json.dumps([out, register])
    assert "p" * 48 not in printed and rotated["IMPACT_PROVISIONER_SECRET"] not in printed
    # `all` rotates it with the rest and asks for the re-alignment; retirement is refused.
    code, out, _ = run_script(capsys, "--env-file", str(env), "rotate", "--family", "all")
    assert code == 0 and out["provider_realign"] == ["provisioner"]
    assert sorted(r["family"] for r in out["results"]) == ["cookie", "provisioner"]
    code, _, err = run_script(
        capsys, "--env-file", str(env), "retire", "--family", "provisioner", "--all-previous"
    )
    assert code == 2 and "no grace secret" in err
    code, out, _ = run_script(capsys, "--env-file", str(env), "retire", "--family", "all", "--all-previous")
    assert code == 0 and [r["family"] for r in out["results"]] == ["cookie"] and out["provider_realign"] == []
    run = tmp_path / "run"
    run.mkdir()
    (run / "config.json").write_text(json.dumps({"cookie_secret": "c" * 96}))
    code, _, err = run_script(capsys, "--config-dir", str(run), "rotate", "--family", "provisioner")
    assert code == 2 and "not configured" in err


def test_signing_family_needs_a_run_directory(tmp_path, capsys):
    env = tmp_path / "secrets.env"
    env.write_text("IMPACT_COOKIE_SECRET=" + "c" * 96 + "\n")
    code, _, err = run_script(capsys, "--env-file", str(env), "rotate", "--family", "signing")
    assert code == 2 and "not configured" in err


# ------------------------------------------------------------------------------------------- live


def cmd(data):
    return {"operation_id": str(uuid4()), "data": data}


def rotated_copy(live, tmp_path):
    """A copy of the suite's run directory: configuration, worker configuration and keypair."""
    target = tmp_path / "run"
    target.mkdir()
    for name in ["config.json", "worker.json", "private.pem", "public.pem"]:
        shutil.copy(live.local / name, target / name)
    return target


@pytest.fixture
def app_factory(monkeypatch):
    from fastapi.testclient import TestClient

    from impact_api.main import create_app

    clients = []

    def start(directory):
        monkeypatch.setenv("IMPACT_CONFIG_FILE", str(directory / "config.json"))
        config = json.loads((directory / "config.json").read_text())
        client = TestClient(create_app(), base_url=config["public_origin"])
        clients.append(client)
        return client, config

    yield start
    for client in clients:
        client.close()


def browser_session(live, actor="author"):
    import httpx

    password = json.loads((live.local / "passwords.json").read_text())[actor]
    with httpx.Client(base_url=live.config["public_origin"], trust_env=False) as browser:
        response = browser.post(
            "/auth/development-login",
            headers={"Origin": live.config["public_origin"]},
            json={"username": actor, "password": password},
        )
        assert response.status_code == 200, response.text
        cookie = browser.cookies.get("impact_dev_session")
        csrf = browser.get("/auth/me").json()["csrf_token"]
    return cookie, csrf


def cursor_kid(cursor):
    raw = cursor.split(".")[0]
    return json.loads(base64.urlsafe_b64decode(raw + "=" * ((-len(raw)) % 4))).get("kid")


def test_values_made_before_rotation_work_during_grace_and_fail_after_retirement(
    live, tmp_path, app_factory, capsys, caplog
):
    caplog.set_level(logging.DEBUG)
    actor = live.fixture["actors"]["author"]
    cookie, csrf = browser_session(live)
    assert csrf.split(".")[0] == key_id("cookie", live.config["cookie_secret"])
    page = live.request(live.path("programmes") + "?limit=1").json()
    cursor = page["next_cursor"]
    assert cursor and cursor_kid(cursor) == key_id("cookie", live.config["cookie_secret"])
    old_token = live.signed(actor["identity_id"])
    legacy_csrf = hmac.new(
        live.config["cookie_secret"].encode(), ("csrf:" + cookie).encode(), hashlib.sha256
    ).hexdigest()

    run = rotated_copy(live, tmp_path)
    code, out, _ = run_script(capsys, "--config-dir", str(run), "rotate", "--family", "all")
    assert code == 0 and {r["family"] for r in out["results"]} == {
        "cookie",
        "invitation",
        "delivery",
        "signing",
    }
    grace, config = app_factory(run)
    assert config["cookie_secret"] != live.config["cookie_secret"]
    assert config["cookie_secret_previous"] == live.config["cookie_secret"]
    session = {"Cookie": "impact_dev_session=" + cookie}
    origin = {"Origin": config["public_origin"]}
    bearer = {"Authorization": "Bearer " + old_token}
    # During grace: the old session's CSRF token (kid-tagged and legacy), the old cursor and the old
    # bearer token all still work; the session itself never depended on the secret.
    for token in [csrf, legacy_csrf]:
        response = grace.post(
            live.path("programmes"),
            headers={**session, **origin, "X-CSRF-Token": token},
            json=cmd({"title": "Grace"}),
        )
        assert response.status_code == 201, response.text
    assert grace.get(live.path("programmes") + "?limit=1&cursor=" + cursor, headers=bearer).status_code == 200
    # New values carry the new kids.
    me = grace.get("/auth/me", headers=session).json()
    assert me["csrf_token"].split(".")[0] == key_id("cookie", config["cookie_secret"])
    new_token = mint(config, run, actor["identity_id"])
    assert json.loads(base64.urlsafe_b64decode(new_token.split(".")[0] + "==="))["kid"] == rsa_key_id(
        (run / "public.pem").read_bytes()
    )
    fresh = grace.get(
        live.path("programmes") + "?limit=1", headers={"Authorization": "Bearer " + new_token}
    ).json()
    assert cursor_kid(fresh["next_cursor"]) == key_id("cookie", config["cookie_secret"])

    code, out, _ = run_script(capsys, "--config-dir", str(run), "retire", "--family", "all", "--all-previous")
    assert code == 0 and all(len(r["retired"]) == 1 for r in out["results"])
    retired, config = app_factory(run)
    assert config["cookie_secret_previous"] == ""
    # After retirement every old value fails; the session and the new values still work.
    for token in [csrf, legacy_csrf]:
        refused = retired.post(
            live.path("programmes"),
            headers={**session, **origin, "X-CSRF-Token": token},
            json=cmd({"title": "Late"}),
        )
        assert (refused.status_code, refused.json().get("reason_code")) == (403, "CSRF_REQUIRED")
    late = retired.get(
        live.path("programmes") + "?limit=1&cursor=" + cursor,
        headers={"Authorization": "Bearer " + new_token},
    )
    assert (late.status_code, late.json()["code"]) == (400, "INVALID_CURSOR")
    assert retired.get(live.path("programmes"), headers=bearer).status_code == 401
    assert (
        retired.get(live.path("programmes"), headers={"Authorization": "Bearer " + new_token}).status_code
        == 200
    )
    me = retired.get("/auth/me", headers=session).json()
    response = retired.post(
        live.path("programmes"),
        headers={**session, **origin, "X-CSRF-Token": me["csrf_token"]},
        json=cmd({"title": "After retirement"}),
    )
    assert response.status_code == 201, response.text
    # No secret value reached a response, a log record of this process or the suite API's log.
    values = [live.config[n] for n in ["cookie_secret", "invitation_secret", "delivery_secret"]]
    values += [config[n] for n in ["cookie_secret", "invitation_secret", "delivery_secret"]]
    logged = "\n".join(r.getMessage() for r in caplog.records) + (live.local / "api.log").read_text()
    for value in values:
        assert value not in logged and value not in late.text and value not in refused.text


def test_delivery_and_invitation_secrets_rotate_for_the_worker(live, tmp_path, app_factory, capsys):
    from test_administration import invitation_token, invite
    from test_worker import deliveries, invitation, make_worker, sink_lines

    from impact_api.worker import empty_summary

    def claimed(worker, tenant, event_id):
        # Claim the due rows, keep this test's row and release every other one at once (attempts
        # restored): a row of an earlier test left leased here would become due in the middle of a
        # later test that expects to be the only sender (test_native_worker's SIGTERM case).
        rows = worker.claim(tenant, empty_summary())
        [mine] = [row for row in rows if str(row["event_id"]) == str(event_id)]
        others = [row for row in rows if row is not mine]
        assert worker.release(tenant, others) == len(others)
        return mine

    tenant = live.fixture["tenant_a"]
    # Two invitations made by the suite API before the rotation.
    body, kept = invite(live, "rotation-" + uuid4().hex[:8] + "@example.test")
    [kept_row] = deliveries(live, kept["object_id"])
    assert sealed_kid(kept_row["recipient_sealed"]) == key_id("delivery", live.config["delivery_secret"])

    run = rotated_copy(live, tmp_path)
    code, _, _ = run_script(capsys, "--config-dir", str(run), "rotate", "--family", "all")
    assert code == 0
    config = json.loads((run / "config.json").read_text())
    worker_config = json.loads((run / "worker.json").read_text())
    assert worker_config["delivery_secret_previous"] == live.config["delivery_secret"]
    grace_keys = {
        name: worker_config[name]
        for name in [
            "invitation_secret",
            "delivery_secret",
            "invitation_secret_previous",
            "delivery_secret_previous",
        ]
    }
    # During grace the worker unseals the old recipient and re-derives the link issued before.
    worker = make_worker(live, **grace_keys)
    worker.process(tenant, claimed(worker, tenant, kept_row["event_id"]), empty_summary())
    [state] = deliveries(live, kept["object_id"])
    assert state["state"] == "SENT", state["last_error_class"]
    [message] = [m for m in sink_lines(worker.s) if m["event_id"] == str(kept_row["event_id"])]
    assert invitation_token(kept) in message["body"]
    # A receipt replay on the rotated API returns the link that was issued, not a re-signed one.
    grace, _ = app_factory(run)
    admin = {"Authorization": "Bearer " + mint(config, run, live.fixture["actors"]["admin"]["identity_id"])}
    replay = grace.post(live.path("member-invitations"), headers=admin, json=body)
    assert replay.status_code == 200, replay.text
    assert invitation_token(replay.json()) == invitation_token(kept)
    # A new invitation is sealed under the new delivery kid and signed with the new secret.
    _, fresh = invite_on(grace, live, admin)
    [fresh_row] = deliveries(live, fresh["object_id"])
    assert sealed_kid(fresh_row["recipient_sealed"]) == key_id("delivery", config["delivery_secret"])
    # After retirement an intent sealed under the old key is unreadable; with only the invitation
    # secret retired, the old link can no longer be derived.
    # Each worker below claims every due row it finds, so each intent is made just before its check.
    _, dropped = invitation(live)
    [dropped_row] = deliveries(live, dropped["object_id"])
    signing_only = make_worker(live, **{**grace_keys, "invitation_secret_previous": ""})
    signing_only.process(tenant, claimed(signing_only, tenant, dropped_row["event_id"]), empty_summary())
    [state] = deliveries(live, dropped["object_id"])
    assert (state["state"], state["last_error_class"]) == ("DEAD", "SIGNING_KEY_MISMATCH")
    _, late = invitation(live)
    [late_row] = deliveries(live, late["object_id"])
    retired = make_worker(
        live, **{**grace_keys, "invitation_secret_previous": "", "delivery_secret_previous": ""}
    )
    retired.process(tenant, claimed(retired, tenant, late_row["event_id"]), empty_summary())
    [state] = deliveries(live, late["object_id"])
    assert (state["state"], state["last_error_class"]) == ("DEAD", "RECIPIENT_UNREADABLE")


def invite_on(client, live, headers):
    from test_administration import command, expiry, role, tenant_scope

    body = command(
        {
            "email": "rotated-" + uuid4().hex[:8] + "@example.test",
            "role_template_id": role(live, "AUTHOR")["object_id"],
            "scope_ids": [tenant_scope(live)],
            "expires_at": expiry(5),
            "membership_expires_at": expiry(20),
            "external": True,
            "reason": "Rotation qualification",
        }
    )
    response = client.post(live.path("member-invitations"), headers=headers, json=body)
    assert response.status_code == 200, response.text
    return body, response.json()


def test_development_tokens_verify_by_kid(live, tmp_path, app_factory, capsys):
    run = rotated_copy(live, tmp_path)
    identity = live.fixture["actors"]["author"]["identity_id"]
    old = live.signed(identity)
    unkeyed = __import__("jwt").encode(
        {
            "iss": live.config["issuer"],
            "sub": identity,
            "aud": live.config["audience"],
            "azp": live.config["client_id"],
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,
            "auth_time": time.time(),
        },
        (live.local / "private.pem").read_bytes(),
        algorithm="RS256",
    )
    code, _, _ = run_script(capsys, "--config-dir", str(run), "rotate", "--family", "signing")
    assert code == 0
    client, config = app_factory(run)
    path = live.path("programmes")
    assert client.get(path, headers={"Authorization": "Bearer " + old}).status_code == 200
    # A token without a kid verifies only with the current key.
    assert client.get(path, headers={"Authorization": "Bearer " + unkeyed}).status_code == 401
    # An unknown kid is refused even when the signature is from a key in grace.
    foreign = __import__("jwt").encode(
        {"sub": identity},
        (live.local / "private.pem").read_bytes(),
        algorithm="RS256",
        headers={"kid": "rs-0000"},
    )
    assert client.get(path, headers={"Authorization": "Bearer " + foreign}).status_code == 401
    keyset = json.loads((run / "signing-keys.json").read_text())
    assert [k["status"] for k in keyset["keys"]] == ["grace"] and "PRIVATE" not in json.dumps(keyset)
