"""Qualification reads the actual child environment without mistaking argv for credentials."""

import ctypes
import subprocess
import sys

import pytest
from process_environment import darwin_environment, process_environment


def packed(argv, environment):
    count = len(argv).to_bytes(ctypes.sizeof(ctypes.c_int), sys.byteorder, signed=True)
    return count + b"/synthetic/python\0\0\0" + b"\0".join(argv) + b"\0" + b"\0".join(environment) + b"\0\0"


def test_darwin_parser_retains_whitespace_values_and_ignores_argument_lookalikes():
    raw = packed(
        [b"python", b"PGPASSWORD=argument-only", b"", b"path with spaces"],
        [b"IMPACT_CONFIG_FILE=/private/tmp/test path/config.json", b"SYNTHETIC=value with = and spaces"],
    )
    assert darwin_environment(raw) == [
        "IMPACT_CONFIG_FILE=/private/tmp/test path/config.json",
        "SYNTHETIC=value with = and spaces",
    ]


def test_empty_environment_is_not_replaced_by_the_runner_environment():
    assert darwin_environment(packed([b"python"], [])) == []


@pytest.mark.parametrize(
    "raw",
    [b"", b"bad", b"\xff" * 8, packed([b"python"], [b"missing-equals"]), packed([b"python"], [b"=bad"])],
)
def test_malformed_kernel_buffers_are_refused(raw):
    with pytest.raises(ValueError):
        darwin_environment(raw)


@pytest.mark.parametrize("pid", [0, -1, "1", True])
def test_process_identifier_is_closed(pid):
    with pytest.raises(ValueError):
        process_environment(pid)


def test_actual_synthetic_child_environment_is_read_from_the_kernel():
    variable, value = "TOLA_SYNTHETIC_ENVIRONMENT_MARKER", "value with spaces=kept"
    child = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.buffer.read(1)", "PGPASSWORD=argument-only"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={variable: value},
    )
    try:
        entries = process_environment(child.pid)
        present = variable + "=" + value in entries
        assert present, "Actual child marker must be visible"
        keys = [entry.split("=", 1)[0] for entry in entries]
        assert "PGPASSWORD" not in keys, "An argument must never be mistaken for an environment variable"
        assert "IMPACT_ADMIN_DSN" not in keys, "Caller environment must not substitute for the child"
    finally:
        child.communicate(b"x", timeout=10)
