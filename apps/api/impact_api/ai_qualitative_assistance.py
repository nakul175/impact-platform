"""Source-verifiable qualitative suggestions and individual governed review."""

import hashlib
from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from . import ai_policy
from .ai_runtime_activation import activated
from .ai_safety import require_available
from .domain import DomainError
from .service import revision
from .store import audit, authorize, context, hash_data, load, write

USE_CASE = "QUALITATIVE_ASSISTANCE"
PURPOSE = "QUALITATIVE_SUGGESTION"


class AIQualitativeAssistance:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def create(self, identity, tenant, body, correlation):
        fingerprint = hash_data(["create_ai_qualitative_run", body])
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "create_ai_qualitative_run", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_qualitative_run WHERE tenant_id=%s AND requested_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._stored(c, replay)
            codebook = revision(
                c,
                ctx,
                body["codebook_revision_id"],
                "Codebook",
                "qualitative-extracts.read",
            )
            if str(codebook["object_id"]) != body["codebook_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            codebook_head = load(
                c,
                ctx,
                codebook["object_id"],
                "Codebook",
                "qualitative-extracts.read",
            )
            if (
                codebook_head["lifecycle_state"] not in {"Approved", "Active"}
                or str(codebook_head["head_revision"]) != body["codebook_revision_id"]
            ):
                raise DomainError("INVALID_STATE", 409, reason="APPROVED_CODEBOOK_REQUIRED")
            policy = ai_policy.in_force(c, tenant)
            source_rows = self._sources(c, ctx, body["sources"])
            highest = max(
                source_rows.values(),
                key=lambda item: ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"].index(
                    item["classification"]
                ),
            )["classification"]
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                highest,
                self.destination,
                body["language"],
                (),
                PURPOSE,
                activated_use_cases=activated(self.service),
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            allowed_codes = {
                str(item["code"])
                for item in codebook["payload"].get("codes", [])
                if isinstance(item, dict) and item.get("code")
            }
            if not allowed_codes:
                raise DomainError("VALIDATION_FAILED", reason="CODEBOOK_CODES_REQUIRED")
        contents = {}
        for source in body["sources"]:
            artifact = self.service.evidence.content(
                identity,
                tenant,
                UUID(source["object_id"]),
                UUID(source["revision_id"]),
                correlation,
            )
            if artifact["media_type"] != "text/plain":
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_UTF8_TEXT_REQUIRED")
            try:
                contents[source["revision_id"]] = artifact["body"].decode("utf-8-sig")
            except UnicodeDecodeError:
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_UTF8_TEXT_REQUIRED") from None
        suggestions = self._validate_candidates(body["candidates"], source_rows, contents, allowed_codes)
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "create_ai_qualitative_run", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_qualitative_run WHERE tenant_id=%s AND requested_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint:
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._stored(c, replay)
            self._recheck(c, ctx, body)
            run_id = uuid4()
            c.execute(
                "INSERT INTO impact.ai_qualitative_run VALUES(%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    run_id,
                    UUID(body["codebook_id"]),
                    UUID(body["codebook_revision_id"]),
                    body["policy_version"],
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            )
            for item in suggestions:
                c.execute(
                    "INSERT INTO impact.ai_qualitative_suggestion VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        tenant,
                        run_id,
                        UUID(item["suggestion_id"]),
                        UUID(item["source_object_id"]),
                        UUID(item["source_revision_id"]),
                        item["source_classification"],
                        item["source_language"],
                        item["viewpoint"],
                        item["start_character"],
                        item["end_character"],
                        item["excerpt"],
                        item["excerpt_sha256"],
                        item["speaker_reference"],
                        Jsonb(item["suggested_codes"]),
                        item["theme"],
                        item["translation_language"],
                        item["translation_text"],
                        item["translation_status"],
                    ),
                )
            row = {"run_id": run_id, "codebook_revision_id": body["codebook_revision_id"]}
            return self._view(row, suggestions)

    def review(self, identity, tenant, suggestion_id, body, correlation):
        fingerprint = hash_data(["review_ai_qualitative_suggestion", str(suggestion_id), body])
        with self.service.db.transaction(tenant) as c:
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
            ctx = context(c, identity, tenant, write=True)
            authorize(c, ctx, "review_ai_qualitative_suggestion", hidden=True)
            replay = c.execute(
                "SELECT * FROM impact.ai_qualitative_review WHERE tenant_id=%s AND reviewed_by=%s AND operation_id=%s",
                (tenant, ctx.principal_id, body["operation_id"]),
            ).fetchone()
            if replay:
                if bytes(replay["request_hash"]) != fingerprint or str(replay["suggestion_id"]) != str(
                    suggestion_id
                ):
                    raise DomainError("CONFLICT_OPERATION", 409)
                return self._review_view(replay)
            suggestion = c.execute(
                "SELECT s.*,r.codebook_revision_id,r.policy_version FROM impact.ai_qualitative_suggestion s "
                "JOIN impact.ai_qualitative_run r ON r.tenant_id=s.tenant_id AND r.run_id=s.run_id "
                "WHERE s.tenant_id=%s AND s.suggestion_id=%s",
                (tenant, suggestion_id),
            ).fetchone()
            if not suggestion:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            if c.execute(
                "SELECT 1 FROM impact.ai_qualitative_review WHERE tenant_id=%s AND suggestion_id=%s",
                (tenant, suggestion_id),
            ).fetchone():
                raise DomainError("CONFLICT_OPERATION", 409, reason="QUALITATIVE_ALREADY_REVIEWED")
            source = revision(
                c,
                ctx,
                suggestion["source_revision_id"],
                "Evidence",
                "evidence.read",
            )
            if str(source["object_id"]) != str(suggestion["source_object_id"]):
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                suggestion["policy_version"],
                suggestion["source_classification"],
                self.destination,
                suggestion["source_language"],
                (),
                PURPOSE,
                activated_use_cases=activated(self.service),
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            codebook = revision(
                c,
                ctx,
                suggestion["codebook_revision_id"],
                "Codebook",
                "qualitative-extracts.read",
            )
            codebook_head = load(
                c,
                ctx,
                codebook["object_id"],
                "Codebook",
                "qualitative-extracts.read",
            )
            if codebook_head["lifecycle_state"] not in {"Approved", "Active"} or str(
                codebook_head["head_revision"]
            ) != str(suggestion["codebook_revision_id"]):
                raise DomainError("INVALID_STATE", 409, reason="APPROVED_CODEBOOK_REQUIRED")
            allowed_codes = {
                str(item["code"])
                for item in codebook["payload"].get("codes", [])
                if isinstance(item, dict) and item.get("code")
            }
            final_codes = body["final_codes"] if body["disposition"] == "ACCEPTED" else []
            extract = None
            translation_status = suggestion["translation_status"]
            final_translation = body["final_translation"]
            if translation_status == "NOT_REQUESTED" and final_translation:
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_TRANSLATION_NOT_PROPOSED")
            if (
                translation_status == "MACHINE_UNREVIEWED"
                and not body["translation_reviewed"]
                and final_translation != suggestion["translation_text"]
            ):
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_TRANSLATION_REVIEW_REQUIRED")
            if translation_status == "MACHINE_UNREVIEWED" and body["translation_reviewed"]:
                if not final_translation:
                    raise DomainError("VALIDATION_FAILED", reason="REVIEWED_TRANSLATION_REQUIRED")
                translation_status = "HUMAN_REVIEWED"
            if body["disposition"] == "ACCEPTED":
                authorize(c, ctx, "create_qualitative_extracts")
                if not final_codes:
                    raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_CODES_REQUIRED")
                if not set(final_codes) <= allowed_codes:
                    raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_CODE_UNKNOWN")
                if not body["final_theme"]:
                    raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_THEME_REQUIRED")
                interpretation = body["final_theme"]
                if final_translation:
                    interpretation += f" | translation[{translation_status}]: {final_translation}"
                data = {
                    "evidence_version": str(suggestion["source_revision_id"]),
                    "source_span": {
                        "start_character": suggestion["start_character"],
                        "end_character": suggestion["end_character"],
                        "quotation_sha256": suggestion["excerpt_sha256"],
                    },
                    "codebook_version": str(suggestion["codebook_revision_id"]),
                    "assigned_codes": final_codes,
                    "interpretation": interpretation,
                }
                self.service.validate_data(c, ctx, "QualitativeExtract", data, ctx.principal_id)
                extract = write(c, ctx, "QualitativeExtract", data)
                extract.update(operation_id=body["operation_id"], correlation_id=correlation)
                c.execute(
                    "UPDATE impact.object_registry SET classification=%s WHERE tenant_id=%s AND object_id=%s",
                    (suggestion["source_classification"], tenant, extract["object_id"]),
                )
                audit(c, ctx, "create_qualitative_extracts", extract, correlation)
            c.execute(
                "INSERT INTO impact.ai_qualitative_review VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,statement_timestamp())",
                (
                    tenant,
                    suggestion_id,
                    body["disposition"],
                    Jsonb(final_codes),
                    body["final_theme"] if body["disposition"] == "ACCEPTED" else None,
                    final_translation,
                    translation_status,
                    extract["object_id"] if extract else None,
                    extract["revision_id"] if extract else None,
                    ctx.principal_id,
                    UUID(body["operation_id"]),
                    fingerprint,
                ),
            )
            return {
                "suggestion_id": str(suggestion_id),
                "disposition": body["disposition"],
                "translation_status": translation_status,
                "qualitative_extract_id": extract["object_id"] if extract else None,
                "qualitative_extract_revision_id": extract["revision_id"] if extract else None,
                "source_classification_inherited": bool(extract),
            }

    @staticmethod
    def _sources(c, ctx, selectors):
        rows = {}
        for selector in selectors:
            if selector["revision_id"] in rows:
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_SOURCE_DUPLICATED")
            item = revision(c, ctx, selector["revision_id"], "Evidence", "evidence.read")
            if str(item["object_id"]) != selector["object_id"]:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            head = load(c, ctx, selector["object_id"], "Evidence", "evidence.read")
            if str(head["head_revision"]) != selector["revision_id"]:
                raise DomainError("CONFLICT_VERSION", 409, reason="QUALITATIVE_SOURCE_CHANGED")
            rows[selector["revision_id"]] = {
                "object_id": selector["object_id"],
                "revision_id": selector["revision_id"],
                "classification": head["classification"],
                "language": selector["language"],
                "speaker_reference": item["payload"].get("speaker_reference"),
            }
        return rows

    def _recheck(self, c, ctx, body):
        codebook = revision(c, ctx, body["codebook_revision_id"], "Codebook", "qualitative-extracts.read")
        if str(codebook["object_id"]) != body["codebook_id"]:
            raise DomainError("RESOURCE_UNAVAILABLE", 404)
        source_rows = self._sources(c, ctx, body["sources"])
        highest = max(
            source_rows.values(),
            key=lambda item: ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"].index(
                item["classification"]
            ),
        )["classification"]
        policy = ai_policy.in_force(c, ctx.tenant_id)
        ai_policy.require(
            policy,
            USE_CASE,
            body["policy_version"],
            highest,
            self.destination,
            body["language"],
            (),
            PURPOSE,
            activated_use_cases=activated(self.service),
        )
        require_available(c, ctx.tenant_id, USE_CASE, self.destination, self.configuration)

    @staticmethod
    def _validate_candidates(candidates, sources, contents, allowed_codes):
        results = []
        for candidate in candidates:
            source = sources.get(candidate["source_revision_id"])
            if not source:
                raise DomainError("RESOURCE_UNAVAILABLE", 404)
            text = contents[candidate["source_revision_id"]]
            start, end = candidate["start_character"], candidate["end_character"]
            excerpt = text[start:end]
            if (
                excerpt != candidate["excerpt"]
                or hashlib.sha256(excerpt.encode()).hexdigest() != candidate["excerpt_sha256"]
            ):
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_QUOTATION_FABRICATED")
            if candidate["speaker_reference"] != source["speaker_reference"]:
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_SPEAKER_FABRICATED")
            if not set(candidate["suggested_codes"]) <= allowed_codes:
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_CODE_UNKNOWN")
            translation = candidate["translation_text"]
            status = "MACHINE_UNREVIEWED" if translation else "NOT_REQUESTED"
            if bool(translation) != bool(candidate["translation_language"]):
                raise DomainError("VALIDATION_FAILED", reason="QUALITATIVE_TRANSLATION_LABEL_REQUIRED")
            results.append(
                {
                    "suggestion_id": str(uuid4()),
                    "source_object_id": source["object_id"],
                    "source_revision_id": source["revision_id"],
                    "source_classification": source["classification"],
                    "source_language": source["language"],
                    "viewpoint": candidate["viewpoint"],
                    "start_character": start,
                    "end_character": end,
                    "excerpt": excerpt,
                    "excerpt_sha256": candidate["excerpt_sha256"],
                    "speaker_reference": candidate["speaker_reference"],
                    "suggested_codes": candidate["suggested_codes"],
                    "theme": candidate["theme"],
                    "translation_language": candidate["translation_language"],
                    "translation_text": translation,
                    "translation_status": status,
                }
            )
        return results

    @staticmethod
    def _view(row, suggestions):
        return {
            "run_id": str(row["run_id"]),
            "codebook_revision_id": str(row["codebook_revision_id"]),
            "suggestions": [AIQualitativeAssistance._suggestion_view(item) for item in suggestions],
            "individual_review_required": True,
            "consensus_inferred": False,
        }

    @staticmethod
    def _stored(c, row):
        suggestions = c.execute(
            "SELECT * FROM impact.ai_qualitative_suggestion WHERE tenant_id=%s AND run_id=%s ORDER BY suggestion_id",
            (row["tenant_id"], row["run_id"]),
        ).fetchall()
        return AIQualitativeAssistance._view(row, suggestions)

    @staticmethod
    def _suggestion_view(row):
        keys = (
            "suggestion_id",
            "source_object_id",
            "source_revision_id",
            "source_classification",
            "source_language",
            "viewpoint",
            "start_character",
            "end_character",
            "excerpt",
            "excerpt_sha256",
            "speaker_reference",
            "suggested_codes",
            "theme",
            "translation_language",
            "translation_text",
            "translation_status",
        )
        result = {key: row[key] for key in keys}
        for key in ("suggestion_id", "source_object_id", "source_revision_id"):
            result[key] = str(result[key])
        return result

    @staticmethod
    def _review_view(row):
        return {
            "suggestion_id": str(row["suggestion_id"]),
            "disposition": row["disposition"],
            "translation_status": row["translation_status"],
            "qualitative_extract_id": (
                str(row["qualitative_extract_id"]) if row["qualitative_extract_id"] else None
            ),
            "qualitative_extract_revision_id": (
                str(row["qualitative_extract_revision_id"])
                if row["qualitative_extract_revision_id"]
                else None
            ),
            "source_classification_inherited": bool(row["qualitative_extract_id"]),
        }
