"""Bounded local document/source checks; no product execution or approval."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0')
REPO = ROOT / 'work/imprana-framework-refinement-20261011'
OUT = ROOT / 'outputs/imprana-qa-reconciliation-20261011'
BASE = 'c1bcae29718bcae0fac51000d69734a536061fba'
EDITION = REPO / 'docs/qa/current-20261011'
ALLOWED_EXISTING = {'docs/DOCUMENTATION-INDEX.md', 'docs/current/DOCUMENTATION-INDEX.md', 'docs/qa/README.md'}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def subsequence(old, new):
    remaining = iter(new)
    return all(any(line == candidate for candidate in remaining) for line in old)

checks = []
details = {}
def check(name, passed, info=None):
    checks.append({'check': name, 'passed': bool(passed), 'detail': info})

check('expected documentation baseline HEAD', git('rev-parse', 'HEAD').decode().strip() == BASE)
tree = git('ls-tree', '-r', '-z', BASE).split(b'\0')
protected_errors = []
protected_count = 0
for item in tree:
    if not item:
        continue
    metadata, raw_path = item.split(b'\t', 1)
    mode, kind, oid = metadata.decode().split()
    path = raw_path.decode()
    if kind != 'blob' or path in ALLOWED_EXISTING:
        continue
    actual = REPO / path
    if not actual.exists() and not actual.is_symlink():
        protected_errors.append({'path': path, 'error': 'missing'})
        continue
    data = os.readlink(actual).encode() if mode == '120000' else actual.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    actual_mode = '120000' if actual.is_symlink() else ('100755' if actual.stat().st_mode & 0o111 else '100644')
    if blob != oid or actual_mode != mode:
        protected_errors.append({'path': path, 'expected_blob': oid, 'observed_blob': blob, 'expected_mode': mode, 'observed_mode': actual_mode})
    protected_count += 1
check('every other baseline tracked file preserves exact blob and mode', not protected_errors, {'count': protected_count, 'errors': protected_errors})

for path in sorted(ALLOWED_EXISTING):
    before = git('show', f'{BASE}:{path}').decode().splitlines()
    after = (REPO/path).read_text().splitlines()
    check(f'original index content preserved: {path}', subsequence(before, after))

markdown = sorted(EDITION.glob('*.md'))
check('seven current planning documents present', len(markdown) == 7)
link_errors = []
link_count = 0
for path in markdown:
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
        target = target.strip('<>')
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith('#'):
            continue
        linked = (path.parent / unquote(parsed.path)).resolve()
        link_count += 1
        if not linked.is_relative_to(REPO) or not linked.exists():
            link_errors.append({'source': str(path.relative_to(REPO)), 'target': target})
check('new documentation relative links exist and stay in repository', not link_errors, {'count': link_count, 'errors': link_errors})
unrelated = [(str(p.relative_to(REPO)), token) for p in markdown for token in ('Saha', 'saha', 'patient', 'controller188', 'D03') if token in p.read_text()]
check('current authored prose stays within Imprana scope', not unrelated, unrelated)

census = json.loads((EDITION/'evidence/PRIMARY-SOURCE-CENSUS.json').read_text())
check('primary census active and historical populations explicit', census['source_counts']['active_original_scenarios'] == 1328 and census['source_counts']['retained_Split_original_scenarios'] == 7 and census['source_counts']['active_story_records'] == 368 and census['source_counts']['task_dependency_edges'] == 779)
check('primary census records thirteen source-only checks', len(census['source_checks']) == 13 and all(census['source_checks'].values()))
check('source census declares no approved export/version/execution', census['original_source_has_individual_ac_version_field'] is False and census['safe_export_recommendation']['decision'] == 'NO_CHECKER_READY_EXPORT_OR_NORMALIZED_REGISTERS_NOW' and census['authority_or_readiness_established'] is False and census['application_or_package_checks_executed'] is False)
for name in ('PRIMARY-SOURCE-CENSUS.json', 'BRIDGE-AUTHORING-RECEIPT.json'):
    check(f'byte-exact author artifact copy: {name}', (OUT/name).read_bytes() == (EDITION/'evidence'/name).read_bytes())
check('canonical backlog CSV hash still matches census', digest((REPO/census['primary_source']['path']).read_bytes()) == census['primary_source']['sha256'])

details['document_pins'] = [{'path': str(p.relative_to(REPO)), 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in markdown]
details['census_pin'] = {'sha256': digest((EDITION/'evidence/PRIMARY-SOURCE-CENSUS.json').read_bytes()), 'bytes': (EDITION/'evidence/PRIMARY-SOURCE-CENSUS.json').stat().st_size}
record = {'scope': 'Imprana source-bound QA planning edition local integration checks; not product testing, owner review, adoption or release approval', 'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'documentation_base': BASE, 'checks': checks, 'passed_checks': sum(c['passed'] for c in checks), 'total_checks': len(checks), 'details': details, 'product_tests_executed': False, 'remote_actions': False, 'owner_approval': False}
target = OUT/(sys.argv[1] if len(sys.argv) > 1 else 'ROOT-INTEGRATION-CHECKS.json')
assert not target.exists(), 'Preserve prior check receipt; use a new attempt file'
target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'receipt': str(target), 'passed_checks': record['passed_checks'], 'total_checks': record['total_checks'], 'failed': [c for c in checks if not c['passed']]}, indent=2))
raise SystemExit(0 if all(c['passed'] for c in checks) else 1)
