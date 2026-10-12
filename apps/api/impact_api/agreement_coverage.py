"""US-CM-09 one organisation agreement/DPA bundle for every deployment."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from psycopg.types.json import Jsonb
from .contracts import validate
from .domain import DomainError, unavailable
from .sponsored_access import record_audit
from .store import authorize, context, hash_data


def record_deployment_coverage(c, tenant, plan_id, deployment_id, solution_id, principal, observed):
    agreement = c.execute(
        "SELECT r.* FROM impact.organisation_agreement_current x JOIN impact.organisation_agreement_revision r USING(tenant_id,revision_id) WHERE x.tenant_id=%s AND r.effective_on<=%s::date FOR SHARE OF r",
        (tenant, observed),
    ).fetchone()
    if not agreement:
        raise DomainError("INVALID_STATE", 409, reason="AGREEMENT_BUNDLE_REQUIRED")
    c.execute(
        "INSERT INTO impact.solution_agreement_coverage VALUES(%s,%s,%s,%s,%s,'MASTER_AGREEMENT_FLOW_DOWN',false,false,%s,%s)",
        (
            tenant,
            deployment_id,
            plan_id,
            solution_id,
            agreement["revision_id"],
            principal,
            observed,
        ),
    )
    return str(agreement["revision_id"])


class AgreementCoverage:
    def __init__(self, service):
        self.service = service

    def configure(self, identity, tenant, body, correlation):
        validate("OrganisationAgreementConfigure", body)
        fingerprint = hash_data(["configure_organisation_agreement", body])
        observed = datetime.now(timezone.utc)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "configure_organisation_agreement", hidden=True)
            old = c.execute(
                "SELECT * FROM impact.operation_receipt WHERE tenant_id=%s AND actor_id=%s AND command_type='configure_organisation_agreement' AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if old:
                if bytes(old["payload_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return old["outcome"]
            revision_id = str(uuid4())
            c.execute(
                "INSERT INTO impact.organisation_agreement_revision VALUES(%s,%s,%s,%s,%s,'ALL_PLATFORM_SOLUTIONS','MASTER_AGREEMENT_FLOW_DOWN',%s,%s)",
                (
                    tenant,
                    revision_id,
                    body["master_agreement_reference"].strip(),
                    body["dpa_reference"].strip(),
                    body["effective_on"],
                    ctx.principal_id,
                    observed,
                ),
            )
            c.execute(
                "INSERT INTO impact.organisation_agreement_current VALUES(%s,%s) ON CONFLICT(tenant_id) DO UPDATE SET revision_id=excluded.revision_id",
                (tenant, revision_id),
            )
            outcome = {
                "revision_id": revision_id,
                "master_agreement_reference": body["master_agreement_reference"].strip(),
                "dpa_reference": body["dpa_reference"].strip(),
                "effective_on": body["effective_on"],
                "coverage_scope": "ALL_PLATFORM_SOLUTIONS",
                "partner_terms_mode": "MASTER_AGREEMENT_FLOW_DOWN",
                "separate_contract_required": False,
                "separate_dpa_required": False,
            }
            record_audit(c, ctx, "agreement.bundle.configure", revision_id, observed, correlation)
            c.execute(
                "INSERT INTO impact.operation_receipt VALUES(%s,%s,'configure_organisation_agreement',%s,%s,'SUCCEEDED',%s,%s)",
                (
                    tenant,
                    ctx.principal_id,
                    body["operation_id"],
                    fingerprint,
                    Jsonb(outcome),
                    observed + timedelta(days=7),
                ),
            )
            return outcome

    def read(self, identity, tenant):
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "read_organisation_agreements", hidden=True)
            agreement = c.execute(
                "SELECT r.* FROM impact.organisation_agreement_current x JOIN impact.organisation_agreement_revision r USING(tenant_id,revision_id) WHERE x.tenant_id=%s",
                (tenant,),
            ).fetchone()
            if not agreement:
                unavailable()
            rows = c.execute(
                "SELECT * FROM impact.solution_agreement_coverage WHERE tenant_id=%s ORDER BY deployment_attestation_id",
                (tenant,),
            ).fetchall()
            return {
                "revision_id": str(agreement["revision_id"]),
                "master_agreement_reference": agreement["master_agreement_reference"],
                "dpa_reference": agreement["dpa_reference"],
                "effective_on": agreement["effective_on"].isoformat(),
                "coverage_scope": agreement["coverage_scope"],
                "partner_terms_mode": agreement["partner_terms_mode"],
                "separate_contract_required": False,
                "separate_dpa_required": False,
                "deployments": [
                    {
                        "deployment_attestation_id": str(row["deployment_attestation_id"]),
                        "plan_id": str(row["plan_id"]),
                        "solution_id": row["solution_id"],
                        "agreement_revision_id": str(row["agreement_revision_id"]),
                    }
                    for row in rows
                ],
            }
