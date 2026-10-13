#!/usr/bin/env python3
"""Bounded read-only document/source review; never executes product/package gates."""
import csv
import datetime
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import Counter
from pathlib import Path

BASE = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0')
REPO = BASE / 'work/imprana-framework-refinement-20261011'
OUT = BASE / 'outputs/imprana-qa-reconciliation-20261011/bridge-independent-review'
PACKAGE = BASE / 'outputs/imprana-qa-v13-audit-20261011/reference/aplyd-testing-qa-v1.3'
HEAD = 'c1bcae29718bcae0fac51000d69734a536061fba'
checks = []
pins = {}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git_raw(path):
    return subprocess.check_output(['git', 'show', HEAD + ':' + path], cwd=REPO)

def read(path):
    raw = (REPO / path).read_bytes()
    pins[path] = {'sha256': sha(raw), 'bytes': len(raw)}
    return raw

def check(identity, value, observation):
    checks.append({'check_id': identity, 'result': 'PASS' if value else 'FAIL', 'observation': observation})

# Enumerate primary CSV first; neither matrix nor census establishes its denominator.
CSV = 'docs/backlog/backlog.csv'
raw_csv = read(CSV)
rows = list(csv.DictReader(io.StringIO(raw_csv.decode('utf-8'), newline='')))
by_story = {r['ID']: r for r in rows}
primary = {}
source_parts = {}
missing_given = []
for row in rows:
    text = row['Acceptance and rejection criteria (Gherkin)']
    starts = list(re.finditer(r'(?m)^Scenario: (.+)$', text))
    parts = []
    for index, match in enumerate(starts):
        # Retained separator convention is one LF before each later Scenario.
        start = 0 if index == 0 else match.start() - 1
        end = starts[index + 1].start() - 1 if index + 1 < len(starts) else len(text)
        block = text[start:end]
        key = (row['ID'], index + 1)
        primary[key] = {'label': match.group(1), 'block': block, 'start': start, 'end': end,
                        'full_hash': sha(text.encode()), 'hash': sha(block.encode())}
        parts.append(block)
        if row['Status'] != 'Split' and not re.search(r'(?m)^\s+Given ', block):
            missing_given.append(key)
    source_parts[row['ID']] = parts
active_rows = [r for r in rows if r['Status'] != 'Split']
history_rows = [r for r in rows if r['Status'] == 'Split']
active = {k: v for k, v in primary.items() if by_story[k[0]]['Status'] != 'Split'}
history = {k: v for k, v in primary.items() if by_story[k[0]]['Status'] == 'Split'}
check('BRIDGE-01', len(rows) == len(by_story) == 370 and len(active_rows) == 368 and len(history_rows) == 2,
      {'all': len(rows), 'active': len(active_rows), 'Split': len(history_rows)})
check('BRIDGE-02', len(active) == 1328 and len(history) == 7 and len(primary) == 1335 and
      {r['ID'] for r in history_rows} == {'FR-AI-016', 'US-DX-01'},
      {'active_scenarios': len(active), 'retained_Split_scenarios': len(history), 'all_scenarios': len(primary)})
check('BRIDGE-03', all(''.join(source_parts[r['ID']]) == r['Acceptance and rejection criteria (Gherkin)'] for r in rows),
      'Independent primary-text blocks reconstruct all370 complete Gherkin fields exactly.')
check('BRIDGE-04', raw_csv == git_raw(CSV), 'Current primary CSV bytes match the pinned documentation commit.')

