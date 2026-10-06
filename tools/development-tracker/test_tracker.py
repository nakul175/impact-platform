"""Offline tracker qualification. All data here is synthetic and temporary."""

from __future__ import annotations

import copy
import io
import json
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from build_backlog import build
from tracker import DATA, MAX_BYTES, ROOT, Handler, read_json, snapshot, validate_sprint, validate_stream
from update import apply_patch, atomic_json


@pytest.fixture
def source(tmp_path: Path) -> Path:
    data = tmp_path / "state"
    (data / "streams").mkdir(parents=True)
    sprint = copy.deepcopy(read_json(DATA / "sprint.json"))
    sprint["stream_ids"] = ["synthetic"]
    sprint["rollup"].update(integrated_increments=0, verified_increments=0)
    atomic_json(data / "sprint.json", sprint)
    original = copy.deepcopy(read_json(DATA / "streams/tracker.json"))
    original.update(
        id="synthetic",
        status="BUILDING",
        delivered=[],
        evidence=[],
        history=[],
        updated_at="2026-10-05T08:30:00Z",
    )
    atomic_json(data / "streams/synthetic.json", original)
    atomic_json(data / "backlog.json", read_json(DATA / "backlog.json"))
    return data


def test_updates_are_read_from_files_without_restarting_the_server(source: Path) -> None:
    assert snapshot(source)["streams"][0]["summary"] != "Synthetic review completed"
    apply_patch(
        source, {"summary": "Synthetic review completed", "status": "REVIEWING"}, "synthetic", root=None
    )
    result = snapshot(source)
    assert result["streams"][0]["summary"] == "Synthetic review completed"
    assert result["streams"][0]["status"] == "REVIEWING"
    assert result["streams"][0]["history"][-1]["summary"] == "Synthetic review completed"


@pytest.mark.parametrize("integrated", [0, 2])
def test_elapsed_time_cannot_complete_or_advance_a_workstream(source: Path, integrated: int) -> None:
    sprint = read_json(source / "sprint.json")
    sprint["rollup"]["integrated_increments"] = integrated
    atomic_json(source / "sprint.json", sprint)
    before = read_json(source / "streams/synthetic.json")
    with patch("tracker.utc_now", return_value="2026-10-06T23:59:59Z"):
        result = snapshot(source)
    assert result["streams"][0] == before
    assert result["sprint"]["rollup"]["integrated_increments"] == integrated
    assert result["streams"][0]["status"] == "BUILDING"


@pytest.mark.parametrize("bad_id", ["../sprint", "synthetic/other", "/tmp/state", "", "Other"])
def test_updater_refuses_path_traversal_or_unknown_identifiers(source: Path, bad_id: str) -> None:
    before = (source / "sprint.json").read_bytes()
    with pytest.raises(ValueError):
        apply_patch(source, {"summary": "refused"}, bad_id, root=None)
    assert (source / "sprint.json").read_bytes() == before


@pytest.mark.parametrize(
    "patch_data",
    [{"percent_complete": 95}, {"id": "other"}, {"updated_at": "2099-01-01T00:00:00Z"}, {"history": []}],
)
def test_unknown_or_owned_fields_leave_the_saved_file_unchanged(source: Path, patch_data: dict) -> None:
    path = source / "streams/synthetic.json"
    before = path.read_bytes()
    with pytest.raises(ValueError):
        apply_patch(source, patch_data, "synthetic", root=None)
    assert path.read_bytes() == before


def test_unestimated_eta_must_remain_unknown(source: Path) -> None:
    bad = {
        "earliest": "2026-10-05T09:00:00Z",
        "latest": "2026-10-05T09:30:00Z",
        "confidence": "UNESTIMATED",
        "basis": "Unknown scope",
    }
    with pytest.raises(ValueError):
        apply_patch(source, {"eta": bad}, "synthetic", root=None)


def test_reversed_estimate_cannot_replace_the_old_record(source: Path) -> None:
    before = (source / "streams/synthetic.json").read_bytes()
    bad = {
        "earliest": "2026-10-05T10:00:00Z",
        "latest": "2026-10-05T09:30:00Z",
        "confidence": "LOW",
        "basis": "Synthetic",
    }
    with pytest.raises(ValueError):
        apply_patch(source, {"eta": bad}, "synthetic", root=None)
    assert (source / "streams/synthetic.json").read_bytes() == before


