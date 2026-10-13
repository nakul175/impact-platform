"""Read-only local source/evidence checks; never execute the product or package checker."""
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

BASE = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0')
REPO = BASE / 'work/imprana-framework-refinement-20261011'
OUT = BASE / 'outputs/imprana-qa-reconciliation-20261011'
PACKAGE = BASE / 'outputs/imprana-qa-v13-audit-20261011/reference/aplyd-testing-qa-v1.3'
BASELINE = 'c1bcae29718bcae0fac51000d69734a536061fba'
APP = '8a1e405f0086033dfb25ad834689a08bfe9f1eea'
DOCROOT = Path('docs/qa/current-20261011')
NAMES = ['README.md', 'CURRENT-TEST-STRATEGY.md', 'TEST-DATA-AND-ENVIRONMENTS.md',
         'SPECIALIST-VERIFICATION-PLANS.md', 'RELEASE-TEST-PLAN.md',
         'EXECUTION-AND-DEFECT-PROTOCOL.md']
CHECKS = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def pin(path, root=REPO):
    data = (root / path).read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)

def check(name, passed, detail, kind='mechanical_source_check'):
    CHECKS.append({'check': name, 'passed': bool(passed), 'kind': kind, 'detail': detail})

texts = {name: (REPO / DOCROOT / name).read_text() for name in NAMES}
pins = [pin(DOCROOT / name) for name in NAMES]
check('Documentation HEAD equals declared baseline', git('rev-parse', 'HEAD').decode().strip() == BASELINE, BASELINE)
check('All six reviewed documents bind the documentation and application source',
      all(BASELINE in t and APP in t for t in texts.values()), {'reviewed_documents': 6})
versions = json.loads((REPO / 'VERSION.json').read_text())
check('Actual source versions and immutable migration population',
      versions['build'] == '0.39.0' and versions['domain_api'] == '1.28.0'
      and versions['platform_api'] == '1.11.0'
      and len(list((REPO / 'infrastructure/migrations').glob('*.sql'))) == 43,
      {'versions': versions, 'sql_migrations': len(list((REPO / 'infrastructure/migrations').glob('*.sql')))})

linked_indices = {'docs/DOCUMENTATION-INDEX.md', 'docs/current/DOCUMENTATION-INDEX.md', 'docs/qa/README.md'}
tracked = []
errors = []
for row in git('ls-tree', '-r', '-z', BASELINE).split(b'\0'):
    if not row:
        continue
    meta, path_raw = row.split(b'\t')
    mode, kind, blob = meta.decode().split()
    name = path_raw.decode()
    if name in linked_indices:
        continue
    path = REPO / name
    if mode == '120000':
        data = os.readlink(path).encode()
        actual_mode = '120000'
    elif path.is_file():
        data = path.read_bytes()
        actual_mode = '100755' if path.stat().st_mode & 0o111 else '100644'
    else:
        errors.append({'path': name, 'reason': 'not an ordinary protected tracked file'})
        continue
    actual_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual_blob != blob or actual_mode != mode:
        errors.append({'path': name, 'expected_blob': blob, 'actual_blob': actual_blob,
                       'expected_mode': mode, 'actual_mode': actual_mode})
    tracked.append({'path': name, 'blob': blob, 'mode': mode})
check('All protected baseline tracked blobs and modes preserved', not errors,
      {'checked_count': len(tracked), 'excluded_additive_index_paths': sorted(linked_indices), 'errors': errors})

additive = []
for name in linked_indices:
    diff = git('diff', '--unified=0', BASELINE, '--', name).decode()
    deleted = [line for line in diff.splitlines() if line.startswith('-') and not line.startswith('---')]
    additive.append({'path': name, 'deleted_content_lines': deleted})
check('Existing index/readme content remains additive', all(not item['deleted_content_lines'] for item in additive), additive)