# Only now compare the proposed census and existing alias/matrix.
census_path = BASE / 'outputs/imprana-qa-reconciliation-20261011/PRIMARY-SOURCE-CENSUS.json'
census_raw = census_path.read_bytes()
census = json.loads(census_raw)
bridge_path = 'docs/qa/current-20261011/CRITERIA-AND-CASE-BRIDGE.md'
bridge_raw = read(bridge_path)
bridge = bridge_raw.decode()
alias_path = 'docs/product/framework-v4-20261011/bundle-review/CRITERION-ALIAS-MAP.json'
matrix_path = 'docs/product/framework-v4-20261011/task-author/acceptance-task-matrix.proposed.json'
aliases = json.loads(read(alias_path))
criteria = json.loads(read(matrix_path))['criteria']
aliases_by_key = {(r['storyId'], r['scenarioOrdinal']): r for r in aliases}
matrix_by_key = {(r['story_id'], int(r['criterion_id'].rsplit('-', 1)[1])): r for r in criteria}
reconciled = {(r['source_story_id'], r['scenario_ordinal']): r for r in census['same_scenario_alias_reconciliation']}
check('BRIDGE-05', len(aliases) == len(aliases_by_key) == len(criteria) == len(matrix_by_key) ==
      len(reconciled) == 1328 and set(aliases_by_key) == set(matrix_by_key) == set(reconciled) == set(active),
      'Primary-source identity set equals all1328 unique alias, matrix and census identities; no substitutions/duplicates.')
alias_errors = []
for key, source in active.items():
    a, m, c = aliases_by_key[key], matrix_by_key[key], reconciled[key]
    expected_ids = {'task_matrix_id': 'AC-' + key[0] + '-' + f'{key[1]:03}',
                    'story_annotation_id': key[0] + '-AC-' + f'{key[1]:02}',
                    'evaluation_plan_id': 'EVAL-' + key[0] + '-' + f'{key[1]:03}'}
    exact = (a['sourceScenarioTitle'] == m['source_scenario'] == c['source_scenario_label'] == source['label']
             and a['sourceFullGherkinSha256'] == m['source_provenance']['source_story_gherkin_sha256'] == source['full_hash']
             and a['exactSourceBlockSha256'] == m['source_provenance']['exact_scenario_block_sha256'] == c['source_block_sha256'] == source['hash']
             and m['source_provenance']['original_scenario_block'] == source['block']
             and c['existing_same_scenario_anchor_ids'] == expected_ids
             and a['taskMatrixId'] == m['criterion_id'] == expected_ids['task_matrix_id']
             and a['storyAnnotationId'] == expected_ids['story_annotation_id']
             and m['evaluation_plan_id'] == expected_ids['evaluation_plan_id'])
    if not exact:
        alias_errors.append(list(key))
check('BRIDGE-06', not alias_errors, {'exact_source_and_alias_mismatches': alias_errors})
check('BRIDGE-07', all(m['actual_execution'] == {'state': 'Not run', 'run_id': None, 'date': None,
      'result': None, 'observed_evidence': []} for m in criteria), 'All1328 existing proposed execution fields remain Not run/no evidence.')

expected_stories = []
for row in rows:
    text = row['Acceptance and rejection criteria (Gherkin)']
    expected_stories.append({'source_story_id': row['ID'], 'source_status': row['Status'],
        'scenario_count': len(source_parts[row['ID']]), 'source_full_gherkin_sha256': sha(text.encode()),
        'source_full_gherkin_bytes': len(text.encode()), 'all_block_bytes_concatenate_to_original_full_gherkin': True})
expected_history = []
for key, source in history.items():
    expected_history.append({'source_story_id': key[0], 'source_status': 'Split', 'scenario_ordinal': key[1],
        'source_scenario_label': source['label'], 'source_full_gherkin_sha256': source['full_hash'],
        'source_block_sha256': source['hash'], 'source_character_start': source['start'],
        'source_character_end_exclusive': source['end'], 'source_block_utf8_bytes': len(source['block'].encode())})
check('BRIDGE-08', census['source_story_protection'] == expected_stories and census['historical_Split_sources'] == expected_history,
      'All370 story hashes/statuses/counts and7 historical block identities/offsets/UTF8 lengths are exact.')

