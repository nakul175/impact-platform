"""Loopback mail capture for a deployment that has no email provider yet.

The worker refuses the synthetic adapter in staging and production (SMTP_AND_HTTPS_REQUIRED), and
refuses any non-loopback SMTP host without STARTTLS. Until the owner chooses an email provider,
deploy/compose.yaml runs this sink in the network namespace the worker shares, so the worker's
SMTP adapter holds a real SMTP conversation with 127.0.0.1:2525 and every message is captured
here instead of being sent. Nothing leaves the server. Each accepted message becomes one JSON line
(the same fields the worker's synthetic sink records) in a 0600 file on a named volume.

Plain SMTP without STARTTLS or AUTH, bounded: 64 KiB per line, 1 MiB per message, 50 recipients.
"""

import argparse
import json
import os
import re
import socketserver
import sys
from datetime import datetime, timezone
from email import message_from_bytes, policy

MAX_LINE = 65536
MAX_MESSAGE = 1048576
MAX_RECIPIENTS = 50
ADDRESS = re.compile(r"<([^<>\s]{0,320})>")


def record(raw, sender, recipients):
    message = message_from_bytes(raw, policy=policy.default)
    try:
        body = message.get_body(preferencelist=("plain",))
        text = body.get_content() if body is not None else ""
    except (KeyError, LookupError, ValueError):
        text = ""
    return {
        "event_id": message.get("X-Impact-Delivery"),
        "message_id": message.get("Message-ID"),
        "envelope_from": sender,
        "envelope_to": recipients,
        "from": message.get("From"),
        "to": message.get("To"),
        "subject": message.get("Subject"),
        "body": text,
        "at": datetime.now(timezone.utc).isoformat(),
    }


def append(path, entry):
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "a") as handle:
        handle.write(json.dumps(entry) + "\n")


def handler_for(path):
    class Handler(socketserver.StreamRequestHandler):
        timeout = 60

        def reply(self, line):
            self.wfile.write((line + "\r\n").encode())

        def line(self):
            raw = self.rfile.readline(MAX_LINE + 1)
            if len(raw) > MAX_LINE:
                raise ValueError("line too long")
            return raw

        def handle(self):
            self.reply("220 impact-mail-capture ESMTP")
            sender, recipients = None, []
            try:
                while True:
                    raw = self.line()
                    if not raw:
                        return
                    text = raw.decode(errors="replace").rstrip("\r\n")
                    verb = text[:4].upper()
                    if verb == "EHLO":
                        self.reply("250-impact-mail-capture")
                        self.reply("250-SIZE " + str(MAX_MESSAGE))
                        self.reply("250 8BITMIME")
                    elif verb == "HELO":
                        self.reply("250 impact-mail-capture")
                    elif verb == "MAIL":
                        found = ADDRESS.search(text)
                        sender, recipients = (found.group(1) if found else ""), []
                        self.reply("250 OK")
                    elif verb == "RCPT":
                        found = ADDRESS.search(text)
                        if sender is None or not found:
                            self.reply("503 Bad sequence of commands")
                        elif len(recipients) >= MAX_RECIPIENTS:
                            self.reply("452 Too many recipients")
                        else:
                            recipients.append(found.group(1))
                            self.reply("250 OK")
                    elif verb == "DATA":
                        if not recipients:
                            self.reply("503 Bad sequence of commands")
                            continue
                        self.reply("354 End data with <CR><LF>.<CR><LF>")
                        chunks, size = [], 0
                        while True:
                            chunk = self.line()
                            if not chunk or chunk in (b".\r\n", b".\n"):
                                break
                            size += len(chunk)
                            chunks.append(chunk[1:] if chunk.startswith(b"..") else chunk)
                        if size > MAX_MESSAGE:
                            self.reply("552 Message size exceeds limit")
                        else:
                            append(path, record(b"".join(chunks), sender, list(recipients)))
                            self.reply("250 OK captured, not delivered")
                        sender, recipients = None, []
                    elif verb == "RSET":
                        sender, recipients = None, []
                        self.reply("250 OK")
                    elif verb == "NOOP":
                        self.reply("250 OK")
                    elif verb == "QUIT":
                        self.reply("221 Bye")
                        return
                    else:
                        self.reply("502 Command not implemented")
            except (ValueError, OSError):
                return

    return Handler


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=2525)
    p.add_argument("--sink", default="/var/lib/impact/mail/captured.jsonl")
    args = p.parse_args(argv)
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        raise SystemExit("The capture sink listens on loopback only")
    os.makedirs(os.path.dirname(args.sink), exist_ok=True)
    with Server((args.host, args.port), handler_for(args.sink)) as server:
        print(json.dumps({"listening": args.host + ":" + str(args.port), "sink": args.sink}), flush=True)
        server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
