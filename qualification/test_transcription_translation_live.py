"""Positive user journey for FR-EVD-006 / APL-644 transcription and translation."""

from types import SimpleNamespace
from uuid import uuid4

from impact_api.store import Context, write
from test_evidence import evidence, unique, uploaded
from test_forms import temporary_grants
from test_live_application import expect


def _seed_approved_destination(live):
    """Trusted synthetic precondition; production destinations require a governed admin flow."""
    actor = live.fixture["actors"]["author"]
    ctx = Context(
        actor["tenant_id"],
        actor["principal_id"],
        actor["membership_id"],
        SimpleNamespace(natural_identity_id=actor["natural_identity_id"]),
        0,
        0,
        [],
    )
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (actor["tenant_id"],))
        return write(
            c,
            ctx,
            "ProcessingDestination",
            {"name": "Synthetic approved processor", "permitted_tasks": ["TRANSLATE"]},
            "Approved",
        )


def _stored(live, object_id):
    tenant = live.fixture["actors"]["author"]["tenant_id"]
    with live.db() as c:
        c.execute("SELECT set_config('impact.tenant_id',%s,true)", (tenant,))
        return c.execute(
            "SELECT r.object_type,r.lifecycle_state,v.revision_id::text,v.predecessor_revision::text,v.payload "
            "FROM impact.object_registry r JOIN impact.object_revision v "
            "ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_id=%s",
            (tenant, object_id),
        ).fetchone()


def _post(live, route, data):
    return expect(
        live.request(
            live.path(route),
            actor="author",
            method="POST",
            body={"operation_id": str(uuid4()), "data": data},
        ),
        201,
    )


def test_analyst_corrects_translation_and_quotes_the_reviewed_meaning(live):
    """A corrected segment remains pinned to the recording and retains automated text."""
    recording_bytes = unique(b"Synthetic interview recording transcript placeholder\n")
    recording = expect(
        evidence(
            live,
            uploaded(live, recording_bytes, "text/plain", "interview.txt")["upload_id"],
            evidence_type="INTERVIEW_RECORDING",
            source="Synthetic field interview",
        ),
        201,
    )
    destination = _seed_approved_destination(live)
    revoke = temporary_grants(live, "author", ["evaluations.draft.edit", "evaluations.read", "evidence.read"])
    generated = _post(
        live,
        "transcription-requests",
        {
            "recording_id": recording["object_id"],
            "destination_id": destination["object_id"],
            "language": "en",
            "task": "TRANSLATE",
            "segments": [
                {
                    "segment_id": "segment-03m12s",
                    "start_ms": 192000,
                    "end_ms": 197000,
                    "speaker": None,
                    "text": "The clinic was easy to reach.",
                }
            ],
        },
    )
    generated_row = _stored(live, generated["object_id"])
    assert generated_row["payload"]["fallback"] == "PROHIBITED"
    assert generated_row["payload"]["segments"][0]["speaker"] == "UNKNOWN"
    assert generated_row["payload"]["recording_revision"] == recording["revision_id"]

    corrected = _post(
        live,
        "transcript-corrections",
        {
            "artifact_id": generated["object_id"],
            "segment_id": "segment-03m12s",
            "corrected_text": "The clinic was difficult to reach.",
        },
    )
    corrected_row = _stored(live, corrected["object_id"])
    segment = corrected_row["payload"]["segments"][0]
    assert corrected["object_id"] == generated["object_id"]
    assert corrected_row["predecessor_revision"] == generated["revision_id"]
    assert segment["original_automated_text"] == "The clinic was easy to reach."
    assert segment["text"] == "The clinic was difficult to reach."

    quotation = _post(
        live,
        "quotation-references",
        {
            "artifact_id": generated["object_id"],
            "segment_id": "segment-03m12s",
            "original_meaning_reviewed": True,
        },
    )
    quotation_row = _stored(live, quotation["object_id"])
    assert quotation_row["payload"]["artifact_revision"] == corrected["revision_id"]
    assert quotation_row["payload"]["recording_id"] == recording["object_id"]
    assert quotation_row["payload"]["recording_revision"] == recording["revision_id"]
    denied = expect(
        live.request(
            live.path("transcript-corrections"),
            actor="partner",
            method="POST",
            body={
                "operation_id": str(uuid4()),
                "data": {
                    "artifact_id": generated["object_id"],
                    "segment_id": "segment-03m12s",
                    "corrected_text": "An unauthorised correction must not be saved.",
                },
            },
        ),
        403,
    )
    assert denied["code"] == "POLICY_DENIED"
    revoke()
