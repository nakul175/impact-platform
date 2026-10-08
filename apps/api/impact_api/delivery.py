"""Delivery intents for the worker (v0.16): closed templates, sealed recipients, derived secrets.

An intent is one `delivery.requested` outbox event plus its `outbox_delivery` row, written in the
same transaction as the business change that needs it. The row names a channel, a template from a
closed set and a reference (invitation, recovery challenge or notification) and never carries a
token, code or clear address:

- the invitation link is re-derived by the worker from (tenant, invitation, generation) with the
  invitation signing secret, exactly as the API derives it, and only while that generation is the
  invitation's current one;
- the recovery-channel code is an HMAC of the challenge identifier under the delivery secret; the
  database keeps only a second, differently keyed HMAC of it for comparison;
- an email address is AES-256-GCM sealed under a key derived from the delivery secret and bound to
  tenant, template and reference, so a sealed value cannot be replayed onto another intent.

Since v0.25 part A the delivery and invitation secrets are keyrings (impact_api/keyring.py): a sealed
address starts with the kid of the delivery key that sealed it, and values made under a secret in its
grace window (address, link, code) are still opened or matched until that secret is retired.
"""

import hashlib
import hmac
from json import dumps
from urllib.parse import quote
from uuid import uuid4

from psycopg.types.json import Jsonb

from .clock import now
from .identity_profile import normalize_email
from .keyring import Keyring

# template -> channel; the database repeats this set in a CHECK constraint (migration 0018).
TEMPLATES = {
    "IN_APP_NOTICE": "IN_APP",
    "MEMBER_INVITATION": "EMAIL",
    "RECOVERY_CHANNEL_VERIFICATION": "EMAIL",
}
CODE_DIGITS = 8


def _key(secret, purpose):
    return hmac.new(secret.encode(), purpose.encode(), hashlib.sha256).digest()


def _binding(tenant, template, reference):
    return ("impact-delivery-v1:" + str(tenant) + ":" + template + ":" + str(reference)).encode()


def _ring(secret):
    """A delivery keyring from a Keyring or a single secret string."""
    return secret if isinstance(secret, Keyring) else Keyring("delivery", secret)


def _recipient_key(secret):
    return _key(secret, "impact-delivery-recipient-v1")


def seal_recipient(secret, tenant, template, reference, address):
    """Header (marker + kid of the current delivery secret) + nonce + AES-GCM ciphertext; `secret`
    is the delivery keyring or one secret (v0.25 part A adds the kid header)."""
    return _ring(secret).seal(
        _recipient_key, normalize_email(address).encode(), _binding(tenant, template, reference)
    )


def unseal_recipient(secret, tenant, template, reference, sealed):
    """The clear address under any non-retired delivery secret (kid-tagged or legacy value); raises
    cryptography.exceptions.InvalidTag for a foreign, altered or retired-key value."""
    return _ring(secret).unseal(_recipient_key, sealed, _binding(tenant, template, reference)).decode()


def code_secret(keys, challenge_id, code_hash):
    """The non-retired delivery secret whose derived code matches the stored keyed hash of a
    recovery challenge, or None (the challenge was made under a retired or foreign secret)."""
    for secret in _ring(keys).secrets():
        if hmac.compare_digest(
            channel_code_hash(secret, challenge_id, channel_code(secret, challenge_id)), bytes(code_hash)
        ):
            return secret
    return None


def channel_code(secret, challenge_id):
    digest = hmac.new(
        _key(secret, "impact-recovery-channel-code-v1"), str(challenge_id).encode(), hashlib.sha256
    ).digest()
    return str(int.from_bytes(digest[:8], "big") % 10**CODE_DIGITS).zfill(CODE_DIGITS)


def channel_code_hash(secret, challenge_id, code):
    return hmac.new(
        _key(secret, "impact-recovery-channel-hash-v1"),
        (str(challenge_id) + ":" + str(code)).encode(),
        hashlib.sha256,
    ).digest()


def invitation_token(secret, tenant, invitation, generation):
    message = "impact-invitation-v1:" + str(tenant) + ":" + str(invitation) + ":" + str(generation)
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return str(invitation) + "." + str(generation) + "." + signature


def invitation_url(public_origin, tenant, token):
    return (
        public_origin
        + "/#invite="
        + quote(dumps({"tenant_id": str(tenant), "token": token}, separators=(",", ":")))
    )


def enqueue(c, tenant, template, reference_id, reference_generation=None, recipient_sealed=None):
    """Record one delivery intent in the caller's transaction; returns its event identifier."""
    channel = TEMPLATES[template]
    if (channel == "EMAIL") != (recipient_sealed is not None):
        raise ValueError("An email intent needs a sealed recipient and an in-app intent none")
    event_id, at = str(uuid4()), now()
    payload = {
        "event_id": event_id,
        "tenant_id": str(tenant),
        "event_type": "delivery.requested",
        "schema_version": "1.0",
        "channel": channel,
        "template": template,
        "reference_id": str(reference_id),
        "reference_generation": reference_generation,
        "occurred_at": at.isoformat(),
    }
    c.execute(
        "INSERT INTO impact.outbox_event(tenant_id,event_id,event_type,occurred_at,payload) VALUES(%s,%s,%s,%s,%s)",
        (str(tenant), event_id, "delivery.requested", at, Jsonb(payload)),
    )
    c.execute(
        "INSERT INTO impact.outbox_delivery(tenant_id,event_id,channel,template,reference_id,reference_generation,recipient_sealed) VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (str(tenant), event_id, channel, template, str(reference_id), reference_generation, recipient_sealed),
    )
    return event_id


# Closed plain-text templates. Every field is produced by the platform (a link it derived, a code,
# an instant); nothing a user typed is rendered, and no HTML part exists.
SUBJECTS = {
    "MEMBER_INVITATION": "Your invitation to an Impact Platform workspace",
    "RECOVERY_CHANNEL_VERIFICATION": "Impact Platform recovery contact verification code",
}
BODIES = {
    "MEMBER_INVITATION": (
        "You have been invited to join a workspace on the Impact Platform.\n\n"
        "Open this link while signed in with the account the invitation names:\n{url}\n\n"
        "The invitation expires at {expires_at} (UTC). Receiving this message does not make you a "
        "member; the workspace administrator can see whether the invitation was accepted.\n\n"
        "If you did not expect this invitation, ignore this message.\n"
    ),
    "RECOVERY_CHANNEL_VERIFICATION": (
        "Your recovery contact verification code is:\n\n    {code}\n\n"
        "Enter it on the recovery contact page of the Impact Platform while signed in. The code can "
        "be used once and expires at {expires_at} (UTC).\n\n"
        "Being a recovery contact does not let anyone reset accounts or take over a workspace. If you "
        "did not ask for this code, ignore this message.\n"
    ),
}
FIELDS = {"MEMBER_INVITATION": {"url", "expires_at"}, "RECOVERY_CHANNEL_VERIFICATION": {"code", "expires_at"}}


def render(template, **fields):
    if template not in SUBJECTS or set(fields) != FIELDS[template]:
        raise ValueError("Unknown template or fields")
    for value in fields.values():
        if not isinstance(value, str) or any(ch in value for ch in "\r\n<>"):
            raise ValueError("Unsafe template field")
    return SUBJECTS[template], BODIES[template].format(**fields)
