"""Qualification of web forms, continued (v0.27): language versions inside the reviewed and
published Form revision (FR-FRM-004), collection rounds and assignments with coverage per round
(FR-FRM-005), and the correction of returned responses (FR-FRM-006)."""
# ruff: noqa: F811

import uuid

from impact_api.contracts import validate
from test_live_application import cmd, expect
from test_measurement import get, create, action, submit, approve  # noqa: F401
from test_forms import (  # noqa: F401
    ANSWERED,
    WHEN,
    create_as,
    form_data,
    observations,
    planned,
    publish,
    published,
    response,
    send,
    workflow_of,
    workflow_version,
)
from test_planning import db_counts, failure, post

HINDI = {
    "language": "hi",
    "name": "हिन्दी",
    "fields": {
        "consent": {"label": "सहमति दी गई"},
        "sex": {"label": "उत्तरदाता का लिंग", "choices": {"F": "महिला", "M": "पुरुष"}},
        "households": {"label": "पहुँचे हुए परिवार", "help": "इस दौरे में गिने गए परिवार"},
        "note": {"label": "टिप्पणी"},
    },
}


def translated(indicator, **extra):
    return form_data(indicator, **{"default_language": "en", "translation_versions": [HINDI], **extra})


def completeness(live, form, actor="author"):
    return get(live, "forms", form["object_id"] + "/completeness", actor=actor)


# FR-FRM-004 ------------------------------------------------------------------------------------
def test_language_versions_are_reviewed_published_and_collected_under_one_stable_code(live):
    indicator, period, units = planned(live)
    form = create(live, "forms", translated(indicator))
    report = completeness(live, form)
    validate("FormCompleteness", report)
    assert report["default_language"] == "en" and report["complete"] is True
    assert [(x["language"], x["name"], x["complete"], x["gaps"]) for x in report["languages"]] == [
        ("hi", "हिन्दी", True, [])
    ]
    # The reviewer sees the languages in the candidate; the published version carries them.
    workflow = submit(live, "forms", form)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    assert candidate["record"]["data"]["translation_versions"] == [HINDI]
    approve(live, workflow)
    form = get(live, "forms", form["object_id"])
    action(
        live, "forms", form, "publish", {"approved_candidate_revision": form["revision_id"]}, actor="reviewer"
    )
    version = get(live, "forms", form["object_id"] + "/published")
    assert version["data"]["default_language"] == "en"
    assert version["data"]["translation_versions"] == [HINDI]
    # The same choice submitted in English and in Hindi maps to the one stable code, and each
    # response retains the language presented to the respondent.
    english = create_as(
        live,
        "submissions",
        {
            "form_version": version["form_version"],
            **WHEN,
            "answers": ANSWERED,
            "unit_key": units[0],
            "language": "en",
        },
        "author",
    )
    hindi = create_as(
        live,
        "submissions",
        {
            "form_version": version["form_version"],
            **WHEN,
            "answers": ANSWERED,
            "unit_key": units[1],
            "language": "hi",
        },
        "author",
    )
    send(live, english)
    send(live, hindi)
    for row, language in [(english, "en"), (hindi, "hi")]:
        saved = get(live, "submissions", row["object_id"])
        assert saved["data"]["language"] == language and saved["data"]["review_state"] == "SUBMITTED"
        [obs] = observations(live, saved)
        assert obs["data"]["dimension_values"] == {"sex": "F"} and obs["data"]["value"] == "7"
    # A language the version does not carry cannot be presented.
    failure(
        live.request(
            live.path("submissions"),
            method="POST",
            body=cmd({"form_version": version["form_version"], **WHEN, "answers": {}, "language": "sw"}),
        ),
        422,
        "FORM_LANGUAGE_NOT_AVAILABLE",
    )
    # Translations are part of the published revision: revising the form (back to Draft) with
    # another translation changes nothing collection sees until a successor is published.
    revised = {
        "translation_versions": [HINDI, {"language": "fr", "fields": {}}],
    }
    form = get(live, "forms", form["object_id"])  # publication wrote the Published revision
    expect(post(live, "forms", revised, revision=form["revision_id"], obj=form["object_id"]), 200)
    assert get(live, "forms", form["object_id"] + "/published")["data"]["translation_versions"] == [HINDI]
    head = completeness(live, form)
    assert head["lifecycle_state"] == "Draft" and head["complete"] is False
    assert [x["language"] for x in head["languages"]] == ["hi", "fr"]
    assert len(head["languages"][1]["gaps"]) == 6  # four labels and two choice labels
    # The same version collects in every language it declares, so an unknown language is a 404
    # for another tenant and a 422 for a member exactly as any other invalid value.
    expect(live.request(live.path("forms", form["object_id"] + "/completeness"), actor="other_tenant"), 404)


