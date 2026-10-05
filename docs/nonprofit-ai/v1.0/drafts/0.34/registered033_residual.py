from pathlib import Path
import contextlib,hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
ROOT=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform');HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));import migrate
from provision_logins import LOGINS,grant_database_access,login_dsn,verify_login
DB='impact_test_tola_ai_portability_registered033_residual01';params=dict(host='127.0.0.1',port=55437,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip())
passwords=json.loads(Path('/private/tmp/tola-ai-native-build/login-passwords-033.json').read_text())
with psycopg.connect(dbname='postgres',**params,autocommit=True) as c:
 assert not c.execute('SELECT 1 FROM pg_database WHERE datname=%s',(DB,)).fetchone();c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DB)));grant_database_access(c,DB)
dsn=make_conninfo(dbname=DB,**params);os.environ['IMPACT_ALLOW_FIXTURE_LOAD']='1'
with contextlib.redirect_stdout(open(os.devnull,'w')):migrate.run(dsn,dsn,until=39,fixture=True)
topology={login:verify_login(login_dsn(dsn,login,passwords[login]),role) for login,(role,_) in LOGINS.items()}
raw=HERE/'native-registered033-advice-retention-diagnostic.json';assert not raw.exists()
env=dict(os.environ,PORTABILITY_ADVICE_DIAGNOSTIC_DB=DB,PORTABILITY_ADVICE_DIAGNOSTIC_REPORT=str(raw))
r=subprocess.run([sys.executable,str(HERE/'advice_retention_diagnostic.py')],env=env,capture_output=True,text=True);assert r.returncode==0,('guarded_fixture_or_probe_failed',r.returncode)
private=json.loads(raw.read_text());evidence=ROOT/'docs/evidence/sprint-0.33-human-advice-retention-definer-residual.json';prior=evidence.read_bytes();(HERE/'registered033-residual-prior-sanitized-report.json').write_bytes(prior)
out=json.loads(prior);out['prior_unregistered_scratch_diagnostic_preserved']=True;out['registered_schema39_only_reproduction']={'recorded_at':datetime.now(timezone.utc).isoformat(),'schema_version':39,'unregistered_export_draft_applied':False,'source_qualified_database_untouched':True,'database':'New owned scratch applied fresh frozen1→39 plus approved disposable acceptance fixture','all_six_actual_login_topology':topology,'fixture':'Storage-valid synthetic Open case anchored to a readable plan and two expired create/action pointers, current independent fixture members. Receipt expiry/action pointer is a negative storage fixture, not a supported API retention/transition workflow.','guards_disabled_or_old_immutable_rows_changed':False,'connection_method':'Actual impact_worker_login, SET LOCAL ROLE impact_worker; transaction-local current tenant; no participant context; both probes roll back to savepoint','observations':[{'overload_arguments':x['overload_arguments'],'private_keys_returned':len(x['private_case_operation_keys_returned']),'commands':['create_human_advice_case','human_advice_cancel'],'literal_private_identifiers_omitted':True,'rollback_after_probe':True} for x in private['observations']]}
with psycopg.connect(dsn) as c:
 ledger=c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version').fetchall();assert len(ledger)==39 and ledger[-1][0]==39
 defs=[{'signature':sig,'definition_sha256':hashlib.sha256(definition.encode()).hexdigest()} for sig,definition in c.execute("SELECT p.oid::regprocedure::text,pg_get_functiondef(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='impact' AND p.proname='retention_purge_receipts' ORDER BY p.pronargs").fetchall()]
 out['registered_schema39_only_reproduction']['actual_server_version']=c.execute('SHOW server_version').fetchone()[0]
 assert c.execute("SELECT to_regclass('impact.ai_plan_export_issuance')").fetchone()[0] is None
 out['registered_schema39_only_reproduction']['actual_applied_migrations']=[{'version':v,'sha256':h} for v,h in ledger]
 out['registered_schema39_only_reproduction']['actual_existing_definer_source_hashes']=defs
 out['registered_schema39_only_reproduction']['existing_definer_hashes_equal_prior']=all(x['definition_sha256']==y['definition_sha256'] for x,y in zip(defs,out['actual_existing_definers']))
out['unresolved_registered033_residual_confirmed_without_export_draft']=True;out['report_update_runner_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();evidence.write_text(json.dumps(out,indent=2)+'\n');print('Registered schema39-only actual worker residual reproduced; sanitized report strengthened.')
