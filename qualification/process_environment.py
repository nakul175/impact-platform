"""Read a test-owned process environment from the host kernel, never a shell listing.

Linux supplies /proc/<pid>/environ; macOS supplies CTL_KERN/KERN_PROCARGS2.
The Darwin constants/layout are verified against the installed SDK sys/sysctl.h and Apple's
XNU bsd/kern/kern_sysctl.c. A refused or omitted environment fails qualification; it never
falls back to the runner's environment. Callers must not log returned values.
"""

import ctypes
import os
import sys
from pathlib import Path

MAX_PROCESS_BYTES = 16 * 1024 * 1024


def darwin_environment(raw):
    """Skip argc, executable path/padding and exactly argc NUL-terminated arguments."""
    width = ctypes.sizeof(ctypes.c_int)
    if not isinstance(raw, bytes) or not width < len(raw) <= MAX_PROCESS_BYTES:
        raise ValueError("Invalid process argument buffer")
    argc = int.from_bytes(raw[:width], sys.byteorder, signed=True)
    if not 1 <= argc <= 65536:
        raise ValueError("Invalid process argument count")
    offset = raw.find(b"\0", width)
    if offset == -1:
        raise ValueError("Executable path is not terminated")
    offset += 1
    while offset < len(raw) and raw[offset] == 0:
        offset += 1
    for _ in range(argc):
        end = raw.find(b"\0", offset)
        if end == -1:
            raise ValueError("Process argument is not terminated")
        offset = end + 1
    entries = []
    while offset < len(raw) and raw[offset] != 0:
        end = raw.find(b"\0", offset)
        if end == -1:
            raise ValueError("Process environment is not terminated")
        entry = raw[offset:end]
        if b"=" not in entry or entry.startswith(b"="):
            raise ValueError("Process environment entry is invalid")
        entries.append(entry.decode(errors="replace"))
        offset = end + 1
    return entries


def process_environment(pid):
    if type(pid) is not int or pid < 1:
        raise ValueError("Positive process identifier required")
    if sys.platform == "linux":
        raw = Path(f"/proc/{pid}/environ").read_bytes()
        return [entry.decode(errors="replace") for entry in raw.split(b"\0") if entry]
    if sys.platform != "darwin":
        raise RuntimeError("Kernel process-environment inspection is unsupported on this host")
    libc = ctypes.CDLL(None, use_errno=True)
    query = libc.sysctl
    query.argtypes = [
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.c_void_p,
        ctypes.c_size_t,
    ]
    query.restype = ctypes.c_int
    # Installed Darwin SDK: CTL_KERN=1, KERN_PROCARGS2=49.
    mib = (ctypes.c_int * 3)(1, 49, pid)
    length = ctypes.c_size_t()
    if query(mib, 3, None, ctypes.byref(length), None, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    if not ctypes.sizeof(ctypes.c_int) < length.value <= MAX_PROCESS_BYTES:
        raise RuntimeError("Kernel process-environment size is invalid")
    buffer = ctypes.create_string_buffer(length.value)
    if query(mib, 3, buffer, ctypes.byref(length), None, 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    return darwin_environment(buffer.raw[: length.value])
