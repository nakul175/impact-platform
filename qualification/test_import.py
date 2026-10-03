"""Qualification of import and data quality (v0.21): bounded CSV/XLSX import batches mapped by header
name to indicator instances, a unit column and one period; a staging preview that classifies every row
ACCEPTED, QUARANTINED or DUPLICATE with quality findings; and an atomic commit that writes IMPORT
observations into the existing independent observation review."""
# ruff: noqa: F811

import base64
import io
import os
import uuid
import zipfile

import pytest
from impact_api.application_executor import ApplicationExecutor, ExecutorSettings
from impact_api.contracts import validate
from test_live_application import cmd, expect
from test_measurement import get, create, action, approve, submit  # noqa: F401
from test_measurement_unit import definition
from test_native_roles import connect, denied, query  # noqa: F401
from test_period_governance import request_close
from test_planning import db_counts, failure, post
from test_forms import planned, workflow_of, workflow_version

HOUSEHOLDS = dict(code="IMP", name="Households reached")
PERCENT = dict(
    code="IMPP",
    measurement_type="PERCENTAGE",
    unit="percent",
    combination_rule="POOLED_RATIO",
    numerator_meaning="Households with safe water",
    denominator_meaning="Households visited",
    display_decimals=2,
)


def mapping(indicator, **extra):
    return {
        "unit_column": "district",
        "columns": [
            {
                "column": "households",
                "indicator_id": indicator["object_id"],
                "value_role": "VALUE",
                "unit": "households",
            }
        ],
        **extra,
    }


def batch_data(indicator, period, content, **extra):
    return {
        "format": "CSV",
        "file_name": "districts.csv",
        "content": content,
        "programme_id": indicator["data"]["programme_id"],
        "period_id": period["object_id"],
        "mode": "APPEND",
        "atomic": False,
        "mapping": mapping(indicator),
        **extra,
    }


def preview(live, batch, actor="author", status=200):
    receipt = expect(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/preview",
            actor=actor,
            method="POST",
            body=cmd({}, batch["revision_id"]),
        ),
        status,
    )
    return get(live, "imports", batch["object_id"]) if status == 200 else receipt


def commit_body(batch, accept=None, operation=None, wf=None, live=None):
    data = {"preview_hash": batch["data"]["preview"]["preview_hash"], "workflow_version": wf}
    if accept is not None:
        data["accept_warnings"] = accept
    return cmd(data, batch["revision_id"], operation)


def commit(live, batch, actor="author", status=200, accept=None, operation=None):
    return expect(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/commit",
            actor=actor,
            method="POST",
            body=commit_body(batch, accept, operation, workflow_version(live)),
        ),
        status,
    )


def outcomes(batch):
    return [
        (r["row_number"], r["row_key"], r["outcome"], r["reasons"]) for r in batch["data"]["preview"]["rows"]
    ]


@pytest.fixture
def counted(live):
    indicator, period, _ = planned(live, **HOUSEHOLDS)
    return indicator, period


def test_csv_import_preview_commit_review_and_receipts(live, counted):
    indicator, period = counted
    unit = "D" + str(uuid.uuid4())[:6]
    content = (
        "district,households,remarks\n"
        f"{unit}-001,12,first\n"
        f"{unit}-002,,blank is missing\n"
        f"{unit}-003,NA,declared not applicable\n"
        f"{unit}-004,0,zero is a value\n"
        f'00123{unit},7,"quoted, comma"\n'
        "12345678901234567890,3,twenty-digit identifier\n"
    )
    batch = create(
        live,
        "imports",
        batch_data(
            indicator, period, content, mapping=mapping(indicator, missing_codes={"NA": "NOT_APPLICABLE"})
        ),
    )
    validate("ImportJob", batch)
    assert batch["lifecycle_state"] == "Draft" and batch["data"]["source_namespace"] == "IMPORT"
    assert db_counts(live, batch["object_id"], "create_imports") == {
        "revisions": 1,
        "audit": 1,
        "outbox": 1,
        "receipts": 1,
    }
    staged = preview(live, batch)
    validate("ImportJob", staged)
    assert staged["lifecycle_state"] == "Previewed"
    view = staged["data"]["preview"]
    assert view["counts"] == {
        "rows": 6,
        "accepted": 6,
        "quarantined": 0,
        "duplicate": 0,
        "warnings": 0,
        "observations": 6,
        "unplanned": 6,
    }
    assert view["dropped_columns"] == ["remarks"]
    states = [
        (r["row_key"], r["observations"][0]["value_state"], r["observations"][0]["value"])
        for r in view["rows"]
    ]
    # A blank is MISSING and a declared token keeps its state; neither becomes zero. Leading zeros
    # and the quoted comma are kept exactly (raw beside the interpretation).
    assert states == [
        (unit + "-001", "PRESENT", "12"),
        (unit + "-002", "MISSING", None),
        (unit + "-003", "NOT_APPLICABLE", None),
        (unit + "-004", "PRESENT", "0"),
        ("00123" + unit, "PRESENT", "7"),
        ("12345678901234567890", "PRESENT", "3"),
    ]
    assert view["rows"][4]["raw"] == {"district": "00123" + unit, "households": "7"}
    # Each staged value carries the plannable source key (unit, indicator and period; never the
    # batch); this indicator's approved plan names form units only, so every value is unplanned.
    keys = [r["observations"][0]["source_key"] for r in view["rows"]]
    assert keys == [f"{u}/{indicator['object_id']}/{period['object_id']}" for u, _, _ in states]
    assert all(r["observations"][0]["planned"] is False for r in view["rows"])
    assert view["counts"]["unplanned"] == 6
    assert view["plan_check"] == {"evaluated_indicators": [indicator["object_id"]]}
    # Nothing is written by preview.
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.observation_current WHERE source_namespace='IMPORT' AND source_version=%s",
                (staged["revision_id"],),
            ).fetchone()["n"]
            == 0
        )
    operation = str(uuid.uuid4())
    receipt = commit(live, staged, operation=operation)
    # Exact retry returns the original receipt; another payload with the same identifier conflicts.
    assert commit(live, staged, operation=operation) == receipt
    other = commit_body(staged, accept=True, operation=operation, wf=workflow_version(live))
    conflict = failure(
        live.request(live.path("imports", batch["object_id"]) + "/actions/commit", method="POST", body=other),
        409,
    )
    assert conflict["code"] == "CONFLICT_OPERATION"
    done = get(live, "imports", batch["object_id"])
    validate("ImportJob", done)
    assert done["lifecycle_state"] == "Committed"
    ids = done["data"]["committed"]["observation_ids"]
    assert len(ids) == 6
    first = get(live, "observations", ids[0])
    assert first["lifecycle_state"] == "Submitted"
    assert first["data"]["source_namespace"] == "IMPORT"
    assert (
        first["data"]["source_key"] == keys[0] == f"{unit}-001/{indicator['object_id']}/{period['object_id']}"
    )
    assert first["data"]["source_version"] == staged["revision_id"]
    assert first["data"]["event_at"] == period["data"]["starts_at"]
    # Batch: draft, preview and commit revisions; one audit, receipt and outbox event per command.
    assert db_counts(live, batch["object_id"], "action_imports_commit") == {
        "revisions": 3,
        "audit": 1,
        "outbox": 3,
        "receipts": 1,
    }
    # Each observation and its review workflow carry their own audit and outbox events.
    obs_counts = db_counts(live, ids[0], "action_imports_commit")
    assert (obs_counts["revisions"], obs_counts["audit"], obs_counts["outbox"]) == (2, 1, 1)
    with live.db() as c:
        register = c.execute(
            "SELECT unit_key,observation_id::text AS o FROM impact.import_unit_register WHERE import_id=%s ORDER BY row_number",
            (batch["object_id"],),
        ).fetchall()
    assert [r["o"] for r in register] == ids
    # The importer authored every produced observation and cannot approve it.
    workflow = workflow_of(live, ids[0])
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Mine"},
        workflow["revision_id"],
    )
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve", method="POST", body=body
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    approve(live, workflow)
    assert get(live, "observations", ids[0])["data"]["approval_state"] == "APPROVED"
    # A committed batch is final: no second commit, no edit, no cancel.
    failure(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/commit",
            method="POST",
            body=commit_body(done, wf=workflow_version(live)),
        ),
        409,
    )
    failure(
        post(live, "imports", {"file_name": "x.csv"}, revision=done["revision_id"], obj=batch["object_id"]),
        409,
    )