def test_stale_expected_timestamp_refuses_update(source: Path) -> None:
    before = (source / "streams/synthetic.json").read_bytes()
    with pytest.raises(ValueError):
        apply_patch(source, {"summary": "refused"}, "synthetic", "2026-10-05T08:29:59Z", root=None)
    assert (source / "streams/synthetic.json").read_bytes() == before


def test_atomic_replace_failure_retains_complete_previous_json_and_cleans_temporary_file(
    source: Path,
) -> None:
    path = source / "streams/synthetic.json"
    before = path.read_bytes()
    with patch("update.os.replace", side_effect=OSError("synthetic replace failure")), pytest.raises(OSError):
        apply_patch(source, {"summary": "not committed"}, "synthetic", root=None)
    assert path.read_bytes() == before
    assert list(path.parent.glob(".tracker-*.tmp")) == []


def test_history_is_bounded_and_heartbeat_does_not_fabricate_progress(source: Path) -> None:
    for index in range(105):
        apply_patch(source, {"summary": f"Synthetic source update {index}"}, "synthetic", root=None)
    final = read_json(source / "streams/synthetic.json")
    assert len(final["history"]) == 100
    apply_patch(source, {}, "synthetic", root=None)
    assert read_json(source / "streams/synthetic.json")["history"] == final["history"]


def test_missing_stream_returns_explicit_unavailable_state_instead_of_fake_progress(source: Path) -> None:
    (source / "streams/synthetic.json").unlink()
    result = snapshot(source)
    assert result["streams"] == []
    assert result["errors"] == [
        {
            "stream_id": "synthetic",
            "message": "This stream file is missing or invalid; its progress is not available.",
        }
    ]


def test_invalid_stream_is_isolated_and_never_exposes_raw_contents(source: Path) -> None:
    (source / "streams/synthetic.json").write_text("synthetic invalid source content")
    result = snapshot(source)
    assert result["streams"] == []
    assert "synthetic invalid source content" not in json.dumps(result)


def test_duplicate_json_keys_and_oversized_files_are_refused(tmp_path: Path) -> None:
    file = tmp_path / "source.json"
    file.write_text('{"status":"BUILDING","status":"COMPLETE"}')
    with pytest.raises(ValueError):
        read_json(file)
    file.write_bytes(b" " * (MAX_BYTES + 1))
    with pytest.raises(ValueError):
        read_json(file)


