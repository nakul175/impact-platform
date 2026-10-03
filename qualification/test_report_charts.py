"""Charts in frozen report packages (v0.27): bars of bound OFFICIAL results of the locked snapshot,
optionally beside the target the snapshot pinned, rendered deterministically as inline SVG (HTML)
and vector drawings (PDF) and as data tables (XLSX, DOCX). Values are built end to end through the
review, calculation and period-close flow of test_dashboards; nothing is recomputed for a chart.
"""
# ruff: noqa: F811

import hashlib
import uuid

import pytest

from impact_api.export_render import build_model, render
from impact_api.report_charts import chart_models, chart_svg
from impact_api.reporting import REPORT_CSP, REPORT_STYLE_HASH
from test_dashboards import RATIO, calculate, card, close, measure, ratio_source, target
from test_live_application import cmd, expect
from test_measurement import approve, create, get, submit
from test_report_exports import drain, pdf_text, docx_text, request_export, xlsx_rows, export_row
from test_worker import make_worker

# -- pure ------------------------------------------------------------------------------------------


def chart_model(**series_changes):
    report = {
        "language": "en",
        "sections": [
            {
                "section_code": "results",
                "heading": "Results",
                "narrative": "Coverage reached {{water}}.",
                "bindings": [
                    {"binding_code": "water", "result_revision": "r1"},
                    {"binding_code": "latrines", "result_revision": "r2"},
                    {"binding_code": "blank", "result_revision": "r3"},
                ],
                "charts": [
                    {
                        "chart_code": "access",
                        "title": "Access versus target",
                        "kind": "BAR",
                        "series": [
                            {"binding_code": "water", "label": "Water", "target_revision": "t1"},
                            {"binding_code": "latrines", "target_revision": "t2"},
                            {"binding_code": "blank"},
                        ],
                    }
                ],
            }
        ],
    }
    values = {
        ("results", "water"): {
            "displayed_value": "46.36",
            "unit": "PERCENT",
            "value": "46.363636363636",
            "value_state": "PRESENT",
            "display_decimals": 2,
        },
        ("results", "latrines"): {
            "displayed_value": "-12.50",
            "unit": "PERCENT",
            "value": "-12.5",
            "value_state": "PRESENT",
            "display_decimals": 2,
        },
        ("results", "blank"): {
            "displayed_value": "Undefined",
            "unit": "PERCENT",
            "value": None,
            "value_state": "UNDEFINED",
            "display_decimals": 2,
        },
    }
    targets = {
        "t1": {"value_state": "PRESENT", "value": "50"},
        "t2": {"value_state": "MISSING", "value": None},
    }
    return build_model(
        "r-1",
        "rev-1",
        report,
        {"title": "Quarterly report"},
        "s-1",
        {"locked_at": "2026-09-30T10:00:00+00:00"},
        "ab" * 32,
        values,
        targets,
    )


def test_chart_renders_are_byte_deterministic_and_draw_only_stored_values():
    document = chart_model()
    chart = document["sections"][0]["charts"][0]
    assert chart["unit"] == "PERCENT" and chart["with_targets"] is True
    # An UNDEFINED result draws no bar and is never shown as zero; a missing target is "not set".
    bars = {bar["binding_code"]: bar for bar in chart["bars"]}
    assert bars["blank"]["value"] is None and bars["blank"]["displayed_value"] == "Undefined"
    assert bars["water"]["target_displayed_value"] == "50.00" and bars["latrines"]["target_value"] is None
    svg = chart_svg(chart)
    assert svg == chart_svg(chart)
    assert 'role="img"' in svg and "<title" in svg and "<desc" in svg
    # Two official bars, one target bar and two legend swatches; no bar for the missing target.
    assert svg.count("<rect") == 5
    assert "46.36" in svg and "50.00" in svg and "-12.50" in svg and "Undefined" in svg
    assert 'height="0"' not in svg
    for format in ["PDF", "XLSX", "DOCX"]:
        first, second = render(format, document), render(format, document)
        assert hashlib.sha256(first).digest() == hashlib.sha256(second).digest(), format
    pdf = pdf_text(render("PDF", document))
    assert "(Access versus target) Tj" in pdf and "(46.36) Tj" in pdf and "(50.00) Tj" in pdf
    sheets = xlsx_rows(render("XLSX", document))
    rows = [[value for value, _ in line] for line in sheets["Charts"]]
    assert ["Water", "46.36", "PERCENT", "50.00", "PRESENT"] in rows
    # openpyxl reads an empty text cell back as None: no target, no number, never 0.
    assert ["blank", "Undefined", "PERCENT", None, "UNDEFINED"] in rows
    # Every filled cell is text (blank separator cells read back as empty, never as a number).
    assert all(kind == "s" for line in sheets["Charts"] for value, kind in line if value is not None)
    lines = docx_text(render("DOCX", document))
    assert "Water | 46.36 | PERCENT | 50.00 | PRESENT" in lines


def test_chart_model_refuses_unknown_references():
    section = {
        "section_code": "s",
        "charts": [{"chart_code": "c", "title": "T", "series": [{"binding_code": "x"}]}],
    }
    with pytest.raises(KeyError):
        chart_models(section, {})


# -- live ------------------------------------------------------------------------------------------


