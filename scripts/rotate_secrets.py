"""Rotate and retire the application's own secrets without printing a value (v0.25 part A).

Two targets:

  --env-file PATH    a KEY=VALUE file such as /opt/impact/secrets.env on the staging server
                     (IMPACT_<FAMILY>_SECRET and IMPACT_<FAMILY>_SECRET_PREVIOUS);
  --config-dir DIR   a local run directory such as .local/dev (config.json, worker.json and the
                     development RS256 keypair private.pem/public.pem with signing-keys.json).

Commands:

  status                               families, current kid, grace kids and their grace end
  rotate  --family F [--grace-days N]  a new current secret; the old one joins the grace list
  retire  --family F (--kid K | --all-previous | --expired)
                                       remove grace secrets; values made with them stop working

Families: cookie (CSRF tokens, signed cursors, sealed provider logout hints), invitation (invitation
links), delivery (sealed recipients, recovery-channel codes), signing (development RS256 bearer
tokens; --config-dir only), provisioner (the `impact-provisioner` client secret the API uses at the
identity provider; --env-file only, no grace: the provider holds one secret, which
deploy/rotate-secrets.sh re-aligns through deploy/keycloak_admin.py right after the file is written,
as every deploy/update.sh run does) and all (every family the target holds).

Every write is atomic (temporary file in the same directory, mode 0600, fsync, rename) and
--dry-run writes nothing. A register of kids, never values, is kept beside the target
(<env-file>.keys.json or <config-dir>/keyring-register.json) as rotation evidence. The output is one
JSON document with kids only. --sync-to PATH (env-file mode) copies the changed keys into a second
env file, such as the compose.env the containers are started from.
"""

import argparse
import json
import os
import re
import secrets
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api"))
from impact_api.keyring import (  # noqa: E402
    FAMILIES,
    MIN_SECRET_LENGTH,
    key_id,
    rsa_key_id,
    split_previous,
)

# Grace windows by default: a cookie secret protects CSRF tokens, 15-minute cursors and logout hints
# of sessions that last at most 8 hours; invitation links and receipts live at most 7 days, and a
# resend reuses the recipient sealed for the first intent; development tokens live at most 1 hour.
DEFAULT_GRACE_DAYS = {"cookie": 1, "invitation": 8, "delivery": 8, "signing": 1, "provisioner": 0}
# A shared secret with the identity provider: one value on each side, no grace list, API only.
PROVISIONER = "provisioner"
PROVISIONER_KEY = "IMPACT_PROVISIONER_SECRET"
# The worker holds only these two families; the cookie secret never leaves the API.
WORKER_FAMILIES = ("invitation", "delivery")
ENV_LINE = re.compile(r"^([A-Z0-9_]+)=(.*)$")


