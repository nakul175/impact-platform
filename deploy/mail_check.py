"""Send one test message through the configured email provider and print the SMTP conversation
with every secret removed (v0.27 email readiness). Run on the server by deploy/mail-check.sh,
inside the worker's container, so it sees exactly the worker's SMTP settings:

    python deploy/mail_check.py --to someone@example.org

Rules are the worker's (apps/api/impact_api/worker.py, SmtpAdapter): STARTTLS with certificate
verification is required for any non-loopback host and for every host under
IMPACT_SMTP_STARTTLS=required; a failed upgrade ends the conversation and nothing is retried in
clear text; credentials are only sent after the upgrade on such a host. The transcript shows the
commands and replies; AUTH exchanges are replaced by [redacted], and the password, the username and
their base64 forms are removed wherever they would appear. The last line is one JSON object:
{"ok": true|false, "reason": ..., "tls": ..., "auth": ..., "message_id": ...}. Exit 0 on success,
1 on a refusal, 2 on a configuration error. Standard library only."""

import argparse
import base64
import ipaddress
import json
import os
import re
import smtplib
import socket
import ssl
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formatdate
from urllib.parse import urlparse
from uuid import uuid4

LOOPBACK = {"127.0.0.1", "::1", "localhost"}
EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}$")
REDACTED = "[redacted]"
ARGUMENT = re.compile(r"(?i)(AUTH (?:PLAIN|LOGIN|CRAM-MD5))\s+[^\s\\'\"]+")


def is_loopback(host):
    if host in LOOPBACK:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def settings_from_environment(env):
    def value(name, default=""):
        return (env.get("IMPACT_SMTP_" + name) or default).strip()

    s = {
        "host": value("HOST", "127.0.0.1"),
        "port": value("PORT", "25"),
        "username": value("USERNAME"),
        "password": env.get("IMPACT_SMTP_PASSWORD") or "",
        "from": value("FROM", "impact-platform@localhost.localdomain"),
        "starttls": value("STARTTLS", "auto").lower(),
        "ca_file": value("CA_FILE"),
        "timeout": float(value("TIMEOUT", "20")),
        "origin": (env.get("IMPACT_PUBLIC_ORIGIN") or "").strip(),
    }
    try:
        s["port"] = int(s["port"])
    except ValueError:
        raise ValueError("INVALID_SMTP_PORT") from None
    if not 1 <= s["port"] <= 65535:
        raise ValueError("INVALID_SMTP_PORT")
    if s["starttls"] not in {"auto", "required"}:
        raise ValueError("INVALID_SMTP_STARTTLS")
    if s["username"] and not s["password"]:
        raise ValueError("SMTP_CREDENTIALS_INCOMPLETE")
    if s["ca_file"] and not os.access(s["ca_file"], os.R_OK):
        raise ValueError("SMTP_CA_FILE_UNREADABLE")
    if not EMAIL.match(s["from"]):
        raise ValueError("INVALID_SMTP_FROM")
    return s


class Transcript(smtplib.SMTP):
    """smtplib's debug output captured in memory instead of stderr."""

    def __init__(self, *args, **kwargs):
        self.lines = []
        super().__init__(*args, **kwargs)
        self.set_debuglevel(1)

    def _print_debug(self, *args):
        self.lines.append(" ".join(str(a) for a in args))


def secret_forms(username, password):
    """Every spelling of the credentials that could appear in a transcript."""
    forms = set()
    for value in (username, password):
        if value:
            forms.add(value)
            raw = value.encode()
            forms.add(base64.b64encode(raw).decode())
    if username and password:
        plain = ("\0" + username + "\0" + password).encode()
        forms.add(base64.b64encode(plain).decode())
        forms.add(base64.b64encode((username + "\0" + username + "\0" + password).encode()).decode())
    return sorted(forms, key=len, reverse=True)


def redact(lines, username, password):
    """AUTH arguments and every client line of an AUTH exchange become [redacted]; then every
    literal or base64 form of the credentials is removed from whatever remains."""
    out, in_auth = [], False
    for line in lines:
        text = line
        if text.startswith("send:"):
            payload = text[len("send:") :].strip()
            if re.match(r"(?i)^['\"b]*AUTH ", payload):
                in_auth = True
                text = ARGUMENT.sub(r"\1 " + REDACTED, text)
                if text == line:
                    text = "send: 'AUTH " + REDACTED + "'"
            elif in_auth:
                text = "send: " + REDACTED
        elif text.startswith("reply:") and in_auth and "334" not in text:
            in_auth = False
        for form in secret_forms(username, password):
            text = text.replace(form, REDACTED)
        out.append(text)
    return out