def test_quarantine_duplicates_and_atomic_mode(live, counted):
    indicator, period = counted
    unit = "Q" + str(uuid.uuid4())[:6]
    first = create(live, "imports", batch_data(indicator, period, f"district,households\n{unit}-A,5\n"))
    commit(live, preview(live, first))
    content = (
        "district,households,date\n"
        f"{unit}-A,9,2026-08-01T00:00:00Z\n"  # already imported for this period
        f"{unit}-B,4,2026-08-02T00:00:00Z\n"
        f"{unit}-B,6,2026-08-03T00:00:00Z\n"  # same unit twice in the batch
        f"{unit}-C,abc,2026-08-04T00:00:00Z\n"
        f"{unit}-D,2.5,2026-08-05T00:00:00Z\n"  # a COUNT must be an integer
        f"{unit}-E,-3,2026-08-06T00:00:00Z\n"
        f"{unit}-F,3,2025-01-01T00:00:00Z\n"  # outside the period
        f"{unit}-G,3,03/04/2026\n"  # ambiguous date without a declared pattern
        f",3,2026-08-07T00:00:00Z\n"
        f"{unit}-H,3\n"  # short row
        f"{unit}-I,1001,2026-08-08T00:00:00Z\n"  # above the mapped maximum
        f"{unit}-J,8,2026-08-09T00:00:00Z\n"
    )
    columns = [
        {
            "column": "households",
            "indicator_id": indicator["object_id"],
            "value_role": "VALUE",
            "unit": "households",
            "minimum": "0",
            "maximum": "1000",
        }
    ]
    data = batch_data(
        indicator,
        period,
        content,
        atomic=True,
        mapping={"unit_column": "district", "event_at_column": "date", "columns": columns},
    )
    batch = preview(live, create(live, "imports", data))
    assert outcomes(batch) == [
        (2, unit + "-A", "DUPLICATE", ["DUPLICATE_UNIT_PERIOD"]),
        (3, unit + "-B", "ACCEPTED", []),
        (4, unit + "-B", "DUPLICATE", ["DUPLICATE_IN_BATCH"]),
        (5, unit + "-C", "QUARANTINED", ["VALUE_NOT_NUMERIC"]),
        (6, unit + "-D", "QUARANTINED", ["VALUE_TYPE_INVALID"]),
        (7, unit + "-E", "QUARANTINED", ["VALUE_OUT_OF_RANGE"]),
        (8, unit + "-F", "QUARANTINED", ["EVENT_OUTSIDE_PERIOD"]),
        (9, unit + "-G", "QUARANTINED", ["EVENT_AT_INVALID"]),
        (10, None, "QUARANTINED", ["UNIT_KEY_MISSING"]),
        (11, None, "QUARANTINED", ["ROW_SHAPE_INVALID"]),
        (12, unit + "-I", "QUARANTINED", ["VALUE_OUT_OF_RANGE"]),
        (13, unit + "-J", "ACCEPTED", []),
    ]
    counts = batch["data"]["preview"]["counts"]
    # Every row is accounted for exactly once.
    assert counts["rows"] == 12 == counts["accepted"] + counts["quarantined"] + counts["duplicate"]
    assert (counts["accepted"], counts["quarantined"], counts["duplicate"]) == (2, 8, 2)
    # Atomic mode commits nothing when any row is not accepted.
    assert failure(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/commit",
            method="POST",
            body=commit_body(batch, wf=workflow_version(live)),
        ),
        422,
        "IMPORT_ATOMIC_REJECTED",
    )
    with live.db() as c:
        assert (
            c.execute(
                "SELECT count(*) AS n FROM impact.observation_current WHERE source_namespace='IMPORT' AND source_version=%s",
                (batch["revision_id"],),
            ).fetchone()["n"]
            == 0
        )
    # Partial mode commits exactly the accepted rows; the rest stay on the batch as its manifest.
    edited = expect(
        post(live, "imports", {"atomic": False}, revision=batch["revision_id"], obj=batch["object_id"]), 200
    )
    batch = get(live, "imports", edited["object_id"])
    # The edit discarded the staged preview: the batch must be previewed again.
    assert batch["lifecycle_state"] == "Draft" and batch["data"]["preview"] is None
    batch = preview(live, batch)
    commit(live, batch)
    done = get(live, "imports", batch["object_id"])
    assert len(done["data"]["committed"]["observation_ids"]) == 2
    # A declared date pattern reads an ambiguous date exactly as declared.
    fixed = create(
        live,
        "imports",
        {
            **data,
            "content": f"district,households,date\n{unit}-G,3,03/08/2026\n",
            "date_pattern": "DD/MM/YYYY",
        },
    )
    staged = preview(live, fixed)
    assert outcomes(staged) == [(2, unit + "-G", "ACCEPTED", [])]
    assert staged["data"]["preview"]["rows"][0]["event_at"] == "2026-08-03T00:00:00Z"


