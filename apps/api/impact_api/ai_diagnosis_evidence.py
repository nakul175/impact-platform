"""Protected-reference resolver used by diagnosis commands and disclosures.

Call within the caller's transaction. Diagnosis command/read authorization remains
the caller's duty. This helper resolves fresh evidence authority under the tenant
lock and returns exact selectors only, never titles, notes, URLs or file bytes.
"""

from copy import deepcopy
from uuid import UUID

from .domain import DomainError, unavailable
from .store import authorize, context, load

MAX_REFERENCES_PER_PROBLEM = 5


def _canonical_id(value):
    try:
        return isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def validate_references(references):
    """Recommended bounded selector shape, without normalization or inferred links."""
    if not isinstance(references, list) or len(references) > MAX_REFERENCES_PER_PROBLEM:
        raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
    seen = set()
    for reference in references:
        if not isinstance(reference, dict) or set(reference) != {"object_id", "revision_id"}:
            raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
        pair = []
        for field in ("object_id", "revision_id"):
            value = reference[field]
            if not _canonical_id(value):
                raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
            pair.append(value)
        pair = tuple(pair)
        if pair in seen:
            raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
        seen.add(pair)


def resolve_references(c, identity, tenant, references):
    """Recheck actual current authority and the exact named available Evidence revision.

    Available metadata may remain UNVERIFIED: a permitted reference is not an
    endorsement. Upload-backed sources must still be CLEAN and not purged;
    external references are stored metadata and are never fetched here.
    """
    validate_references(references)
    return _resolve_checked(c, identity, tenant, references)


def resolve_problem_references(c, identity, tenant, problems):
    """Resolve one bounded diagnosis's optional references with one fresh context."""
    if not isinstance(problems, list) or len(problems) > 20:
        raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
    references = []
    for problem in problems:
        if not isinstance(problem, dict):
            raise DomainError("VALIDATION_FAILED", reason="DIAGNOSIS_EVIDENCE_INVALID")
        refs = problem.get("evidence_references", [])
        validate_references(refs)
        references.extend(refs)
    if references:
        _resolve_checked(c, identity, tenant, references)


def _resolve_checked(c, identity, tenant, references):
    c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (tenant,))
    ctx = context(c, identity, tenant, write=True)
    for reference in references:
        evidence_id, revision_id = reference["object_id"], reference["revision_id"]
        authorize(c, ctx, "get_evidence", evidence_id, hidden=True)
        load(c, ctx, evidence_id, "Evidence", "evidence.read")
        revision = c.execute(
            "SELECT payload FROM impact.object_revision WHERE tenant_id=%s AND object_id=%s "
            "AND revision_id=%s AND object_type='Evidence' AND restriction_state='AVAILABLE'",
            (tenant, evidence_id, revision_id),
        ).fetchone()
        if not revision or not isinstance(revision["payload"], dict):
            unavailable()
        payload = revision["payload"]
        if payload.get("upload_id"):
            if not _canonical_id(payload["upload_id"]):
                unavailable()
            if not c.execute(
                "SELECT 1 FROM impact.upload_session u JOIN impact.file_blob b "
                "ON b.tenant_id=u.tenant_id AND b.blob_id=u.blob_id "
                "WHERE u.tenant_id=%s AND u.upload_id=%s AND u.state='CLEAN' "
                "AND b.scan_state='CLEAN' AND b.purged_at IS NULL",
                (tenant, payload["upload_id"]),
            ).fetchone():
                unavailable()
        elif (
            not isinstance(payload.get("external_reference"), str)
            or not payload["external_reference"].strip()
        ):
            unavailable()
    return deepcopy(references)
