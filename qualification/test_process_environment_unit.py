"""Qualification reads the actual child environment without mistaking argv for credentials."""

import ctypes
import subprocess
import sys
import time

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


@pytest.mark.parametrize("pid", [0, -1, "1", True, 1 << 31, 1 << 64])
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
        # The kernel exposes the new image's environment only once the exec has finished; a loaded
        # runner can be observed in between, so the read is retried for a bounded time.
        deadline = time.monotonic() + 10
        while True:
            entries = process_environment(child.pid)
            present = variable + "=" + value in entries
            if present or time.monotonic() > deadline:
                break
            time.sleep(0.05)
        assert present, "Actual child marker must be visible"
        keys = [entry.split("=", 1)[0] for entry in entries]
        assert "PGPASSWORD" not in keys, "An argument must never be mistaken for an environment variable"
        assert "IMPACT_ADMIN_DSN" not in keys, "Caller environment must not substitute for the child"
    finally:
        child.communicate(b"x", timeout=10)


def test_linux_environment_read_is_bounded_before_accepting_any_marker(monkeypatch):
    from io import BytesIO
    import process_environment as inspector

    class SyntheticProc:
        def __init__(self, path):
            assert path == "/proc/123/environ"

        def open(self, mode):
            assert mode == "rb"
            return BytesIO(b"TOLA_MARKER=present\0" + b"X" * 100)

    monkeypatch.setattr(inspector.sys, "platform", "linux")
    monkeypatch.setattr(inspector, "MAX_PROCESS_BYTES", 32)
    monkeypatch.setattr(inspector, "Path", SyntheticProc)
    with pytest.raises(RuntimeError, match="size is invalid"):
        inspector.process_environment(123)


def test_darwin_kernel_growth_cannot_be_silently_truncated_into_a_valid_environment(monkeypatch):
    import process_environment as inspector

    raw = packed([b"python"], [b"TOLA_MARKER=present"])

    class Query:
        def __init__(self):
            self.calls = 0

        def __call__(self, mib, count, buffer, length, _new, _size):
            self.calls += 1
            assert list(mib) == [1, 49, 123] and count == 3
            metadata = ctypes.cast(length, ctypes.POINTER(ctypes.c_size_t))
            if self.calls == 1:
                metadata.contents.value = len(raw)
            else:
                ctypes.memmove(buffer, raw, len(raw))
                metadata.contents.value = len(raw) + 1
            return 0

    class Library:
        sysctl = Query()

    monkeypatch.setattr(inspector.sys, "platform", "darwin")
    monkeypatch.setattr(inspector.ctypes, "CDLL", lambda *_args, **_kwargs: Library())
    with pytest.raises(RuntimeError, match="returned size is invalid"):
        inspector.process_environment(123)
