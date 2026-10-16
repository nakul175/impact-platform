"""Execute the actual browser-local model, including isolation and invalid transitions."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_disposable_public_workspace_model():
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--test", "tools/browser/public-sandbox-model.test.mjs"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
