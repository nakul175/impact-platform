from pathlib import Path
import json,os,sys
from uuid import uuid4
import psycopg
from psycopg.conninfo import make_conninfo
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import native_probe_helpers as p
DB='impact_test_tola_ai_portability_base03';passwords=json.loads(Path('/private/tmp/tola-ai-native-build/login-passwords-033.json').read_text())
params=dict(host='127.0.0.1',port=55437,dbname=DB)
fixture=json.loads(Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/specification/fixtures/api-fixture.json').read_text());tenant=fixture['tenant_a']
with psycopg.connect(**params,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip()) as c:
 issuance,event=c.execute('SELECT issuance_id,outbox_event_id FROM impact.ai_plan_export_issuance LIMIT 1').fetchone()
os.environ['IMPACT_NATIVE_TEST']='1';out=[]
for label,(login,role) in p.LOGINS.items():
 os.environ['IMPACT_LOGIN_DSN_'+label]=make_conninfo(**params,user=login,password=passwords[login])
 with p.native_connection(label) as c:
  with p.runtime_context(c,label,tenant):
   value=c.execute("SELECT impact.ai_plan_export_record_visible('AuditEvent',%s,true),impact.ai_plan_export_record_visible('AuditEvent',%s,true)",(str(uuid4()),str(issuance))).fetchone()
   pointers=p.pointer_observations(c,tenant,issuance,event);p.assert_pointers_hidden(pointers)
   out.append(dict(login=login,role=role,unknown_record=value[0],private_record=value[1],oracle_residual=value[0]!=value[1],pointers=pointers))
Path(HERE/'native-base03-oracle-diagnostic.json').write_text(json.dumps({'scope':'Actual no-context runtime logins; before correction current draft693bac; pointer reads hidden but public record helper unknown/private responses differ','observations':out},indent=2)+'\n');print('Recorded actual five-login oracle diagnostic; private pointer queries hidden.')