task_path = 'docs/product/refinement/backlog-refinement.json'
task_raw = read(task_path)
refinement = json.loads(task_raw)
tasks = [t for s in refinement['stories'] for t in s['tasks']]
task_ids = {t['id'] for t in tasks}
edges = [(t['id'], dep) for t in tasks for dep in t['depends_on']]
old_refinement = json.loads(git_raw(task_path))
old_tasks = [t for s in old_refinement['stories'] for t in s['tasks']]
old_edges = [(t['id'], dep) for t in old_tasks for dep in t['depends_on']]
check('BRIDGE-09', len(tasks) == len(task_ids) == 1131 and len(edges) == len(set(edges)) == 779 and
      all(a in task_ids and b in task_ids for a, b in edges) and tasks == old_tasks and edges == old_edges,
      {'tasks': len(tasks), 'prerequisite_edges': len(edges), 'complete_task_records_and_edges_equal_pinned_source': tasks == old_tasks and edges == old_edges})
no_qualification = [s['story_id'] for s in refinement['stories'] if not any(t.get('kind') == 'qualification' for t in s['tasks'])]
augments = [m['criterion_id'] for m in criteria if m['original_then'] != m['existing_plan_assertions']]
check('BRIDGE-10', len(missing_given) == 37 and len(augments) == 7 and len(no_qualification) == 13 and
      census['original_gap_preservation']['stories_without_qualification_kind_task'] == no_qualification,
      {'primary_missing_Given': len(missing_given), 'separate_plan_augment_groups': len(augments), 'stories_without_qualification_kind_task': no_qualification})
check('BRIDGE-11', not any('version' in k.lower() for k in rows[0]) and not any('version' in k.lower() for a in aliases for k in a)
      and census['original_source_has_individual_ac_version_field'] is False,
      'Primary CSV/alias map declares no per-scenario AC version; content digest is not owner approval.')

pin_errors = []
for pin in census['source_pins']:
    data = read(pin['path'])
    blob = subprocess.check_output(['git', 'rev-parse', HEAD + ':' + pin['path']], cwd=REPO).decode().strip()
    if not (data == git_raw(pin['path']) and pin['sha256'] == sha(data) and pin['bytes'] == len(data)
            and pin['source_git_commit'] == HEAD and pin['source_git_blob'] == blob):
        pin_errors.append(pin['path'])
tree = subprocess.check_output(['git', 'rev-parse', HEAD + '^{tree}'], cwd=REPO).decode().strip()
check('BRIDGE-12', len(census['source_pins']) == 60 and not pin_errors and census['source_snapshot_git_commit'] == HEAD
      and census['source_snapshot_git_tree'] == tree and census['primary_source'] == census['source_pins'][0],
      {'source_pins': len(census['source_pins']), 'mismatches': pin_errors, 'pinned_tree': tree})
feature_paths = sorted((REPO / 'docs/backlog/features').glob('*.feature'))
feature_count = sum(len(re.findall(rb'(?m)^\s*Scenario(?: Outline)?:', p.read_bytes())) for p in feature_paths)
check('BRIDGE-13', len(feature_paths) == 54 and feature_count == 1335,
      {'feature_files': len(feature_paths), 'specification_scenarios_including_history': feature_count, 'execution_claim': False})
expected_counts = {'all_CSV_story_records': 370, 'active_story_records': 368, 'retained_Split_story_records': 2,
    'active_original_scenarios': 1328, 'retained_Split_original_scenarios': 7,
    'all_CSV_original_scenarios_including_history': 1335, 'feature_files': 54,
    'feature_original_scenarios_including_history': 1335, 'same_scenario_alias_rows': 1328, 'tasks': 1131, 'task_dependency_edges': 779}
check('BRIDGE-14', census['source_counts'] == expected_counts and all(census['source_checks'].values()) and
      all(census[k] is False for k in ['source_modified','native_or_runtime_changes','application_or_package_checks_executed','authority_or_readiness_established']),
      'Census aggregates/limitations agree with independent bounded source observations; author truth flags are not external authority.')

package_paths = ['templates/criteria-source.json', 'templates/case.md', 'standards/register-schema.json',
                 'workflow/CRITERIA-SOURCE-PINNING.md', 'workflow/TRACEABILITY.md',
                 'workflow/CODE-IDS-AND-CONCURRENCY.md', 'checker/criteria_pin.py', 'checker/qa_lint.py']