def test_commit_refuses_a_stale_preview(live, counted):
    indicator, period = counted
    unit = "S" + str(uuid.uuid4())[:6]
    one = preview(
        live, create(live, "imports", batch_data(indicator, period, f"district,households\n{unit},1\n"))
    )
    two = preview(
        live, create(live, "imports", batch_data(indicator, period, f"district,households\n{unit},2\n"))
    )
    commit(live, one)
    # The second batch staged the unit as new; it is now a duplicate, so its preview is stale.
    failure(
        live.request(
            live.path("imports", two["object_id"]) + "/actions/commit",
            method="POST",
            body=commit_body(two, wf=workflow_version(live)),
        ),
        409,
        "PREVIEW_STALE",
    )
    failure(
        live.request(
            live.path("imports", two["object_id"]) + "/actions/commit",
            method="POST",
            body=cmd(
                {"preview_hash": "0" * 64, "workflow_version": workflow_version(live)}, two["revision_id"]
            ),
        ),
        409,
        "PREVIEW_HASH_MISMATCH",
    )
    again = preview(live, get(live, "imports", two["object_id"]))
    assert outcomes(again) == [(2, unit, "DUPLICATE", ["DUPLICATE_UNIT_PERIOD"])]
    assert failure(
        live.request(
            live.path("imports", two["object_id"]) + "/actions/commit",
            method="POST",
            body=commit_body(again, wf=workflow_version(live)),
        ),
        422,
        "IMPORT_NOTHING_TO_COMMIT",
    )
    cancelled = action(live, "imports", again, "cancel", {"reason": "Duplicate of an earlier batch"})
    assert get(live, "imports", cancelled["object_id"])["lifecycle_state"] == "Cancelled"


def test_anomaly_warns_without_blocking(live, counted):
    indicator, period = counted
    unit = "N" + str(uuid.uuid4())[:6]
    history = "district,households\n" + "".join(
        f"{unit}-{i},{v}\n" for i, v in enumerate([10, 11, 12, 9, 10, 11])
    )
    batch = preview(live, create(live, "imports", batch_data(indicator, period, history)))
    assert batch["data"]["preview"]["counts"]["warnings"] == 0
    commit(live, batch)
    for observation_id in get(live, "imports", batch["object_id"])["data"]["committed"]["observation_ids"]:
        approve(live, workflow_of(live, observation_id))
    spike = preview(
        live,
        create(
            live,
            "imports",
            batch_data(indicator, period, f"district,households\n{unit}-X,100\n{unit}-Y,10\n"),
        ),
    )
    rows = spike["data"]["preview"]["rows"]
    assert [r["outcome"] for r in rows] == ["ACCEPTED", "ACCEPTED"]
    assert rows[0]["warnings"] == ["ANOMALY_ROBUST_OUTLIER"] and rows[1]["warnings"] == []
    assert rows[0]["anomalies"][0]["median"] == "10.5" and rows[0]["anomalies"][0]["value"] == "100"
    method = spike["data"]["preview"]["anomaly_method"]
    assert method["method"] == "MODIFIED_Z_MAD" and method["blocking"] is False
    assert indicator["object_id"] in method["evaluated_indicators"]
    # A warning needs an explicit acceptance; the flag never changes the value.
    failure(
        live.request(
            live.path("imports", spike["object_id"]) + "/actions/commit",
            method="POST",
            body=commit_body(spike, wf=workflow_version(live)),
        ),
        422,
        "WARNINGS_NOT_ACCEPTED",
    )
    commit(live, spike, accept=True)
    done = get(live, "imports", spike["object_id"])
    assert done["data"]["committed"]["accepted_warnings"] is True
    assert (
        get(live, "observations", done["data"]["committed"]["observation_ids"][0])["data"]["value"] == "100"
    )