def test_symlinked_tracker_sources_are_refused(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text("{}")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(ValueError):
        read_json(link)


def test_complete_requires_actual_named_deliverables_and_existing_evidence(source: Path) -> None:
    with pytest.raises(ValueError):
        apply_patch(source, {"status": "COMPLETE"}, "synthetic", root=None)
    evidence = {
        "title": "Synthetic record",
        "path": "docs/development-tracker/does-not-exist.json",
        "result": "NOT_RUN",
        "scope": "Synthetic negative check",
        "recorded_at": "2026-10-05T08:30:00Z",
    }
    with pytest.raises(ValueError):
        apply_patch(
            source,
            {"status": "COMPLETE", "delivered": ["Synthetic deliverable"], "evidence": [evidence]},
            "synthetic",
            root=ROOT,
        )


@pytest.mark.parametrize(
    "path", ["../../secrets.env", "/tmp/evidence.json", "docs/.local/result.json", "docs/secrets.env"]
)
def test_evidence_paths_cannot_reference_ignored_or_external_files(source: Path, path: str) -> None:
    evidence = {
        "title": "Refused",
        "path": path,
        "result": "NOT_RUN",
        "scope": "Synthetic",
        "recorded_at": "2026-10-05T08:30:00Z",
    }
    with pytest.raises(ValueError):
        apply_patch(source, {"evidence": [evidence]}, "synthetic", root=None)


def test_bounded_counts_do_not_accept_percentages_or_more_agents_than_available(source: Path) -> None:
    sprint = read_json(source / "sprint.json")
    rollup = dict(sprint["rollup"], active_agents=5)
    with pytest.raises(ValueError):
        apply_patch(source, {"rollup": rollup}, root=None)
    with pytest.raises(ValueError):
        apply_patch(source, {"overall_completion": 70}, root=None)
    rollup = dict(sprint["rollup"], verified_increments=1, integrated_increments=0)
    with pytest.raises(ValueError):
        apply_patch(source, {"rollup": rollup}, root=None)


def test_scope_index_assigns_all_requirements_once_without_mutating_source_registers() -> None:
    paths = [ROOT / "docs/COMPLETION-LEDGER.json", ROOT / "docs/nonprofit-ai/v1.0/requirements.json"]
    before = [path.read_bytes() for path in paths]
    result = build()
    core = [item for domain in result["domains"] for item in domain["impact_requirement_ids"]]
    ai = [item for domain in result["domains"] for item in domain["ai_requirement_ids"]]
    assert len(core) == len(set(core)) == 307
    assert len(ai) == len(set(ai)) == 40
    assert result["baseline"]["impact_accepted"] == 0
    assert [path.read_bytes() for path in paths] == before


def test_http_routes_do_not_serve_arbitrary_files_or_support_writes() -> None:
    handler = object.__new__(Handler)
    handler.server = SimpleNamespace(server_address=("127.0.0.1", 8170))
    handler.headers = Message()
    handler.headers["Host"] = "127.0.0.1:8170"
    handler.path = "/../../.local/credentials.json"
    with patch.object(handler, "respond") as respond:
        handler.do_GET()
    respond.assert_called_once_with(404, b"Not found", "text/plain; charset=utf-8")
    assert not hasattr(Handler, "do_POST")
    assert not hasattr(Handler, "do_PUT")


@pytest.mark.parametrize(
    "host",
    [
        "rebound.example.test:8170",
        "127.0.0.1:8171",
        "localhost",
        "127.0.0.1:8170@rebound.example.test",
        "localhost.:8170",
        "[::1]:8170",
        None,
    ],
)
def test_wrong_or_missing_host_refuses_status_without_loading_any_source(host: str | None) -> None:
    handler = object.__new__(Handler)
    handler.server = SimpleNamespace(server_address=("127.0.0.1", 8170))
    handler.headers = Message()
    if host is not None:
        handler.headers["Host"] = host
    handler.path = "/api/status"
    with patch.object(handler, "respond") as respond, patch("tracker.snapshot") as read:
        handler.do_GET()
    read.assert_not_called()
    respond.assert_called_once_with(421, b"Unrecognised local host", "text/plain; charset=utf-8")


def test_duplicate_host_is_refused_even_when_each_value_is_loopback() -> None:
    handler = object.__new__(Handler)
    handler.server = SimpleNamespace(server_address=("127.0.0.1", 8170))
    handler.headers = Message()
    handler.headers["Host"] = "127.0.0.1:8170"
    handler.headers["Host"] = "localhost:8170"
    handler.path = "/api/status"
    with patch.object(handler, "respond") as respond, patch("tracker.snapshot") as read:
        handler.do_GET()
    read.assert_not_called()
    assert respond.call_args.args[0] == 421


@pytest.mark.parametrize("host", ["127.0.0.1:8170", "localhost:8170", "LOCALHOST:8170"])
def test_only_the_actual_loopback_authority_can_read_live_source(host: str) -> None:
    handler = object.__new__(Handler)
    handler.server = SimpleNamespace(server_address=("127.0.0.1", 8170))
    handler.headers = Message()
    handler.headers["Host"] = host
    handler.path = "/api/status"
    with (
        patch.object(handler, "respond") as respond,
        patch("tracker.snapshot", return_value={"synthetic": "safe"}) as read,
    ):
        handler.do_GET()
    read.assert_called_once_with()
    assert respond.call_args.args[0] == 200


def test_http_response_has_read_only_security_headers() -> None:
    handler = object.__new__(Handler)
    handler.wfile = io.BytesIO()
    with (
        patch.object(handler, "send_response") as status,
        patch.object(handler, "send_header") as headers,
        patch.object(handler, "end_headers"),
    ):
        handler.respond(200, b"{}", "application/json")
    status.assert_called_once_with(200)
    values = dict(call.args for call in headers.call_args_list)
    assert values["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in values["Content-Security-Policy"]
    assert "connect-src 'self'" in values["Content-Security-Policy"]
    assert handler.wfile.getvalue() == b"{}"


def test_initial_source_records_follow_the_closed_contract() -> None:
    result = snapshot()
    validate_sprint(result["sprint"])
    for stream in result["streams"]:
        validate_stream(stream, stream["id"])
    assert result["errors"] == []