class RotationError(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def new_secret():
    # Hex characters only: safe in env files, URLs and comma-separated grace lists.
    secret = secrets.token_hex(48)
    assert len(secret) >= MIN_SECRET_LENGTH
    return secret


def write_private(path, text):
    """Atomic replacement with mode 0600; the previous file stays intact until the rename."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# -- targets -------------------------------------------------------------------------------------


class EnvTarget:
    """A KEY=VALUE file; other lines and keys are preserved in order."""

    def __init__(self, path, sync_to=None):
        self.path = Path(path)
        if not self.path.is_file():
            raise RotationError("env file not found: " + str(self.path))
        self.lines = self.path.read_text().splitlines()
        self.sync_to = Path(sync_to) if sync_to else None
        self.changed = {}
        self.register_path = self.path.with_name(self.path.name + ".keys.json")

    def families(self):
        found = [f for f in FAMILIES if self.get("IMPACT_" + f.upper() + "_SECRET")]
        if self.get(PROVISIONER_KEY):
            found.append(PROVISIONER)
        return found

    def get(self, key):
        value = ""
        for line in self.lines:
            match = ENV_LINE.match(line)
            if match and match.group(1) == key:
                value = match.group(2)
        return value

    def set(self, key, value):
        self.changed[key] = value
        self.lines = set_line(self.lines, key, value)

    def secrets(self, family):
        name = "IMPACT_" + family.upper() + "_SECRET"
        return self.get(name), split_previous(self.get(name + "_PREVIOUS"))

    def store(self, family, current, previous):
        name = "IMPACT_" + family.upper() + "_SECRET"
        self.set(name, current)
        self.set(name + "_PREVIOUS", ",".join(previous))

    def save(self):
        write_private(self.path, "\n".join(self.lines) + "\n")
        if self.sync_to and self.sync_to.exists():
            lines = self.sync_to.read_text().splitlines()
            for key, value in self.changed.items():
                lines = set_line(lines, key, value)
            write_private(self.sync_to, "\n".join(lines) + "\n")

    def touched(self):
        return [str(self.path)] + ([str(self.sync_to)] if self.sync_to and self.sync_to.exists() else [])


def set_line(lines, key, value):
    out, done = [], False
    for line in lines:
        match = ENV_LINE.match(line)
        if match and match.group(1) == key:
            if not done:
                out.append(key + "=" + value)
                done = True
            continue
        out.append(line)
    if not done:
        out.append(key + "=" + value)
    return out


class ConfigTarget:
    """A local run directory: config.json (API), worker.json (worker) and the development keypair."""

    def __init__(self, directory):
        self.dir = Path(directory)
        self.config_path = self.dir / "config.json"
        if not self.config_path.is_file():
            raise RotationError("config.json not found in " + str(self.dir))
        self.config = json.loads(self.config_path.read_text())
        self.worker_path = self.dir / "worker.json"
        self.worker = json.loads(self.worker_path.read_text()) if self.worker_path.is_file() else None
        self.register_path = self.dir / "keyring-register.json"
        self.keyset_path = self.dir / "signing-keys.json"
        self.pending_keys = None

    def families(self):
        found = [f for f in FAMILIES if self.config.get(f + "_secret")]
        if self.config.get("dev_auth") and (self.dir / "private.pem").exists():
            found.append("signing")
        return found

    def secrets(self, family):
        return self.config.get(family + "_secret", ""), split_previous(
            self.config.get(family + "_secret_previous", "")
        )

    def store(self, family, current, previous):
        self.config[family + "_secret"] = current
        self.config[family + "_secret_previous"] = ",".join(previous)
        if self.worker is not None and family in WORKER_FAMILIES:
            self.worker[family + "_secret"] = current
            self.worker[family + "_secret_previous"] = ",".join(previous)

    # Development RS256 signing keys: private.pem/public.pem are the current key; signing-keys.json
    # lists the public keys still accepted by kid during their grace window.
    def keyset(self):
        if self.pending_keys is not None:
            return self.pending_keys
        if self.keyset_path.exists():
            return json.loads(self.keyset_path.read_text())
        return {"keys": []}

    def signing_current(self):
        return rsa_key_id((self.dir / "public.pem").read_bytes())

    def save(self):
        write_private(self.config_path, json.dumps(self.config, indent=2))
        if self.worker is not None:
            write_private(self.worker_path, json.dumps(self.worker, indent=2))
        if self.pending_keys is not None:
            write_private(self.keyset_path, json.dumps(self.pending_keys, indent=2))

    def touched(self):
        return [str(self.config_path)] + ([str(self.worker_path)] if self.worker is not None else [])


# -- register (kids and dates only) --------------------------------------------------------------


def load_register(target):
    path = target.register_path
    if path.exists():
        return json.loads(path.read_text())
    return {"format": "impact-keyring-register-v1", "keys": {}, "events": []}


def note(register, event, family, kid, at, **extra):
    register["events"].append({"event": event, "family": family, "kid": kid, "at": iso(at), **extra})


def actor():
    return os.environ.get("SUDO_USER") or os.environ.get("USER") or "unknown"


# -- commands ------------------------------------------------------------------------------------


def status(target, register):
    families = {}
    for family in target.families():
        if family == "signing":
            current = target.signing_current()
            previous = [k["kid"] for k in target.keyset()["keys"] if k.get("status") != "retired"]
        elif family == PROVISIONER:
            current, previous = key_id(PROVISIONER, target.get(PROVISIONER_KEY)), []
        else:
            secret, grace = target.secrets(family)
            current = key_id(family, secret)
            previous = [key_id(family, s) for s in grace]
        families[family] = {
            "current": {"kid": current, **register["keys"].get(family + ":" + current, {})},
            "grace": [{"kid": kid, **register["keys"].get(family + ":" + kid, {})} for kid in previous],
        }
    return families


def rotate(target, register, family, grace_days, at, reason):
    grace_until = iso(at + timedelta(days=grace_days))
    if family == "signing":
        return rotate_signing(target, register, grace_until, at, reason)
    if family == PROVISIONER:
        return rotate_provisioner(target, register, at, reason)
    current, previous = target.secrets(family)
    if not current:
        raise RotationError("no current " + family + " secret to rotate")
    fresh = new_secret()
    old_kid, new_kid = key_id(family, current), key_id(family, fresh)
    target.store(family, fresh, [current] + previous)
    register["keys"].setdefault(family + ":" + old_kid, {})["grace_until"] = grace_until
    register["keys"][family + ":" + new_kid] = {"since": iso(at)}
    note(
        register,
        "rotate",
        family,
        new_kid,
        at,
        replaced=old_kid,
        grace_until=grace_until,
        by=actor(),
        reason=reason,
    )
    return {"family": family, "new_kid": new_kid, "grace_kid": old_kid, "grace_until": grace_until}


def rotate_signing(target, register, grace_until, at, reason):
    if not isinstance(target, ConfigTarget):
        raise RotationError("the signing family exists only in a local run directory (--config-dir)")
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    old_public = (target.dir / "public.pem").read_bytes()
    old_kid = rsa_key_id(old_public)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode()
    public = (
        key.public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        .decode()
    )
    new_kid = rsa_key_id(public)
    keyset = target.keyset()
    keyset["keys"] = [k for k in keyset["keys"] if k["kid"] != old_kid] + [
        {"kid": old_kid, "public_pem": old_public.decode(), "status": "grace", "grace_until": grace_until}
    ]
    target.pending_keys = keyset
    target.pending_pair = (private, public)
    target.config["dev_signing_keys"] = str(target.keyset_path)
    target.config["dev_public_key"] = str(target.dir / "public.pem")
    register["keys"].setdefault("signing:" + old_kid, {})["grace_until"] = grace_until
    register["keys"]["signing:" + new_kid] = {"since": iso(at)}
    note(
        register,
        "rotate",
        "signing",
        new_kid,
        at,
        replaced=old_kid,
        grace_until=grace_until,
        by=actor(),
        reason=reason,
    )
    return {"family": "signing", "new_kid": new_kid, "grace_kid": old_kid, "grace_until": grace_until}


def rotate_provisioner(target, register, at, reason):
    """A new client secret for the identity provider's `impact-provisioner` client. The file is the
    source of truth: deploy/rotate-secrets.sh re-aligns the provider to it at once and every
    deploy/update.sh run does the same, so a crash between the two leaves nothing to repair by hand.
    No grace: the provider holds one secret, and the API reads it at start."""
    if not isinstance(target, EnvTarget):
        raise RotationError("the provisioner family exists only in an env file (--env-file)")
    current = target.get(PROVISIONER_KEY)
    if not current:
        raise RotationError("no current provisioner secret to rotate")
    fresh = new_secret()
    old_kid, new_kid = key_id(PROVISIONER, current), key_id(PROVISIONER, fresh)
    target.set(PROVISIONER_KEY, fresh)
    register["keys"].setdefault(PROVISIONER + ":" + old_kid, {})["retired_at"] = iso(at)
    register["keys"][PROVISIONER + ":" + new_kid] = {"since": iso(at)}
    note(
        register,
        "rotate",
        PROVISIONER,
        new_kid,
        at,
        replaced=old_kid,
        grace_until=None,
        by=actor(),
        reason=reason,
    )
    return {"family": PROVISIONER, "new_kid": new_kid, "grace_kid": None, "grace_until": None}


def retire(target, register, family, kid, all_previous, expired, at, reason):
    if family == PROVISIONER:
        raise RotationError("the provisioner family keeps no grace secret: rotate it instead")
    if family == "signing":
        keyset = target.keyset()
        chosen = [
            k["kid"]
            for k in keyset["keys"]
            if k.get("status") != "retired"
            and selected(register, family, k["kid"], kid, all_previous, expired, at)
        ]
        # A retired development key is removed from the key set entirely; nothing verifies with it.
        keyset["keys"] = [k for k in keyset["keys"] if k["kid"] not in chosen]
        target.pending_keys = keyset
    else:
        current, previous = target.secrets(family)
        chosen = [
            key_id(family, s)
            for s in previous
            if selected(register, family, key_id(family, s), kid, all_previous, expired, at)
        ]
        target.store(family, current, [s for s in previous if key_id(family, s) not in chosen])
    if kid and kid not in chosen:
        raise RotationError("kid " + kid + " is not a grace key of the " + family + " family")
    for retired in chosen:
        register["keys"].setdefault(family + ":" + retired, {})["retired_at"] = iso(at)
        note(register, "retire", family, retired, at, by=actor(), reason=reason)
    return {"family": family, "retired": chosen}


def selected(register, family, candidate, kid, all_previous, expired, at):
    if all_previous:
        return True
    if kid:
        return candidate == kid
    if expired:
        until = register["keys"].get(family + ":" + candidate, {}).get("grace_until")
        return bool(until) and datetime.fromisoformat(until.replace("Z", "+00:00")) <= at
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--env-file")
    where.add_argument("--config-dir")
    parser.add_argument("--sync-to", help="env-file mode: also update these keys in a second env file")
    parser.add_argument("--dry-run", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    rot = commands.add_parser("rotate")
    rot.add_argument("--family", required=True, choices=list(FAMILIES) + ["signing", PROVISIONER, "all"])
    rot.add_argument("--grace-days", type=float)
    rot.add_argument("--reason", default="")
    ret = commands.add_parser("retire")
    ret.add_argument("--family", required=True, choices=list(FAMILIES) + ["signing", PROVISIONER, "all"])
    choice = ret.add_mutually_exclusive_group(required=True)
    choice.add_argument("--kid")
    choice.add_argument("--all-previous", action="store_true")
    choice.add_argument("--expired", action="store_true")
    ret.add_argument("--reason", default="")
    args = parser.parse_args(argv)
    try:
        if args.sync_to and not args.env_file:
            raise RotationError("--sync-to needs --env-file")
        target = EnvTarget(args.env_file, args.sync_to) if args.env_file else ConfigTarget(args.config_dir)
        register = load_register(target)
        at = now()
        if args.command == "status":
            print(
                json.dumps(
                    {
                        "target": "env-file" if args.env_file else "config-dir",
                        "families": status(target, register),
                    },
                    indent=2,
                )
            )
            return 0
        available = target.families()
        families = available if args.family == "all" else [args.family]
        missing = [f for f in families if f not in available]
        if missing:
            raise RotationError("not configured in this target: " + ", ".join(missing))
        if args.command == "rotate":
            results = [
                rotate(
                    target,
                    register,
                    family,
                    args.grace_days if args.grace_days is not None else DEFAULT_GRACE_DAYS[family],
                    at,
                    args.reason,
                )
                for family in families
            ]
        else:
            results = [
                retire(target, register, family, args.kid, args.all_previous, args.expired, at, args.reason)
                for family in families
                if not (family == PROVISIONER and args.family == "all")
            ]
        if not args.dry_run:
            pair = getattr(target, "pending_pair", None)
            if pair:
                # The new keypair is written before the configuration that names its key set; the old
                # public key is already in the pending key set, so a crash in between loses nothing.
                write_private(target.keyset_path, json.dumps(target.pending_keys, indent=2))
                write_private(target.dir / "private.pem", pair[0])
                write_private(target.dir / "public.pem", pair[1])
            target.save()
            write_private(target.register_path, json.dumps(register, indent=2))
        print(
            json.dumps(
                {
                    "command": args.command,
                    "dry_run": args.dry_run,
                    "results": results,
                    "files": [] if args.dry_run else target.touched(),
                    "restart_required": [] if args.dry_run else restart_for(families),
                    # The shell wrapper re-aligns the identity provider for these families.
                    "provider_realign": [PROVISIONER]
                    if PROVISIONER in families and args.command == "rotate"
                    else [],
                },
                indent=2,
            )
        )
        return 0
    except (RotationError, OSError, ValueError, KeyError) as error:
        # The message names files, families or kids only; a value never reaches an exception here.
        print(json.dumps({"error": type(error).__name__, "message": str(error)[:300]}), file=sys.stderr)
        return 2


def restart_for(families):
    services = {"api"}
    if any(f in WORKER_FAMILIES for f in families):
        services.add("worker")
    return sorted(services)


if __name__ == "__main__":
    sys.exit(main())
