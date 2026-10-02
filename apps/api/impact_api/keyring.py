"""Versioned keyrings for the application's own secrets (v0.25 part A).

Each secret family has one current secret and an ordered list of previous secrets kept for a grace
window. New values (CSRF tokens, cursors, sealed blobs, invitation tokens, recovery codes) are made
with the current secret only; values made before a rotation keep verifying or unsealing while their
secret is still in the previous list, and stop the moment it is removed ("retired").

A key id ("kid") is derived from the secret itself, so rotation needs no separate register and the
kid can be written into the value it protects:

- CSRF tokens are "<kid>.<hex HMAC>";
- signed cursors carry "kid" inside their signed payload;
- sealed blobs (delivery recipients, provider logout hints) start with a 7-byte header: the marker
  byte 0x4B and the 6 bytes of the kid, followed by the AES-GCM nonce and ciphertext.

Values written before this build carry no kid. They are verified (or unsealed) by trying each
non-retired secret in turn; HMAC comparison and the AES-GCM tag make a wrong secret fail closed.

The kid is the first 12 hex characters of SHA-256("impact-key-id-v1:<family>:<secret>"): a
48-character random secret cannot be recovered from it, and the families never share a kid for the
same value. No secret value ever appears in a repr, log line or error raised here.
"""

import hashlib
import hmac
import re
import secrets as random

# cryptography is imported where it is used: scripts/rotate_secrets.py runs this module's key-id
# helpers with the server's plain python3, which has no third-party packages.

FAMILIES = ("cookie", "invitation", "delivery")
MIN_SECRET_LENGTH = 48
SEAL_MARKER = 0x4B
KID_HEX = 12
SEAL_HEADER = 1 + KID_HEX // 2
KID_PATTERN = re.compile(r"^[0-9a-f]{12}$")


class KeyringError(ValueError):
    """A configuration error; the message names families and kids, never a value."""


def key_id(family, secret):
    return hashlib.sha256(("impact-key-id-v1:" + family + ":" + secret).encode()).hexdigest()[:KID_HEX]


