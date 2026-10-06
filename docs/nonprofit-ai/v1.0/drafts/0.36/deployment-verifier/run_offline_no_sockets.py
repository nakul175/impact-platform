"""Run the exact copied 23 offline controls with actual socket/DNS calls refused."""

from pathlib import Path
import runpy
import socket
import sys
from unittest.mock import patch

# Import transport/TLS modules before patching the socket class. MockTransport
# needs those classes to exist, but no test may create a network socket.
import httpx  # noqa: F401


def refused(*args, **kwargs):
    raise AssertionError("Network sockets and DNS are forbidden in private offline preparation")


with (
    patch.object(socket, "socket", side_effect=refused),
    patch.object(socket, "create_connection", side_effect=refused),
    patch.object(socket, "getaddrinfo", side_effect=refused),
):
    sys.argv = [str(Path(__file__).with_name("test_offline.py"))]
    runpy.run_path(sys.argv[0], run_name="__main__")