def test_ratio_components_dimensions_and_mapping_refusals(live):
    indicator, period, _ = planned(live, **PERCENT)
    unit = "R" + str(uuid.uuid4())[:6]
    columns = [
        {
            "column": "safe",
            "indicator_id": indicator["object_id"],
            "value_role": "NUMERATOR",
            "unit": "percent",
        },
        {
            "column": "visited",
            "indicator_id": indicator["object_id"],
            "value_role": "DENOMINATOR",
            "unit": "percent",
        },
    ]
    content = (
        "district,safe,visited\n"
        f"{unit}-1,50,100\n"
        f"{unit}-2,1,10\n"
        f"{unit}-3,0,0\n"  # zero denominator: UNDEFINED, never zero
        f"{unit}-4,5,\n"  # one component blank: MISSING
        f"{unit}-5,60,50\n"  # numerator above denominator
    )
    data = batch_data(indicator, period, content, mapping={"unit_column": "district", "columns": columns})
    staged = preview(live, create(live, "imports", data))
    rows = staged["data"]["preview"]["rows"]
    assert [r["outcome"] for r in rows] == ["ACCEPTED"] * 4 + ["QUARANTINED"]
    assert rows[4]["reasons"] == ["INVALID_COMPONENTS"]
    got = [(o["value_state"], o["value"], o.get("numerator")) for r in rows[:4] for o in r["observations"]]
    assert got == [
        ("PRESENT", "50", "50"),
        ("PRESENT", "10", "1"),
        ("UNDEFINED", None, None),
        ("MISSING", None, None),
    ]
    commit(live, staged)
    # Mapping refusals stop the whole batch before any row is staged.
    for change, reason in [
        ({"columns": columns[:1]}, "MAPPING_ROLE_INVALID"),
        ({"columns": [{**columns[0], "unit": "households"}, columns[1]]}, "MAPPING_UNIT_MISMATCH"),
        ({"columns": [{**columns[0], "column": "safe_renamed"}, columns[1]]}, "MAPPING_COLUMN_MISSING"),
        (
            {"dimension_columns": [{"column": "visited2", "dimension_code": "sex"}]},
            "MAPPING_DIMENSION_INVALID",
        ),
    ]:
        bad = create(live, "imports", {**data, "mapping": {**data["mapping"], **change}})
        failure(
            live.request(
                live.path("imports", bad["object_id"]) + "/actions/preview",
                method="POST",
                body=cmd({}, bad["revision_id"]),
            ),
            422,
            reason,
        )


def test_dimension_column_and_xlsx_source(live):
    indicator, period, _ = planned(live)  # sex-disaggregated household count
    unit = "X" + str(uuid.uuid4())[:6]
    columns = [
        {
            "column": "households",
            "indicator_id": indicator["object_id"],
            "value_role": "VALUE",
            "unit": "households",
        }
    ]
    sheet = [
        ["district", "households", "sex", "date"],
        [unit + "-1", 4, "F", 46235],  # 2026-08-01 as a spreadsheet serial day
        [unit + "-2", 3, "M", "2026-08-02T00:00:00Z"],
        [unit + "-3", 2, "", "2026-08-03T00:00:00Z"],  # exhaustive dimension left blank
        [unit + "-4", ("formula", 5), "F", "2026-08-04T00:00:00Z"],
    ]
    data = batch_data(
        indicator,
        period,
        xlsx(sheet),
        format="XLSX",
        file_name="districts.xlsx",
        mapping={
            "unit_column": "district",
            "event_at_column": "date",
            "columns": columns,
            "dimension_columns": [{"column": "sex", "dimension_code": "sex"}],
        },
    )
    staged = preview(live, create(live, "imports", data))
    assert outcomes(staged) == [
        (2, unit + "-1", "ACCEPTED", []),
        (3, unit + "-2", "ACCEPTED", []),
        (4, unit + "-3", "QUARANTINED", ["DIMENSION_INVALID"]),
        (5, unit + "-4", "QUARANTINED", ["FORMULA_NOT_PERMITTED"]),
    ]
    rows = staged["data"]["preview"]["rows"]
    assert rows[0]["event_at"] == "2026-08-01T00:00:00Z"
    assert rows[0]["observations"][0]["dimension_values"] == {"sex": "F"}
    commit(live, staged)
    # An unreadable or unsafe file is refused before any row is staged.
    for content, reason in [
        ("not base64!", "FILE_UNREADABLE"),
        (base64.b64encode(b"PK-not-a-zip").decode(), "FILE_UNREADABLE"),
    ]:
        bad = create(live, "imports", {**data, "content": content})
        failure(
            live.request(
                live.path("imports", bad["object_id"]) + "/actions/preview",
                method="POST",
                body=cmd({}, bad["revision_id"]),
            ),
            422,
            reason,
        )
    unsafe = xlsx(sheet, doctype=True)
    bad = create(live, "imports", {**data, "content": unsafe})
    failure(
        live.request(
            live.path("imports", bad["object_id"]) + "/actions/preview",
            method="POST",
            body=cmd({}, bad["revision_id"]),
        ),
        422,
        "FILE_UNSAFE",
    )


def test_access_tenancy_independence_and_reserved_namespace(live, counted):
    indicator, period = counted
    unit = "A" + str(uuid.uuid4())[:6]
    data = batch_data(indicator, period, f"district,households\n{unit},3\n")
    # A role without import capabilities is refused; another tenant sees nothing.
    failure(live.request(live.path("imports"), actor="enumerator", method="POST", body=cmd(data)), 403)
    batch = create(live, "imports", data)
    expect(live.request(live.path("imports", batch["object_id"]), actor="other_tenant"), 404)
    expect(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/preview",
            actor="other_tenant",
            method="POST",
            body=cmd({}, batch["revision_id"]),
        ),
        404,
    )
    # A stale expected revision conflicts.
    staged = preview(live, batch)
    failure(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/preview",
            method="POST",
            body=cmd({}, batch["revision_id"]),
        ),
        409,
    )
    # Server-owned fields are never accepted from the body.
    failure(
        post(live, "imports", {"preview": None}, revision=staged["revision_id"], obj=batch["object_id"]),
        422,
    )
    # The reviewer drafts the batch and the author commits it: both are authors of the produced
    # observation, so neither can approve it.
    other = "B" + str(uuid.uuid4())[:6]
    receipt = expect(
        live.request(
            live.path("imports"),
            actor="reviewer",
            method="POST",
            body=cmd(batch_data(indicator, period, f"district,households\n{other},4\n")),
        ),
        201,
    )
    drafted = preview(live, get(live, "imports", receipt["object_id"]))
    commit(live, drafted)
    [observation_id] = get(live, "imports", drafted["object_id"])["data"]["committed"]["observation_ids"]
    workflow = workflow_of(live, observation_id)
    body = cmd(
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Drafted it"},
        workflow["revision_id"],
    )
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve",
            actor="reviewer",
            method="POST",
            body=body,
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    # IMPORT is reserved for observations produced by a committed batch.
    direct = {
        "source_namespace": "IMPORT",
        "source_key": "x/" + unit + "/" + indicator["object_id"],
        "indicator_id": indicator["object_id"],
        "event_at": "2026-08-15T12:00:00Z",
        "captured_at": "2026-08-15T13:00:00Z",
        "capture_zone": "UTC",
        "value_state": "PRESENT",
        "value": "1",
        "source_version": "1",
    }
    failure(
        live.request(live.path("observations"), method="POST", body=cmd(direct)),
        422,
        "SOURCE_NAMESPACE_RESERVED",
    )


