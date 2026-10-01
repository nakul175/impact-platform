"""Private object store for evidence bytes (v0.22).

Objects are content-addressed: the key of a tenant's object is "<tenant_id>/<sha256[:2]>/<sha256>",
so identical bytes are stored once per tenant and a key can never be re-pointed at other content.
The store is never served directly: every byte leaves through the API's mediated download, which
re-authorises the caller and checks the verdict recorded in `impact.file_blob` first.

`FilesystemObjectStore` keeps objects under one configured private directory (0700 directories,
0600 files, atomic rename after fsync). An S3-compatible backend is a later adapter implementing the
same three methods against a private bucket (no public ACL, no presigned URL handed to clients,
server-side encryption, bucket versioning off since keys are immutable); it is not implemented in
this build and `object_store()` refuses any backend other than "filesystem".
"""

import hashlib
import os
import re
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from .domain import DomainError

KEY = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[0-9a-f]{2}/[0-9a-f]{64}$")


def object_key(tenant_id, sha256_hex):
    key = str(tenant_id) + "/" + sha256_hex[:2] + "/" + sha256_hex
    if not KEY.fullmatch(key):
        raise ValueError("invalid object key")
    return key


class ObjectStore(ABC):
    """Write-once, content-addressed byte storage. Implementations must never overwrite an existing
    key with different bytes and must verify the digest on every read."""

    backend = "abstract"

    @abstractmethod
    def put(self, tenant_id, sha256_hex, data):
        """Store `data`, whose SHA-256 the caller has verified, and return its key. Idempotent."""

    @abstractmethod
    def get(self, key, sha256_hex):
        """The bytes under `key`; raises OBJECT_INTEGRITY_FAILED when they no longer hash to
        `sha256_hex` and OBJECT_MISSING when the key is absent."""

    @abstractmethod
    def exists(self, key):
        """Whether an object is stored under `key`."""


class FilesystemObjectStore(ObjectStore):
    backend = "filesystem"

    def __init__(self, root):
        self.root = Path(root)
        if not self.root.is_absolute():
            raise ValueError("object_store_dir must be an absolute path")

    def path(self, key):
        if not KEY.fullmatch(key):
            raise ValueError("invalid object key")
        return self.root.joinpath(*key.split("/"))

    def put(self, tenant_id, sha256_hex, data):
        if hashlib.sha256(data).hexdigest() != sha256_hex:
            raise ValueError("digest mismatch")
        key = object_key(tenant_id, sha256_hex)
        target = self.path(key)
        if target.exists():
            # Content addressing: the same key holds the same bytes. Anything else is corruption,
            # which a write never repairs silently.
            self.get(key, sha256_hex)
            return key
        old = os.umask(0o077)
        try:
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=".incoming-")
            try:
                with os.fdopen(handle, "wb") as out:
                    out.write(data)
                    out.flush()
                    os.fsync(out.fileno())
                os.chmod(temporary, 0o600)
                os.replace(temporary, target)
            except BaseException:
                if os.path.exists(temporary):
                    os.unlink(temporary)
                raise
            directory = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            os.umask(old)
        return key

    def get(self, key, sha256_hex):
        try:
            data = self.path(key).read_bytes()
        except FileNotFoundError:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="OBJECT_MISSING") from None
        if hashlib.sha256(data).hexdigest() != sha256_hex:
            raise DomainError("SERVICE_UNAVAILABLE", 503, reason="OBJECT_INTEGRITY_FAILED")
        return data

    def exists(self, key):
        return self.path(key).is_file()


def object_store(settings):
    """The configured store, or None when evidence storage is not configured (uploads then answer
    SERVICE_UNAVAILABLE with reason OBJECT_STORE_NOT_CONFIGURED)."""
    if not settings.object_store_dir:
        return None
    if settings.object_store_backend != "filesystem":
        raise ValueError("object_store_backend: only 'filesystem' is implemented")
    return FilesystemObjectStore(settings.object_store_dir)
