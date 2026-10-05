"""Storage-valid synthetic case + expired receipts; current0038/39 definer proof."""
from pathlib import Path
import json,os,sys
from datetime import datetime,timezone
from types import SimpleNamespace
from uuid import uuid4
import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
ROOT=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform');HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'apps/api'),str(ROOT/'qualification'),str(HERE)]
from impact_api.store import Context,write,audit,hash_data
from impact_api.human_advice import initial_payload,brief_digest,STORED_VALIDATOR
from test_human_advice_unit import creation
import native_probe_helpers as probes
fixture=json.loads((ROOT/'specification/fixtures/api-fixture.json').read_text());tenant=fixture['tenant_a'];requester=fixture['actors']['admin'];adviser=fixture['actors']['reviewer']
DB=os.environ.get('PORTABILITY_ADVICE_DIAGNOSTIC_DB','impact_test_tola_ai_portability_corrected02');passwords=json.loads(Path('/private/tmp/tola-ai-native-build/login-passwords-033.json').read_text());params=dict(host='127.0.0.1',port=55437,dbname=DB)
ctx=Context(tenant,requester['principal_id'],requester['membership_id'],SimpleNamespace(natural_identity_id=requester['natural_identity_id']),0,0,[])
with psycopg.connect(**params,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip(),row_factory=dict_row) as c:
 c.execute("SELECT set_config('impact.tenant_id',%s,true)",(tenant,))
 plan=write(c,ctx,'AIAdoptionPlan',{'title':'Synthetic readable anchor for private retention diagnostic'},track_author=False)
 body=creation();body['data'].update(context_plan_id=plan['object_id'],context_plan_revision=plan['revision_id'],adviser_membership_id=adviser['membership_id'])
 parties={who+'_'+dest:actor[source] for who,actor in [('requester',requester),('adviser',adviser)] for dest,source in [('principal_id','principal_id'),('membership_id','membership_id'),('natural_id','natural_identity_id')]}
 obj=str(uuid4());nonce=str(uuid4());payload=initial_payload(body['data'],parties,datetime.now(timezone.utc).isoformat(),nonce);STORED_VALIDATOR.validate(payload)
 c.execute("INSERT INTO impact.human_advice_case_current(tenant_id,object_id,revision_id,context_plan_id,context_plan_revision,requester_principal_id,requester_membership_id,requester_natural_id,adviser_principal_id,adviser_membership_id,adviser_natural_id,case_state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Open')",(tenant,obj,str(uuid4()),plan['object_id'],plan['revision_id'],*(parties[k] for k in ['requester_principal_id','requester_membership_id','requester_natural_id','adviser_principal_id','adviser_membership_id','adviser_natural_id'])))
 receipt=write(c,ctx,'HumanAdviceCase',payload,'Open',object_id=obj)
 c.execute('UPDATE impact.human_advice_case_current SET revision_id=%s WHERE tenant_id=%s AND object_id=%s',(receipt['revision_id'],tenant,obj))
 c.execute('INSERT INTO impact.human_advice_private_brief VALUES(%s,%s,%s,%s,%s)',(tenant,obj,body['data']['problem'],brief_digest(body['data']['problem'],nonce),nonce))
 receipt.update(operation_id=body['operation_id'],correlation_id=str(uuid4()));audit(c,ctx,'create_human_advice_case',receipt,receipt['correlation_id'])
 c.execute("INSERT INTO impact.operation_receipt VALUES(%s,%s,'create_human_advice_case',%s,%s,'SUCCEEDED',%s,now()-interval '1 day')",(tenant,requester['principal_id'],body['operation_id'],hash_data(body),Jsonb(receipt)))
 #Second matching-prefix expired pointer is a labelled storage fixture, not a case transition.
 another=str(uuid4());c.execute("INSERT INTO impact.operation_receipt VALUES(%s,%s,'human_advice_cancel',%s,%s,'SUCCEEDED',%s,now()-interval '1 day')",(tenant,requester['principal_id'],another,hash_data(body),Jsonb({**receipt,'operation_id':another})))
os.environ['IMPACT_NATIVE_TEST']='1';os.environ['IMPACT_LOGIN_DSN_WORKER']=make_conninfo(**params,user='impact_worker_login',password=passwords['impact_worker_login'])
results=[]
for arity in [1,2]:
 #One native call per overload; savepoint rollback preserves same negative rows for both.
 with probes.native_connection('WORKER') as c:
  with probes.runtime_context(c,'WORKER',tenant):
   c.execute('SAVEPOINT diagnostic')
   rows=c.execute('SELECT item FROM impact.retention_purge_receipts(5000'+(',7' if arity==2 else '')+')').fetchall()
   keys=[x[0] for x in rows if 'human_advice' in x[0]];assert len(keys)==2
   c.execute('ROLLBACK TO SAVEPOINT diagnostic')
   results.append({'overload_arguments':arity,'private_case_operation_keys_returned':keys,'direct_role_method':'actual impact_worker_login SET LOCAL ROLE impact_worker'})
Path(os.environ.get('PORTABILITY_ADVICE_DIAGNOSTIC_REPORT',str(HERE/'native-current033-advice-retention-diagnostic.json'))).write_text(json.dumps({'scope':'Current0038/39 private case policies and unchanged0027/0030 purge functions, within unregistered export scratch. Storage-valid synthetic Open case and expired receipt fixture; not API creation/expiry workflow','current_private_advice_definer_leak_confirmed':True,'observations':results},indent=2)+'\n');print('Recorded both current private-advice retention definer leaks under actual WORKER login.')