# Planned imports and period close (acceptance gap A5) --------------------------------------------
def import_planned(live, planned_units, calendar_id=None, period=None, year=2026):
    """An active programme (calendar year `year`) with one COUNT indicator on the fixture period (or
    `period` of `calendar_id`) whose approved collection plan names the IMPORT source key of each
    unit in `planned_units`, before any file exists: IMPORT/"<unit>/<indicator id>/<period id>"."""
    programme = create(
        live,
        "programmes",
        {
            "code": "IMPL",
            "title": "Planned imports " + str(uuid.uuid4())[:8],
            "programme_type": "Health",
            "starts_at": f"{year}-01-01T00:00:00Z",
            "ends_at": f"{year + 1}-01-01T00:00:00Z",
            "reporting_calendar_id": calendar_id or get(live, "reporting-calendars")["items"][0]["object_id"],
            "geography_id": get(live, "geographies")["items"][0]["object_id"],
        },
    )
    d = create(live, "indicator-definitions", definition(code="IMPC", name="Households counted"))
    approve(live, submit(live, "indicator-definitions", d))
    d = get(live, "indicator-definitions", d["object_id"])
    indicator = create(
        live,
        "indicator-instances",
        {
            "programme_id": programme["object_id"],
            "definition_version": d["revision_id"],
            "local_applicability": "District registers",
            "collector_id": live.fixture["actors"]["author"]["principal_id"],
            "reviewer_id": live.fixture["actors"]["reviewer"]["principal_id"],
        },
    )
    period = period or get(live, "periods", live.records["period"]["object_id"])
    plan = create(
        live,
        "collection-plans",
        {
            "title": "District register import",
            "indicator_id": indicator["object_id"],
            "period_id": period["object_id"],
            "obligations": [
                {
                    "label": unit,
                    "source_namespace": "IMPORT",
                    "source_key": f"{unit}/{indicator['object_id']}/{period['object_id']}",
                    "due_at": f"{year}-09-01T00:00:00Z",
                }
                for unit in planned_units
            ],
        },
    )
    approve(live, submit(live, "collection-plans", plan))
    action(live, "indicator-instances", indicator, "activate")
    indicator = get(live, "indicator-instances", indicator["object_id"])
    action(live, "programmes", programme, "ready")
    action(live, "programmes", get(live, "programmes", programme["object_id"]), "activate")
    return programme, indicator, period, get(live, "collection-plans", plan["object_id"])


def import_and_approve(live, indicator, period, values):
    """Import `values` ({unit: households}), commit the batch and approve every produced observation
    independently; returns the committed batch and the previewed view."""
    content = "district,households\n" + "".join(f"{u},{v}\n" for u, v in values.items())
    batch = preview(live, create(live, "imports", batch_data(indicator, period, content)))
    commit(live, batch)
    done = get(live, "imports", batch["object_id"])
    for observation_id in done["data"]["committed"]["observation_ids"]:
        approve(live, workflow_of(live, observation_id))
    return done, batch["data"]["preview"]


def close_candidate(live, programme, period):
    workflow = request_close(live, programme, period)
    candidate = get(live, "workflows", workflow["object_id"] + "/candidate", actor="reviewer")
    return workflow, candidate["record"]["data"]


def test_planned_import_units_close_the_period(live):
    """A plan names two import units before the file exists; the imported, approved values are the
    planned ones, so the period closes with coverage complete and the OFFICIAL sum from them."""
    units = ["P" + str(uuid.uuid4())[:6] + "-" + str(i) for i in range(2)]
    programme, indicator, period, _ = import_planned(live, units)
    done, view = import_and_approve(live, indicator, period, {units[0]: "12", units[1]: "30"})
    assert [r["observations"][0]["planned"] for r in view["rows"]] == [True, True]
    assert view["counts"]["unplanned"] == 0
    assert view["plan_check"] == {"evaluated_indicators": [indicator["object_id"]]}
    ids = done["data"]["committed"]["observation_ids"]
    first = get(live, "observations", ids[0])
    assert first["data"]["source_key"] == f"{units[0]}/{indicator['object_id']}/{period['object_id']}"
    assert first["data"]["approval_state"] == "APPROVED"
    # The batch that produced the value is on the observation (its revision) and in the register,
    # not in the key.
    with live.db() as c:
        register = c.execute(
            "SELECT import_id::text AS i, unit_key FROM impact.import_unit_register WHERE observation_id=%s",
            (ids[0],),
        ).fetchone()
        produced_by = c.execute(
            "SELECT object_id::text AS o FROM impact.object_revision WHERE revision_id=%s",
            (first["data"]["source_version"],),
        ).fetchone()
    assert (register["i"], register["unit_key"]) == (done["object_id"], units[0])
    assert produced_by["o"] == done["object_id"]
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    assert get(live, "calculated-results", receipt["object_id"])["data"]["value"] == "42"
    workflow, candidate = close_candidate(live, programme, period)
    assert candidate["blockers"] == []
    [entry] = candidate["entries"]
    measured = entry["coverage"]
    assert (measured["expected_count"], measured["approved_count"], measured["unplanned_count"]) == (2, 2, 0)
    assert measured["complete"] is True and measured["approval_percent"] == "100.00"
    assert {o["source_key"]: o["status"] for o in measured["obligations"]} == {
        first["data"]["source_key"]: "APPROVED",
        f"{units[1]}/{indicator['object_id']}/{period['object_id']}": "APPROVED",
    }
    approve(live, workflow)
    snapshot = next(
        s
        for s in get(live, "snapshots")["items"]
        if s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
    )
    assert snapshot["lifecycle_state"] == "Locked" and len(snapshot["data"]["result_versions"]) == 1
    # The locked period refuses a further import batch for this programme.
    late = create(live, "imports", batch_data(indicator, period, f"district,households\n{units[0]}-late,1\n"))
    assert (
        failure(
            live.request(
                live.path("imports", late["object_id"]) + "/actions/preview",
                method="POST",
                body=cmd({}, late["revision_id"]),
            ),
            409,
        )["reason_code"]
        == "PERIOD_RESTATEMENT_REQUIRED"
    )


