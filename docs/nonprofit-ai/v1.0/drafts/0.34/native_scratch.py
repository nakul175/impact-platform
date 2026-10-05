"""Owned scratch SQL experiment; unregistered0040, not API/upgrade qualification."""
import argparse,contextlib,hashlib,json,os,sys,traceback
from datetime import datetime,timedelta,timezone
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.conninfo import make_conninfo
from psycopg.types.json import Jsonb
ROOT=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'apps/api')]
import migrate
from provision_logins import LOGINS,grant_database_access,verify_login,login_dsn
from impact_api.store import write,Context,hash_data,EVENT_VALIDATOR
import native_probe_helpers as probes
p=argparse.ArgumentParser();p.add_argument('--label',required=True);args=p.parse_args()
assert args.label.replace('_','').isalnum() and args.label.islower()
DB='impact_test_tola_ai_portability_'+args.label
REPORT=HERE/('native-'+args.label+'.json')
assert not REPORT.exists()
fixture=json.loads((ROOT/'specification/fixtures/api-fixture.json').read_text())
TENANT=fixture['tenant_a'];ACTOR=fixture['actors']['admin'];OTHER=fixture['actors']['reviewer']
fixture_dsn=make_conninfo(host='127.0.0.1',port=55437,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip(),dbname=DB)
password_path=Path('/private/tmp/tola-ai-native-build/login-passwords-033.json')
assert password_path.stat().st_mode & 0o777 == 0o600
passwords=json.loads(password_path.read_text());assert set(passwords)==set(LOGINS)
report={'recorded_at':datetime.now(timezone.utc).isoformat(),'database':DB,'scope':'Unregistered private0040 native SQL scratch only; synthetic direct grants, no API/profile-upgrade/erasure/deployment acceptance','draft_sha256':hashlib.sha256((HERE/'0040_ai_plan_portability.sql').read_bytes()).hexdigest(),'checks':[],'credentials_rotated':False}

def record(name,fn):
    try:
        value=fn()
    except Exception as e:
        report['checks'].append({'name':name,'result':'FAIL','exception':type(e).__name__,'sqlstate':getattr(e,'sqlstate',None)})
        REPORT.write_text(json.dumps(report,indent=2,default=str)+'\n')
        print(name+': FAIL '+type(e).__name__+' '+str(getattr(e,'sqlstate','')))
        raise
    else:
        report['checks'].append({'name':name,'result':'PASS','observations':value})
        REPORT.write_text(json.dumps(report,indent=2,default=str)+'\n');print(name+': PASS')
        return value

@contextlib.contextmanager
def admin():
    with psycopg.connect(fixture_dsn,autocommit=True,prepare_threshold=None,row_factory=dict_row) as c:
        with c.transaction():
            c.execute("SELECT set_config('impact.tenant_id',%s,true)",(TENANT,));yield c

@contextlib.contextmanager
def app(principal=ACTOR['principal_id'],login='APP',tenant=TENANT):
    with probes.native_connection(login) as c:
        c.row_factory=dict_row
        with probes.runtime_context(c,login,tenant,principal):
            c.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))",(tenant,));yield c


def ctx(actor=ACTOR):
    return Context(TENANT,actor['principal_id'],actor['membership_id'],SimpleNamespace(natural_identity_id=actor['natural_identity_id']),0,0,[])


def setup():
    with psycopg.connect(make_conninfo(host='127.0.0.1',port=55437,user='tola_fixture',password=Path('/private/tmp/tola-ai-native-build/admin-password').read_text().strip(),dbname='postgres'),autocommit=True) as c:
        assert not c.execute('SELECT 1 FROM pg_database WHERE datname=%s',(DB,)).fetchone()
        c.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(DB)))
        grant_database_access(c,DB)
    with contextlib.redirect_stdout(open(os.devnull,'w')):
        os.environ['IMPACT_ALLOW_FIXTURE_LOAD']='1';migrate.run(fixture_dsn,fixture_dsn,until=39,fixture=True)
    with admin() as c:
        migrate.execute_script(c,(HERE/'0040_ai_plan_portability.sql').read_text())
    with admin() as c:
        rows=c.execute('SELECT version,sha256 FROM impact.schema_migration ORDER BY version').fetchall()
        assert len(rows)==39 and rows[-1]['version']==39
        report['applied_migrations']=rows;report['unregistered_draft_not_in_ledger']=True
    os.environ['IMPACT_NATIVE_TEST']='1'
    topology={}
    for login,(role,suffix) in LOGINS.items():
        dsn=login_dsn(fixture_dsn,login,passwords[login]);os.environ['IMPACT_LOGIN_DSN_'+suffix]=dsn
        topology[login]=verify_login(dsn,role)
    return {'schema_ledger':39,'draft_applied_unledgered':True,'actual_topology':topology}


