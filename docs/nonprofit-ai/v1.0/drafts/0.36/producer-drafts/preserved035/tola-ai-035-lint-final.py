"""Root-owned source-bound repeat of the exact current Makefile lint recipe."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import fcntl
import subprocess
import argparse
ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
EXTRAS = ['Makefile','VERSION.json','apps/api/impact_api/ai_enablement_catalog.py','apps/api/impact_api/ai_learning_content.py','apps/api/impact_api/ai_task_practice.py','apps/api/impact_api/main.py','apps/web/ai-walkthrough.html','apps/web/index.html','apps/web/package-lock.json','apps/web/package.json','apps/web/tsconfig.json','apps/web/vite.config.ts','qualification/test_deploy_unit.py','scripts/run.py','scripts/smoke.py']
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def sources():
    names={ROOT/p for p in EXTRAS}
    names.update(p for p in (ROOT/'apps/web/src').rglob('*') if p.is_file() and p.suffix in {'.ts','.tsx','.css','.json'})
    names.update((ROOT/'tools/browser').glob('*.mjs'))
    assert len(names)==108 and all(p.is_file() and not p.is_symlink() for p in names)
    return {str(p.relative_to(ROOT)):digest(p) for p in sorted(names)}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:
        print(json.dumps({'status':'NOT_RUN','source_count':len(sources()),'recipe':'make lint'}));return
    assert Path.cwd().resolve()==ROOT
    evidence=ROOT/'docs/evidence';old=evidence/'sprint-0.35-lint-source-proof.json'
    preserved=evidence/'sprint-0.35-initial-full-source-qualification'/old.name
    assert old.is_file() and preserved.is_file() and old.read_bytes()==preserved.read_bytes()
    lock=open('/private/tmp/tola-ai-shared-qualification.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    start=datetime.now(timezone.utc).isoformat();before=sources()
    raw=Path('/private/tmp/tola-ai-035-lint-final.log')
    with raw.open('x') as output:
        os.chmod(raw,0o600)
        env=dict(os.environ,PATH='/Users/athena/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin'+os.pathsep+os.environ['PATH'])
        result=subprocess.run(['make','lint'],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=False).returncode
    after=sources();changes=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
    proof={'started_at':start,'recorded_at':datetime.now(timezone.utc).isoformat(),'exit_code':result,'scope':'Exact Makefile Ruff lint, Ruff format and Prettier checks including publicHTML and all registered browser checkers. Fresh repeat after three checker-only corrections. Static scope, no application or hosted assertion.','source_sha256_start':before,'source_sha256_end':after,'source_changed_during_run':changes,'helper_sha256':digest(Path(__file__)),'raw_private_log_sha256':digest(raw),'raw_log_publication':'NOT_PUBLISHED','preserved_initial_proof':str(preserved.relative_to(ROOT))}
    old.write_text(json.dumps(proof,indent=2)+'\n')
    fcntl.flock(lock,fcntl.LOCK_UN)
    print(json.dumps({'exit_code':result,'source_count':len(before),'source_changes':changes,'proof':str(old.relative_to(ROOT))}))
    raise SystemExit(result or (1 if changes else 0))
if __name__=='__main__':main()
