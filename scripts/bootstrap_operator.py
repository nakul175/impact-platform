"""First platform operator and deployment qualification of a real (non-fixture) deployment.

A deployment starts with no identities, no operators and no qualified deployment record; the
control plane cannot create any of them over HTTP (migration 0013: "Provisioned by deployment
administration, never writable by HTTP runtime roles"). This script is that deployment
administration step. It runs as the migration login (`impact_migrator`, acting as `impact_owner`,
IMPACT_MIGRATION_DSN) inside the application image, and has two commands:

    identity   register one identity-provider account (issuer + subject) as a platform identity
               with no authority at all; idempotent. Everyone who will sign in needs one, because
               the platform never creates identities from a provider login.
    operator   register the identity (as above) and make it the FIRST platform operator, and
               record the deployment qualification the control plane checks tenant requests
               against. Refused (exit 3) when any other operator row exists; re-running it for
               the same identity changes nothing and exits 0.

What it never does: create a tenant, a membership, a grant, custody or recovery evidence; those
follow the reviewed control-plane procedures (see docs/current/DEPLOYMENT-GUIDE.md). The evidence
of the bootstrap is the operator row's authority reference plus the JSON printed here (which the
deployment log keeps); `platform_event` cannot hold it because every event belongs to a tenant.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate import assume_owner  # noqa: E402

ALREADY = 0
REFUSED = 3
LOCK = "impact-deployment-bootstrap"


class Refused(RuntimeError):
    pass


def validate(issuer, subject):
    if not issuer.startswith("https://") and not issuer.startswith("http://127.0.0.1"):
        raise ValueError("The issuer must be an HTTPS URL")
    if not subject or len(subject) > 255 or subject.strip() != subject:
        raise ValueError("The provider subject is required")


def ensure_identity(c, issuer, subject):
    """The identity for (issuer, subject): the existing row, or a new identity that is also its own
    natural person. Returns (row, created)."""
    row = c.execute(
        "SELECT identity_id,natural_identity_id FROM impact.auth_identity WHERE issuer=%s AND provider_subject=%s",
        (issuer, subject),
    ).fetchone()
    if row:
        return row, False
    identity = str(uuid4())
    c.execute(
        "INSERT INTO impact.auth_identity(identity_id,issuer,provider_subject,natural_identity_id) VALUES(%s,%s,%s,%s)",
        (identity, issuer, subject, str(uuid4())),
    )
    return c.execute(
        "SELECT identity_id,natural_identity_id FROM impact.auth_identity WHERE identity_id=%s", (identity,)
    ).fetchone(), True


def ensure_qualification(c, environment, issuer, required_acr, region, privacy, recovery, retention, days):
    """An active, unexpired deployment qualification for exactly this environment, issuer, ACR,
    region and privacy reference; created when none matches."""
    row = c.execute(
        "SELECT * FROM impact.deployment_qualification WHERE active AND valid_until>now() AND environment=%s AND issuer=%s AND required_acr=%s AND region=%s AND privacy_reference=%s ORDER BY valid_until DESC LIMIT 1",
        (environment, issuer, required_acr, region, privacy),
    ).fetchone()
    if row:
        return row, False
    qualification = str(uuid4())
    c.execute(
        "INSERT INTO impact.deployment_qualification(qualification_id,revision_id,environment,region,issuer,required_acr,privacy_reference,recovery_reference,retention_max_days,valid_until,active) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true)",
        (
            qualification,
            str(uuid4()),
            environment,
            region,
            issuer,
            required_acr,
            privacy,
            recovery,
            retention,
            datetime.now(timezone.utc) + timedelta(days=days),
        ),
    )
    return c.execute(
        "SELECT * FROM impact.deployment_qualification WHERE qualification_id=%s", (qualification,)
    ).fetchone(), True


def register_identity(c, issuer, subject):
    validate(issuer, subject)
    row, created = ensure_identity(c, issuer, subject)
    return {"identity_id": str(row["identity_id"]), "created": created}


def bootstrap_operator(c, args):
    validate(args.issuer, args.subject)
    if not args.reference.strip() or len(args.reference) > 300:
        raise ValueError("An authority reference of 1-300 characters is required")
    if args.environment not in {"staging", "production"}:
        raise ValueError("Only a staging or production deployment is bootstrapped this way")
    c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (LOCK,))
    identity, identity_created = ensure_identity(c, args.issuer, args.subject)
    operators = c.execute("SELECT identity_id,active,expires_at FROM impact.platform_operator").fetchall()
    others = [o for o in operators if o["identity_id"] != identity["identity_id"]]
    if others:
        raise Refused("A platform operator already exists; the first-operator bootstrap is refused")
    existing = next((o for o in operators if o["identity_id"] == identity["identity_id"]), None)
    if existing is None:
        expires = datetime.now(timezone.utc) + timedelta(days=args.operator_days)
        c.execute(
            "INSERT INTO impact.platform_operator(identity_id,active,expires_at,authority_reference) VALUES(%s,true,%s,%s)",
            (identity["identity_id"], expires, args.reference.strip()),
        )
    else:
        expires = existing["expires_at"]
    qualification, qualification_created = ensure_qualification(
        c,
        args.environment,
        args.issuer,
        args.required_acr,
        args.region,
        args.privacy_reference,
        args.recovery_reference,
        args.retention_max_days,
        args.qualification_days,
    )
    return {
        "outcome": "created" if existing is None else "already-bootstrapped",
        "identity_id": str(identity["identity_id"]),
        "identity_created": identity_created,
        "operator_expires_at": expires.astimezone(timezone.utc).isoformat(),
        "operator_active": True if existing is None else bool(existing["active"]),
        "qualification_id": str(qualification["qualification_id"]),
        "qualification_created": qualification_created,
        "qualification_valid_until": qualification["valid_until"].astimezone(timezone.utc).isoformat(),
        "environment": args.environment,
        "region": args.region,
        "privacy_reference": args.privacy_reference,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("identity", "operator"):
        s = sub.add_parser(name)
        s.add_argument("--issuer", required=True, help="Issuer URL of the realm, exactly as in tokens")
        s.add_argument("--subject", required=True, help="The provider account's subject (Keycloak user ID)")
    op = sub.choices["operator"]
    op.add_argument("--environment", default=os.environ.get("IMPACT_ENVIRONMENT", "staging"))
    op.add_argument("--required-acr", required=True)
    op.add_argument("--reference", required=True, help="Why this person is the first operator (<=300)")
    op.add_argument("--region", required=True)
    op.add_argument("--privacy-reference", required=True)
    op.add_argument("--recovery-reference", required=True)
    op.add_argument("--retention-max-days", type=int, default=3650)
    op.add_argument("--operator-days", type=int, default=365)
    op.add_argument("--qualification-days", type=int, default=365)
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    dsn = os.environ.get("IMPACT_MIGRATION_DSN")
    if not dsn:
        raise RuntimeError("IMPACT_MIGRATION_DSN (the migration login) is required")
    try:
        with psycopg.connect(dsn, autocommit=True, row_factory=dict_row, prepare_threshold=None) as c:
            c.row_factory = psycopg.rows.tuple_row
            assume_owner(c)
            c.row_factory = dict_row
            with c.transaction():
                if args.command == "identity":
                    result = register_identity(c, args.issuer, args.subject)
                else:
                    result = bootstrap_operator(c, args)
    except Refused as e:
        print(json.dumps({"outcome": "refused", "reason": str(e)}))
        return REFUSED
    print(json.dumps(result, sort_keys=True))
    return ALREADY


if __name__ == "__main__":
    sys.exit(main())