def split_previous(value):
    """The previous secrets of a family: a list, or a string separated by commas or whitespace."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = re.split(r"[\s,]+", str(value))
    return [item.strip() for item in items if isinstance(item, str) and item.strip()]


class Keyring:
    """One family's current secret and its previous secrets in grace, newest first."""

    __slots__ = ("family", "_entries")

    def __init__(self, family, current, previous=()):
        self.family = family
        entries, seen = [], set()
        for secret in [current] + list(previous):
            if not secret or secret in seen:
                continue
            seen.add(secret)
            entries.append((key_id(family, secret), secret))
        if len({kid for kid, _ in entries}) != len(entries):
            raise KeyringError("Key id collision in the " + family + " keyring")
        self._entries = tuple(entries)

    def __repr__(self):
        return "Keyring(" + self.family + ", ids=" + repr(self.ids()) + ")"

    __str__ = __repr__

    def __bool__(self):
        return bool(self._entries)

    def ids(self):
        return [kid for kid, _ in self._entries]

    @property
    def current_id(self):
        return self._entries[0][0] if self._entries else None

    @property
    def current(self):
        if not self._entries:
            raise KeyringError("The " + self.family + " keyring has no current secret")
        return self._entries[0][1]

    def get(self, kid):
        for entry_id, secret in self._entries:
            if entry_id == kid:
                return secret
        return None

    def secrets(self):
        """Every non-retired secret, current first (for values that carry no kid)."""
        return [secret for _, secret in self._entries]

    def candidates(self, kid=None):
        """The secret a kid names, or every secret for a value without one; an unknown kid
        (a retired or foreign key) has no candidate."""
        if kid is None:
            return self.secrets()
        secret = self.get(kid)
        return [secret] if secret else []

    # -- HMAC tokens ---------------------------------------------------------------------------

    def sign(self, message):
        """'<kid>.<hex HMAC-SHA256>' of message (bytes) under the current secret."""
        return self.current_id + "." + hmac.new(self.current.encode(), message, hashlib.sha256).hexdigest()

    def verify(self, message, token):
        """True when token is a kid-tagged or legacy (bare hex) HMAC of message under a
        non-retired secret."""
        if not isinstance(token, str) or len(token) > 200:
            return False
        kid, _, mac = token.rpartition(".")
        if kid and not KID_PATTERN.match(kid):
            return False
        ok = False
        for secret in self.candidates(kid or None):
            expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
            ok = hmac.compare_digest(mac, expected) or ok
        return ok

    # -- AES-GCM sealing -----------------------------------------------------------------------

    def seal(self, derive, plaintext, associated):
        """Header (marker + kid) + nonce + AES-GCM ciphertext under derive(current secret)."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = random.token_bytes(12)
        header = bytes([SEAL_MARKER]) + bytes.fromhex(self.current_id)
        return header + nonce + AESGCM(derive(self.current)).encrypt(nonce, plaintext, associated)

    def unseal(self, derive, sealed, associated):
        """The plaintext of a kid-tagged or legacy sealed value; raises InvalidTag when no
        non-retired secret opens it (a retired key, a foreign value or tampering)."""
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        sealed = bytes(sealed)
        kid = sealed_kid(sealed)
        secret = self.get(kid) if kid else None
        if secret:
            body = sealed[SEAL_HEADER:]
            try:
                return AESGCM(derive(secret)).decrypt(body[:12], body[12:], associated)
            except InvalidTag:
                pass
        # A legacy value is nonce + ciphertext and its first byte is random, so a value that only
        # looks tagged (or names a retired kid) is still tried as legacy; the tag decides.
        for secret in self.secrets():
            try:
                return AESGCM(derive(secret)).decrypt(sealed[:12], sealed[12:], associated)
            except (InvalidTag, ValueError):
                continue
        raise InvalidTag()


def sealed_kid(sealed):
    """The kid a sealed value names, or None for a legacy (untagged) value."""
    sealed = bytes(sealed)
    if len(sealed) > SEAL_HEADER + 28 and sealed[0] == SEAL_MARKER:
        return sealed[1:SEAL_HEADER].hex()
    return None


def ring(settings, family, fallback=None):
    """The keyring of a family from any settings object (API Settings, WorkerSettings or a test
    namespace): <family>_secret is current, <family>_secret_previous holds the grace secrets."""
    current = getattr(settings, family + "_secret", "") or ""
    if not current and fallback:
        return ring(settings, fallback)
    return Keyring(family, current, split_previous(getattr(settings, family + "_secret_previous", "")))


def validate(settings, families=FAMILIES, required=()):
    """Every secret of every listed family at least 48 characters, a previous secret never equal to
    a current one, and no secret shared between families. Raises KeyringError naming the family."""
    seen = {}
    for family in families:
        current = getattr(settings, family + "_secret", "") or ""
        previous = split_previous(getattr(settings, family + "_secret_previous", ""))
        if family in required and not current:
            raise KeyringError("A " + family + " secret is required")
        if previous and not current:
            raise KeyringError("Previous " + family + " secrets need a current one")
        for position, secret in enumerate([current] + previous):
            if not secret:
                continue
            if len(secret) < MIN_SECRET_LENGTH:
                raise KeyringError("Every " + family + " secret must be at least 48 characters")
            if position and secret == current:
                raise KeyringError("A previous " + family + " secret repeats the current one")
            other = seen.get(secret)
            if other and other != family:
                raise KeyringError("The " + family + " and " + other + " keyrings share a secret")
            seen[secret] = family
        Keyring(family, current, previous)


# -- RS256 development signing keys ----------------------------------------------------------------


def rsa_key_id(public_pem):
    """The kid of an RS256 public key: the first 16 hex characters of SHA-256 over its DER
    SubjectPublicKeyInfo, so the same key always has the same kid whatever its PEM layout."""
    from cryptography.hazmat.primitives import serialization

    key = serialization.load_pem_public_key(
        public_pem if isinstance(public_pem, bytes) else public_pem.encode()
    )
    der = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    return "rs-" + hashlib.sha256(der).hexdigest()[:16]


def signing_keys(current_path, keyset_path=""):
    """{kid: public PEM bytes} of the development token verifier: the current key (dev_public_key)
    and every key of the key set whose status is not "retired"."""
    import json
    from pathlib import Path

    keys = {}
    if current_path:
        pem = Path(current_path).read_bytes()
        keys[rsa_key_id(pem)] = pem
    if keyset_path and Path(keyset_path).exists():
        for entry in json.loads(Path(keyset_path).read_text()).get("keys", []):
            if entry.get("status") == "retired":
                continue
            pem = entry["public_pem"].encode()
            if rsa_key_id(pem) != entry.get("kid"):
                raise KeyringError("A development signing key does not match its kid")
            keys[entry["kid"]] = pem
    return keys