def test_an_incomplete_or_invalid_translation_cannot_be_reviewed_or_published(live):
    indicator, _, _ = planned(live)
    partial = {**HINDI, "fields": {k: v for k, v in HINDI["fields"].items() if k != "note"}}
    partial["fields"]["sex"] = {"label": "उत्तरदाता का लिंग", "choices": {"F": "महिला"}}
    form = create(live, "forms", translated(indicator, translation_versions=[partial]))
    report = completeness(live, form)
    assert report["complete"] is False
    assert report["languages"][0]["gaps"] == [
        {"field_code": "sex", "choice_code": "M"},
        {"field_code": "note", "choice_code": None},
    ]
    # Submitting for review runs the completeness check: the gap blocks the version.
    failure(
        post(
            live,
            "forms",
            {"workflow_version": workflow_version(live)},
            revision=form["revision_id"],
            obj=form["object_id"],
            verb="submit",
        ),
        422,
        "FORM_TRANSLATION_INCOMPLETE",
    )
    # Translations only add text under stable codes.
    for translation_versions, reason in [
        ([{**HINDI, "fields": {**HINDI["fields"], "unknown": {"label": "?"}}}], "FORM_TRANSLATION_INVALID"),
        (
            [{**HINDI, "fields": {**HINDI["fields"], "sex": {"label": "x", "choices": {"X": "?"}}}}],
            "FORM_TRANSLATION_INVALID",
        ),
        ([HINDI, HINDI], "FORM_LANGUAGE_INVALID"),
        ([{**HINDI, "language": "en"}], "FORM_LANGUAGE_INVALID"),
    ]:
        failure(
            post(
                live,
                "forms",
                {"translation_versions": translation_versions},
                revision=form["revision_id"],
                obj=form["object_id"],
            ),
            422,
            reason,
        )
    # A translation needs a declared default language to fall back to.
    failure(
        live.request(
            live.path("forms"),
            method="POST",
            body=cmd(form_data(indicator, translation_versions=[HINDI])),
        ),
        422,
        "FORM_LANGUAGE_INVALID",
    )
    # Codes are the identity of a language version; "Hindi" is not one.
    failure(
        live.request(
            live.path("forms"), method="POST", body=cmd(translated(indicator, default_language="Hindi"))
        ),
        422,
    )
    # Enumerators cannot design or translate forms: a form they cannot edit is hidden (404), and a
    # create is refused (403).
    expect(
        post(
            live,
            "forms",
            {"translation_versions": [HINDI]},
            actor="enumerator",
            revision=form["revision_id"],
            obj=form["object_id"],
        ),
        404,
    )
    failure(
        live.request(live.path("forms"), actor="enumerator", method="POST", body=cmd(translated(indicator))),
        403,
    )


# FR-FRM-005 ------------------------------------------------------------------------------------
def round_data(form, version, period, units, **extra):
    return {
        "form_id": form["object_id"],
        "form_version": version["form_version"],
        "period_id": period["object_id"],
        "title": "Round 1",
        "due_at": "2026-09-01T00:00:00Z",
        "expected_units": units,
        **extra,
    }


def principal(live, actor):
    return live.fixture["actors"][actor]["principal_id"]