links = []
link_errors = []
external = []
for name, text in texts.items():
    source = REPO / DOCROOT / name
    for m in re.finditer(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
        target = m.group(1).strip().strip('<>')
        line = text[:m.start()].count('\n') + 1
        if re.match(r'^https?://', target):
            external.append({'source': name, 'line': line, 'url': target, 'network_validation': 'NOT_PERFORMED'})
            continue
        if not target or target.startswith('#'):
            continue
        target = unquote(target.split('#')[0])
        resolved = (source.parent / target).resolve()
        row = {'source': name, 'line': line, 'target': target,
               'exists': resolved.exists(), 'confined': resolved.is_relative_to(REPO)}
        links.append(row)
        if not row['exists'] or not row['confined']:
            link_errors.append(row)
check('Six-document relative links resolve and remain confined', not link_errors,
      {'checked_count': len(links), 'errors': link_errors, 'external_links_not_fetched': external})
check('Authored current prose stays within Imprana Commons scope',
      not any(re.search(r'(?i)health\s+saha|routine-visit|ASHA\b', t) for t in texts.values()),
      {'semantic_scope': 'Imprana Commons / impact-platform only'})

fixture_paths = ['specification/fixtures/api-fixture.json', 'specification/fixtures/records.json',
                 'specification/fixtures/grants.json', 'specification/reference-v1/fixtures/vectors.json',
                 'scripts/fixture_support.py', 'qualification/perf_support.py']
fixture_pins = [pin(Path(path)) for path in fixture_paths]
data_text = texts['TEST-DATA-AND-ENVIRONMENTS.md']
check('All six dataset/input SHA claims equal current source bytes',
      all(item['sha256'] in data_text for item in fixture_pins), fixture_pins)
fixture = json.loads((REPO / fixture_paths[0]).read_text())
check('Fixture identity, actor count, start and expiry claims match source',
      fixture['fixture_id'] == 'impact-acceptance-20260925-v1'
      and fixture['fixture_expires_at'] == '2027-09-01T00:00:00Z'
      and len(fixture['actors']) == 10
      and 'FIXTURE_STARTS_AT = "2026-01-01T00:00:00Z"' in (REPO / 'scripts/fixture_support.py').read_text(),
      {'fixture_id': fixture['fixture_id'], 'actors': len(fixture['actors']),
       'expiry': fixture['fixture_expires_at'], 'source_start': '2026-01-01T00:00:00Z'})

schema = json.loads((PACKAGE / 'standards/register-schema.json').read_text())
protocol = texts['EXECUTION-AND-DEFECT-PROTOCOL.md']
schema_result = []
for name, fields in schema.items():
    row = re.search(r'^\| `' + re.escape(name) + r'\.csv` \| ([^\n]+)', protocol, re.M)
    actual = re.findall(r'`([^`]+)`', row.group(1).split('|')[0]) if row else None
    schema_result.append({'schema': name, 'exact_order_and_fields': actual == fields, 'field_count': len(fields)})
check('Eight proposed register field sets exactly match unchanged package schema',
      all(item['exact_order_and_fields'] for item in schema_result), schema_result)
statuses = json.loads((PACKAGE / 'standards/statuses.json').read_text())
status_map = {'Applicability': 'applicability', 'Execution result': 'execution', 'Freshness': 'freshness',
              'Run purpose': 'run_purpose', 'Quality': 'quality', 'Approval': 'approval',
              'Readiness': 'readiness', 'Delivery': 'delivery', 'Learning': 'learning'}
status_result = []
for label, key in status_map.items():
    row = re.search(r'^\| ' + re.escape(label) + r' \| ([^\n]+)', protocol, re.M)
    actual = re.findall(r'`([^`]+)`', row.group(1).split('|')[0]) if row else None
    status_result.append({'dimension': label, 'exact_vocabulary': actual == statuses[key]})
check('Nine distinct status dimensions exactly match package vocabulary',
      all(item['exact_vocabulary'] for item in status_result), status_result)
pin_helper = (PACKAGE / 'checker/criteria_pin.py').read_text()
check('Proposed canonical identity digest matches shipped helper contract',
      "json.dumps(sorted(pairs),ensure_ascii=False,separators=(',',':')).encode()" in pin_helper
      and "ensure_ascii=False" in protocol and "no final newline" in protocol,
      {'method': 'read helper source only; no helper or checker execution'})

review = json.loads((REPO / 'docs/release-reviews/release-review-0.39.0.json').read_text())
check('Open G11/G12 and threat/chain arithmetic remain exact source facts',
      review['passed'] is False and review['gates']['G11']['status'] == 'Not passed'
      and review['gates']['G12']['status'] == 'Not run'
      and len(review['open_critical']) == 14 and len(review['open_other']) == 13
      and len(review['open_chains']) == 2
      and all(c['decision'] == 'BLOCK' for c in review['open_chains']),
      {'G11': review['gates']['G11']['status'], 'G12': review['gates']['G12']['status'],
       'open_critical': len(review['open_critical']), 'open_other': len(review['open_other']),
       'chains': [{'id': c['id'], 'decision': c['decision']} for c in review['open_chains']]})
owners = (REPO / 'docs/CODEOWNERS').read_text()
check('CODEOWNERS location and actual declared owner are correctly distinguished from enforcement',
      bool(re.search(r'^\*\s+@nakul175$', owners, re.M))
      and 'NOT_VERIFIED' in texts['RELEASE-TEST-PLAN.md'],
      {'source': 'docs/CODEOWNERS', 'owner': '@nakul175', 'live_branch_ruleset_enforcement': 'NOT_VERIFIED'})

root_receipt = json.loads((OUT / 'ROOT-INTEGRATION-CHECKS.json').read_text())
root_current = {item['path']: item for item in root_receipt['details']['document_pins']}
preceding_deltas = []
for p in pins:
    old = root_current.get(p['path'])
    if old and old['sha256'] != p['sha256']:
        preceding_deltas.append({'path': p['path'], 'preceding_sha256': old['sha256'], 'current_sha256': p['sha256']})
check('Earlier root receipt remains explicitly scoped to its recorded edition',
      root_receipt['passed_checks'] == root_receipt['total_checks'] == 14
      and len(preceding_deltas) == 1
      and preceding_deltas[0]['path'] == str(DOCROOT / 'CURRENT-TEST-STRATEGY.md'),
      {'earlier_receipt_pin': pin(Path('ROOT-INTEGRATION-CHECKS.json'), OUT),
       'recorded_at_utc': root_receipt['recorded_at_utc'],
       'later_strategy_risk_paragraph_is_reviewed_by_this_receipt': preceding_deltas})

def cite(name, pattern):
    text = texts[name]
    match = re.search(pattern, text)
    return {'path': str(DOCROOT / name), 'line': text[:match.start()].count('\n') + 1 if match else None}

semantic = [
 ('Source planning and live state remain separate', 'RELEASE-TEST-PLAN.md', r'Candidate scope/build/artifact',
  'Source pins do not assert built/deployed qualification. Candidate, scope, environment, dates and authority remain unselected.'),
 ('Source hierarchy and proposed Sprint 2 are preserved', 'RELEASE-TEST-PLAN.md', r'172 active R1 Pilot stories',
  '54 epics/368 active stories/1328 source scenarios/1131 tasks/779 edges; R1 172 and proposed four-story 26 points agree with preserved product sources. Four earlier In Review stories are not promoted.'),
 ('Criteria and test denominators stay distinct', 'CURRENT-TEST-STRATEGY.md', r'825 designed baseline cases',
  '825 designed cases, 50/108 nonprofit designs, 1328 original source scenarios and 1069 supplements are not added or equated; 37/7/13 gaps remain explicit.'),
 ('Complete independent source selection and unknown applicability remain open', 'RELEASE-TEST-PLAN.md', r'Export the complete in-scope PM criterion population',
  'No checker-ready approved export, default criterion versions, mappings, exclusions or complete scope review are invented.'),
 ('Original numerical contracts retained exactly', 'CURRENT-TEST-STRATEGY.md', r'The retained strategy\x27s other numeric conditions',
  'Read against retained strategy §§4/7/9/11: ≥90% critical-module branch target; UAT≥90% unassisted/no critical error; AI≥200 where feasible/20% boundary; supported/citation95/98; extraction95/90; abstention95/≤10; official exact; representative200/400 load,60min/8h,RPO15min/RTO4h. Additional original contracts remain referenced, not replaced.'),
 ('Risk scoring and tier validation depth agree with unchanged package', 'CURRENT-TEST-STRATEGY.md', r'For future reviewed risk records',
  'Impact/likelihood1–4, impact4Critical,High9–16/material irreversible,Medium4–8,Low1–3; provisional unknown likelihood and escalation; mandatory contractual/legal/accessibility requirements nonwaivable. Proposed adoption is not an actual rating/review.'),
 ('Meaningful API/native/browser/component evidence is separated', 'CURRENT-TEST-STRATEGY.md', r'Native database/worker/identity',
  'Real persisted outcomes/current authority/receipts and concurrent native roles are distinct from pure/reference/provider fakes, browser models, markup and health smoke.'),
 ('Supported platforms and accessibility remain unqualified', 'SPECIALIST-VERIFICATION-PLANS.md', r'Resize and reflow',
  '200% text/400% reflow and manual AT/process review address retained statement gaps. Prior Chromium153 synthetic scan and keyboard subset remain historical; no new conformance/support commitment.'),
 ('Synthetic data and fixture setup cannot grant authority', 'TEST-DATA-AND-ENVIRONMENTS.md', r'Use synthetic data only',
  'Private secrets and real personal/participant/supplier data are excluded; distinct synthetic actors model natural-person fences but supply no real approval. Exact expiry/preflight/disposal safeguards match runner/loader/seed source.'),
 ('Environment modes and resource boundaries are honest', 'TEST-DATA-AND-ENVIRONMENTS.md', r'No mode in this table is an approved current execution environment',
  'Owned local/UUID/ports, native provisioned roles, pinned local IDP and fake-provider mechanics match Makefile/runner; no installs, provider calls, paid resources or hosted scope authorised. Cleanup retains history and errors.'),
 ('Immutable attempts and explicit current selection protect failures', 'EXECUTION-AND-DEFECT-PROTOCOL.md', r'One run-register|A PASS cannot|PASS cannot|Ordinary deterministic|Deterministic required',
  'Unique immutable actual attempts/groups, parent retests, preserved earlier selection, full candidate pins, controlled evidence root and all failures/skips; no latest-timestamp/majority rescue or fictional rows.'),
 ('Severity migration and same-case retest remain explicit', 'EXECUTION-AND-DEFECT-PROTOCOL.md', r'S1',
  'S1→D4...S4→D1 is proposed explicit migration, not overwritten history; downgraded/closed defects need authentic independent review and same-case current qualification/fixed build. No fake human closure.'),
 ('Protected invariants and eligible exceptions remain separate', 'EXECUTION-AND-DEFECT-PROTOCOL.md', r'nonwaivable|Nonwaivable',
  'No exception turns FAIL into PASS, supplies missing authority, or waives isolation/current authority/natural-person/history/official decimal/mandatory rights.'),
 ('Statistical AI and unassisted UAT protocols do not create results', 'SPECIALIST-VERIFICATION-PLANS.md', r'Dataset/corpus:',
  'Held-out splits/independent labels, all failures/slices/repetitions, provider/model/prompt/tool/corpus pins and real reviewers remain required. Draft charters have no sessions; UAT cohort/consent/acceptance unresolved; no benefit/ROI claim.'),
 ('Representative NFR and restore limits are retained', 'SPECIALIST-VERIFICATION-PLANS.md', r'PERF-01 retains',
  'Source large-data/cohort/offered-load profile and monthly/quarterly recovery obligations preserved. Sandbox/short/shared/proxy/CI/real-host gaps remain distinct. No target/budget relaxed or measured result supplied.'),
 ('Existing CI portfolio is described without live enforcement claim', 'RELEASE-TEST-PLAN.md', r'Existing hosted gate portfolio',
  'Read actual checks15min and qualification30/20/40/45 jobs, docs paths filter, cancel newer PR and explicit stages. No new aggregator/merge-queue/protection installation; exact-head actual results and financial authority remain required.'),
 ('Package checker observations are not product tests', 'EXECUTION-AND-DEFECT-PROTOCOL.md', r'57',
  'Prior unchanged package57 regression checks/fictional fixtures are subordinate record/source checks, not Imprana feature, ASVS, human or statistical qualification.'),
 ('Readiness, delivery, approval and learning are distinct unresolved states', 'RELEASE-TEST-PLAN.md', r'Quality is UNASSESSED',
  'Current source G11 Notpassed/G12 Notrun/14 critical/13other/2BLOCK and missing confirmation preserved; future qualityUNASSESSED,approvalPENDING,readinessNOTREADY,deliveryNOTESTABLISHED. No owner acceptance or runtime action.'),
]
for name, doc, pattern, note in semantic:
    c = cite(doc, pattern)
    check(name, c['line'] is not None, {'review_observation': note, 'document_citation': c}, 'bounded_AI_semantic_review')

source_names = ['AGENTS.md', 'CLAUDE.md', 'VERSION.json', 'Makefile', 'scripts/run.py',
 'scripts/fixture_support.py', 'specification/fixtures/load.py', 'specification/fixtures/seed.sql',
 'qualification/conftest.py', '.github/workflows/checks.yml', '.github/workflows/qualification.yml',
 'docs/CODEOWNERS', 'docs/current/Impact-Management-Test-Strategy-v1.1.md',
 'docs/current/ACCESSIBILITY-STATEMENT.md', 'docs/governance/AI-EVALUATION-AND-LIMITS.md',
 'docs/governance/BACKUP-DR.md', 'docs/release-reviews/release-review-0.39.0.json',
 'docs/current/threat-register.json', 'docs/product/06-NEXT-SPRINT-REFINEMENT.md',
 'docs/product/04-RELEASE-GOALS.md']
package_names = ['standards/register-schema.json', 'standards/statuses.json',
 'standards/STATUS-MODEL.md', 'standards/RISK-CLASSIFICATION.md', 'checker/criteria_pin.py',
 'workflow/REPETITION-POLICY.md', 'workflow/CRITERIA-SOURCE-PINNING.md',
 'workflow/EVIDENCE-ROOT.md', 'workflow/SOURCE-PROTECTION.md', 'checker/README.md']

receipt = {
 'record': 'IMPRANA-CURRENT-QA-INDEPENDENT-SOURCE-REVIEW-20261011',
 'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
 'scope': 'Separate bounded AI document/source-evidence review of six non-owned Imprana current QA documents; not owner approval, adoption, product qualification or release certification',
 'documentation_baseline': BASELINE, 'application_source': APP,
 'reviewed_document_pins': pins,
 'authorship_exclusion': ['docs/qa/current-20261011/CRITERIA-AND-CASE-BRIDGE.md',
                         'PRIMARY-SOURCE-CENSUS.json', 'BRIDGE-AUTHORING-RECEIPT.json'],
 'authorship_exclusion_note': 'Another agent independently reviews these authored artifacts. This receipt uses their previously observed census facts only as references and independently checks unchanged protected source, not own-authored semantics.',
 'mechanical_source_checks': [c for c in CHECKS if c['kind'] == 'mechanical_source_check'],
 'bounded_AI_semantic_review_checks': [c for c in CHECKS if c['kind'] == 'bounded_AI_semantic_review'],
 'source_pins': [pin(Path(p)) for p in source_names],
 'package_pins': [pin(Path(p), PACKAGE) for p in package_names],
 'relative_links': links,
 'findings': [{'id': 'OBS-01', 'severity': 'PROVENANCE_LIMITATION', 'blocking_document_defect': False,
               'detail': 'Earlier root14/14 receipt predates the added risk scoring paragraph and preserves strategy870192... rather than currentd555.... It must remain a dated earlier-edition observation; this fresh source review explicitly binds currentd555. Parent notified before any correction.',
               'source': preceding_deltas}],
 'unresolved_product_decisions': ['Actual complete approved operating source scope/criterion revision identities and independent completeness/applicability review',
 'Actual reviewed case/code/manual bindings and normalized register/evidence selection adoption',
 'Actual candidate/artifact/environment/data/tool/model/provider/protocol pins and authorised resource boundary',
 'Named accountable QA/specialist/domain/operations reviewers, real decisions, participants/data permissions and financial authority',
 'Current G11/G12 threats/chains and all required actual qualification/acceptance results',
 'Live target-branch/source protection, required checks/fresh review and bypass enforcement'],
 'limitations': ['AI reviewer is not an externally authorised human or appointed specialist.',
 'No application/unit/API/native/browser/performance/provider/package tests or live CI/protection checks were run.',
 'No network, credentials, external messages, deployment, release action or source changes occurred.',
 'External W3C/GitHub URLs are recorded references; no network link/standard verification performed in this bounded local review.',
 'This is semantic source agreement and document integration evidence, not a proof that future test procedures are implemented or exhaustive.',
 'Initial read-path/glob misses and output truncation were resolved with bounded exact reads; no product failure inference or fabricated executed check.',
 'Only reviewed exact document bytes apply. Later content must receive an explicit separate delta review.'],
 'check_totals': {'passed': sum(c['passed'] for c in CHECKS), 'failed': sum(not c['passed'] for c in CHECKS), 'total': len(CHECKS)},
 'disposition': 'NO_BLOCKING_DOCUMENT_DEFECT_FOUND_IN_REVIEWED_SCOPE' if all(c['passed'] for c in CHECKS) else 'SOURCE_REVIEW_CHECK_FAILURE_REQUIRES_RECONCILIATION',
 'product_test_result': 'NOT_RUN_BY_THIS_REVIEW', 'owner_approval': False,
 'adoption_approval': False, 'product_ready': False, 'release_approval': False,
 'repo_or_native_mutations': False,
}
target = OUT / 'INDEPENDENT-CURRENT-QA-DOCUMENT-REVIEW.json'
target.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'path': str(target), 'bytes': target.stat().st_size,
                  'sha256': sha(target.read_bytes()), 'checks': receipt['check_totals'],
                  'disposition': receipt['disposition'],
                  'failed_checks': [c['check'] for c in CHECKS if not c['passed']]}))
