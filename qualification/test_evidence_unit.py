"""Evidence file safety and the filesystem object store without a database (v0.22): declaration
checks, magic-byte sniffing, the deterministic scanners and content-addressed, write-once storage."""

import hashlib
import os
import stat

import pytest

from impact_api.config import Settings
from impact_api.content_safety import (
    EICAR,
    MAX_EVIDENCE_BYTES,
    RefusingScanner,
    SignatureScanner,
    check_declaration,
    scanner,
    sniff,
)
from impact_api.domain import DomainError
from impact_api.object_store import FilesystemObjectStore, object_key, object_store

TENANT = "ce56220a-32a5-5ca5-a45f-860dc3d9c958"
PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + bytes(17)
PDF = b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n"


def reason(call, *args):
    with pytest.raises(DomainError) as refused:
        call(*args)
    return refused.value.reason


def test_declaration_allow_list_names_and_size():
    check_declaration("text/csv", "visits.csv", 10)
    check_declaration("image/jpeg", "Photo 1.JPEG", MAX_EVIDENCE_BYTES)
    assert reason(check_declaration, "application/zip", "a.zip", 1) == "MEDIA_TYPE_NOT_ALLOWED"
    assert reason(check_declaration, "application/x-msdownload", "a.exe", 1) == "MEDIA_TYPE_NOT_ALLOWED"
    assert reason(check_declaration, "text/csv", "a.csv", MAX_EVIDENCE_BYTES + 1) == "FILE_TOO_LARGE"
    for name in ["report.pdf.exe", "photo.png", "noextension", ".pdf"]:
        assert reason(check_declaration, "application/pdf", name, 1) in {
            "FILE_EXTENSION_MISMATCH",
            "FILENAME_INVALID",
        }, name
    for name in ["../etc/passwd.txt", "a\\b.txt", "line\nbreak.txt", "trailing.txt ", "x" * 201 + ".txt"]:
        assert reason(check_declaration, "text/plain", name, 1) == "FILENAME_INVALID", name


def test_sniffing_identifies_actual_content():
    sniff(PNG, "image/png")
    sniff(PDF, "application/pdf")
    sniff(b"\xff\xd8\xff\xe0rest", "image/jpeg")
    sniff("name,value\nÅsa,1\n".encode(), "text/csv")
    assert reason(sniff, PDF, "image/png") == "CONTENT_TYPE_MISMATCH"
    assert reason(sniff, PNG, "application/pdf") == "CONTENT_TYPE_MISMATCH"
    assert reason(sniff, b"MZ\x90\x00binary", "application/pdf") == "EXECUTABLE_REFUSED"
    assert reason(sniff, b"#!/bin/sh\nrm -rf /\n", "text/plain") == "EXECUTABLE_REFUSED"
    assert reason(sniff, b"\x7fELF\x02\x01", "text/plain") == "EXECUTABLE_REFUSED"
    assert reason(sniff, b"<!DOCTYPE html><script>x</script>", "text/plain") == "CONTENT_TYPE_MISMATCH"
    assert reason(sniff, b"a,b\n\x00\x01", "text/csv") == "CONTENT_TYPE_MISMATCH"
    assert reason(sniff, b"\xff\xfe\x00bad", "text/csv") == "CONTENT_TYPE_MISMATCH"
    active = PDF.replace(b"/Type /Catalog", b"/Type /Catalog /OpenAction << /S /JavaScript >>")
    assert reason(sniff, active, "application/pdf") == "ACTIVE_CONTENT_REFUSED"
    # A name that merely starts like an active one is not refused.
    sniff(PDF.replace(b"/Catalog", b"/Catalog /JSONData 1"), "application/pdf")


def test_scanners_are_deterministic_and_named():
    assert SignatureScanner().scan(b"plain text") == ("CLEAN", "NO_SIGNATURE_MATCH")
    assert SignatureScanner().scan(b"prefix " + EICAR + b" suffix") == ("INFECTED", "EICAR_TEST_SIGNATURE")
    assert RefusingScanner().scan(b"anything") == ("FAILED", "SCANNER_NOT_CONFIGURED")
    assert scanner("eicar-signature").name == "eicar-signature/1"
    with pytest.raises(ValueError):
        scanner("clamav")


