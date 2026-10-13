"""Exercise actual runner argument gates without creating files or starting runtimes."""

import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


class ReachedFixturePreflight(Exception):
    """Stop accepted CLI arguments before fixture reads, files or runtime actions."""


@pytest.fixture
def runner(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("pooler_browser_cli_runner", ROOT / "scripts/run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    reached = []

    def stop_before_fixture():
        reached.append(True)
        raise ReachedFixturePreflight

    monkeypatch.setattr(module, "preflight_fixture", stop_before_fixture)
    return module, reached, tmp_path


@pytest.mark.parametrize("mode", ["test", "ai-diagnosis-browser"])
def test_native_pooler_supported_modes_reach_preflight_before_any_runtime(runner, monkeypatch, mode):
    module, reached, local = runner
    monkeypatch.setattr(sys, "argv", ["run.py", mode, "--native", "--pooler", "pgbouncer"])
    with pytest.raises(ReachedFixturePreflight):
        module.main()
    assert reached == [True]
    assert list(local.iterdir()) == [], "Accepted arguments must stop before creating a local run directory"


@pytest.mark.parametrize(
    "arguments",
    [
        ["test"],
        ["ai-diagnosis-browser"],
        ["dev"],
        ["dev", "--native"],
        ["ai-enablement-browser", "--native"],
        ["check", "--native"],
    ],
)
def test_pooler_unsupported_modes_refuse_before_preflight_or_runtime(runner, monkeypatch, capsys, arguments):
    module, reached, local = runner
    monkeypatch.setattr(sys, "argv", ["run.py", *arguments, "--pooler", "pgbouncer"])
    with pytest.raises(SystemExit) as refused:
        module.main()
    assert refused.value.code == 2
    assert reached == []
    assert list(local.iterdir()) == []
    assert "--pooler pgbouncer" in capsys.readouterr().err