def assign(live, round_row, version, unit, actor="author", **extra):
    data = {
        "round_id": round_row["object_id"],
        "form_version": version["form_version"],
        "assignee_id": principal(live, actor),
        "unit_key": unit,
        "due_at": "2026-08-31T00:00:00Z",
        **extra,
    }
    return create(live, "assignments", data)


def coverage(live, round_row, actor="author"):
    report = get(live, "collection-rounds", round_row["object_id"] + "/coverage", actor=actor)
    return validate("RoundCoverage", report)


def test_rounds_assignments_my_work_and_coverage(live, published):
    indicator, period, form, version, units = published
    round_row = create(live, "collection-rounds", round_data(form, version, period, units))
    assert round_row["lifecycle_state"] == "Draft" and round_row["data"]["expected_units"] == units
    # Nothing assigned or received yet: three expected units, none covered.
    report = coverage(live, round_row)
    assert (report["expected_count"], report["assigned_count"], report["received_count"]) == (3, 0, 0)
    assert report["coverage_percent"] == "0.00" and report["coverage_state"] == "MEASURED"
    first = assign(live, round_row, version, units[0])
    second = assign(live, round_row, version, units[1], actor="enumerator")
    assert first["data"]["assignee_id"] == principal(live, "author")
    # One stable task per round and unit; only expected units; only the round's version.
    failure(
        live.request(
            live.path("assignments"),
            method="POST",
            body=cmd(
                {
                    "round_id": round_row["object_id"],
                    "form_version": version["form_version"],
                    "assignee_id": principal(live, "author"),
                    "unit_key": units[0],
                    "due_at": "2026-08-31T00:00:00Z",
                }
            ),
        ),
        409,
        "ASSIGNMENT_UNIT_TAKEN",
    )
    for change, status, reason in [
        ({"unit_key": "not-expected"}, 422, "ASSIGNMENT_UNIT_NOT_EXPECTED"),
        ({"form_version": form["revision_id"]}, 422, "ASSIGNMENT_FORM_VERSION_MISMATCH"),
        ({"assignee_id": principal(live, "reviewer")}, 409, "ASSIGNEE_INELIGIBLE"),
    ]:
        failure(
            live.request(
                live.path("assignments"),
                method="POST",
                body=cmd(
                    {
                        "round_id": round_row["object_id"],
                        "form_version": version["form_version"],
                        "assignee_id": principal(live, "author"),
                        "unit_key": units[2],
                        "due_at": "2026-08-31T00:00:00Z",
                        **change,
                    }
                ),
            ),
            status,
            reason,
        )
    # My work: the enumerator lists the assignments they hold, the supervisor every one.
    # (The seed carries one legacy fixture assignment held by the enumerator, so the list is
    # filtered, not empty.)
    mine = get(live, "assignments", actor="enumerator")["items"]
    assert second["object_id"] in {a["object_id"] for a in mine}
    assert first["object_id"] not in {a["object_id"] for a in mine}
    assert all(a["data"]["assignee_id"] == principal(live, "enumerator") for a in mine)
    assert {a["object_id"] for a in get(live, "assignments")["items"]} >= {
        first["object_id"],
        second["object_id"],
    }
    # A response names its assignment: the unit comes from it, and only its holder may respond.
    draft = create_as(
        live,
        "submissions",
        {
            "form_version": version["form_version"],
            **WHEN,
            "answers": ANSWERED,
            "assignment_id": first["object_id"],
        },
        "author",
    )
    assert draft["data"]["unit_key"] == units[0]
    failure(
        live.request(
            live.path("submissions"),
            method="POST",
            body=cmd(
                {
                    "form_version": version["form_version"],
                    **WHEN,
                    "answers": ANSWERED,
                    "assignment_id": second["object_id"],
                }
            ),
        ),
        403,
        "ASSIGNMENT_NOT_HELD",
    )
    failure(
        live.request(
            live.path("submissions"),
            method="POST",
            body=cmd(
                {
                    "form_version": version["form_version"],
                    **WHEN,
                    "answers": ANSWERED,
                    "assignment_id": first["object_id"],
                    "unit_key": units[2],
                }
            ),
        ),
        422,
        "ASSIGNMENT_UNIT_MISMATCH",
    )
    send(live, draft)
    submission = get(live, "submissions", draft["object_id"])
    assert submission["data"]["review_state"] == "SUBMITTED"
    [obs] = observations(live, submission)
    assert obs["data"]["source_key"] == units[0] + "/" + indicator["object_id"]
    # The visit is complete: the assignment closed with the submission (one audit event of its
    # own), nobody can respond to it again, and it cannot be reassigned.
    done = get(live, "assignments", first["object_id"])
    assert done["lifecycle_state"] == "Completed"
    assert db_counts(live, first["object_id"], "action_submissions_submit")["audit"] == 1
    failure(
        live.request(
            live.path("submissions"),
            method="POST",
            body=cmd(
                {
                    "form_version": version["form_version"],
                    **WHEN,
                    "answers": ANSWERED,
                    "assignment_id": first["object_id"],
                }
            ),
        ),
        409,
        "ASSIGNMENT_COMPLETED",
    )
    failure(
        post(
            live,
            "assignments",
            {"assignee_id": principal(live, "enumerator"), "reason": "Too late"},
            revision=done["revision_id"],
            obj=done["object_id"],
            verb="reassign",
        ),
        409,
        "ASSIGNMENT_COMPLETED",
    )
    # An assignment is work, never authority: the assignee cannot approve what it produced.
    workflow = workflow_of(live, obs["object_id"])
    failure(
        post(
            live,
            "workflows",
            {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Mine"},
            revision=workflow["revision_id"],
            obj=workflow["object_id"],
            verb="approve",
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    # Coverage: three expected, two assigned, one received; the denominator is the expected set.
    report = coverage(live, round_row)
    assert (report["assigned_count"], report["received_count"], report["missing_count"]) == (2, 1, 2)
    assert report["unassigned_count"] == 1 and report["coverage_percent"] == "33.33"
    by_unit = {u["unit_key"]: u for u in report["units"]}
    assert by_unit[units[0]]["received"] and by_unit[units[0]]["submission_id"] == submission["object_id"]
    assert by_unit[units[0]]["assignment_state"] == "Completed"
    assert (
        by_unit[units[1]]["assignee_id"] == principal(live, "enumerator")
        and not by_unit[units[1]]["received"]
    )
    assert by_unit[units[2]]["assignment_id"] is None
    # Only a programme manager reassigns: without assignment.reassign the task is hidden.
    expect(
        post(
            live,
            "assignments",
            {"assignee_id": principal(live, "author"), "reason": "Not mine to move"},
            actor="reviewer",
            revision=second["revision_id"],
            obj=second["object_id"],
            verb="reassign",
        ),
        404,
    )
    # Reassignment keeps the task identity and records the previous holder and the reason; the
    # old holder can no longer respond to it.
    receipt = expect(
        post(
            live,
            "assignments",
            {"assignee_id": principal(live, "author"), "reason": "Collector B covers the village"},
            revision=second["revision_id"],
            obj=second["object_id"],
            verb="reassign",
        ),
        200,
    )
    reassigned = get(live, "assignments", second["object_id"])
    assert reassigned["revision_id"] == receipt["revision_id"] and reassigned["lifecycle_state"] == "Draft"
    assert reassigned["data"]["assignee_id"] == principal(live, "author")
    assert reassigned["data"]["previous_assignee_id"] == principal(live, "enumerator")
    assert reassigned["data"]["reason"] == "Collector B covers the village"
    assert db_counts(live, second["object_id"], "action_assignments_reassign")["revisions"] == 2
    assert second["object_id"] not in {
        a["object_id"] for a in get(live, "assignments", actor="enumerator")["items"]
    }
    failure(
        live.request(
            live.path("submissions"),
            actor="enumerator",
            method="POST",
            body=cmd(
                {
                    "form_version": version["form_version"],
                    **WHEN,
                    "answers": {},
                    "assignment_id": second["object_id"],
                }
            ),
        ),
        403,
        "ASSIGNMENT_NOT_HELD",
    )
    # The assignee changes only through reassign; a patch may move the due time only.
    failure(
        post(
            live,
            "assignments",
            {"assignee_id": principal(live, "enumerator")},
            revision=reassigned["revision_id"],
            obj=reassigned["object_id"],
        ),
        422,
        "ASSIGNMENT_IMMUTABLE",
    )
    expect(
        post(
            live,
            "assignments",
            {"due_at": "2026-09-15T00:00:00Z"},
            revision=reassigned["revision_id"],
            obj=reassigned["object_id"],
        ),
        200,
    )
    # A round keeps its form, version and period; an assigned unit cannot be dropped.
    failure(
        post(
            live,
            "collection-rounds",
            {"expected_units": units[1:]},
            revision=round_row["revision_id"],
            obj=round_row["object_id"],
        ),
        409,
        "ROUND_UNIT_ASSIGNED",
    )
    failure(
        post(
            live,
            "collection-rounds",
            {"period_id": str(uuid.uuid4())},
            revision=round_row["revision_id"],
            obj=round_row["object_id"],
        ),
        422,
        "ROUND_IMMUTABLE",
    )
    # Zero expected units is not applicable, never 100 %.
    empty = create(live, "collection-rounds", round_data(form, version, period, [], title="Empty"))
    report = coverage(live, empty)
    assert report["coverage_state"] == "NOT_APPLICABLE" and report["coverage_percent"] is None
    # Boundaries: another tenant sees nothing; a collector defines no rounds; an unpublished
    # revision opens no round.
    for obj in [round_row["object_id"], round_row["object_id"] + "/coverage"]:
        expect(live.request(live.path("collection-rounds", obj), actor="other_tenant"), 404)
    expect(live.request(live.path("assignments", first["object_id"]), actor="other_tenant"), 404)
    failure(
        live.request(
            live.path("collection-rounds"),
            actor="enumerator",
            method="POST",
            body=cmd(round_data(form, version, period, units)),
        ),
        403,
    )
    failure(
        live.request(
            live.path("collection-rounds"),
            method="POST",
            body=cmd(round_data(form, version, period, units, form_version=form["revision_id"])),
        ),
        409,
        "FORM_VERSION_NOT_PUBLISHED",
    )
    validate("CollectionRound", round_row)
    validate("Assignment", reassigned)


def open_workflow(live, observation_id):
    """The review currently open for an observation (a correction opens a second one)."""
    with live.db() as c:
        row = c.execute(
            "SELECT r.object_id FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision WHERE r.object_type='Workflow' AND r.lifecycle_state='InReview' AND v.payload->>'candidate_id'=%s",
            (observation_id,),
        ).fetchone()
    return get(live, "workflows", str(row["object_id"]))


# FR-FRM-006 ------------------------------------------------------------------------------------
def test_returned_work_is_corrected_as_a_new_revision_under_the_same_review(live, published):
    indicator, period, form, version, units = published
    draft = response(live, version, ANSWERED, unit=units[0])
    send(live, draft)
    submission = get(live, "submissions", draft["object_id"])
    [obs] = observations(live, submission)
    corrected = {**ANSWERED, "households": {"kind": "INTEGER", "value": 9}}
    body = {
        "workflow_version": workflow_version(live),
        "reason": "Recount of the register",
        "answers": corrected,
    }
    # Only returned work is corrected.
    failure(
        post(
            live,
            "submissions",
            body,
            revision=submission["revision_id"],
            obj=submission["object_id"],
            verb="correct",
        ),
        409,
        "CORRECTION_REQUIRES_RETURNED_WORK",
    )
    workflow = workflow_of(live, obs["object_id"])
    action(
        live,
        "workflows",
        workflow,
        "return",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Count the register again"},
        actor="reviewer",
    )
    assert get(live, "observations", obs["object_id"])["lifecycle_state"] == "Returned"
    # Corrected answers are validated like any response: a hidden answer is refused.
    hidden = {**corrected, "consent": {"kind": "BOOLEAN", "value": False}}
    failure(
        post(
            live,
            "submissions",
            {**body, "answers": hidden},
            revision=submission["revision_id"],
            obj=submission["object_id"],
            verb="correct",
        ),
        422,
        "ANSWER_NOT_RELEVANT",
    )
    operation = str(uuid.uuid4())
    receipt = expect(
        post(
            live,
            "submissions",
            body,
            operation=operation,
            revision=submission["revision_id"],
            obj=submission["object_id"],
            verb="correct",
        ),
        200,
    )
    # Exact retry resolves to the same receipt; a stale revision conflicts.
    assert (
        expect(
            post(
                live,
                "submissions",
                body,
                operation=operation,
                revision=submission["revision_id"],
                obj=submission["object_id"],
                verb="correct",
            ),
            200,
        )
        == receipt
    )
    failure(
        post(
            live,
            "submissions",
            body,
            revision=submission["revision_id"],
            obj=submission["object_id"],
            verb="correct",
        ),
        409,
    )
    after = get(live, "submissions", submission["object_id"])
    validate("Submission", after)
    assert after["lifecycle_state"] == "Submitted" and after["revision_id"] == receipt["revision_id"]
    assert after["data"]["answers"] == corrected
    assert after["data"]["correction_of_revision"] == submission["revision_id"]
    assert after["data"]["correction_reason"] == "Recount of the register"
    assert after["data"]["observation_ids"] == [obs["object_id"]]
    # The returned observation got a new revision (nothing edited), submitted into a new review.
    again = get(live, "observations", obs["object_id"])
    assert again["lifecycle_state"] == "Submitted" and again["data"]["value"] == "9"
    assert again["data"]["source_key"] == obs["data"]["source_key"]
    counts = db_counts(live, obs["object_id"], "action_submissions_correct")
    # Draft, submitted, returned, corrected draft, resubmitted: five revisions, nothing overwritten.
    assert counts["revisions"] == 5 and counts["audit"] == 1
    with live.db() as c:
        # The three revisions that carried 7 (draft, submitted, returned) are all still there.
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.object_revision WHERE object_id=%s AND payload->>'value'='7'",
                (obs["object_id"],),
            ).fetchone()["n"]
            == 3
        )
    assert db_counts(live, submission["object_id"], "action_submissions_correct")["receipts"] == 1
    # The corrector is an author of the corrected observation: independence still applies.
    new_workflow = open_workflow(live, obs["object_id"])
    assert new_workflow["object_id"] != workflow["object_id"]
    failure(
        post(
            live,
            "workflows",
            {"candidate_revision": new_workflow["data"]["candidate_revision"], "reason": "Mine"},
            revision=new_workflow["revision_id"],
            obj=new_workflow["object_id"],
            verb="approve",
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    approve(live, new_workflow)
    assert get(live, "observations", obs["object_id"])["lifecycle_state"] == "Approved"
    result = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    assert get(live, "calculated-results", result["object_id"])["data"]["value"] == "9"
    # Approved work is never corrected; other tenants and wrong roles are refused.
    failure(
        post(
            live, "submissions", body, revision=after["revision_id"], obj=after["object_id"], verb="correct"
        ),
        409,
        "CORRECTION_REQUIRES_RETURNED_WORK",
    )
    expect(
        post(
            live,
            "submissions",
            body,
            actor="other_tenant",
            revision=after["revision_id"],
            obj=after["object_id"],
            verb="correct",
        ),
        404,
    )
    # A partner holds no submission.correct: the response is hidden from them (404, as every
    # object action without the capability), never a 403 that would confirm it exists.
    expect(
        post(
            live,
            "submissions",
            body,
            actor="partner",
            revision=after["revision_id"],
            obj=after["object_id"],
            verb="correct",
        ),
        404,
    )
