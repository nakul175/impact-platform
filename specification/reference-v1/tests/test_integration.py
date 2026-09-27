import concurrent.futures, uuid
from api_support import ApiCase

class Integration(ApiCase):
    def test_IT_001(self):self.expect_error(self.request(self.path('programmes'),actor=None),401,'AUTH_REQUIRED')
    def test_IT_002(self):
        status,obj=self.request(self.path('programmes',object_key='programme_a'));self.assertEqual(status,200);self.assertEqual(obj['tenant_id'],self.fixture['tenant_a'])
    def test_IT_003(self):self.expect_error(self.request(self.path('programmes',tenant='tenant_b',object_key='programme_b')),404,'RESOURCE_UNAVAILABLE')
    def test_IT_004(self):self.expect_error(self.request(self.path('programmes',object_key='programme_b')),404,'RESOURCE_UNAVAILABLE')
    def test_IT_005(self):
        status,body=self.request(self.path('reports',object_key='report_a'),actor='revoked');self.assertIn(status,[401,404]);self.assertNotIn('data',body)
    def test_IT_006(self):
        status,body=self.request(self.path('me/access'));self.assertEqual(status,200);self.assertEqual(body['tenant_id'],self.fixture['tenant_a']);self.assertIsInstance(body['capabilities'],list)
    def test_IT_007(self):self.expect_error(self.request(self.path('programmes')+'?limit=101'),422,'VALIDATION_FAILED')
    def test_IT_008(self):
        status,body=self.request(self.path('programmes')+'?limit=1');self.assertEqual(status,200);self.assertLessEqual(len(body['items']),1);self.assertIn('scope_label',body);self.assertIn('next_cursor',body)
    def test_IT_009(self):
        status,body=self.request(self.path('calculated-results',object_key='pooled_result'));self.assertEqual(status,200)
        d=body['data'];self.assertEqual(d['mode'],'OFFICIAL');self.assertEqual(d['value_state'],'PRESENT');self.assertEqual(d['value'],'46.363636363636');self.assertEqual(d['displayed_value'],'46.36');self.assertTrue(d['lineage_manifest_id'])
    def test_IT_010(self):
        status,body=self.request(self.path('memberships'),actor='partner');self.assertIn(status,[403,404]);self.assertNotIn('items',body)
    def test_IT_011(self):
        missing=self.path('programmes')+'/'+str(uuid.uuid4());hidden=self.path('programmes',object_key='programme_b')
        a=self.expect_error(self.request(missing),404,'RESOURCE_UNAVAILABLE');b=self.expect_error(self.request(hidden),404,'RESOURCE_UNAVAILABLE');self.assertEqual(set(a),set(b));self.assertEqual(a['message'],b['message'])
    def test_IT_012(self):
        status,body=self.request(self.path('connections',object_key='connection_a'),actor='admin');self.assertEqual(status,200)
        def walk(obj):
            if isinstance(obj,dict):
                for key,value in obj.items():self.assertNotIn(key.lower(),['secret','password','access_token','refresh_token','client_secret']);walk(value)
            elif isinstance(obj,list):
                for value in obj:walk(value)
        walk(body)
    def test_IT_013(self):
        self.require_mutations();f=self.fixture
        body=self.expect_error(self.request(self.path('workflows',object_key='own_workflow')+'/actions/approve',method='POST',payload=self.command(f['workflow_revision'],{'candidate_revision':f['candidate_revision'],'reason':'Qualification attempt'})),403,'POLICY_DENIED');self.assertEqual(body['reason_code'],'INDEPENDENCE_REQUIRED')
    def test_IT_014(self):
        self.require_mutations();self.expect_error(self.request(self.path('programmes',object_key='mutable_programme'),method='PATCH',payload=self.command('00000000-0000-4000-8000-000000000000',{'title':'stale attempt'})),409,'CONFLICT_VERSION')
    def test_IT_015(self):
        self.require_mutations();path=self.path('programmes',object_key='mutable_programme');status,obj=self.request(path);self.assertEqual(status,200)
        self.expect_error(self.request(path,method='PATCH',payload=self.command(obj['revision_id'],{'lifecycle_state':'Approved'})),422,'VALIDATION_FAILED')
    def test_IT_016(self):
        self.require_mutations();path=self.path('programmes',object_key='mutable_programme');status,obj=self.request(path);self.assertEqual(status,200);old=obj['data']['title'];title='Replay '+str(uuid.uuid4());cmd=self.command(obj['revision_id'],{'title':title})
        try:
            first=self.request(path,method='PATCH',payload=cmd);self.assertEqual(first[0],200)
            second=self.request(path,method='PATCH',payload=cmd);self.assertEqual(first,second)
            changed={**cmd,'data':{'title':title+' changed'}};self.expect_error(self.request(path,method='PATCH',payload=changed),409,'CONFLICT_OPERATION')
            status,head=self.request(path);self.assertEqual(status,200);self.assertEqual(head['data']['title'],title);self.assertEqual(head['revision_id'],first[1]['revision_id'])
        finally:self.restore_title(old)
    def test_IT_017(self):
        self.require_mutations();path=self.path('programmes',object_key='mutable_programme');status,obj=self.request(path);self.assertEqual(status,200);old=obj['data']['title'];titles=['Race A '+str(uuid.uuid4()),'Race B '+str(uuid.uuid4())]
        try:
            cmds=[self.command(obj['revision_id'],{'title':t}) for t in titles]
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda cmd:self.request(path,method='PATCH',payload=cmd),cmds))
            self.assertEqual(sorted(x[0] for x in results),[200,409]);loser=next(x for x in results if x[0]==409);self.assertEqual(loser[1]['code'],'CONFLICT_VERSION')
            winner=next(x for x in results if x[0]==200);status,head=self.request(path);self.assertEqual(status,200);self.assertEqual(head['revision_id'],winner[1]['revision_id']);self.assertIn(head['data']['title'],titles)
        finally:self.restore_title(old)
    def test_IT_018(self):
        self.require_mutations();self.expect_error(self.request(self.path('offline-sync'),actor='enumerator',method='POST',payload={'operation_id':str(uuid.uuid4()),'data':self.fixture['expired_sync_payload']}),410,'EXPIRED_GRANT')
