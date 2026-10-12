"""FR-AI-011 server-owned tool and untrusted-source boundary.

Policy permission is only a ceiling. A runtime independently supplies its closed tool catalogue and
scoped argument schemas; model text and source documents can never add tools or widen arguments.
Sources are wrapped as JSON data under an explicit untrusted label. We record only coarse attempt
categories, never the source text, prompt, credentials or provider response.
"""

import json
import re

from .domain import DomainError

MAX_UNTRUSTED_BYTES = 128 * 1024
INDICATORS = {
    "CREDENTIAL_DISCLOSURE": re.compile(
        r"\b(reveal|show|print|return|send|expose)\b.{0,80}\b(passwords?|credentials?|api[- ]?keys?|tokens?|secrets?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "CROSS_TENANT_RETRIEVAL": re.compile(
        r"\b(retrieve|fetch|list|export|read|show)\b.{0,80}\b(all|every)\s+(tenant|workspace|organisation|organization)s?\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "BULK_EXPORT": re.compile(
        r"\b(export|download|send|copy)\b.{0,80}\b(all|every)\s+(records?|rows?|files?|participants?)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "UNAPPROVED_DESTINATION": re.compile(
        r"\b(send|post|upload|forward|exfiltrate)\b.{0,80}\b(elsewhere|external|webhook|url|endpoint|email)\b",
        re.IGNORECASE | re.DOTALL,
    ),
}


def untrusted_envelope(**sources):
    """Return a bounded data-only envelope plus detected unsafe-instruction categories."""
    raw = json.dumps(sources, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(raw.encode("utf-8")) > MAX_UNTRUSTED_BYTES:
        raise DomainError("LIMIT_EXCEEDED", 413, reason="AI_UNTRUSTED_SOURCE_TOO_LARGE")
    attempts = sorted(name for name, pattern in INDICATORS.items() if pattern.search(raw))
    return {"untrusted_sources": sources, "embedded_instruction_authority": False}, attempts


def runtime_tools(catalogue, requested):
    """Resolve only server-owned tool definitions; model/source names never become capabilities."""
    if not isinstance(catalogue, dict):
        raise RuntimeError("AI tool catalogue must be server owned")
    unavailable = sorted(set(requested) - set(catalogue))
    if unavailable:
        raise DomainError(
            "VALIDATION_FAILED",
            422,
            message="The requested AI tool is not available in this runtime.",
            reason="AI_TOOL_UNAVAILABLE",
        )
    return [catalogue[name] for name in requested]
