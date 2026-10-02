"""A minimal loopback SMTP server for qualification. By default plain SMTP (no STARTTLS, no AUTH),
recording every accepted message and answering the end of DATA with scripted rejections, so the
worker's SMTP adapter holds a real SMTP conversation without any mail leaving the machine.

Since v0.27 it can also behave like a provider's submission port: with `tls_context` it advertises
STARTTLS and upgrades the connection (a self-signed certificate is generated per run by
`make_certificate`); with `credentials` it advertises AUTH (PLAIN and/or LOGIN) and checks them,
answering scripted `auth_rejections` first. `advertise_starttls_without_tls` advertises STARTTLS
but closes on it, and `plain_auth_allowed` controls whether AUTH is offered before TLS. Every verb
received is recorded in `commands` as (verb, under_tls) so a test can prove that nothing was sent
in clear after a failed upgrade."""

import base64
import datetime as dt
import ipaddress
import re
import socketserver
import ssl
import threading
from email import message_from_bytes, policy
from pathlib import Path

DEFAULT_SERVER_NAME = "smtp.qualification.test"


class SmtpSink:
    def __init__(
        self,
        rejections=None,
        on_data=None,
        mail_rejections=None,
        rcpt_rejections=None,
        tls_context=None,
        credentials=None,
        auth_mechanisms=("PLAIN", "LOGIN"),
        auth_rejections=None,
        advertise_starttls_without_tls=False,
        plain_auth_allowed=False,
    ):
        self.messages = []
        self.rejections = list(rejections or [])
        self.mail_rejections = list(mail_rejections or [])
        self.rcpt_rejections = list(rcpt_rejections or [])
        self.auth_rejections = list(auth_rejections or [])
        self.on_data = on_data
        self.tls_context = tls_context
        self.credentials = dict(credentials or {})
        self.auth_mechanisms = tuple(m.upper() for m in auth_mechanisms)
        self.advertise_starttls_without_tls = advertise_starttls_without_tls
        self.plain_auth_allowed = plain_auth_allowed
        self.conversations = 0
        self.tls_failures = 0
        self.commands = []
        self.authenticated = []
        sink = self

        class Handler(socketserver.StreamRequestHandler):
            tls = False
            authenticated_as = None

            def reply(self, line):
                self.wfile.write((line + "\r\n").encode())

            def auth_offered(self):
                if not sink.credentials:
                    return False
                return self.tls or sink.plain_auth_allowed or not sink.tls_context

            def ehlo(self):
                lines = ["sink.test", "8BITMIME"]
                if (sink.tls_context or sink.advertise_starttls_without_tls) and not self.tls:
                    lines.append("STARTTLS")
                if self.auth_offered():
                    lines.append("AUTH " + " ".join(sink.auth_mechanisms))
                for item in lines[:-1]:
                    self.reply("250-" + item)
                self.reply("250 " + lines[-1])

            def check(self, user, password):
                if sink.auth_rejections:
                    self.reply(sink.auth_rejections.pop(0))
                    return
                if sink.credentials.get(user) == password and password != "":
                    self.authenticated_as = user
                    sink.authenticated.append((user, self.tls))
                    self.reply("235 2.7.0 Authentication successful")
                else:
                    self.reply("535 5.7.8 Authentication credentials invalid")

            def auth(self, line):
                parts = line.split(" ", 2)
                mechanism = parts[1].upper() if len(parts) > 1 else ""
                if not self.auth_offered() or mechanism not in sink.auth_mechanisms:
                    self.reply("504 5.5.4 Unrecognized authentication type")
                    return
                if mechanism == "PLAIN":
                    initial = parts[2] if len(parts) > 2 else None
                    if initial is None:
                        self.reply("334 ")
                        initial = self.rfile.readline().decode(errors="replace").strip()
                    try:
                        _, user, password = base64.b64decode(initial).decode().split("\0")
                    except (ValueError, UnicodeDecodeError):
                        self.reply("501 5.5.2 Cannot decode response")
                        return
                    self.check(user, password)
                else:  # LOGIN
                    user_b64 = parts[2] if len(parts) > 2 else None
                    if user_b64 is None:
                        self.reply("334 VXNlcm5hbWU6")
                        user_b64 = self.rfile.readline().decode(errors="replace").strip()
                    self.reply("334 UGFzc3dvcmQ6")
                    password_b64 = self.rfile.readline().decode(errors="replace").strip()
                    try:
                        user = base64.b64decode(user_b64).decode()
                        password = base64.b64decode(password_b64).decode()
                    except (ValueError, UnicodeDecodeError):
                        self.reply("501 5.5.2 Cannot decode response")
                        return
                    self.check(user, password)

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
                    sink.commands.append((line.split(" ", 1)[0].upper(), self.tls))
                    if verb == "EHLO":
                        self.ehlo()
                    elif verb == "HELO":
                        self.reply("250 sink.test")
                    elif verb == "STAR" and line.upper().startswith("STARTTLS"):
                        if self.tls or not (sink.tls_context or sink.advertise_starttls_without_tls):
                            self.reply("503 5.5.1 Bad sequence of commands")
                            continue
                        self.reply("220 2.0.0 Ready to start TLS")
                        self.wfile.flush()
                        if not sink.tls_context:
                            sink.tls_failures += 1
                            return  # advertised, never offered: the connection just ends
                        try:
                            secured = sink.tls_context.wrap_socket(self.connection, server_side=True)
                        except (ssl.SSLError, OSError):
                            sink.tls_failures += 1
                            return
                        self.connection = secured
                        self.rfile = secured.makefile("rb", -1)
                        self.wfile = secured.makefile("wb", 0)
                        self.tls = True
                        sender, recipients = None, []
                    elif verb == "AUTH":
                        self.auth(line)
                    elif verb == "MAIL":
                        if sink.credentials and self.authenticated_as is None:
                            self.reply("530 5.7.0 Authentication required")
                            continue
                        found = re.search(r"<([^>]*)>", line)
                        sender, recipients = found.group(1) if found else None, []
                        self.reply(sink.mail_rejections.pop(0) if sink.mail_rejections else "250 OK")
                    elif verb == "RCPT":
                        if sink.rcpt_rejections:
                            self.reply(sink.rcpt_rejections.pop(0))
                            continue
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
                                "tls": self.tls,
                                "authenticated_as": self.authenticated_as,
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

    def commands_in_clear(self):
        """Verbs received on the unencrypted connection, other than the handshake verbs."""
        return [
            verb
            for verb, tls in self.commands
            if not tls and verb not in {"EHLO", "HELO", "STARTTLS", "QUIT"}
        ]


def make_certificate(directory, names=(DEFAULT_SERVER_NAME,), ips=("127.0.0.1",), days=1):
    """A self-signed server certificate generated for this run only (never committed: *.pem and
    *.key are ignored). Returns (certificate_path, key_path); the certificate is its own CA."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, names[0])])
    now = dt.datetime.now(dt.timezone.utc)
    alternatives = [x509.DNSName(name) for name in names] + [
        x509.IPAddress(ipaddress.ip_address(ip)) for ip in ips
    ]
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(days=days))
        .add_extension(x509.SubjectAlternativeName(alternatives), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    certificate_path = directory / "smtp-server.pem"
    key_path = directory / "smtp-server.key"
    certificate_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return certificate_path, key_path


def server_context(certificate_path, key_path):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(str(certificate_path), str(key_path))
    return context
