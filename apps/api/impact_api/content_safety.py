"""File receipt checks for evidence media (v0.22, FR-SEC-005 subset): a closed media-type allow-list,
declared-name checks, magic-byte sniffing of the actual bytes, and a pluggable scanner.

Bounded and honest: the allow-list excludes executables, archives and office documents (no macro or
archive-expansion profile is qualified), and the shipped scanners are not anti-malware engines. The
signature scanner recognises only the EICAR anti-virus test file; a real engine is a later adapter
behind the same `Scanner.scan` interface. A passed scan never establishes that a file is true or
safe (FR-EVD-002)."""

import base64
import re
import unicodedata

from .domain import DomainError

# Media accepted as evidence in this build: declared type -> permitted file-name extensions.
MEDIA_TYPES = {
    "application/pdf": (".pdf",),
    "image/png": (".png",),
    "image/jpeg": (".jpg", ".jpeg"),
    "text/plain": (".txt",),
    "text/csv": (".csv",),
}
# The design contract's ceiling for EVIDENCE_MEDIA uploads (upload_session CHECK, put_upload_content).
MAX_EVIDENCE_BYTES = 25_000_000
# Leading bytes of executable formats refused whatever the declared type.
EXECUTABLE_PREFIXES = (b"MZ", b"\x7fELF", b"\xfe\xed\xfa", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe", b"#!")
# PDF name objects that make a document active (scripts, launch actions, embedded files). A plain
# byte search: names hidden inside compressed object streams are not found (a stated limit).
PDF_ACTIVE = (b"/JavaScript", b"/JS", b"/Launch", b"/EmbeddedFile", b"/OpenAction", b"/AA", b"/RichMedia")
MARKUP = (b"<!doctype", b"<html", b"<script", b"<svg", b"<?xml", b"<iframe")
FILENAME = re.compile(r"^[^\x00-\x1f\x7f/\\:*?\"<>|]{1,200}$")
# The EICAR anti-virus test file, kept encoded so that the source tree itself carries no copy.
EICAR = base64.b64decode(
    b"WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="
)


def refuse(reason, status=422):
    raise DomainError("VALIDATION_FAILED", status, reason=reason)


def check_declaration(media_type, filename, size):
    """The declared media type, name and size of an evidence upload, before any byte arrives."""
    if media_type not in MEDIA_TYPES:
        refuse("MEDIA_TYPE_NOT_ALLOWED")
    if size > MAX_EVIDENCE_BYTES:
        refuse("FILE_TOO_LARGE", 413)
    name = unicodedata.normalize("NFC", filename)
    if name != filename or not FILENAME.fullmatch(name) or name.strip(" .") != name:
        refuse("FILENAME_INVALID")
    # One extension, and the one the declared type permits: "report.pdf.exe" or "photo.png" holding
    # a PDF is refused here or by sniffing.
    stem, dot, extension = name.rpartition(".")
    if not dot or not stem or "." + extension.lower() not in MEDIA_TYPES[media_type]:
        refuse("FILE_EXTENSION_MISMATCH")


def sniff(data, media_type):
    """Identify the actual content from its bytes and refuse anything that is not the declared,
    allowed type. Returns nothing; raises VALIDATION_FAILED with a reason code."""
    if data.startswith(EXECUTABLE_PREFIXES):
        refuse("EXECUTABLE_REFUSED")
    if media_type == "application/pdf":
        if not data.startswith(b"%PDF-"):
            refuse("CONTENT_TYPE_MISMATCH")
        if any(re.search(re.escape(name) + rb"(?![A-Za-z0-9])", data) for name in PDF_ACTIVE):
            refuse("ACTIVE_CONTENT_REFUSED")
    elif media_type == "image/png":
        if not (data.startswith(b"\x89PNG\r\n\x1a\n") and data[12:16] == b"IHDR"):
            refuse("CONTENT_TYPE_MISMATCH")
    elif media_type == "image/jpeg":
        if not data.startswith(b"\xff\xd8\xff"):
            refuse("CONTENT_TYPE_MISMATCH")
    elif media_type in {"text/plain", "text/csv"}:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            refuse("CONTENT_TYPE_MISMATCH")
        if any(ch < " " and ch not in "\t\n\r\f" for ch in text) or "\x7f" in text:
            refuse("CONTENT_TYPE_MISMATCH")
        head = data.lstrip(b"\xef\xbb\xbf \t\r\n")[:64].lower()
        if head.startswith(MARKUP):
            refuse("CONTENT_TYPE_MISMATCH")
    else:
        refuse("MEDIA_TYPE_NOT_ALLOWED")


class Scanner:
    """A content scanner. `scan` receives the complete bytes of one blob outside any database
    transaction and returns (state, detail): state CLEAN, INFECTED or FAILED; detail a short code."""

    name = "abstract"

    def scan(self, data):
        raise NotImplementedError


class SignatureScanner(Scanner):
    """Deterministic test scanner: INFECTED when the bytes contain the EICAR test file, otherwise
    CLEAN. It detects nothing else and is not malware protection."""

    name = "eicar-signature/1"

    def scan(self, data):
        return ("INFECTED", "EICAR_TEST_SIGNATURE") if EICAR in data else ("CLEAN", "NO_SIGNATURE_MATCH")


class RefusingScanner(Scanner):
    """No engine configured: every scan FAILED, so nothing ever becomes downloadable."""

    name = "none/1"

    def scan(self, data):
        return ("FAILED", "SCANNER_NOT_CONFIGURED")


SCANNERS = {"eicar-signature": SignatureScanner, "none": RefusingScanner}


def scanner(name):
    if name not in SCANNERS:
        raise ValueError("evidence_scanner must be one of " + ", ".join(sorted(SCANNERS)))
    return SCANNERS[name]()
