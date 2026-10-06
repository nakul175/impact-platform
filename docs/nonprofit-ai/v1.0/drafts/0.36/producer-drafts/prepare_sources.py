"""Write private producer source proposals. Does not import or run a producer."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import difflib

ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
DEST = Path('/private/tmp/tola-ai-036-producer-draft')
EXTRAS = ['Makefile','VERSION.json','apps/api/impact_api/ai_enablement_catalog.py','apps/api/impact_api/ai_learning_content.py','apps/api/impact_api/ai_task_practice.py','apps/api/impact_api/main.py','apps/web/ai-walkthrough.html','apps/web/index.html','apps/web/package-lock.json','apps/web/package.json','apps/web/tsconfig.json','apps/web/vite.config.ts','qualification/test_deploy_unit.py','scripts/run.py','scripts/smoke.py']
FULL_ROOTS = ['apps/api/impact_api','apps/web/src','qualification','scripts','deploy','infrastructure','packages/contracts','specification/reference-v1','.github/workflows','tools/browser','tools/dev-db']
FULL_EXTRAS = ['VERSION.json','Makefile','docs/current/CURRENT-DATA-DICTIONARY.md','apps/web/package.json','apps/web/package-lock.json','apps/web/vite.config.ts','apps/web/index.html','apps/web/ai-walkthrough.html','tools/browser/package.json','tools/browser/package-lock.json','tools/dev-db/package.json','tools/dev-db/package-lock.json']
SUFFIXES = {'.py','.json','.sql','.sh','.ts','.tsx','.css','.yaml','.yml','.mjs'}
ADDITIONS = ['apps/web/src/AIProcurementPreviewModel.ts','apps/web/src/AIProcurementPreview.tsx','tools/browser/ai-procurement-preview-model-check.mjs']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(v): return json.dumps(v,sort_keys=True,separators=(',',':'))
def dep_sha(p):
    v=json.loads(p.read_text());v.pop('version',None)
    if 'packages' in v: v['packages'][''].pop('version',None)
    return hashlib.sha256(encode(v).encode()).hexdigest()
build=set(EXTRAS)|{str(p.relative_to(ROOT)) for p in (ROOT/'apps/web/src').rglob('*') if p.is_file() and p.suffix in {'.ts','.tsx','.css','.json'}}
lint=build|{str(p.relative_to(ROOT)) for p in (ROOT/'tools/browser').glob('*.mjs')}
full=set(FULL_EXTRAS)|{str(p.relative_to(ROOT)) for d in FULL_ROOTS for p in (ROOT/d).rglob('*') if p.is_file() and not any(x in {'__pycache__','node_modules','dist'} for x in p.parts) and p.suffix in SUFFIXES}
assert (len(full),len(build),len(lint))==(417,72,108)
future={'full':sorted(full|set(ADDITIONS)), 'build':sorted(build|set(ADDITIONS[:2])), 'lint':sorted(lint|set(ADDITIONS))}
assert tuple(map(len,[future['full'],future['build'],future['lint']]))==(420,74,111)
migrations={p.name:sha(p) for p in sorted((ROOT/'infrastructure/migrations').glob('*.sql'))}
manifest=json.loads((ROOT/'docs/evidence/sprint-0.34-local-summary.json').read_text())
assert len(migrations)==40 and migrations=={Path(p).name:h for p,h in manifest['migration_sha256'].items()}
version=json.loads((ROOT/'VERSION.json').read_text());assert version['build']=='0.35.0'
version['build']='0.36.0'
constants='\nEXPECTED_VERSION = '+repr(version)+'\nFROZEN_MIGRATIONS = '+repr(migrations)+'\nDEPENDENCY_SHA256 = '+repr({p:dep_sha(ROOT/p) for p in ['apps/web/package.json','apps/web/package-lock.json']})+'\n'
guards=(DEST/'guard-template.py.txt').read_text()
baselines=DEST/'preserved035';baselines.mkdir(exist_ok=False)
for kind,file in [('full','tola-ai-035-full-qualification.py'),('unit','tola-ai-035-unit.py'),('lint','tola-ai-035-lint-final.py')]:
    original=Path('/private/tmp')/file;shutil.copyfile(original,baselines/file)
    source=original.read_text()
    def replace(a,b):
        nonlocal_unused=None
        global source
        assert source.count(a)==1,(kind,a)
        source=source.replace(a,b,1)
    source=source.replace('sprint-0.35-','sprint-0.36-').replace('checkpoint035_','checkpoint036_')
    if kind=='full':
        replace("sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'apps/api')]\nimport run as runner\n",'')
        replace("parser.add_argument('--database', default='impact_test_tola_ai_checkpoint036_native')", "parser.add_argument('--database', default='impact_test_tola_ai_checkpoint036_native')\nparser.add_argument('--execute', action='store_true')\nparser.add_argument('--baseline-commit')\nparser.add_argument('--preserved-prior', type=Path)")
        replace("args = parser.parse_args()\n", "args = parser.parse_args()\nif not args.execute:\n    print(json.dumps(dict(status='NOT_RUN', expected_source_count=420, mode=args.mode, baseline_commit_required=True)))\n    raise SystemExit(0)\nqualification_guard(args.baseline_commit)\nsys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'apps/api')]\nimport run as runner\n")
        replace("source_start = sources()\n", "source_start = sources()\nif set(source_start) != set(EXPECTED_SOURCE_NAMES):\n    raise RuntimeError('Exact closed 420-file full source inventory required')\n")
        replace("fixture_dsn = None\n", "preserved_prior = preserve_prior_outputs(evidence, prefix, args.preserved_prior)\nfixture_dsn = None\n")
        replace("source_end = sources()\n", "source_end = sources()\n    if set(source_end) != set(EXPECTED_SOURCE_NAMES):\n        raise RuntimeError('Full source inventory changed during qualification')\n")
        replace("proof = dict(started_at=started", "if changes:\n        result = result or 1\n    proof = dict(baseline_commit=args.baseline_commit, preserved_prior_proofs=preserved_prior, migration_sha256=FROZEN_MIGRATIONS, started_at=started")
    elif kind=='unit':
        replace("import fcntl\n", "import argparse\nimport fcntl\n")
        replace("if Path.cwd().resolve()!=ROOT:\n", "parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--baseline-commit');args=parser.parse_args()\nif not args.execute:\n    print(json.dumps(dict(status='NOT_RUN',expected_source_count=420,recipe='make unit PY=.venv/bin/python',baseline_commit_required=True)))\n    raise SystemExit(0)\nqualification_guard(args.baseline_commit)\nif Path.cwd().resolve()!=ROOT:\n")
        replace("before=sources()\n", "before=sources()\nif set(before)!=set(EXPECTED_SOURCE_NAMES):raise RuntimeError('Exact closed 420-file unit inventory required')\n")
        replace("end=sources()\n", "end=sources()\n    if set(end)!=set(EXPECTED_SOURCE_NAMES):raise RuntimeError('Unit source inventory changed during qualification')\n")
        replace("summary=dict(started_at=started", "if changes: result=result or 1\n    summary=dict(baseline_commit=args.baseline_commit,migration_sha256=FROZEN_MIGRATIONS,started_at=started")
    else:
        replace("assert len(names)==108", "assert len(names)==111 and {str(p.relative_to(ROOT)) for p in names}==set(EXPECTED_SOURCE_NAMES)")
        replace("parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()", "parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--baseline-commit');args=parser.parse_args()")
        replace("print(json.dumps({'status':'NOT_RUN','source_count':len(sources()),'recipe':'make lint'}));return", "print(json.dumps({'status':'NOT_RUN','expected_source_count':111,'recipe':'make lint','baseline_commit_required':True}));return")
        replace("assert Path.cwd().resolve()==ROOT\n", "assert Path.cwd().resolve()==ROOT\n    qualification_guard(args.baseline_commit)\n")
        replace("assert old.is_file() and preserved.is_file() and old.read_bytes()==preserved.read_bytes()", "prior=prior_proof(old,preserved)")
        replace("tola-ai-035-lint-final.log", "tola-ai-036-lint-final.log")
        replace("Fresh repeat after three checker-only corrections.", "Source-bound 0.36 qualification; first run or explicitly preserved repeat.")
        replace("proof={'started_at':start", "if changes: result=result or 1\n    proof={'baseline_commit':args.baseline_commit,'migration_sha256':FROZEN_MIGRATIONS,'started_at':start")
        replace("'preserved_initial_proof':str(preserved.relative_to(ROOT))", "'preserved_initial_proof':prior")
    # Definitions precede execution; all defaults stop before runtime imports/locks.
    anchor="ROOT = Path(" if kind!='unit' else "ROOT=Path("
    lines=source.splitlines(True);at=next(i for i,l in enumerate(lines) if l.startswith(anchor))
    while ')' not in lines[at]:at+=1
    source=''.join(lines[:at+1])+constants+'EXPECTED_SOURCE_NAMES = '+repr(future['lint' if kind=='lint' else 'full'])+'\n'+guards+'\n'+''.join(lines[at+1:])
    target=DEST/('tola-ai-036-'+{'full':'full-qualification','unit':'unit','lint':'lint-final'}[kind]+'.py')
    ast.parse(source);target.write_text(source)
    (DEST/(kind+'.patch')).write_text(''.join(difflib.unified_diff(original.read_text().splitlines(True),source.splitlines(True),fromfile=str(original),tofile=str(target))))
(DEST/'frozen-inventories.json').write_text(json.dumps({'source_derivation':'Independent original 0.35 producer definitions and exact root-confirmed build/lint extras; not the supplied report under validation','expected_version':version,'inventories':future,'migration_sha256':migrations,'dependency_sha256':{p:dep_sha(ROOT/p) for p in ['apps/web/package.json','apps/web/package-lock.json']}},indent=2)+'\n')
