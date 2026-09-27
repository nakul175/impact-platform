import json, os, unittest, uuid
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlparse

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

class ApiCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=os.environ.get('IMPACT_BASE_URL','').rstrip('/'); fixture=os.environ.get('IMPACT_FIXTURE_FILE')
        if not base or not fixture:raise unittest.SkipTest('Set IMPACT_BASE_URL and IMPACT_FIXTURE_FILE for an isolated provisioned API fixture')
        u=urlparse(base)
        if u.scheme!='https' and not (u.scheme=='http' and u.hostname in ('localhost','127.0.0.1','::1')):raise AssertionError('HTTPS is required outside loopback')
        if u.username or u.password or u.query or u.fragment:raise AssertionError('Base URL must not contain credentials, query or fragment')
        with open(fixture) as f:cls.fixture=json.load(f)
        cls.base=base;cls.opener=build_opener(NoRedirect())

    def token(self,actor):
        env=self.fixture['actors'][actor]['token_env']; value=os.environ.get(env)
        if not value:raise unittest.SkipTest('Missing token environment variable '+env)
        return value

    def request(self,path,actor='author',method='GET',payload=None):
        headers={'Accept':'application/json','X-Correlation-ID':str(uuid.uuid4())}
        if actor:headers['Authorization']='Bearer '+self.token(actor)
        data=None
        if payload is not None:headers['Content-Type']='application/json';data=json.dumps(payload,allow_nan=False).encode()
        try:
            response=self.opener.open(Request(self.base+path,data=data,headers=headers,method=method),timeout=15)
        except HTTPError as error:response=error
        with response:
            raw=response.read(2_000_001)
            self.assertLessEqual(len(raw),2_000_000,'Response must remain bounded')
            self.assertIn('application/json',response.headers.get('Content-Type',''))
            try:body=json.loads(raw)
            except ValueError:self.fail('Expected JSON without printing sensitive response')
            return response.status,body

    def path(self,resource,tenant='tenant_a',object_key=None):
        p='/v1/tenants/'+self.fixture[tenant]+'/'+resource
        return p+('/'+self.fixture[object_key] if object_key else '')

    def expect_error(self,result,status,code):
        actual,body=result;self.assertEqual(actual,status);self.assertEqual(body['code'],code)
        self.assertIsInstance(body['retryable'],bool);self.assertTrue(body['correlation_id'])
        self.assertIsInstance(body['permitted_actions'],list)
        return body

    def require_mutations(self):
        if os.environ.get('IMPACT_ALLOW_MUTATIONS')!='1' or self.fixture.get('allow_mutations') is not True:
            self.skipTest('Mutation tests require explicit runner and fixture opt in')
        status,manifest=self.request('/v1/runtime-manifest')
        self.assertEqual(status,200)
        self.assertIn(manifest['environment'],['development','test','staging'])
        self.assertIs(manifest['mutation_tests_allowed'],True)
        self.assertEqual(manifest['fixture_id'],self.fixture['fixture_id'])

    def command(self,revision,data=None,operation=None):
        return {'operation_id':operation or str(uuid.uuid4()),'expected_revision':revision,'data':data or {}}

    def restore_title(self,title):
        path=self.path('programmes',object_key='mutable_programme')
        status,current=self.request(path);self.assertEqual(status,200)
        status,receipt=self.request(path,method='PATCH',payload=self.command(current['revision_id'],{'title':title}))
        self.assertEqual(status,200,'Restoration failed; quarantine fixture for operator review')
