from pathlib import Path
import json,os,sys
import psycopg
from psycopg.conninfo import make_conninfo
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import native_probe_helpers as p
DB='impact_test_tola_ai_portability_corrected02';passwords=json.loads(Path('/private/tmp/tola-ai-native-build/login-passwords-033.json').read_text());params=dict(host='127.0.0.1',port=55437,dbname=DB)
fixture=json.loads(Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/specification/fixtures/api-fixture.json').read_text());tenant=fixture['tenant_a']
os.environ['IMPACT_NATIVE_TEST']='1';os.environ['IMPACT_LOGIN_DSN_WORKER']=make_conninfo(**params,user='impact_worker_login',password=passwords['impact_worker_login'])
with p.native_connection('WORKER') as c:
 with p.runtime_context(c,'WORKER',tenant):
  returned=c.execute('SELECT item FROM impact.retention_purge_receipts(5000,7)').fetchall()
  export=[x[0] for x in returned if ':issue_ai_plan_export:' in x[0]]
  assert export
Path(HERE/'native-corrected02-retention-diagnostic.json').write_text(json.dumps({'scope':'Actual impact_worker_login SET LOCAL ROLE impact_worker; unregistered corrected draft661a0a18; existing owner-definer returns private export operation keys despite worker pointer RLS','private_export_keys_returned':export,'returned_count':len(returned),'privacy_residual_confirmed':True},indent=2)+'\n');print('Recorded actual worker private-operation retention diagnostic.')
