"""A loopback receiver for the alert webhook (deploy/ops_alerts.py notify), for the CI container
stack and for an owner who wants to see what a channel would get (standard library only).

    python3 scripts/webhook_receiver.py --port 18080 --log received.jsonl

Every POST is appended to the log as one JSON line: {"received_at", "path", "signature_valid"
(None without ALERT_WEBHOOK_SECRET in the environment), "body"}. Answers 200 to a POST whose body
is JSON, 400 otherwise, 401 when a secret is configured and the signature does not verify."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "deploy"))
from ops_alerts import verify_signature  # noqa: E402


def make_handler(log_path, secret):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):  # quiet
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(min(length, 1_000_000))
            try:
                body = json.loads(raw)
            except ValueError:
                self.send_response(400)
                self.end_headers()
                return
            valid = None
            if secret:
                valid = verify_signature(
                    secret, self.headers.get("X-Impact-Signature") or "", raw, datetime.now(timezone.utc)
                )
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            "path": self.path,
                            "signature_valid": valid,
                            "body": body,
                        },
                        sort_keys=True,
                    )
                    + "\n"
                )
            self.send_response(401 if valid is False else 200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}\n' if valid is not False else b'{"ok":false}\n')

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--log", required=True)
    args = parser.parse_args(argv)
    server = HTTPServer(
        (args.host, args.port), make_handler(args.log, os.environ.get("ALERT_WEBHOOK_SECRET") or "")
    )
    print(json.dumps({"listening": args.host + ":" + str(server.server_port), "log": args.log}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