def build_message(s, to):
    message = EmailMessage()
    message["From"] = s["from"]
    message["To"] = to
    message["Subject"] = "Impact Platform email check"
    message["Date"] = formatdate(usegmt=True)
    host = urlparse(s["origin"]).hostname if s["origin"] else None
    message["Message-ID"] = (
        "<mail-check-" + uuid4().hex + "@" + (host or socket.gethostname() or "impact") + ">"
    )
    message["Auto-Submitted"] = "auto-generated"
    message.set_content(
        "This is a test message from your Impact Platform deployment.\n\n"
        "It was sent by deploy/mail-check.sh at "
        + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        + " to confirm that the email provider is configured. No action is needed.\n"
    )
    return message


def send(s, to):
    """One conversation; returns (ok, reason, transcript lines, details)."""
    loopback = is_loopback(s["host"])
    upgrade = (not loopback) or s["starttls"] == "required"
    details = {"host": s["host"], "port": s["port"], "tls": False, "auth": None, "message_id": None}
    message = build_message(s, to)
    details["message_id"] = message["Message-ID"]
    smtp = None
    try:
        smtp = Transcript(s["host"], s["port"], timeout=s["timeout"])
        smtp.ehlo()
        if upgrade:
            if not smtp.has_extn("starttls"):
                return False, "STARTTLS_UNAVAILABLE", smtp.lines, details
            context = ssl.create_default_context(cafile=s["ca_file"] or None)
            smtp.starttls(context=context)
            details["tls"] = True
            details["tls_version"] = smtp.sock.version()
            smtp.ehlo()
        if s["username"]:
            if not smtp.has_extn("auth"):
                return False, "AUTH_UNAVAILABLE", smtp.lines, details
            smtp.login(s["username"], s["password"])
            details["auth"] = "ok"
        refused = smtp.send_message(message)
        if refused:
            return False, "RECIPIENT_REFUSED", smtp.lines, details
        return True, "SENT", smtp.lines, details
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP_AUTHENTICATION", smtp.lines, details
    except smtplib.SMTPRecipientsRefused:
        return False, "RECIPIENT_REFUSED", smtp.lines, details
    except smtplib.SMTPSenderRefused:
        return False, "SMTP_SENDER_REJECTED", smtp.lines, details
    except smtplib.SMTPResponseException as exc:
        code = exc.smtp_code
        if code in {530, 534, 535, 538}:
            return False, "SMTP_AUTHENTICATION", smtp.lines, details
        return (
            False,
            ("SMTP_PERMANENT_REJECTION" if 500 <= code < 600 else "SMTP_TRANSIENT_REJECTION"),
            smtp.lines,
            details,
        )
    except ssl.SSLError:
        return False, "TLS_FAILURE", smtp.lines if smtp else [], details
    except (smtplib.SMTPException, OSError) as exc:
        return (
            False,
            "SMTP_CONNECTION",
            (smtp.lines if smtp else []) + ["error: " + type(exc).__name__],
            details,
        )
    finally:
        if smtp is not None:
            try:
                smtp.close()
            except OSError:
                pass


def main(argv=None, env=None, out=None):
    out = out or sys.stdout
    env = os.environ if env is None else env
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--to", required=True, help="the address that should receive the test message")
    args = p.parse_args(argv)
    if not EMAIL.match(args.to):
        print(json.dumps({"ok": False, "reason": "INVALID_ADDRESS"}), file=out)
        return 2
    try:
        s = settings_from_environment(env)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}), file=out)
        return 2
    ok, reason, lines, details = send(s, args.to)
    print("SMTP conversation with " + s["host"] + ":" + str(s["port"]) + " (secrets removed)", file=out)
    for line in redact(lines, s["username"], s["password"]):
        print("  " + line, file=out)
    result = {"ok": ok, "reason": reason, "to": args.to, **details}
    print(json.dumps(result, sort_keys=True), file=out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
