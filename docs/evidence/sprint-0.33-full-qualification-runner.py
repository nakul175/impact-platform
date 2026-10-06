"""Coordinated local checkpoint qualification; own disposable databases only."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'apps/api')]
import run as runner

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['native', 'local'])
parser.add_argument('--database', default='impact_test_tola_ai_checkpoint033_native')
args = parser.parse_args()
if Path.cwd().resolve() != ROOT:
    raise RuntimeError('Run in the explicitly owned repository')
lock = open('/private/tmp/tola-ai-shared-qualification.lock', 'a+')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
started = datetime.now(timezone.utc).isoformat()
tick = time.monotonic()
node = '/Users/athena/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin'
native_bin = '/private/tmp/tola-ai-native-build/runtime/bin'
os.environ.update(PATH=node + os.pathsep + native_bin + os.pathsep + os.environ['PATH'], IMPACT_PORT='8184')

def sources():
    roots = ['apps/api/impact_api', 'apps/web/src', 'qualification', 'scripts', 'deploy',
             'infrastructure', 'packages/contracts', 'specification/reference-v1']
    paths = [p for name in roots for p in (ROOT / name).rglob('*')
             if p.is_file() and '__pycache__' not in p.parts
             and p.suffix in {'.py', '.json', '.sql', '.sh', '.ts', '.tsx', '.css', '.yaml', '.yml'}]
    paths += [ROOT / 'VERSION.json', ROOT / 'Makefile', ROOT / 'docs/current/CURRENT-DATA-DICTIONARY.md']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

source_start = sources()
evidence = ROOT / 'docs/evidence'
generic = ['application-tests.xml', 'native-application-tests.xml', 'native-qualification.json',
           'native-restore-drill.json', 'golden-reconciliation.json']
old = {name: (evidence / name).read_bytes() if (evidence / name).is_file() else None for name in generic}
prefix = 'sprint-0.33-full-' + args.mode
fixture_dsn = None
if args.mode == 'native':
    import psycopg
    from psycopg import sql
    from psycopg.conninfo import make_conninfo
    from provision_logins import LOGINS, grant_database_access, login_dsn, verify_login
    if not args.database.startswith('impact_test_tola_ai_checkpoint033_') or not all(c.islower() or c.isdigit() or c == '_' for c in args.database):
        raise RuntimeError('Refuse a non-owned disposable database')
    password_file = Path('/private/tmp/tola-ai-native-build/login-passwords-033.json')
    if password_file.stat().st_mode & 0o077:
        raise RuntimeError('Private runtime password map permissions required')
    passwords = json.loads(password_file.read_text())
    if set(passwords) != set(LOGINS) or not all(isinstance(v, str) and v for v in passwords.values()):
        raise RuntimeError('Complete persisted map required; no random or reset fallback')
    params = dict(host='127.0.0.1', port=55437, user='tola_fixture',
                  password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip())
    with psycopg.connect(dbname='postgres', **params, autocommit=True) as c:
        if c.execute('SELECT 1 FROM pg_database WHERE datname=%s', (args.database,)).fetchone():
            raise RuntimeError('Refuse modifying an existing qualified database')
        c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(args.database)))
    fixture_dsn = make_conninfo(dbname=args.database, **params)
    def reuse_existing(admin_dsn, supplied, database):
        if supplied != passwords or database != args.database:
            raise RuntimeError('Native credential/database boundary changed')
        with psycopg.connect(admin_dsn, autocommit=True, prepare_threshold=None) as c:
            grant_database_access(c, database)
            rows = c.execute("SELECT l.rolname,l.rolcanlogin,l.rolsuper,l.rolbypassrls,l.rolinherit,COALESCE((SELECT array_agg(r.rolname ORDER BY r.rolname) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.roleid WHERE m.member=l.oid),'{}') FROM pg_roles l WHERE l.rolname=ANY(%s)", (list(LOGINS),)).fetchall()
            topology = {r[0]:dict(login=r[1],superuser=r[2],bypass_rls=r[3],inherit=r[4],memberships=r[5]) for r in rows}
            for login, (group, _) in LOGINS.items():
                r = topology.get(login)
                if not r or not r['login'] or r['superuser'] or r['bypass_rls'] or r['inherit'] or r['memberships'] != [group]:
                    raise RuntimeError('Actual existing login topology refused')
            public = c.execute("SELECT CASE WHEN datacl IS NULL THEN true ELSE EXISTS(SELECT 1 FROM aclexplode(datacl) a WHERE a.grantee=0 AND a.privilege_type='CONNECT') END FROM pg_database WHERE datname=%s", (database,)).fetchone()[0]
        verified = {login: verify_login(login_dsn(admin_dsn,login,passwords[login]),group) for login,(group,_) in LOGINS.items()}
        return dict(database=database,privilege_roles_created=[],public_connect=public,logins=topology,verified=verified)
    runner.provision = reuse_existing
    os.environ.update(IMPACT_FIXTURE_DSN=fixture_dsn, IMPACT_ADMIN_DSN=fixture_dsn, IMPACT_UPGRADE_BASELINE='33')
    for login, (_, suffix) in LOGINS.items():
        os.environ['IMPACT_LOGIN_PASSWORD_' + suffix] = passwords[login]
else:
    for key in list(os.environ):
        if key.startswith('IMPACT_LOGIN_') or key in {'IMPACT_FIXTURE_DSN','IMPACT_ADMIN_DSN','IMPACT_NATIVE_TEST'}:
            os.environ.pop(key)

sys.argv = ['run.py', 'test'] + (['--native'] if args.mode == 'native' else [])
result = 1
written = []
try:
    try:
        result = runner.main() or 0
    except SystemExit as error:
        result = error.code or 0
    mapping = {'application-tests.xml':'tests.xml', 'native-application-tests.xml':'tests.xml',
               'native-qualification.json':'qualification.json','native-restore-drill.json':'restore-drill.json',
               'golden-reconciliation.json':'golden.json'}
    for name, suffix in mapping.items():
        path = evidence / name
        if path.is_file() and path.read_bytes() != old[name]:
            target = evidence / (prefix + '-' + suffix)
            target.write_bytes(path.read_bytes())
            written.append(target.name)
    if args.mode == 'native':
        qualification = json.loads((evidence / 'native-qualification.json').read_text())
        for phase in ('phase_1', 'phase_2'):
            path = qualification.get('restart_check', {}).get(phase, {}).get('junit')
            if path:
                source = ROOT / path
                if not source.resolve().is_relative_to((ROOT / '.local').resolve()):
                    raise RuntimeError('Restart report escaped its owned fixture')
                target = evidence / (prefix + '-restart-' + phase + '-tests.xml')
                target.write_bytes(source.read_bytes())
                written.append(target.name)
    applied = None
    if fixture_dsn:
        with psycopg.connect(fixture_dsn, autocommit=True, prepare_threshold=None) as c:
            applied = [dict(version=v,sha256=h,applied_at=t.isoformat()) for v,h,t in c.execute('SELECT version,sha256,applied_at FROM impact.schema_migration ORDER BY version').fetchall()]
        path=evidence / (prefix + '-applied-migrations.json')
        path.write_text(json.dumps(dict(recorded_at=datetime.now(timezone.utc).isoformat(),database=args.database,applied_migrations=applied),indent=2)+'\n')
        written.append(path.name)
    else:
        ledger_path = evidence / 'sprint-0.33-retained-visibility-pglite-applied-migrations.json'
        ledger = json.loads(ledger_path.read_text())
        if ledger.get('environment') != 'PGLITE' or datetime.fromisoformat(ledger['recorded_at']) < datetime.fromisoformat(started):
            raise RuntimeError('Refuse a stale or differently qualified local ledger')
        migrations = sorted((ROOT / 'infrastructure/migrations').glob('*.sql'))
        if len(ledger['migrations']) != len(migrations):
            raise RuntimeError('Actual local migration ledger incomplete')
        for row, source in zip(ledger['migrations'], migrations, strict=True):
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if row['file'] != source.name or row['applied_sha256'] != digest or row['current_source_sha256'] != digest:
                raise RuntimeError('Actual local ledger checksum mismatch')
        path = evidence / (prefix + '-applied-migrations.json')
        path.write_bytes(ledger_path.read_bytes())
        written.append(path.name)
    source_end = sources()
    changes = [p for p in sorted(set(source_start)|set(source_end)) if source_start.get(p)!=source_end.get(p)]
    proof = dict(started_at=started,recorded_at=datetime.now(timezone.utc).isoformat(),duration_seconds=round(time.monotonic()-tick,3),exit_code=result,
                 scope='Full local checkpoint qualification. Actual native restart/restore/populated33 upgrade are included only in native mode. No live IdP/container/hosted/UAT/provider acceptance.',
                 source_sha256_start=source_start,source_sha256_end=source_end,source_changed_during_run=changes,
                 reports_written_this_run=written,helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (evidence / (prefix + '-source-proof.json')).write_text(json.dumps(proof,indent=2)+'\n')
    if changes:
        result = result or 1
finally:
    if result:
        for name, data in old.items():
            path=evidence/name
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
    fcntl.flock(lock, fcntl.LOCK_UN)
print(json.dumps(dict(mode=args.mode,exit_code=result,reports_written_this_run=written)))
raise SystemExit(result)