def test_unplanned_import_units_still_block_close(live):
    """Only one of two imported units is named by the plan: the other commits and is approved, but
    close is blocked (UNPLANNED_VALUES) and nothing locks — until an independently approved plan
    amendment names the imported key exactly, after which the period closes."""
    units = ["U" + str(uuid.uuid4())[:6] + "-" + str(i) for i in range(2)]
    programme, indicator, period, plan = import_planned(live, units[:1])
    done, view = import_and_approve(live, indicator, period, {units[0]: "5", units[1]: "7"})
    assert [r["observations"][0]["planned"] for r in view["rows"]] == [True, False]
    assert view["counts"]["unplanned"] == 1 and view["counts"]["accepted"] == 2
    assert len(done["data"]["committed"]["observation_ids"]) == 2
    action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    workflow, candidate = close_candidate(live, programme, period)
    [entry] = candidate["entries"]
    assert (entry["coverage"]["approved_count"], entry["coverage"]["unplanned_count"]) == (1, 1)
    assert [b["code"] for b in candidate["blockers"]] == ["UNPLANNED_VALUES"]
    denied = action(
        live,
        "workflows",
        workflow,
        "approve",
        {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Cannot close."},
        actor="reviewer",
        status=422,
    )
    assert denied["reason_code"] == "PERIOD_CLOSE_BLOCKED"
    assert get(live, "workflows", workflow["object_id"])["lifecycle_state"] == "InReview"
    assert not any(
        s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
        for s in get(live, "snapshots")["items"]
    )
    # A reviewed plan amendment names the imported key exactly (the value already exists for this
    # indicator inside the period, so the key is available to this plan); the amended plan makes the
    # value planned, the result is recalculated against it and the period closes.
    unplanned_key = view["rows"][1]["observations"][0]["source_key"]
    assert unplanned_key == f"{units[1]}/{indicator['object_id']}/{period['object_id']}"
    proposal = expect(
        live.request(
            live.path("measurement-changes"),
            method="POST",
            body=cmd(
                {
                    "target_kind": "CollectionPlan",
                    "target_id": plan["object_id"],
                    "target_revision": plan["revision_id"],
                    "reason": "The register import also covers the second district.",
                    "proposed_data": {
                        "obligations": plan["data"]["obligations"]
                        + [
                            {
                                "label": units[1],
                                "source_namespace": "IMPORT",
                                "source_key": unplanned_key,
                                "due_at": "2026-09-01T00:00:00Z",
                            }
                        ]
                    },
                }
            ),
        ),
        201,
    )
    approve(
        live, submit(live, "measurement-changes", get(live, "measurement-changes", proposal["object_id"]))
    )
    amended = get(live, "collection-plans", plan["object_id"])
    assert amended["lifecycle_state"] == "Approved" and len(amended["data"]["obligations"]) == 2
    receipt = action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    assert get(live, "calculated-results", receipt["object_id"])["data"]["value"] == "12"
    second, candidate = close_candidate(live, programme, period)
    assert candidate["blockers"] == []
    [entry] = candidate["entries"]
    assert (entry["coverage"]["approved_count"], entry["coverage"]["unplanned_count"]) == (2, 0)
    approve(live, second)
    assert any(
        s["lifecycle_state"] == "Locked"
        and s["data"]["period_id"] == period["object_id"]
        and s["data"].get("programme_id") == programme["object_id"]
        for s in get(live, "snapshots")["items"]
    )


def calendar_periods(live, frequency, year, codes):
    """A calendar of `frequency` for `year` that the tenant administrator creates through the governed
    reference-data command (v0.26a), and its periods with the given codes, in code order."""
    receipt = expect(
        live.request(
            live.path("reporting-calendars"),
            actor="admin",
            method="POST",
            body=cmd(
                {
                    "title": frequency.title() + " import calendar " + str(uuid.uuid4())[:8],
                    "frequency": frequency,
                    "zone": "UTC",
                    "first_year": year,
                    "years": 1,
                    "reason": "A unit reports in every period",
                }
            ),
        ),
        200,
    )
    with live.db() as c:
        rows = c.execute(
            "SELECT r.object_id::text AS id FROM impact.object_registry r JOIN impact.object_revision v ON v.tenant_id=r.tenant_id AND v.revision_id=r.head_revision "
            "WHERE r.tenant_id=%s AND r.object_type='Period' AND v.payload->>'calendar_version'=%s AND v.payload->>'code' = ANY(%s) ORDER BY v.payload->>'code'",
            (live.fixture["tenant_a"], receipt["revision_id"], list(codes)),
        ).fetchall()
    assert len(rows) == len(codes)
    return receipt["object_id"], [get(live, "periods", r["id"]) for r in rows]


def monthly_periods(live, year=2025):
    """July and August of a monthly calendar, so that a unit can be imported in two periods. The year
    is kept apart from the fixture quarter (2026) so that no other test's calendar or period listing
    changes; the period lock check itself has considered every overlapping calendar since build
    0.27.0 (`test_a_locked_period_refuses_late_values_when_another_calendar_overlaps_it`)."""
    return calendar_periods(live, "MONTHLY", year, [f"{year}-07", f"{year}-08"])


def test_a_unit_imports_again_in_a_later_period_without_colliding(live):
    """The key carries the period, so the same unit and indicator imported for a second period is a
    new source identity: the tenant-wide source key register holds one key per period and the
    second batch is neither a duplicate nor a conflict."""
    calendar_id, (july, august) = monthly_periods(live)
    unit = "R" + str(uuid.uuid4())[:6]
    programme, indicator, _, _ = import_planned(live, [unit], calendar_id=calendar_id, period=july, year=2025)
    first = preview(
        live, create(live, "imports", batch_data(indicator, july, f"district,households\n{unit},3\n"))
    )
    assert first["data"]["preview"]["rows"][0]["observations"][0]["planned"] is True
    commit(live, first)
    second = preview(
        live, create(live, "imports", batch_data(indicator, august, f"district,households\n{unit},4\n"))
    )
    assert outcomes(second) == [(2, unit, "ACCEPTED", [])]
    value = second["data"]["preview"]["rows"][0]["observations"][0]
    assert value["source_key"] == f"{unit}/{indicator['object_id']}/{august['object_id']}"
    # August has no approved plan for this indicator: nothing is marked planned or unplanned.
    assert "planned" not in value and second["data"]["preview"]["counts"]["unplanned"] == 0
    assert second["data"]["preview"]["plan_check"] == {"evaluated_indicators": []}
    commit(live, second)
    with live.db() as c:
        keys = c.execute(
            "SELECT source_key FROM impact.source_key_registry WHERE tenant_id=%s AND namespace='IMPORT' AND source_key LIKE %s ORDER BY source_key",
            (live.fixture["tenant_a"], unit + "/%"),
        ).fetchall()
    assert [k["source_key"] for k in keys] == sorted(
        f"{unit}/{indicator['object_id']}/{p['object_id']}" for p in [july, august]
    )


def test_a_locked_period_refuses_late_values_when_another_calendar_overlaps_it(live):
    """Regression (build 0.27.0 integration; defect found by the v0.27 imports slice): with two
    calendars in one tenant, a value whose event lies inside a programme's locked quarter is refused
    although another calendar's later-starting month that also contains it is Open for that
    programme. Before the fix the lock check looked only at the latest-starting containing period
    (the month) and admitted the late value."""
    year = 2024
    quarterly, [quarter] = calendar_periods(live, "QUARTERLY", year, [f"{year}-Q3"])
    _, [august] = calendar_periods(live, "MONTHLY", year, [f"{year}-08"])
    assert august["data"]["starts_at"] > quarter["data"]["starts_at"]
    unit = "Q" + str(uuid.uuid4())[:6]
    programme, indicator, period, _ = import_planned(
        live, [unit], calendar_id=quarterly, period=quarter, year=year
    )
    import_and_approve(live, indicator, period, {unit: "9"})
    action(live, "indicator-instances", indicator, "calculate", {"period_id": period["object_id"]})
    workflow, candidate = close_candidate(live, programme, period)
    assert candidate["blockers"] == []
    approve(live, workflow)
    late = create(
        live,
        "observations",
        {
            "source_namespace": "MANUAL",
            "source_key": "late-" + str(uuid.uuid4()),
            "indicator_id": indicator["object_id"],
            "event_at": f"{year}-08-15T12:00:00Z",
            "captured_at": f"{year}-08-15T13:00:00Z",
            "capture_zone": "UTC",
            "value_state": "PRESENT",
            "value": "4",
            "source_version": "1",
            "dimension_values": {},
        },
    )
    denied = action(
        live, "observations", late, "submit", {"workflow_version": workflow_version(live)}, status=409
    )
    assert denied["reason_code"] == "PERIOD_RESTATEMENT_REQUIRED"
    # The month of the other calendar is still Open for this programme: only the locked quarter refuses.
    with live.db() as c:
        assert not c.execute(
            "SELECT 1 FROM impact.programme_period_state WHERE tenant_id=%s AND programme_id=%s AND period_id=%s",
            (live.fixture["tenant_a"], programme["object_id"], august["object_id"]),
        ).fetchone()


def test_bounds_are_enforced(live, counted):
    indicator, period = counted
    many = "district,households\n" + "".join(f"L{i},1\n" for i in range(501))
    batch = create(live, "imports", batch_data(indicator, period, many))
    failure(
        live.request(
            live.path("imports", batch["object_id"]) + "/actions/preview",
            method="POST",
            body=cmd({}, batch["revision_id"]),
        ),
        422,
        "IMPORT_ROW_LIMIT",
    )
    # The content field is bounded by the contract below the 256 KiB request cap.
    too_big = batch_data(indicator, period, "district,households\n" + "x" * 196608)
    failure(live.request(live.path("imports"), method="POST", body=cmd(too_big)), 422)


def test_queued_commit_fails_when_requester_loses_authority(live, counted):
    indicator, period = counted
    prefix = "R" + uuid.uuid4().hex[:8]
    content = "district,households\n" + "".join(f"{prefix}-{n:03},1\n" for n in range(51))
    batch = preview(live, create(live, "imports", batch_data(indicator, period, content)))
    commit(live, batch)
    executor = ApplicationExecutor(ExecutorSettings(live.config["app_dsn"], require_unprivileged_db=False))
    tenant = live.fixture["tenant_a"]
    principal = live.fixture["actors"]["author"]["principal_id"]
    try:
        with live.db() as c:
            c.execute(
                "UPDATE impact.tenant_principal SET active=false WHERE tenant_id=%s AND principal_id=%s",
                (tenant, principal),
            )
        executor.run_once()
    finally:
        with live.db() as c:
            c.execute(
                "UPDATE impact.tenant_principal SET active=true WHERE tenant_id=%s AND principal_id=%s",
                (tenant, principal),
            )
    failed = get(live, "imports", batch["object_id"])
    assert failed["lifecycle_state"] == "Failed"
    assert failed["data"]["processing"]["last_error_class"] == "AUTHORITY_CHANGED"
    assert failed["data"]["committed"] is None


def test_large_commit_is_queued_fenced_and_reviewed(live, counted):
    indicator, period = counted
    prefix = "A" + uuid.uuid4().hex[:8]
    content = "district,households\n" + "".join(f"{prefix}-{n:03},1\n" for n in range(51))
    batch = preview(live, create(live, "imports", batch_data(indicator, period, content)))
    queued_receipt = commit(live, batch)
    assert queued_receipt["business_state"] == "Queued"
    queued = get(live, "imports", batch["object_id"])
    validate("ImportJob", queued)
    assert queued["lifecycle_state"] == queued["data"]["processing"]["state"] == "Queued"
    assert "commit_request" not in queued["data"]
    executor = ApplicationExecutor(ExecutorSettings(live.config["app_dsn"], require_unprivileged_db=False))
    tenant = live.fixture["tenant_a"]
    job_id = queued["data"]["processing"]["job_id"]
    assert tenant in executor.due_tenants()
    assert executor.claim(tenant) == (job_id, 1)
    with live.db() as c:
        c.execute(
            "UPDATE impact.job SET lease_expires_at=statement_timestamp()-interval '1 second' "
            "WHERE tenant_id=%s AND job_id=%s",
            (tenant, job_id),
        )
    assert executor.claim(tenant) == (job_id, 2)
    assert executor.perform(tenant, job_id, 1) is False
    assert executor.fail(tenant, job_id, 1, "COMMIT_DEFECT") is False
    assert executor.perform(tenant, job_id, 2) is True
    done = get(live, "imports", batch["object_id"])
    validate("ImportJob", done)
    assert done["lifecycle_state"] == done["data"]["processing"]["state"] == "Committed"
    assert done["data"]["processing"]["attempts"] == 2
    assert len(done["data"]["committed"]["observation_ids"]) == 51
    assert executor.fail(tenant, job_id, 2, "COMMIT_DEFECT") is False
    executor.heartbeat()
    operators = expect(live.request("/v1/platform/workers", actor="admin"), 200)
    assert any(
        w["worker_id"] == executor.s.executor_id and w["kind"] == "application" and not w["stale"]
        for w in operators["items"]
    )
    first = done["data"]["committed"]["observation_ids"][0]
    workflow = workflow_of(live, first)
    failure(
        live.request(
            live.path("workflows", workflow["object_id"]) + "/actions/approve",
            method="POST",
            body=cmd(
                {"candidate_revision": workflow["data"]["candidate_revision"], "reason": "Mine"},
                workflow["revision_id"],
            ),
        ),
        403,
        "INDEPENDENCE_REQUIRED",
    )
    approve(live, workflow)


@pytest.mark.skipif(
    os.environ.get("IMPACT_NATIVE_TEST") != "1",
    reason="native PostgreSQL only: PGlite serves one superuser session and has no login-role topology",
)
def test_native_import_unit_register_is_fenced_and_insert_only(connect, live, counted):
    indicator, period = counted
    unit = "F" + str(uuid.uuid4())[:6]
    batch = preview(
        live, create(live, "imports", batch_data(indicator, period, f"district,households\n{unit},2\n"))
    )
    commit(live, batch)
    tenant_a, tenant_b = live.fixture["tenant_a"], live.fixture["tenant_b"]
    c = connect("APP")
    assert query(c, "SELECT count(*) FROM impact.import_unit_register", role="impact_app") == [(0,)]
    for statement in [
        "UPDATE impact.import_unit_register SET registered_at=now()",
        "DELETE FROM impact.import_unit_register",
    ]:
        assert "permission denied" in denied(c, statement, role="impact_app", tenant=tenant_a)
    count = "SELECT count(*) FROM impact.import_unit_register WHERE import_id=%s"
    assert query(c, count, (batch["object_id"],), role="impact_app", tenant=tenant_a) == [(1,)]
    assert query(c, count, (batch["object_id"],), role="impact_app", tenant=tenant_b) == [(0,)]
    for login, role in [("PLATFORM", "impact_platform"), ("IDENTITY", "impact_identity")]:
        other = connect(login)
        assert "permission denied" in denied(
            other, "SELECT count(*) FROM impact.import_unit_register", role=role, tenant=tenant_a
        )


def xlsx(rows, doctype=False):
    """A minimal .xlsx (first worksheet, inline strings, numbers and one formula form) built with the
    standard library, base64-encoded as the import contract carries it."""

    def ref(r, c):
        return chr(65 + c) + str(r + 1)

    cells = []
    for r, row in enumerate(rows):
        out = []
        for c, value in enumerate(row):
            if isinstance(value, tuple):
                out.append(f'<c r="{ref(r, c)}"><f>2+3</f><v>{value[1]}</v></c>')
            elif isinstance(value, (int, float)):
                out.append(f'<c r="{ref(r, c)}"><v>{value}</v></c>')
            elif value != "":
                out.append(f'<c r="{ref(r, c)}" t="inlineStr"><is><t>{value}</t></is></c>')
        cells.append(f'<row r="{r + 1}">' + "".join(out) + "</row>")
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    prolog = '<?xml version="1.0" encoding="UTF-8"?>' + ('<!DOCTYPE x [<!ENTITY a "b">]>' if doctype else "")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr(
            "xl/workbook.xml",
            f'{prolog}<workbook xmlns="{main}" xmlns:r="{rel}"><sheets><sheet name="Data" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        z.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        )
        z.writestr(
            "xl/worksheets/sheet1.xml",
            f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="{main}"><sheetData>'
            + "".join(cells)
            + "</sheetData></worksheet>",
        )
    return base64.b64encode(buffer.getvalue()).decode()
