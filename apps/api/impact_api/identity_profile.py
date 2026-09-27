import hashlib
import re
from .domain import DomainError

EMAIL = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)


def normalize_email(value):
    if not isinstance(value, str) or len(value) > 254 or not EMAIL.fullmatch(value):
        raise DomainError("VALIDATION_FAILED", reason="INVALID_EMAIL")
    local, domain = value.split("@")
    if local.startswith(".") or local.endswith(".") or ".." in local:
        raise DomainError("VALIDATION_FAILED", reason="INVALID_EMAIL")
    return local.lower() + "@" + domain.lower()


def email_hash(value):
    return hashlib.sha256(normalize_email(value).encode()).digest()


def masked_email(value):
    local, domain = normalize_email(value).split("@")
    return local[:2] + "***@" + domain