def test_filesystem_store_is_content_addressed_private_and_verified(tmp_path):
    store = FilesystemObjectStore(tmp_path / "objects")
    data = b"household,visited\nH1,yes\n"
    digest = hashlib.sha256(data).hexdigest()
    key = store.put(TENANT, digest, data)
    assert key == object_key(TENANT, digest) == TENANT + "/" + digest[:2] + "/" + digest
    assert store.put(TENANT, digest, data) == key and store.exists(key)
    assert store.get(key, digest) == data
    path = tmp_path / "objects" / TENANT / digest[:2] / digest
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    assert stat.S_IMODE(os.stat(path.parent).st_mode) == 0o700
    assert not [p for p in path.parent.iterdir() if p.name.startswith(".incoming-")]
    with pytest.raises(ValueError):
        store.put(TENANT, digest, data + b"x")
    with pytest.raises(ValueError):
        store.path("../../etc/passwd")
    path.chmod(0o600)
    path.write_bytes(b"tampered")
    with pytest.raises(DomainError) as broken:
        store.get(key, digest)
    assert broken.value.reason == "OBJECT_INTEGRITY_FAILED" and broken.value.status == 503
    path.unlink()
    with pytest.raises(DomainError) as missing:
        store.get(key, digest)
    assert missing.value.reason == "OBJECT_MISSING"


def test_store_and_scanner_configuration(monkeypatch, tmp_path):
    import json

    config = {
        "environment": "test",
        "app_dsn": "postgresql://app",
        "identity_dsn": "postgresql://identity",
        "public_origin": "http://127.0.0.1:8000",
        "issuer": "http://127.0.0.1:8080/realms/impact-dev",
        "client_id": "web",
        "audience": "api",
        "jwks_url": "",
        "authorization_url": "",
        "token_url": "",
        "cookie_secret": "x" * 64,
    }
    path = tmp_path / "config.json"
    monkeypatch.setenv("IMPACT_CONFIG_FILE", str(path))
    for name in ["IMPACT_ENVIRONMENT", "IMPACT_OBJECT_STORE_DIR", "IMPACT_EVIDENCE_SCANNER"]:
        monkeypatch.delenv(name, raising=False)
    path.write_text(json.dumps(config))
    assert object_store(Settings.load()) is None
    for extra, message in [
        ({"object_store_dir": str(tmp_path)}, "explicitly configured evidence_scanner"),
        ({"object_store_dir": "relative/dir", "evidence_scanner": "none"}, "absolute"),
        ({"object_store_dir": str(tmp_path), "evidence_scanner": "clamav"}, "evidence_scanner"),
        ({"object_store_backend": "s3"}, "only 'filesystem'"),
    ]:
        path.write_text(json.dumps({**config, **extra}))
        with pytest.raises(ValueError, match=message):
            Settings.load()
    path.write_text(json.dumps({**config, "object_store_dir": str(tmp_path), "evidence_scanner": "none"}))
    assert isinstance(object_store(Settings.load()), FilesystemObjectStore)


def test_store_failures_are_bounded_reason_codes_and_leave_no_partial_object(monkeypatch, tmp_path):
    """QA 2026-10 degradation: an operating-system failure of the store is SERVICE_UNAVAILABLE with
    OBJECT_STORE_FULL (no space or quota) or OBJECT_STORE_UNAVAILABLE, never a raw OSError, and a
    failed write leaves neither the object nor its temporary file behind."""
    import errno
    from types import SimpleNamespace

    from impact_api import object_store as module

    store = FilesystemObjectStore(tmp_path / "objects")
    data = b"bytes that never fit\n"
    digest = hashlib.sha256(data).hexdigest()
    real = module.os

    def no_space(_):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(module, "os", SimpleNamespace(**{**vars(real), "fsync": no_space}))
    with pytest.raises(DomainError) as full:
        store.put(TENANT, digest, data)
    monkeypatch.setattr(module, "os", real)
    assert (full.value.status, full.value.reason) == (503, "OBJECT_STORE_FULL")
    assert [p for p in (tmp_path / "objects").rglob("*") if p.is_file()] == []
    (tmp_path / "not-a-directory").write_bytes(b"x")
    blocked = FilesystemObjectStore(tmp_path / "not-a-directory")
    with pytest.raises(DomainError) as unavailable:
        blocked.put(TENANT, digest, data)
    assert (unavailable.value.status, unavailable.value.reason) == (503, "OBJECT_STORE_UNAVAILABLE")
    key = store.put(TENANT, digest, data)
    store.path(key).unlink()
    store.path(key).mkdir()
    assert reason(store.get, key, digest) == "OBJECT_STORE_UNAVAILABLE"
