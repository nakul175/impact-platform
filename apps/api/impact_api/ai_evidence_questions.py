"""Permission-filtered, source-pinned answers over governed calculated results."""

import re

from . import ai_policy
from .ai_safety import require_available
from .domain import DomainError
from .service import revision
from .store import authorize, context, load

USE_CASE = "EVIDENCE_QUESTION"
PURPOSE = "EVIDENCE_BASED_QUESTION"
SOURCE_MODE = "SELECTED_GOVERNED_RESULTS"
MAX_SOURCES = 20
TOKENS = re.compile(r"[a-z0-9]+")


def words(value):
    return set(TOKENS.findall(value.casefold()))


def clarification(body):
    missing = [
        field
        for field in ("programme_id", "programme_revision_id", "period_id", "period_revision_id")
        if not body.get(field)
    ]
    if body.get("source_mode") != SOURCE_MODE:
        missing.append("source_mode")
    if not body.get("sources"):
        missing.append("sources")
    return missing


def scalar_claims(payload, question):
    """Return only stored result fields; no arithmetic or model-generated fact is introduced."""
    requested = words(question)
    candidates = [
        (
            "value",
            payload.get("displayed_value", payload.get("value")),
            "/displayed_value" if payload.get("displayed_value") is not None else "/value",
        ),
        ("value state", payload.get("value_state"), "/value_state"),
        ("mode", payload.get("mode"), "/mode"),
        ("unit", (payload.get("formula") or {}).get("unit"), "/formula/unit"),
        (
            "coverage expected count",
            (payload.get("coverage") or {}).get("expected_count"),
            "/coverage/expected_count",
        ),
        (
            "coverage received count",
            (payload.get("coverage") or {}).get("received_count"),
            "/coverage/received_count",
        ),
        (
            "coverage approved count",
            (payload.get("coverage") or {}).get("approved_count"),
            "/coverage/approved_count",
        ),
        ("coverage complete", (payload.get("coverage") or {}).get("complete"), "/coverage/complete"),
    ]
    selected = []
    for label, value, pointer in candidates:
        if value is None:
            continue
        label_words = words(label)
        if requested & label_words or (label == "value" and requested & {"result", "number", "total"}):
            selected.append((label, str(value).lower() if isinstance(value, bool) else str(value), pointer))
    return selected


class AIEvidenceQuestions:
    def __init__(self, service, destination, configuration):
        self.service = service
        self.destination = destination
        self.configuration = configuration

    def answer(self, identity, tenant, body):
        missing_scope = clarification(body)
        if missing_scope:
            return {
                "state": "CLARIFICATION_REQUIRED",
                "answer": None,
                "clarification_fields": missing_scope,
                "claims": [],
                "citations": [],
                "missing_evidence": [
                    "Authorised programme, period and selected source revisions are required."
                ],
                "contradictions": [],
                "official_number_guessed": False,
                "protected_resource_confirmed": False,
                "fabricated_citations": False,
            }
        with self.service.db.transaction(tenant) as c:
            ctx = context(c, identity, tenant)
            authorize(c, ctx, "answer_ai_evidence_question", hidden=True)
            policy = ai_policy.in_force(c, tenant)
            ai_policy.require(
                policy,
                USE_CASE,
                body["policy_version"],
                "CONFIDENTIAL",
                self.destination,
                body["language"],
                (),
                PURPOSE,
            )
            require_available(c, tenant, USE_CASE, self.destination, self.configuration)
            try:
                programme = load(c, ctx, body["programme_id"], "Programme", "programmes.read")
                period = load(c, ctx, body["period_id"], "Period", "periods.read")
                if (
                    str(programme["head_revision"]) != body["programme_revision_id"]
                    or str(period["head_revision"]) != body["period_revision_id"]
                ):
                    raise DomainError("RESOURCE_UNAVAILABLE", 404)
                sources = []
                for selector in body["sources"]:
                    source = revision(
                        c,
                        ctx,
                        selector["revision_id"],
                        "CalculatedResult",
                        "calculated-results.read",
                    )
                    if str(source["object_id"]) != selector["object_id"]:
                        raise DomainError("RESOURCE_UNAVAILABLE", 404)
                    binding = c.execute(
                        "SELECT b.indicator_id,b.period_id,i.programme_id FROM impact.result_binding b "
                        "JOIN impact.indicator_instance_current i ON i.tenant_id=b.tenant_id "
                        "AND i.object_id=b.indicator_id WHERE b.tenant_id=%s AND b.result_id=%s",
                        (tenant, source["object_id"]),
                    ).fetchone()
                    if (
                        not binding
                        or str(binding["programme_id"]) != body["programme_id"]
                        or str(binding["period_id"]) != body["period_id"]
                    ):
                        raise DomainError("RESOURCE_UNAVAILABLE", 404)
                    sources.append((source, binding))
            except DomainError:
                return {
                    "state": "ABSTAINED",
                    "answer": None,
                    "clarification_fields": [],
                    "claims": [],
                    "citations": [],
                    "missing_evidence": ["No authorised evidence is available for that question."],
                    "contradictions": [],
                    "official_number_guessed": False,
                    "protected_resource_confirmed": False,
                    "fabricated_citations": False,
                }

            claims, citations, missing_items = [], [], []
            comparison = {}
            for source, binding in sources:
                payload = source["payload"]
                if payload.get("value_state") != "PRESENT" and payload.get("reason_code"):
                    missing_items.append("Result unavailable: " + payload["reason_code"])
                if (payload.get("coverage") or {}).get("complete") is False:
                    missing_items.append("Coverage is incomplete.")
                for limitation in payload.get("limitations") or []:
                    if isinstance(limitation, dict) and limitation.get("code"):
                        missing_items.append("Limitation: " + str(limitation["code"]))
                extracted = scalar_claims(payload, body["question"])
                for label, value, pointer in extracted:
                    citation_number = len(citations) + 1
                    claims.append(
                        {
                            "text": f"{label}: {value}",
                            "citation_numbers": [citation_number],
                            "material": True,
                        }
                    )
                    citations.append(
                        {
                            "number": citation_number,
                            "object_id": str(source["object_id"]),
                            "revision_id": str(source["revision_id"]),
                            "object_type": "CalculatedResult",
                            "location": pointer,
                        }
                    )
                    comparison.setdefault((str(binding["indicator_id"]), label), set()).add(value)
            contradictions = [
                {
                    "field": label,
                    "indicator_id": indicator,
                    "values": sorted(values),
                }
                for (indicator, label), values in comparison.items()
                if len(values) > 1
            ][:80]
            missing_evidence = list(dict.fromkeys(missing_items))[:20]
            if not claims:
                missing_evidence.append("Selected governed results do not support the requested claim.")
            answer = (
                " ".join(f"{claim['text']} [{claim['citation_numbers'][0]}]" for claim in claims)
                or "The selected governed results do not contain a supported answer."
            )
            return {
                "state": "ANSWERED",
                "answer": answer,
                "clarification_fields": [],
                "claims": claims,
                "citations": citations,
                "missing_evidence": missing_evidence,
                "contradictions": contradictions,
                "official_number_guessed": False,
                "protected_resource_confirmed": False,
                "fabricated_citations": False,
            }
