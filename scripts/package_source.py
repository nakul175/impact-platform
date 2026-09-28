from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
excluded = {".venv", ".local", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", ".git"}
files = [
    p
    for p in ROOT.rglob("*")
    if p.is_file()
    and not excluded.intersection(p.relative_to(ROOT).parts)
    and p.suffix not in {".pyc", ".log", ".pem", ".key"}
    and not p.name.endswith("-failure.png")
    and p.name
    not in {
        ".env",
        "SHA256SUMS.json",
        "browser-failure.png",
        "admin-browser-failure.png",
        "measurement-browser-failure.png",
        "reporting-browser-failure.png",
    }
]
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
(ROOT / "SHA256SUMS.json").write_text(json.dumps(manifest, indent=2))
files.append(ROOT / "SHA256SUMS.json")
archive = ROOT.parent / "Impact-Platform-Source-v0.14.0.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sorted(files):
        z.write(p, Path("impact-platform") / p.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:
    names = z.namelist()
    assert len(names) == len(set(names))
    assert all(name.startswith("impact-platform/") for name in names)
    assert all(".." not in Path(name).parts and not Path(name).is_absolute() for name in names)
    assert z.testzip() is None
    for name, digest in manifest.items():
        assert hashlib.sha256(z.read("impact-platform/" + name)).hexdigest() == digest
print(json.dumps({"archive": str(archive), "files": len(files), "bytes": archive.stat().st_size}))
