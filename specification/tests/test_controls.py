import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_controls import canonical,upload_manifest,part_replay,evaluate,PART_SIZE
RULES=json.loads((ROOT/'contracts/access-policy.json').read_text())['operations']
def rule(cap):return next(r for r in RULES if r['capability']==cap)
def context(cap):return {'authenticated':True,'tenant_match':True,'membership_active':True,'membership_unexpired':True,'tenant_allows_operation':True,'grants':[cap],'scope_match':True,'classification_allowed':True,'purpose_allowed':True,'epochs_current':True,'assurance_age_seconds':0,'natural_actor_id':'reviewer','material_author_ids':['author'],'lifecycle_allows':True,'revision_matches':True}
class Controls(unittest.TestCase):
    def test_policy_boundary_vectors(self):
        r=rule('workflow.approve');c=context(r['capability'])
        for key,result in [('authenticated','AUTH_REQUIRED'),('tenant_match','RESOURCE_UNAVAILABLE'),('membership_active','RESOURCE_UNAVAILABLE'),('membership_unexpired','RESOURCE_UNAVAILABLE'),('tenant_allows_operation','POLICY_DENIED'),('scope_match','RESOURCE_UNAVAILABLE'),('classification_allowed','POLICY_DENIED'),('epochs_current','POLICY_DENIED'),('lifecycle_allows','STATE_TRANSITION_DENIED'),('revision_matches','CONFLICT_VERSION')]:
            with self.subTest(key=key):self.assertEqual(evaluate(r,{**c,key:False}),result)
    def test_permitted_review(self):r=rule('workflow.approve');self.assertEqual(evaluate(r,context(r['capability'])),'ALLOW')
    def test_no_grant(self):r=rule('workflow.approve');self.assertEqual(evaluate(r,{**context(r['capability']),'grants':[]}),'POLICY_DENIED')
    def test_natural_person_self_approval(self):r=rule('workflow.approve');self.assertEqual(evaluate(r,{**context(r['capability']),'natural_actor_id':'author'}),'INDEPENDENCE_REQUIRED')
    def test_assurance_edges(self):
        r=rule('report.publish');c=context(r['capability'])
        for age,result in [(0,'ALLOW'),(300,'ALLOW'),(301,'ASSURANCE_REQUIRED'),(-1,'ASSURANCE_REQUIRED'),(None,'ASSURANCE_REQUIRED')]:
            with self.subTest(age=age):self.assertEqual(evaluate(r,{**c,'assurance_age_seconds':age}),result)
    def test_purpose_required(self):r=rule('privacy.execute');self.assertEqual(evaluate(r,{**context(r['capability']),'purpose_allowed':False}),'POLICY_DENIED')
    def test_invitation_exception_is_bounded(self):
        r=next(r for r in RULES if r['operation_id']=='accept_invitation');c={'authenticated':True,'intended_invitee':True,'valid_invitation':True,'inviter_still_authorised':True}
        self.assertEqual(evaluate(r,c),'ALLOW')
        for k in c:self.assertNotEqual(evaluate(r,{**c,k:False}),'ALLOW')
    def test_public_readiness(self):self.assertEqual(evaluate(rule('public'),{}),'ALLOW')
    def test_ai_has_no_approval_or_grant_capability(self):
        # AI is not an authority-bearing role; requester authority applies only to typed draft commands.
        p=json.loads((ROOT/'contracts/access-policy.json').read_text());self.assertNotIn('AI',p['roles'])
    def test_upload_valid_boundaries(self):
        for n in [1,PART_SIZE,PART_SIZE+1,25000000]:
            with self.subTest(bytes=n):self.assertEqual(len(upload_manifest(n,self.parts(n))),64)
    def parts(self,n):return [{'part_number':i+1,'bytes':min(PART_SIZE,n-i*PART_SIZE),'sha256':'a'*64} for i in range((n+PART_SIZE-1)//PART_SIZE)]
    def test_upload_oversize(self):
        for n in [0,-1,25000001,True]:
            with self.subTest(bytes=n):
                with self.assertRaises(ValueError):upload_manifest(n,[])
    def test_import_maximum(self):self.assertEqual(len(upload_manifest(100000000,self.parts(100000000),'SOURCE_IMPORT')),64)
    def test_missing_part(self):
        with self.assertRaises(ValueError):upload_manifest(PART_SIZE+1,self.parts(PART_SIZE))
    def test_reordered_manifest(self):
        with self.assertRaises(ValueError):upload_manifest(PART_SIZE+1,list(reversed(self.parts(PART_SIZE+1))))
    def test_bad_part_size(self):
        p=self.parts(PART_SIZE+1);p[-1]['bytes']=2
        with self.assertRaises(ValueError):upload_manifest(PART_SIZE+1,p)
    def test_bad_digest(self):
        p=self.parts(1);p[0]['sha256']='z'*64
        with self.assertRaises(ValueError):upload_manifest(1,p)
    def test_chunk_replay_and_authority(self):
        for expected,args in [('ACCEPT',(None,{'sha256':'a'})),('REPLAY',({'sha256':'a'},{'sha256':'a'})),('CONFLICT',({'sha256':'a'},{'sha256':'b'})),('SEALED',(None,{},'CLEAN',True)),('DENIED',(None,{},'OPEN',False))]:
            with self.subTest(expected=expected):self.assertEqual(part_replay(*args),expected)
    def test_canonical_command_order(self):self.assertEqual(canonical({'b':1,'a':'0'}),canonical({'a':'0','b':1}))
    def test_binary_float_rejected(self):
        with self.assertRaises(ValueError):canonical({'value':0.1})