zip_path = Path('/Users/athena/Downloads/APLYD-Software-Testing-QA-v1.3.zip')
zip_hash = sha(zip_path.read_bytes())
package_pins = []
with zipfile.ZipFile(zip_path) as archive:
    for name in package_paths:
        candidates = [s for s in archive.namelist() if s.endswith('/' + name) or s == name]
        assert len(candidates) == 1, (name, candidates)
        data = (PACKAGE / name).read_bytes()
        package_pins.append({'path': name, 'sha256': sha(data), 'bytes': len(data), 'exact_attached_zip_entry': archive.read(candidates[0]) == data})
check('BRIDGE-15', zip_hash == census['package_contract_reference']['ZIP_sha256'] and
      all(p['exact_attached_zip_entry'] for p in package_pins),
      {'attached_zip_sha256': zip_hash, 'exact_reference_files': len(package_pins)})
template = json.loads((PACKAGE / 'templates/criteria-source.json').read_text())
helper = (PACKAGE / 'checker/criteria_pin.py').read_text()
field_names = ['source_id', 'source_version', 'scope_id', 'review_ref', 'criteria']
check('BRIDGE-16', all(f in template for f in field_names) and
      census['package_contract_reference']['required_source_fields'] == field_names and
      census['package_contract_reference']['required_criterion_fields'] == ['ac_id', 'ac_version', 'applicability'] and
      "r'[A-Za-z][A-Za-z0-9_.-]*'" in helper and "['YES','NO','UNKNOWN']" in helper,
      'Bridge source/criterion fields and valid-encoding/applicability warning match actual attached source/helper contract.')
check('BRIDGE-17', "json.dumps(sorted(pairs),ensure_ascii=False,separators=(',',':')).encode()" in helper and
      "hashlib.sha256(raw).hexdigest()" in helper and 'Candidate values only' in helper,
      'Claimed canonical identity-set/source-byte hashing and candidate-only helper boundary match attachment source; helper not executed.')
links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', bridge)
local_links = [link for link in links if '://' not in link]
check('BRIDGE-18', all((REPO / bridge_path).parent.joinpath(link.split('#')[0]).resolve().is_file() for link in local_links),
      {'local_links_checked': len(local_links), 'external_link_qualification': 'NOT_PERFORMED'})

# Minimal corruption controls for this review oracle; copies in memory only.
corruption_controls = {
    'primary_wrong_active_total_detected': expected_counts != {**expected_counts, 'active_original_scenarios': 1335},
    'original_word_change_detected': sha(next(iter(active.values()))['block'].replace('release', 'RELAXED', 1).encode()) != next(iter(active.values()))['hash'],
    'task_edge_loss_detected': old_edges[:-1] != edges,
    'alias_id_substitution_detected': aliases_by_key[next(iter(active))]['taskMatrixId'] != 'AC-OTHER-001',
}
check('BRIDGE-19', all(corruption_controls.values()), corruption_controls)
OUT.mkdir(parents=True, exist_ok=True)
actual = {'review_type': 'AI_BOUNDED_SOURCE_DOCUMENT_REVIEW', 'product': 'Imprana Commons',
          'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'documentation_baseline': HEAD, 'reviewed_inputs': {
              bridge_path: {'sha256': sha(bridge_raw), 'bytes': len(bridge_raw)},
              str(census_path.relative_to(BASE)): {'sha256': sha(census_raw), 'bytes': len(census_raw)}},
          'checks': checks, 'pass': sum(c['result'] == 'PASS' for c in checks),
          'fail': sum(c['result'] == 'FAIL' for c in checks), 'package_source_pins': package_pins,
          'independent_repository_source_pins': pins,
          'non_claims': ['Source-owner completeness/applicability review', 'Actual AC-version convention or release scope selection',
                         'Human approval', 'Product/test execution or qualification', 'Package checker gate/adoption',
                         'Live Linear/GitHub review enforcement', 'Independent external security or AI assurance']}
(OUT / 'ACTUAL-SOURCE-CHECKS.json').write_text(json.dumps(actual, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'pass': actual['pass'], 'fail': actual['fail'], 'output': str(OUT / 'ACTUAL-SOURCE-CHECKS.json')}, indent=2))
raise SystemExit(bool(actual['fail']))
