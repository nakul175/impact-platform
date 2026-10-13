"""Snapshot-bound report proposals with immutable human review ancestry."""

from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .reporting import BARE_NUMBER, BINDING_TOKEN
from .service import revision
from .store import authorize, context, hash_data, load

USE_CASE = "REPORT_DRAFT"
PURPOSE = "SNAPSHOT_BOUND_REPORT_DRAFT"


def section_map(sections):
    return {item["section_code"]: item for item in sections}


class AIReportDrafting:
    def __init__(self, service, reporting, destination, configuration):
        self.service = service
        self.reporting = reporting
        self.destination = destination
        self.configuration = configuration

    def create(self, identity, tenant, body):
        fingerprint = hash_data(["create_ai_report_draft", body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_report_draft", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_report_draft WHERE tenant_id=%s AND requested_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._draft_view(replay)
            snapshot = load(c, ctx, body["snapshot_id"], "Snapshot", "snapshots.read")
            if snapshot["lifecycle_state"] != "Locked":
                raise DomainError("INVALID_STATE", 409, reason="LOCKED_SNAPSHOT_REQUIRED")
            if str(snapshot["head_revision"]) != body["snapshot_revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="REPORT_SNAPSHOT_CHANGED")
            template = revision(
                c,
                ctx,
                body["template_revision_id"],
                "ReportTemplate",
                "report-templates.read",
            )
            template_head = load(c, ctx, template["object_id"], "ReportTemplate", "report-templates.read")
            if (
                template_head["lifecycle_state"] not in {"Approved", "Active"}
                or str(template_head["head_revision"]) != body["template_revision_id"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="APPROVED_REPORT_TEMPLATE_REQUIRED")
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                snapshot["classification"],
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            inputs = section_map(body["section_inputs"])
            if len(inputs) != len(body["section_inputs"]):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_REPORT_SECTION")
            template_sections = section_map(template["payload"].get("sections", []))
            if not set(inputs) <= set(template_sections):
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_SECTION_UNKNOWN")
            prior, generation = self._prior(c, tenant, ctx, body, snapshot, template)
            regenerate = set(body["regenerated_section_codes"])
            if not regenerate <= set(template_sections):
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_SECTION_UNKNOWN")
            if prior is None and regenerate:
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_REGENERATION_WITHOUT_PRIOR")
            if prior is not None and not regenerate:
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_REVIEWED_DIFF_REQUIRED")
            proposed, gaps, caveats = self._propose(
                c, ctx, snapshot, template_sections, inputs, prior, regenerate
            )
            report_data = {
                "template_version": body["template_revision_id"],
                "snapshot_id": body["snapshot_id"],
                "language": body["language"],
                "audience_class": "INTERNAL",
                "sections": proposed,
            }
            self.reporting.reconcile(c, ctx, report_data, complete=False)
            draft_id = uuid4()
            c.execute(
                "INSERT INTO impact.ai_report_draft VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    draft_id,
                    UUID(body["snapshot_id"]),
                    UUID(body["snapshot_revision_id"]),
                    UUID(body["template_revision_id"]),
                    body["policy_version"],
                    body["language"],
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                    generation,
                    UUID(body["prior_draft_id"]) if body["prior_draft_id"] else None,
                    Jsonb(sorted(regenerate)),
                    Jsonb(proposed),
                    Jsonb(gaps),
                    Jsonb(caveats),
                ),
            )
            return self._view(draft_id, generation, proposed, gaps, caveats, body["prior_draft_id"])

    def review(self, identity, tenant, draft_id, body):
        fingerprint = hash_data(["review_ai_report_draft", str(draft_id), body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "review_ai_report_draft", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_report_draft_review WHERE tenant_id=%s AND reviewed_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint or str(replay["draft_id"]) != str(draft_id):
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._review_view(replay)
            draft = c.execute(
                "SELECT * FROM impact.ai_report_draft WHERE tenant_id=%s AND draft_id=%s FOR UPDATE",
                (tenant, draft_id),
            ).fetchone()
            if not draft:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_report_draft_review WHERE tenant_id=%s AND draft_id=%s",
                (tenant, draft_id),
            ).fetchone():
                raise DomainError("CONFLICT_OPERATION", 409, reason="REPORT_DRAFT_ALREADY_REVIEWED")
            self._recheck_sources(c, ctx, draft)
            final_sections = body["final_sections"]
            final_by_code = section_map(final_sections)
            if len(final_by_code) != len(final_sections):
                raise DomainError("VALIDATION_FAILED", reason="DUPLICATE_REPORT_SECTION")
            if set(final_by_code) != set(section_map(draft["proposed_sections"])):
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_SECTION_SET_CHANGED")
            if body["mandatory_caveat_codes"] != draft["mandatory_caveat_codes"]:
                raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_CAVEAT_REMOVED")
            corrections = []
            proposed = section_map(draft["proposed_sections"])
            for section in final_sections:
                original = proposed[section["section_code"]]
                if {key: value for key, value in section.items() if key != "narrative"} != {
                    key: value for key, value in original.items() if key != "narrative"
                }:
                    raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_REVIEW_WORDING_ONLY")
                if section != original:
                    corrections.append(
                        {
                            "section_code": section["section_code"],
                            "before": original,
                            "after": section,
                        }
                    )
            report_data = {
                "template_version": str(draft["template_revision_id"]),
                "snapshot_id": str(draft["snapshot_id"]),
                "language": draft["language"],
                "audience_class": "INTERNAL",
                "sections": final_sections,
            }
            self.reporting.reconcile(c, ctx, report_data, complete=False)
            self._reject_unbound_numbers(final_sections)
            c.execute(
                "INSERT INTO impact.ai_report_draft_review VALUES(%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    draft_id,
                    Jsonb(corrections),
                    Jsonb(final_sections),
                    Jsonb(body["mandatory_caveat_codes"]),
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            )
            return {
                "draft_id": str(draft_id),
                "state": "HUMAN_REVIEWED",
                "corrections": corrections,
                "final_sections": final_sections,
                "ai_origin_retained": True,
                "domain_objects_changed": False,
            }

    def _prior(self, c, tenant, ctx, body, snapshot, template):
        if not body["prior_draft_id"]:
            return None, 1
        prior = c.execute(
            "SELECT d.*,r.final_sections FROM impact.ai_report_draft d JOIN impact.ai_report_draft_review r "
            "ON r.tenant_id=d.tenant_id AND r.draft_id=d.draft_id WHERE d.tenant_id=%s AND d.draft_id=%s",
            (tenant, body["prior_draft_id"]),
        ).fetchone()
        if not prior:
            raise DomainError("VALIDATION_FAILED", reason="REPORT_DRAFT_REVIEW_REQUIRED")
        self._recheck_sources(c, ctx, prior)
        if (
            str(prior["snapshot_id"]) != str(snapshot["object_id"])
            or str(prior["snapshot_revision_id"]) != str(snapshot["head_revision"])
            or str(prior["template_revision_id"]) != str(template["revision_id"])
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="REPORT_DRAFT_CONTEXT_CHANGED")
        return prior, prior["generation"] + 1

    def _propose(self, c, ctx, snapshot, template_sections, inputs, prior, regenerate):
        prior_final = section_map(prior["final_sections"]) if prior else {}
        proposed, gaps, caveats = [], [], []
        for code, template in template_sections.items():
            caveats.extend(template.get("caveat_codes", []))
            if prior and code not in regenerate:
                if code in prior_final:
                    proposed.append(prior_final[code])
                continue
            item = inputs.get(code)
            if not item:
                if template.get("required"):
                    gaps.append({"section_code": code, "reason": "REQUIRED_SECTION_MISSING"})
                continue
            missing_bindings = sorted(
                set(template.get("required_binding_codes", []))
                - {binding["binding_code"] for binding in item["bindings"]}
            )
            if missing_bindings:
                gaps.append(
                    {
                        "section_code": code,
                        "reason": "REQUIRED_BINDINGS_MISSING",
                        "binding_codes": missing_bindings,
                    }
                )
            proposed.append(
                {
                    "section_code": code,
                    "heading": template["heading"],
                    "narrative": item["narrative"],
                    "bindings": item["bindings"],
                    "evidence_revisions": item["evidence_revisions"],
                    "charts": [],
                }
            )
        self._reject_unbound_numbers(proposed)
        return proposed, gaps, sorted(set(caveats))

    @staticmethod
    def _reject_unbound_numbers(sections):
        for section in sections:
            codes = {item["binding_code"] for item in section["bindings"]}
            if any(token not in codes for token in BINDING_TOKEN.findall(section["narrative"])):
                raise DomainError("VALIDATION_FAILED", reason="UNKNOWN_NARRATIVE_BINDING")
            if BARE_NUMBER.search(BINDING_TOKEN.sub("", section["narrative"])):
                raise DomainError("VALIDATION_FAILED", reason="UNBOUND_NARRATIVE_NUMBER")

    def _recheck_sources(self, c, ctx, draft):
        snapshot = load(c, ctx, draft["snapshot_id"], "Snapshot", "snapshots.read")
        if snapshot["lifecycle_state"] != "Locked" or str(snapshot["head_revision"]) != str(
            draft["snapshot_revision_id"]
        ):
            raise DomainError("CONFLICT_VERSION", 409, reason="REPORT_SNAPSHOT_CHANGED")
        template = revision(c, ctx, draft["template_revision_id"], "ReportTemplate", "report-templates.read")
        head = load(c, ctx, template["object_id"], "ReportTemplate", "report-templates.read")
        if str(head["head_revision"]) != str(draft["template_revision_id"]):
            raise DomainError("CONFLICT_VERSION", 409, reason="REPORT_TEMPLATE_CHANGED")
        policy = ai_policy.in_force(c, ctx.tenant_id)
        if policy["version"] != draft["policy_version"]:
            raise DomainError("CONFLICT_VERSION", 409, reason="AI_POLICY_CHANGED")
        ai_policy.require(
            policy,
            USE_CASE,
            draft["policy_version"],
            snapshot["classification"],
            self.destination,
            draft["language"],
            (),
            PURPOSE,
        )
        require_available(c, ctx.tenant_id, USE_CASE, self.destination, self.configuration)

    @staticmethod
    def _view(draft_id, generation, sections, gaps, caveats, prior):
        return {
            "draft_id": str(draft_id),
            "generation": generation,
            "prior_draft_id": prior,
            "proposed_sections": sections,
            "evidence_gaps": gaps,
            "mandatory_caveat_codes": caveats,
            "ai_origin": True,
            "domain_objects_changed": False,
        }

    @staticmethod
    def _draft_view(row):
        return AIReportDrafting._view(
            row["draft_id"],
            row["generation"],
            row["proposed_sections"],
            row["evidence_gaps"],
            row["mandatory_caveat_codes"],
            str(row["prior_draft_id"]) if row["prior_draft_id"] else None,
        )

    @staticmethod
    def _review_view(row):
        return {
            "draft_id": str(row["draft_id"]),
            "state": "HUMAN_REVIEWED",
            "corrections": row["corrections"],
            "final_sections": row["final_sections"],
            "ai_origin_retained": True,
            "domain_objects_changed": False,
        }
