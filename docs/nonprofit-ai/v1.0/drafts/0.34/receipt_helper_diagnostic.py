from pathlib import Path
import json,os,sys
import psycopg
from psycopg.conninfo import make_conninfo
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import native_probe_helpers as p
DB='impact_test_tola_ai_portability_corrected02';passwords=json.loads(Path('/private/tmp/tola-ai-native-build/login-passwords-033.json').read_text());params=dict(host='127.0.0.1',port=55437,dbname=DB)
fixture=json.loads(Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/specification/fixtures/api-fixture.json').read_text());tenant=fixture['tenant_a']
with psycopg.connect(**params,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip()) as c:
 row=c.execute("SELECT actor_id,operation_id,payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE command_type='issue_ai_plan_export' LIMIT 1").fetchone()
os.environ['IMPACT_NATIVE_TEST']='1';os.environ['IMPACT_LOGIN_DSN_APP']=make_conninfo(**params,user='impact_app_login',password=passwords['impact_app_login'])
from psycopg.types.json import Jsonb
with p.native_connection('APP') as c:
 with p.runtime_context(c,'APP',tenant):
  value=c.execute('SELECT impact.ai_plan_export_receipt_match(%s,%s,%s,%s,%s)',(*row[:3],Jsonb(row[3]),row[4])).fetchone()[0]
  assert value is True
Path(HERE/'native-corrected02-receipt-helper-diagnostic.json').write_text(json.dumps({'scope':'Actual impact_app_login SET LOCAL ROLE impact_app missing current principal; structural receipt helper accepts exact prior receipt independently of authority','unauthorized_structural_receipt_match':value,'privacy_residual_confirmed':True},indent=2)+'\n');print('Recorded actual APP structural-receipt helper diagnostic.')
