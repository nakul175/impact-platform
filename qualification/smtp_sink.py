"""A minimal loopback SMTP server for qualification: plain SMTP (no STARTTLS, no AUTH), records
every accepted message and can answer the end of DATA with scripted rejections. It lets the
worker's SMTP adapter hold a real SMTP conversation without any mail leaving the machine."""

import re
import socketserver
import threading
from email import message_from_bytes, policy


class SmtpSink:
    def __init__(self, rejections=None, on_data=None):
        self.messages = []
        self.rejections = list(rejections or [])
        self.on_data = on_data
        self.conversations = 0
        sink = self

        class Handler(socketserver.StreamRequestHandler):
            def reply(self, line):
                self.wfile.write((line + "\r\n").encode())

            def handle(self):
                sink.conversations += 1
                self.reply("220 sink.test ESMTP qualification sink")
                sender, recipients = None, []
                while True:
                    raw = self.rfile.readline()
                    if not raw:
                        return
                    line = raw.decode(errors="replace").rstrip("\r\n")
                    verb = line[:4].upper()
                    if verb == "EHLO":
                        self.reply("250-sink.test")
                        self.reply("250 8BITMIME")
                    elif verb == "HELO":
                        self.reply("250 sink.test")
                    elif verb == "MAIL":
                        found = re.search(r"<([^>]*)>", line)
                        sender, recipients = found.group(1) if found else None, []
                        self.reply("250 OK")
                    elif verb == "RCPT":
                        found = re.search(r"<([^>]*)>", line)
                        recipients.append(found.group(1) if found else None)
                        self.reply("250 OK")
                    elif verb == "DATA":
                        self.reply("354 End data with <CR><LF>.<CR><LF>")
                        lines = []
                        while True:
                            chunk = self.rfile.readline()
                            if not chunk or chunk in (b".\r\n", b".\n"):
                                break
                            lines.append(chunk[1:] if chunk.startswith(b"..") else chunk)
                        body = b"".join(lines)
                        if sink.on_data:
                            sink.on_data()
                        if sink.rejections:
                            self.reply(sink.rejections.pop(0))
                            continue
                        sink.messages.append(
                            {
                                "from": sender,
                                "to": list(recipients),
                                "raw": body,
                                "message": message_from_bytes(body, policy=policy.default),
                            }
                        )
                        self.reply("250 OK queued")
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

        class Server(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        self.server = Server(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.server.shutdown()
        self.server.server_close()

    def for_recipient(self, address):
        return [m for m in self.messages if address in m["to"]]