def package_with_chart(live, *, series_changes=None, chart_changes=None, keys=2):
    """An active programme closed through the real flow (51/110 = 46.36 OFFICIAL, target 50) and
    the report data binding its OFFICIAL result with one official-versus-target chart."""
    programme, indicator, period, sources = measure(live, keys=keys)
    ratio_source(live, indicator, sources[0], "50", "100")
    ratio_source(live, indicator, sources[1], "1", "10")
    calculate(live, indicator, period)
    goal = target(live, indicator, period, "50")
    close(live, programme, period)
    body, row = card(live, programme, indicator, period)
    series = {"binding_code": "water", "label": "Safe water", "target_revision": goal["revision_id"]}
    series.update(series_changes or {})
    chart = {"chart_code": "access", "title": "Safe water versus target", "kind": "BAR", "series": [series]}
    chart.update(chart_changes or {})
    data = {
        "template_version": live.records["report_template"]["revision_id"],
        "snapshot_id": body["snapshot"]["snapshot_id"],
        "language": "en",
        "audience_class": "INTERNAL",
        "sections": [
            {
                "section_code": "results",
                "heading": "Verified results",
                "narrative": "Safe water access reached {{water}} against the approved target.",
                "bindings": [
                    {
                        "binding_code": "water",
                        "result_revision": row["official"]["result_revision"],
                        "display_decimals": 2,
                        "unit": RATIO["unit"],
                    }
                ],
                "evidence_revisions": [],
                "charts": [chart],
            }
        ],
    }
    return data, programme, indicator, period, goal


def test_report_with_chart_is_frozen_rendered_and_exported_from_the_snapshot(live):
    data, programme, indicator, period, goal = package_with_chart(live)
    report = create(live, "reports", data)
    approve(live, submit(live, "reports", report))
    report = get(live, "reports", report["object_id"])
    assert report["lifecycle_state"] == "Approved"
    response = live.request(live.path("reports", report["object_id"]) + "/export")
    assert response.status_code == 200, response.text
    html = response.text
    assert response.headers["content-security-policy"] == REPORT_CSP and REPORT_STYLE_HASH in REPORT_CSP
    assert '<svg class="report-chart"' in html and 'role="img"' in html
    assert "Safe water versus target" in html and "46.36" in html and "50.00" in html
    assert "Chart data: Safe water versus target" in html
    assert "<script" not in html
    # Two reads render identical bytes: the chart comes from the frozen package only.
    assert live.request(live.path("reports", report["object_id"]) + "/export").text == html
    # The worker renders the same chart into the PDF, XLSX and DOCX artifacts.
    jobs = {format: request_export(live, report, format)["job_id"] for format in ["PDF", "XLSX", "DOCX"]}
    drain(make_worker(live), live.fixture["tenant_a"])
    for format, job_id in jobs.items():
        assert export_row(live, report, job_id)["state"] == "Succeeded", format
    with live.db() as c:
        bodies = {
            row["format"]: bytes(row["body"])
            for row in c.execute(
                "SELECT format,body FROM impact.report_export_artifact WHERE job_id=ANY(%s::uuid[])",
                (list(jobs.values()),),
            ).fetchall()
        }
    pdf = pdf_text(bodies["PDF"])
    assert "(Safe water versus target) Tj" in pdf and "(46.36) Tj" in pdf and "(50.00) Tj" in pdf
    rows = [[value for value, _ in line] for line in xlsx_rows(bodies["XLSX"])["Charts"]]
    assert ["Safe water", "46.36", "percent", "50.00", "PRESENT"] in rows
    assert "Safe water | 46.36 | percent | 50.00 | PRESENT" in docx_text(bodies["DOCX"])
    # A chart-less package of the same shape keeps a different digest: charts are reconciled.
    with live.db() as c:
        binding = c.execute(
            "SELECT reconciliation_digest FROM impact.report_package_binding WHERE report_revision=%s",
            (report["revision_id"],),
        ).fetchone()
    assert bytes(binding["reconciliation_digest"]).hex() in html


def refused(live, data, status=422):
    return expect(live.request(live.path("reports"), method="POST", body=cmd(data)), status)


def with_chart(data, **changes):
    chart = {**data["sections"][0]["charts"][0], **changes}
    return {**data, "sections": [{**data["sections"][0], "charts": [chart]}]}


def test_chart_references_are_validated_against_the_section_and_the_snapshot(live):
    data, programme, indicator, period, goal = package_with_chart(live)
    # A bar must be one of the section's own bindings.
    unknown = refused(live, with_chart(data, series=[{"binding_code": "nope"}]))
    assert unknown["reason_code"] == "UNKNOWN_CHART_BINDING"
    # A target must be one the snapshot pinned.
    foreign = with_chart(data, series=[{"binding_code": "water", "target_revision": str(uuid.uuid4())}])
    assert refused(live, foreign)["reason_code"] == "TARGET_NOT_IN_SNAPSHOT"
    # A pinned target of another programme's close never decorates this bar.
    other_data, *_ = package_with_chart(live)
    other_target = other_data["sections"][0]["charts"][0]["series"][0]["target_revision"]
    mismatch = with_chart(data, series=[{"binding_code": "water", "target_revision": other_target}])
    assert refused(live, mismatch)["reason_code"] in {"TARGET_NOT_IN_SNAPSHOT", "CHART_TARGET_MISMATCH"}
    # Duplicate chart codes and an unknown chart kind are refused; an empty series list too.
    twice = {**data, "sections": [{**data["sections"][0], "charts": [data["sections"][0]["charts"][0]] * 2}]}
    assert refused(live, twice)["reason_code"] == "DUPLICATE_REPORT_CHART"
    assert refused(live, with_chart(data, kind="PIE"))["code"] == "VALIDATION_FAILED"
    assert refused(live, with_chart(data, series=[]))["code"] == "VALIDATION_FAILED"
    # A target-less chart over the same binding is a valid package.
    plain = create(live, "reports", with_chart(data, series=[{"binding_code": "water", "label": "Water"}]))
    assert plain["data"]["sections"][0]["charts"][0]["series"] == [
        {"binding_code": "water", "label": "Water"}
    ]
