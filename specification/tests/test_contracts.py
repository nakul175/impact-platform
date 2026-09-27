import copy,json,re,unittest
from pathlib import Path
from jsonschema import Draft202012Validator,FormatChecker,RefResolver
from pglast import parse_sql
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'contracts/openapi.json').read_text());SCHEMAS=SPEC['components']['schemas']
def validator(name):return Draft202012Validator(SCHEMAS[name],resolver=RefResolver.from_schema(SPEC),format_checker=FormatChecker())
class Contracts(unittest.TestCase):
    def test_schema_metaschemas(self):
        for name,schema in SCHEMAS.items():
            with self.subTest(schema=name):Draft202012Validator.check_schema(schema)
    def test_local_refs_resolve(self):
        def walk(v):
            if isinstance(v,dict):
                if '$ref' in v:
                    target=SPEC
                    for p in v['$ref'].removeprefix('#/').split('/'):target=target[p]
                for x in v.values():walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(SPEC)
    def test_no_untyped_collections(self):
        def walk(v):
            if isinstance(v,dict):
                if v.get('type')=='object':self.assertTrue('properties' in v or 'patternProperties' in v);self.assertIs(v.get('additionalProperties'),False)
                if v.get('type')=='array':self.assertTrue(v.get('items'))
                for x in v.values():walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(SCHEMAS)
    def test_unique_operation_ids(self):
        ids=[op['operationId'] for p in SPEC['paths'].values() for k,op in p.items() if k in ['get','post','put','patch','delete']]
        self.assertEqual(len(ids),len(set(ids)))
    def test_cookie_mutations_require_csrf(self):
        for path in SPEC['paths'].values():
            for verb,op in path.items():
                if verb in ['post','put','patch','delete']:self.assertIn({'sessionCookie':[],'csrfToken':[]},op['security'])
    def test_server_fields_cannot_be_forged(self):
        cases=[('ObservationDraftData','approval_state','APPROVED'),('EvidenceDraftData','scan_state','CLEAN'),('MembershipDraftData','status','Active'),('GrantDraftData','issuer_id','11111111-1111-4111-8111-111111111111'),('SubmissionDraftData','original_author_id','11111111-1111-4111-8111-111111111111')]
        for schema,field,value in cases:
            with self.subTest(schema=schema):self.assertFalse(validator(schema).is_valid({field:value}))
    def test_decimal_string_boundaries(self):
        for val,ok in [('0',True),('-0.1',True),('99999999999999999999999999.999999999999',True),('1e2',False),('0.1234567890123',False),(1.5,False),('NaN',False)]:
            with self.subTest(value=val):self.assertEqual(validator('ObservationDraftData').is_valid({'value_state':'PRESENT','value':val}),ok)
    def test_missing_is_not_zero(self):
        v=validator('ObservationDraftData');self.assertTrue(v.is_valid({'value_state':'MISSING','value':None}));self.assertFalse(v.is_valid({'value_state':'MISSING','value':'0'}));self.assertFalse(v.is_valid({'value_state':'PRESENT'}))
    def test_typed_answers(self):
        v=validator('AnswerMap');self.assertTrue(v.is_valid({'safe_water':{'kind':'SINGLE_CHOICE','value':'yes'}}));self.assertFalse(v.is_valid({'safe_water':'yes'}));self.assertFalse(v.is_valid({'safe_water':{'kind':'EXECUTE','value':'code'}}))
    def test_repeat_row_bounds(self):
        row={'row_id':'11111111-1111-4111-8111-111111111111','answers':{}}
        v=validator('AnswerREPEAT');self.assertTrue(v.is_valid({'kind':'REPEAT','value':[row]*100}));self.assertFalse(v.is_valid({'kind':'REPEAT','value':[row]*101}))
    def test_recipient_exactly_one_identity(self):
        v=validator('Recipient');uid='11111111-1111-4111-8111-111111111111'
        self.assertTrue(v.is_valid({'membership_id':uid,'allow_download':False}));self.assertFalse(v.is_valid({'allow_download':True}));self.assertFalse(v.is_valid({'membership_id':uid,'audience_group_id':uid,'allow_download':False}))
    def test_event_rejects_secrets_and_missing_sequence(self):
        schema=json.loads((ROOT/'contracts/event.schema.json').read_text());v=Draft202012Validator(schema,format_checker=FormatChecker());u='11111111-1111-4111-8111-111111111111'
        e={'event_id':u,'tenant_id':u,'event_type':'programme.changed','schema_version':'1.0','aggregate_type':'Programme','aggregate_id':u,'aggregate_revision':u,'aggregate_sequence':1,'occurred_at':'2026-09-25T00:00:00Z','actor_id':u,'correlation_id':u,'payload':{'object_id':u,'revision_id':u,'state':'Active'}}
        self.assertTrue(v.is_valid(e));self.assertFalse(v.is_valid({**e,'password':'x'}));e.pop('aggregate_sequence');self.assertFalse(v.is_valid(e))
    def test_sql_parses(self):
        for f in list((ROOT/'database/migrations').glob('*.sql'))+[ROOT/'fixtures/seed.sql']:
            with self.subTest(file=f.name):self.assertGreater(len(parse_sql(f.read_text())),0)
    def test_rls_and_privileges_cover_tables(self):
        m=json.loads((ROOT/'database/catalogue.json').read_text());sql=(ROOT/'database/migrations/0003_security.sql').read_text()
        for t in m['tenant_tables']:self.assertIn(f'ALTER TABLE impact.{t} FORCE ROW LEVEL SECURITY',sql)
        for t in m['partition_tables']:self.assertNotRegex(sql,r'GRANT [^;]+ ON impact\.'+t+r'\b')
        self.assertNotIn('TRUNCATE',sql);self.assertNotIn('BYPASSRLS',sql)
        for t in m['append_only_tables']:self.assertNotIn(f'GRANT SELECT,INSERT,UPDATE ON impact.{t} ',sql)
    def test_permission_inventory_exact(self):
        policy=json.loads((ROOT/'contracts/access-policy.json').read_text());ids={x['operation_id'] for x in policy['operations']};actual={op['operationId'] for p in SPEC['paths'].values() for k,op in p.items() if k in ['get','post','put','patch','delete']}
        self.assertEqual(ids,actual)
        for r in policy['operations']:self.assertTrue(r['role_templates'],r['capability']);self.assertNotIn('*',r['capability'])
    def test_backlog_has_every_requirement_once(self):
        rows=json.loads((ROOT/'implementation-backlog.json').read_text())['requirements'];source=json.loads((ROOT/'contracts/fsd-requirements.json').read_text());actual={x['id'] for key in ['functional','nonfunctional'] for x in source[key]}
        self.assertEqual({x['requirement'] for x in rows},actual);self.assertEqual(len(rows),len(actual))
    def test_dependency_graph_acyclic(self):
        packs=json.loads((ROOT/'implementation-backlog.json').read_text())['packages'];todo={x['id']:set(x['dependencies']) for x in packs};done=set()
        while todo:
            ready={k for k,v in todo.items() if v<=done};self.assertTrue(ready)
            done|=ready
            for k in ready:del todo[k]
    def test_fixture_entity_data_schemas(self):
        for row in json.loads((ROOT/'fixtures/records.json').read_text()):
            n=row['object_type']+'Data'
            if n not in SCHEMAS:continue
            with self.subTest(key=row['key']):validator(n).validate(row['data'])
    def test_fixture_reference_types_and_tenants(self):
        rows=json.loads((ROOT/'fixtures/records.json').read_text());objects={(r['tenant_id'],r['object_id']):r for r in rows};revisions={(r['tenant_id'],r['revision_id']):r for r in rows};mapping=json.loads((ROOT/'database/reference-map.json').read_text())
        for r in rows:
            for field in [x for x in mapping if x['entity']==r['object_type']]:
                value=r['data'].get(field['field']);code=field['reference']
                if value is None or not code.startswith(('O:','R:')):continue
                target=(objects if code.startswith('O:') else revisions).get((r['tenant_id'],value));self.assertIsNotNone(target,(r['key'],field['field']))
                if code[2:]!='*':self.assertEqual(target['object_type'],code[2:])
