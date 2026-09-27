from api_support import ApiCase

class Smoke(ApiCase):
    def test_SM_001(self):
        status,b=self.request('/health/ready',actor=None);self.assertEqual(status,200);self.assertEqual(b['status'],'ready')
    def test_SM_002(self):
        status,b=self.request('/v1/runtime-manifest');self.assertEqual(status,200);self.assertTrue(b['build_id']);self.assertTrue(b['schema_version'])
    def test_SM_003(self):
        status,b=self.request(self.path('me/access'));self.assertEqual(status,200);self.assertEqual(b['tenant_id'],self.fixture['tenant_a'])
    def test_SM_004(self):self.assertEqual(self.request(self.path('programmes',object_key='programme_a'))[0],200)
    def test_SM_005(self):
        status,b=self.request(self.path('calculated-results',object_key='pooled_result'));self.assertEqual(status,200);self.assertEqual(b['data']['value_state'],'PRESENT');self.assertEqual(b['data']['displayed_value'],'46.36')
    def test_SM_006(self):self.assertEqual(self.request(self.path('evidence',object_key='evidence_a'))[0],200)
    def test_SM_007(self):self.assertEqual(self.request(self.path('reports',object_key='report_a'))[0],200)
    def test_SM_008(self):self.assertEqual(self.request(self.path('forms',object_key='form_a'))[0],200)
    def test_SM_009(self):self.expect_error(self.request(self.path('programmes'),actor=None),401,'AUTH_REQUIRED')
    def test_SM_010(self):self.expect_error(self.request(self.path('programmes',object_key='programme_b')),404,'RESOURCE_UNAVAILABLE')
    def test_SM_011(self):
        status,b=self.request(self.path('indicator-instances')+'?limit=10');self.assertEqual(status,200);self.assertLessEqual(len(b['items']),10)
    def test_SM_012(self):
        status,b=self.request(self.path('reports',object_key='report_a'),actor='revoked');self.assertIn(status,[401,404]);self.assertNotIn('data',b)
