"""Serial final unit qualification without overwriting shared golden evidence."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
ROOT=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
if Path.cwd().resolve()!=ROOT:
    raise RuntimeError('Run only in explicitly owned repo')
lock=open('/private/tmp/tola-ai-shared-qualification.lock','a+')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
evidence=ROOT/'docs/evidence'
started=datetime.now(timezone.utc).isoformat()
def sources():
    paths=[p for d in ['apps/api/impact_api','apps/web/src','qualification','scripts','infrastructure','packages/contracts','deploy','specification/reference-v1','.github/workflows','tools/browser','tools/dev-db'] for p in (ROOT/d).rglob('*') if p.is_file() and not any(part in {'__pycache__','node_modules','dist'} for part in p.parts) and p.suffix in {'.py','.json','.sql','.ts','.tsx','.css','.sh','.yaml','.yml','.mjs'}]
    paths += [ROOT/'Makefile',ROOT/'VERSION.json',ROOT/'docs/current/CURRENT-DATA-DICTIONARY.md',ROOT/'apps/web/package.json',ROOT/'apps/web/package-lock.json',ROOT/'apps/web/vite.config.ts',ROOT/'apps/web/index.html',ROOT/'apps/web/ai-walkthrough.html',ROOT/'tools/browser/package.json',ROOT/'tools/browser/package-lock.json',ROOT/'tools/dev-db/package.json',ROOT/'tools/dev-db/package-lock.json']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
before=sources()
for name in ['tests.xml','summary.json','golden.json']:
    p=evidence/('sprint-0.35-unit-'+name)
    if p.is_file():
        dest=evidence/('sprint-0.35-unit-initial-'+name)
        if dest.exists() and dest.read_bytes()!=p.read_bytes():
            raise RuntimeError('Refuse replacing earlier preserved unit evidence')
        dest.write_bytes(p.read_bytes())
golden=evidence/'golden-reconciliation.json'
old=golden.read_bytes() if golden.exists() else None
report=evidence/'sprint-0.35-unit-tests.xml'
env=dict(os.environ,PYTEST_ADDOPTS='--junitxml='+str(report))
result=1
try:
    result=subprocess.run(['make','unit','PY=.venv/bin/python'],cwd=ROOT,env=env,check=False).returncode
    if golden.exists() and golden.read_bytes()!=old:
        (evidence/'sprint-0.35-unit-golden.json').write_bytes(golden.read_bytes())
    end=sources()
    changes=[p for p in sorted(set(before)|set(end)) if before.get(p)!=end.get(p)]
    suite=ET.parse(report).getroot()
    counts={k:sum(int(s.get(k,'0')) for s in suite.iter('testsuite')) for k in ['tests','failures','errors','skipped']}
    summary=dict(started_at=started,recorded_at=datetime.now(timezone.utc).isoformat(),exit_code=result,counts=counts,scope='Exact Makefile unit recipe. Explicit database-dependent skips retained; no production or formal specified-case acceptance.',source_sha256_start=before,source_sha256_end=end,source_changed_during_run=changes,helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (evidence/'sprint-0.35-unit-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if changes: result=result or 1
    print(json.dumps(dict(exit_code=result,counts=counts,source_changes=changes)))
finally:
    if old is None:golden.unlink(missing_ok=True)
    else:golden.write_bytes(old)
    fcntl.flock(lock,fcntl.LOCK_UN)
raise SystemExit(result)