def seed():
    # Synthetic SQL storage authority only; this is not current capability policy or reviewed widening.
    with admin() as c:
        scope=c.execute("SELECT scope_id FROM impact.scope_definition WHERE tenant_id=%s AND scope_type='TENANT' LIMIT 1",(TENANT,)).fetchone()['scope_id']
        for actor in [ACTOR,OTHER]:
            for capability in ['ai.enablement.read','ai.enablement.export']:
                data={'subject_id':actor['principal_id'],'capability':capability,'scope_id':str(scope),'starts_at':'2026-01-01T00:00:00Z','expires_at':'2027-09-01T00:00:00Z','issuer_id':fixture['actors']['owner']['principal_id']}
                write(c,ctx(actor),'Grant',data,'Active')
        global PLAN
        PLAN=write(c,ctx(),'AIAdoptionPlan',{'title':'Synthetic retained export source','profile':{'goal':'Synthetic'}},'Draft',track_author=False)
    return {'authority':'Synthetic direct SQL grants with all existing guards enabled; not reviewed capability upgrade','plan_id':PLAN['object_id'],'plan_revision':PLAN['revision_id']}


def create(c,*,omit=None,change=None,expired=False,operation=None,issuer=ACTOR,plan=None,owner=False):
    change=change or {}; plan=plan or PLAN
    time=c.execute('SELECT statement_timestamp() AS now').fetchone()['now']
    if expired:time-=timedelta(days=8)
    issuance=str(uuid4());operation=operation or str(uuid4());correlation=str(uuid4());eventid=str(uuid4())
    body=b'{"synthetic":"original immutable body"}'
    digest=hashlib.sha256(body).digest();fingerprint=hash_data({'operation_id':operation,'plan':plan['object_id'],'revision':plan['revision_id']})
    adata={'real_actor_id':issuer['principal_id'],'effective_actor_id':issuer['principal_id'],'action_type':'issue_ai_plan_export','object_reference':plan['object_id'],'outcome':'SUCCEEDED','occurred_at':time.isoformat(),'correlation_id':correlation,'specification_ref':'FR-NPA059'}
    adata.update(change.get('audit',{}))
    if change.get('raw_audit'):
        # Deliberate actual APP direct-SQL malformed payload, not a closed API/writer call.
        audit={'revision_id':str(uuid4())}
        c.execute("INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) VALUES(%s,%s,'AuditEvent',%s,'Recorded','INTERNAL',%s,%s,%s,%s)",(TENANT,issuance,audit['revision_id'],issuer['principal_id'],time,issuer['principal_id'],time))
        c.execute("INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,schema_version,payload,payload_sha256,author_id,created_at,revision_number) VALUES(%s,%s,%s,'AuditEvent','1.2',%s,%s,%s,%s,1)",(TENANT,issuance,audit['revision_id'],Jsonb(adata),hash_data(adata),issuer['principal_id'],time))
        projection={'tenant_id':TENANT,'object_id':issuance,'revision_id':audit['revision_id'],**adata}
        c.execute(sql.SQL('INSERT INTO impact.audit_event_current({}) VALUES({})').format(sql.SQL(',').join(map(sql.Identifier,projection)),sql.SQL(',').join(sql.Placeholder() for _ in projection)),list(projection.values()))
    else:
        audit=write(c,ctx(issuer),'AuditEvent',adata,'Recorded',object_id=issuance,track_author=False)
    row={'tenant_id':TENANT,'issuance_id':issuance,'audit_revision_id':audit['revision_id'],'plan_object_id':plan['object_id'],'plan_revision_id':plan['revision_id'],'principal_id':issuer['principal_id'],'membership_id':issuer['membership_id'],'operation_id':operation,'request_sha256':fingerprint,'format':'JSON','restriction':'INTERNAL_SELF','package_schema_version':'nonprofit-ai-plan-export-v1','renderer_version':'nonprofit-ai-plan-json-v1','guidance_status':'UNAVAILABLE','generated_at':time,'replay_until':time+timedelta(hours=168),'content_sha256':digest,'byte_count':len(body),'correlation_id':correlation,'outbox_event_id':eventid}
    row.update(change.get('metadata',{}))
    if omit!='metadata':
        c.execute(sql.SQL('INSERT INTO impact.ai_plan_export_issuance({}) VALUES({})').format(sql.SQL(',').join(map(sql.Identifier,row)),sql.SQL(',').join(sql.Placeholder() for _ in row)),list(row.values()))
    if omit!='bytes' and omit!='metadata':c.execute('INSERT INTO impact.ai_plan_export_bytes VALUES(%s,%s,%s)',(TENANT,issuance,change.get('body',body)))
    event={'event_id':eventid,'tenant_id':TENANT,'event_type':'object.changed','schema_version':'1.1','aggregate_type':'AuditEvent','aggregate_id':issuance,'aggregate_revision':audit['revision_id'],'aggregate_sequence':1,'occurred_at':time.isoformat(),'actor_id':issuer['principal_id'],'correlation_id':correlation,'payload':{'object_id':issuance,'revision_id':audit['revision_id'],'state':'Recorded'}}
    event.update(change.get('event',{}))
    if omit!='event' and omit!='metadata':
        EVENT_VALIDATOR.validate(event)
        c.execute('INSERT INTO impact.outbox_event VALUES(%s,%s,%s,%s,%s)',(TENANT,eventid,'object.changed',time,Jsonb(event)))
        if omit!='delivery':c.execute('INSERT INTO impact.outbox_delivery(tenant_id,event_id) VALUES(%s,%s)',(TENANT,eventid))
    receipt={'object_id':issuance,'revision_id':audit['revision_id'],'business_state':'Issued','operation_id':operation,'correlation_id':correlation,'saved_at':time.isoformat(),'content_sha256':digest.hex(),'byte_count':len(body),'replay_until':row['replay_until'].isoformat()}
    receipt.update(change.get('receipt',{}))
    if omit!='receipt' and omit!='metadata':c.execute('INSERT INTO impact.operation_receipt VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(TENANT,issuer['principal_id'],'issue_ai_plan_export',operation,fingerprint,'SUCCEEDED',Jsonb(receipt),row['replay_until']))
    c.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return {'issuance_id':issuance,'event_id':eventid,'revision_id':audit['revision_id'],'operation_id':operation,'body_hex':body.hex()}


def legitimate():
    global ISSUED
    with app() as c:
        assert c.execute('SELECT impact.ai_plan_export_authority(%s,%s,%s,%s) AS allowed',(ACTOR['principal_id'],ACTOR['membership_id'],PLAN['object_id'],PLAN['revision_id'])).fetchone()['allowed']
        ISSUED=create(c)
        assert c.execute('SELECT body FROM impact.ai_plan_export_bytes WHERE tenant_id=%s AND issuance_id=%s',(TENANT,ISSUED['issuance_id'])).fetchone()['body'].hex()==ISSUED['body_hex']
    return {'creation':'actual impact_app_login + SET LOCAL ROLE impact_app','one_audit_one_event_one_receipt':True}



def expect_failure(fn,sqlstates=None):
    try:fn()
    except psycopg.Error as e:
        assert not sqlstates or e.sqlstate in sqlstates,(type(e).__name__,e.sqlstate)
        return {'exception':type(e).__name__,'sqlstate':e.sqlstate,'message':e.diag.message_primary if e.diag.message_primary in {'AI_PLAN_EXPORT_CHILD_RETAINED','AI_PLAN_EXPORT_STORAGE_LIMIT','AI_PLAN_EXPORT_SLOT_SERVER_ASSIGNED'} else 'redacted_sql_diagnostic'}
    else:raise AssertionError('Expected refusal')


def pointers(c,item= None):
    from psycopg.rows import tuple_row
    item=item or ISSUED;old=c.row_factory;c.row_factory=tuple_row
    try:return probes.pointer_observations(c,TENANT,item['issuance_id'],item['event_id'])
    finally:c.row_factory=old


def seed_pointer_rows():
    with admin() as c:
        c.execute('INSERT INTO impact.object_natural_author VALUES(%s,%s,%s)',(TENANT,ISSUED['issuance_id'],ACTOR['natural_identity_id']))
        c.execute('INSERT INTO impact.consumer_receipt VALUES(%s,%s,%s,now())',(TENANT,'synthetic-pointer-probe',ISSUED['event_id']))
    return {'natural_author_consumer':'trusted synthetic pointer fixture only, not official issuance side effects'}


def rls_structure():
    with admin() as c:
        rows=c.execute("SELECT relname,relrowsecurity,relforcerowsecurity FROM pg_class WHERE oid=ANY(ARRAY['impact.ai_plan_export_issuance'::regclass,'impact.ai_plan_export_bytes'::regclass])").fetchall()
        assert len(rows)==2 and all(x['relrowsecurity'] and x['relforcerowsecurity'] for x in rows)
        roles=['impact_app','impact_worker','impact_identity','impact_platform','impact_privacy','impact_sensitive','impact_observer']
        acl=[]
        for role in roles:
            for table in ['ai_plan_export_issuance','ai_plan_export_bytes']:
                value=c.execute("SELECT has_table_privilege(%s,%s,'SELECT') AS read,has_table_privilege(%s,%s,'INSERT') AS insert,has_table_privilege(%s,%s,'UPDATE') AS update,has_table_privilege(%s,%s,'DELETE') AS delete",(role,'impact.'+table,role,'impact.'+table,role,'impact.'+table,role,'impact.'+table)).fetchone()
                assert not value['update'] and not value['delete'];assert value['read']==value['insert']==(role=='impact_app')
                acl.append({'role':role,'table':table,**value})
        manifest=c.execute('SELECT manifest FROM impact.platform_access_profile WHERE profile_hash=%s',('422b86a900e54a661f6c4a4a35ee8146a504ff7d026478e18e9fafe19e510d3f',)).fetchone()['manifest']
        assert manifest==json.loads((HERE/'proposed-bootstrap-profile.json').read_text())
    return {'forced_rls':rows,'acl':acl,'registered_manifest_exact':True}


def pointer_roles():
    observations=[]
    with app() as c:
        visible=pointers(c);assert all(v=={'access':'ROWS','count':1} for v in visible.values()),visible
        observations.append({'role':'APP current issuer','pointers':visible})
    for label in probes.LOGINS:
        with probes.native_connection(label) as c:
            with probes.runtime_context(c,label,TENANT):
                observed=probes.pointer_observations(c,TENANT,ISSUED['issuance_id'],ISSUED['event_id']);probes.assert_pointers_hidden(observed)
                uniform=c.execute("SELECT impact.ai_plan_export_record_visible('AuditEvent',%s,true),impact.ai_plan_export_record_visible('AuditEvent',%s,true),impact.ai_plan_export_object_visible(%s,true),impact.ai_plan_export_object_visible(%s,true),impact.ai_plan_export_event_visible(%s,true),impact.ai_plan_export_event_visible(%s,true)",(str(uuid4()),ISSUED['issuance_id'],str(uuid4()),ISSUED['issuance_id'],str(uuid4()),ISSUED['event_id'])).fetchone()
                assert uniform==(False,)*6,uniform
                observations.append({'actual_login':probes.LOGINS[label][0],'context':'missing','pointers':observed,'public_helpers_unknown_hidden_uniform_false':True})
            with probes.runtime_context(c,label,TENANT,OTHER['principal_id']):
                observed=probes.pointer_observations(c,TENANT,ISSUED['issuance_id'],ISSUED['event_id']);probes.assert_pointers_hidden(observed)
                observations.append({'actual_login':probes.LOGINS[label][0],'context':'different authorised issuer / forged app context for other roles','pointers':observed})
            probes.assert_context_cleared(c)
    for principal,tenant in [('bad-uuid',TENANT),(ACTOR['principal_id'],fixture['tenant_b'])]:
        with app(principal=principal,tenant=tenant) as c:probes.assert_pointers_hidden(pointers(c))
    return observations


def atomic_failures():
    outcomes=[]
    cases=[({'omit':part},None) for part in ['metadata','bytes','event','delivery','receipt']]
    cases += [({'change':{'audit':{'outcome':'FAILED'}}},None),({'change':{'audit':{'real_actor_id':OTHER['principal_id']}}},None),({'change':{'raw_audit':True,'audit':{'occurred_at':None}}},None),({'change':{'body':b'wrong bytes'}},None),({'change':{'receipt':{'body':'private text'}}},None),({'change':{'metadata':{'membership_id':OTHER['membership_id']}}},None),({'change':{'metadata':{'issuer_slot':42}}},{'42501'})]
    for spec,states in cases:
        with admin() as c:before=c.execute('SELECT (SELECT count(*) FROM impact.ai_plan_export_issuance) AS issuance,(SELECT count(*) FROM impact.object_registry) AS objects,(SELECT count(*) FROM impact.operation_receipt) AS receipts,(SELECT count(*) FROM impact.outbox_event) AS events').fetchone()
        def attempt():
            with app() as c:create(c,**spec)
        failure=expect_failure(attempt,states)
        with admin() as c:after=c.execute('SELECT (SELECT count(*) FROM impact.ai_plan_export_issuance) AS issuance,(SELECT count(*) FROM impact.object_registry) AS objects,(SELECT count(*) FROM impact.operation_receipt) AS receipts,(SELECT count(*) FROM impact.outbox_event) AS events').fetchone()
        assert before==after,(spec,before,after)
        outcomes.append({'case':list(spec.get('change',{})) or spec['omit'],**failure,'rollback_all_counts_unchanged':True})
    return outcomes


def immutable_and_child():
    outcomes=[]
    for table in ['ai_plan_export_issuance','ai_plan_export_bytes']:
        column='byte_count' if table.endswith('issuance') else 'body'
        for owner in [False,True]:
            for statement in [f'DELETE FROM impact.{table} WHERE tenant_id=%s AND issuance_id=%s',f'UPDATE impact.{table} SET {column}={column} WHERE tenant_id=%s AND issuance_id=%s']:
                def attempt():
                    with (admin() if owner else app()) as c:c.execute(statement,(TENANT,ISSUED['issuance_id']))
                outcomes.append({'table':table,'owner':owner,**expect_failure(attempt,{'42501'})})
    for object_id,revision in [(PLAN['object_id'],PLAN['revision_id']),(ISSUED['issuance_id'],ISSUED['revision_id'])]:
        def attempt():
            with admin() as c:c.execute("UPDATE impact.object_revision SET payload=NULL,restriction_state='REMOVED' WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",(TENANT,object_id,revision))
        refusal=expect_failure(attempt,{'42501'});assert refusal['message']=='AI_PLAN_EXPORT_CHILD_RETAINED';outcomes.append({'retained_parent_removal_refused':True,**refusal})
    def header():
        with app() as c:c.execute('UPDATE impact.object_registry SET updated_at=now() WHERE tenant_id=%s AND object_id=%s',(TENANT,ISSUED['issuance_id']))
    outcomes.append({'audit_header':True,**expect_failure(header,{'42501'})})
    def delivery():
        with app() as c:c.execute("UPDATE impact.outbox_delivery SET channel='EMAIL' WHERE tenant_id=%s AND event_id=%s",(TENANT,ISSUED['event_id']))
    outcomes.append({'no_delivery':True,**expect_failure(delivery,{'42501'})})
    return outcomes


def expired_and_uniqueness():
    global EXPIRED
    with admin() as c:EXPIRED=create(c,expired=True,owner=True)
    with app() as c:
        observed=pointers(c,EXPIRED);assert observed['issuance']=={'access':'ROWS','count':1};assert observed['bytes']=={'access':'ROWS','count':0}
    def duplicate():
        with app() as c:create(c,operation=EXPIRED['operation_id'])
    refused=expect_failure(duplicate,{'23505'})
    def expired_parent():
        with admin() as c:c.execute("UPDATE impact.object_revision SET payload=NULL,restriction_state='REMOVED' WHERE tenant_id=%s AND object_id=%s AND revision_id=%s",(TENANT,PLAN['object_id'],PLAN['revision_id']))
    assert expect_failure(expired_parent,{'42501'})['message']=='AI_PLAN_EXPORT_CHILD_RETAINED'
    return {'fixture':'Trusted synthetic immutable expired-at-insertion record','expired_metadata_visible_bytes_hidden':observed,'operation_never_reused':refused,'expiry_does_not_remove_copy':True}


def visibility_revocations():
    outcomes=[]
    # Mutate only ordinary current authority projections, restore exact values afterwards.
    alterations=[("UPDATE impact.grant_current SET purpose='SCRATCH_HIDDEN' WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.export' AND purpose IS NULL",(TENANT,ACTOR['principal_id']),"UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.export' AND purpose='SCRATCH_HIDDEN'"),
      ("UPDATE impact.tenant_principal SET active=false WHERE tenant_id=%s AND principal_id=%s",(TENANT,ACTOR['principal_id']),"UPDATE impact.tenant_principal SET active=true WHERE tenant_id=%s AND principal_id=%s")]
    for query,parameters,undo in alterations:
        with admin() as c:c.execute(query,parameters)
        try:
            with app() as c:observed=pointers(c);probes.assert_pointers_hidden(observed)
            outcomes.append({'authority_gate':query.split(' SET ')[0],'all10_hidden':observed})
        finally:
            with admin() as c:c.execute(undo,parameters)
    return outcomes


def native_cap():
    #100 actual retained records are made storage-valid including expired and then
    # scope-hidden originals; no retention policy, old-row mutation or broad count grant.
    with admin() as c:count=c.execute('SELECT count(*) AS count FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND principal_id=%s',(TENANT,ACTOR['principal_id'])).fetchone()['count']
    for _ in range(100-count):
        with app() as c:create(c)
    with admin() as c:
        c.execute("UPDATE impact.object_registry SET classification='RESTRICTED' WHERE tenant_id=%s AND object_id=%s",(TENANT,PLAN['object_id']))
        second=write(c,ctx(),'AIAdoptionPlan',{'title':'New readable source after storage exhaustion'},'Draft',track_author=False)
        actual=c.execute('SELECT count(*) AS retained,count(DISTINCT issuer_slot) AS slots,min(issuer_slot) AS first,max(issuer_slot) AS last FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND principal_id=%s',(TENANT,ACTOR['principal_id'])).fetchone()
        assert actual=={'retained':100,'slots':100,'first':1,'last':100}
    with app() as c:
        assert c.execute('SELECT count(*) AS count FROM impact.ai_plan_export_issuance WHERE tenant_id=%s AND principal_id=%s',(TENANT,ACTOR['principal_id'])).fetchone()['count']==0
    def attempt():
        with app() as c:create(c,plan=second)
    refusal=expect_failure(attempt,{'54000'});assert refusal['message']=='AI_PLAN_EXPORT_STORAGE_LIMIT'
    with app(principal=OTHER['principal_id']) as c:other=create(c,issuer=OTHER,plan=second)
    return {'actual_retained_storage':actual,'current_visible_before101st':0,'101st_on_readable_new_plan':refusal,'another_tenant_principal_has_independent_slots':True,'no_perhuman_or_tenantquota_claim':True}


def current_receipt_helper():
    with app() as c:
        row=c.execute("SELECT actor_id,operation_id,payload_hash,outcome,expires_at FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='issue_ai_plan_export' AND operation_id=%s",(TENANT,ISSUED['operation_id'])).fetchone()
        values=[row['actor_id'],row['operation_id'],row['payload_hash'],Jsonb(row['outcome']),row['expires_at']]
        assert c.execute('SELECT impact.ai_plan_export_receipt_match(%s,%s,%s,%s,%s) AS matches',values).fetchone()['matches']
    for principal in [None,OTHER['principal_id']]:
        with app(principal=principal) as c:assert not c.execute('SELECT impact.ai_plan_export_receipt_match(%s,%s,%s,%s,%s) AS matches',values).fetchone()['matches']
    def structural():
        with app() as c:c.execute('SELECT impact.ai_plan_export_receipt_structural_match(%s,%s,%s,%s,%s)',values)
    denied=expect_failure(structural,{'42501'})
    with admin() as c:c.execute("UPDATE impact.grant_current SET purpose='SCRATCH_RECEIPT_REVOKED' WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.export' AND purpose IS NULL",(TENANT,ACTOR['principal_id']))
    try:
        with app() as c:assert not c.execute('SELECT impact.ai_plan_export_receipt_match(%s,%s,%s,%s,%s) AS matches',values).fetchone()['matches']
    finally:
        with admin() as c:c.execute("UPDATE impact.grant_current SET purpose=NULL WHERE tenant_id=%s AND subject_id=%s AND capability='ai.enablement.export' AND purpose='SCRATCH_RECEIPT_REVOKED'",(TENANT,ACTOR['principal_id']))
    return {'current_matching_receipt':True,'missing_different_revoked_current_principal':False,'structural_helper_runtime_execute':denied}


def seed_advice():
    sys.path.insert(0,str(ROOT/'qualification'))
    from impact_api.human_advice import initial_payload,brief_digest,STORED_VALIDATOR
    from test_human_advice_unit import creation
    from impact_api.store import audit
    global CASE,CASEEVENT
    with admin() as c:
        body=creation();body['data'].update(context_plan_id=PLAN['object_id'],context_plan_revision=PLAN['revision_id'],adviser_membership_id=OTHER['membership_id'])
        parties={who+'_'+dest:actor[source] for who,actor in [('requester',ACTOR),('adviser',OTHER)] for dest,source in [('principal_id','principal_id'),('membership_id','membership_id'),('natural_id','natural_identity_id')]}
        obj=str(uuid4());nonce=str(uuid4());payload=initial_payload(body['data'],parties,datetime.now(timezone.utc).isoformat(),nonce);STORED_VALIDATOR.validate(payload)
        c.execute("INSERT INTO impact.human_advice_case_current(tenant_id,object_id,revision_id,context_plan_id,context_plan_revision,requester_principal_id,requester_membership_id,requester_natural_id,adviser_principal_id,adviser_membership_id,adviser_natural_id,case_state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Open')",(TENANT,obj,str(uuid4()),PLAN['object_id'],PLAN['revision_id'],*(parties[k] for k in ['requester_principal_id','requester_membership_id','requester_natural_id','adviser_principal_id','adviser_membership_id','adviser_natural_id'])))
        receipt=write(c,ctx(),'HumanAdviceCase',payload,'Open',object_id=obj)
        c.execute('UPDATE impact.human_advice_case_current SET revision_id=%s WHERE tenant_id=%s AND object_id=%s',(receipt['revision_id'],TENANT,obj))
        c.execute('INSERT INTO impact.human_advice_private_brief VALUES(%s,%s,%s,%s,%s)',(TENANT,obj,body['data']['problem'],brief_digest(body['data']['problem'],nonce),nonce))
        receipt.update(operation_id=body['operation_id'],correlation_id=str(uuid4()));CASEEVENT=audit(c,ctx(),'create_human_advice_case',receipt,receipt['correlation_id'])
        c.execute("INSERT INTO impact.operation_receipt VALUES(%s,%s,'create_human_advice_case',%s,%s,'SUCCEEDED',%s,now()-interval '1 day')",(TENANT,ACTOR['principal_id'],body['operation_id'],hash_data(body),Jsonb(receipt)))
        another=str(uuid4());c.execute("INSERT INTO impact.operation_receipt VALUES(%s,%s,'human_advice_cancel',%s,%s,'SUCCEEDED',%s,now()-interval '1 day')",(TENANT,ACTOR['principal_id'],another,hash_data(body),Jsonb({**receipt,'operation_id':another})))
        CASE=receipt
    return {'case_state':'Open','fixture':'Current0038/39 storage-valid independent actual fixture members; expired receipt pointers are synthetic, not an API expiry workflow'}


def human_helper_composition():
    for label in probes.LOGINS:
        with probes.native_connection(label) as c:
            with probes.runtime_context(c,label,TENANT,ACTOR['principal_id']):
                flags=c.execute("SELECT impact.ai_plan_export_record_visible('HumanAdviceCase',%s,true),impact.ai_plan_export_object_visible(%s,true),impact.ai_plan_export_event_visible(%s,true)",(CASE['object_id'],CASE['object_id'],CASEEVENT)).fetchone();assert flags==(False,False,False)
                if label=='APP':
                    c.execute("SELECT set_config('impact.human_advice_principal',%s,true)",(ACTOR['principal_id'],))
                    flags=c.execute("SELECT impact.ai_plan_export_record_visible('HumanAdviceCase',%s,true),impact.ai_plan_export_object_visible(%s,true),impact.ai_plan_export_event_visible(%s,true)",(CASE['object_id'],CASE['object_id'],CASEEVENT)).fetchone();assert flags==(True,True,True)
    return {'new_helpers_preserve_existing_case_privacy':True,'authorised_app_requester_remains_readable':True,'other_actual_runtime_flags_cannot_bypass':True}


def protected_retention():
    ordinary=str(uuid4())
    with admin() as c:
        c.execute("INSERT INTO impact.operation_receipt VALUES(%s,%s,'synthetic_ordinary_operation',%s,%s,'SUCCEEDED',%s,now()-interval '1 day')",(TENANT,ACTOR['principal_id'],ordinary,hash_data(ordinary),Jsonb({'synthetic':True})))
    observations=[]
    for arity in [1,2]:
        with probes.native_connection('WORKER') as c:
            with probes.runtime_context(c,'WORKER',TENANT):
                c.execute('SAVEPOINT retention_proof');items=[r[0] for r in c.execute('SELECT item FROM impact.retention_purge_receipts(5000'+(',7' if arity==2 else '')+')').fetchall()]
                assert items==[ACTOR['principal_id']+':synthetic_ordinary_operation:'+ordinary],items
                c.execute('ROLLBACK TO SAVEPOINT retention_proof');observations.append({'overload_arguments':arity,'ordinary_expired_purged':1,'private_export_advice_keys_or_count_returned':0,'actual_login':'impact_worker_login'})
    with probes.native_connection('WORKER') as c:
        with probes.runtime_context(c,'WORKER',TENANT):assert len(c.execute('SELECT item FROM impact.retention_purge_receipts(5000,7)').fetchall())==1
    with admin() as c:
        assert c.execute("SELECT count(*) AS count FROM impact.operation_receipt WHERE tenant_id=%s AND operation_id=%s",(TENANT,ordinary)).fetchone()['count']==0
        assert c.execute("SELECT count(*) AS count FROM impact.operation_receipt WHERE tenant_id=%s AND (command_type='issue_ai_plan_export' OR command_type~'^(human_advice_|create_human_advice_case$)') AND expires_at<now()",(TENANT,)).fetchone()['count']==3
        #Trusted negative operation-receipt purge fixture, not a new operated privacy path.
        c.execute("DELETE FROM impact.operation_receipt WHERE tenant_id=%s AND command_type='issue_ai_plan_export' AND operation_id=%s",(TENANT,EXPIRED['operation_id']))
    def replay_after_trusted_purge():
        with app() as c:create(c,operation=EXPIRED['operation_id'])
    duplicate=expect_failure(replay_after_trusted_purge,{'23505'})
    return {'overloads':observations,'expired_private_pointers_retained':3,'owner_only_receipt_deletion_fixture_permanent_dedup':duplicate,'no_retention_acceptance_or_duration_claim':True}


def unavailable_exact_pins():
    observations=[]
    for restriction in ['RESTRICTED','REMOVED']:
        with admin() as c:
            obj,old,new=(str(uuid4()) for _ in range(3));data={'title':'Synthetic negative unavailable old pin'};stamp=datetime.now(timezone.utc)
            c.execute("INSERT INTO impact.object_registry(tenant_id,object_id,object_type,head_revision,lifecycle_state,classification,owner_id,created_at,created_by,updated_at) VALUES(%s,%s,'AIAdoptionPlan',%s,'Draft','INTERNAL',%s,%s,%s,%s)",(TENANT,obj,new,ACTOR['principal_id'],stamp,ACTOR['principal_id'],stamp))
            for revision,prev,num,state in [(old,None,1,restriction),(new,old,2,'AVAILABLE')]:
                c.execute("INSERT INTO impact.object_revision(tenant_id,object_id,revision_id,object_type,predecessor_revision,schema_version,payload,payload_sha256,author_id,created_at,restriction_state,revision_number) VALUES(%s,%s,%s,'AIAdoptionPlan',%s,'1.2',%s,%s,%s,%s,%s,%s)",(TENANT,obj,revision,prev,Jsonb(data) if state!='REMOVED' else None,hash_data(data),ACTOR['principal_id'],stamp,state,num))
            pinned={'object_id':obj,'revision_id':old};item=create(c,plan=pinned,owner=True)
        with app() as c:
            observed=pointers(c,item);probes.assert_pointers_hidden(observed)
            assert not c.execute('SELECT impact.ai_plan_export_authority(%s,%s,%s,%s) AS allowed',(ACTOR['principal_id'],ACTOR['membership_id'],obj,old)).fetchone()['allowed']
            assert c.execute('SELECT impact.ai_plan_export_authority(%s,%s,%s,%s) AS allowed',(ACTOR['principal_id'],ACTOR['membership_id'],obj,new)).fetchone()['allowed']
        def attack():
            with app() as c:create(c,plan=pinned)
        refused=expect_failure(attack,{'42501'})
        observations.append({'old_pin':restriction,'readable_current_head':True,'all10_old_pin_pointers_hidden':observed,'actual_app_create_refused':refused,'fixture':'Storage-valid unavailable-at-insertion old revision and readable successor; no old-row edit or supported API creation claim'})
    #Historical AVAILABLE, unchanged source content, readable successor is valid.
    with admin() as c:
        newer=write(c,ctx(),'AIAdoptionPlan',{'title':'Readable successor'},'Draft',previous={'object_id':PLAN['object_id'],'head_revision':PLAN['revision_id'],'revision_number':1},track_author=False)
    with app() as c:historical=create(c,plan=PLAN)
    observations.append({'historical_AVAILABLE_noncurrent_pin_exportable':True})
    return observations

def main():
    record('apply039_plus_unregistered0040_and_actual_login_topology',setup)
    record('labelled_synthetic_authority_fixture',seed)
    record('actual_app_creation_order_and_original_bytes',legitimate)
    record('forced_rls_privileges_exact_profile',rls_structure)
    record('labelled_optional_pointer_fixtures',seed_pointer_rows)
    record('actual_five_login_all10_pointer_and_helper_privacy',pointer_roles)
    record('public_current_receipt_match_private_structural_execute_denied',current_receipt_helper)
    record('labelled_current_private_advice_storage_fixture',seed_advice)
    record('new_helpers_compose_existing_human_advice_privacy',human_helper_composition)
    record('atomic_null_mismatch_and_missing_parts_rollback',atomic_failures)
    record('insert_only_audit_nondelivery_and_retained_parent_refusal',immutable_and_child)
    record('expired_original_bytes_and_permanent_operation_identity',expired_and_uniqueness)
    record('private_retention_exclusions_ordinary_positive_purge_and_permanent_dedup',protected_retention)
    record('current_authority_loss_all10_pointers_hidden',visibility_revocations)
    record('exact_old_pin_RESTRICTED_REMOVED_and_AVAILABLE_historical_boundary',unavailable_exact_pins)
    record('actual100_hidden_expired_retained_storage_101st_refusal',native_cap)

try:
    main()
except Exception as e:
    # Never print driver errors/DSNs/parameter values. Source line number only for debugging.
    report['terminated']={'exception':type(e).__name__,'sqlstate':getattr(e,'sqlstate',None),'trace_lines':[{'function':f.name,'line':f.lineno,'file':Path(f.filename).name} for f in traceback.extract_tb(e.__traceback__)]}
    REPORT.write_text(json.dumps(report,indent=2,default=str)+'\n');raise SystemExit(1)
else:
    report['completed']=True;report['draft_sha256_end']=hashlib.sha256((HERE/'0040_ai_plan_portability.sql').read_bytes()).hexdigest();assert report['draft_sha256_end']==report['draft_sha256'];report['runner_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();REPORT.write_text(json.dumps(report,indent=2,default=str)+'\n')
