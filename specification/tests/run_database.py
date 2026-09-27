import json,os,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not os.environ.get('IMPACT_TEST_DSN'):print(json.dumps({'status':'BLOCKED','reason':'IMPACT_TEST_DSN and PostgreSQL 17 required','executed':0}));sys.exit(3)
try:import psycopg
except ImportError:print('BLOCKED: psycopg is required');sys.exit(3)
F=json.loads((ROOT/'fixtures/api-fixture.json').read_text())
class Database(unittest.TestCase):
    def setUp(self):
        self.c=psycopg.connect(os.environ['IMPACT_TEST_DSN']);self.cur=self.c.cursor();self.cur.execute('SELECT current_database()');self.assertIn(self.cur.fetchone()[0],['impact_test','impact_dev']);self.cur.execute('SET LOCAL ROLE impact_app')
    def tearDown(self):self.c.rollback();self.c.close()
    def tenant(self,t):self.cur.execute("SELECT set_config('impact.tenant_id',%s,true)",(t,))
    def test_missing_context_denies(self):self.cur.execute('SELECT count(*) FROM impact.programme_current');self.assertEqual(self.cur.fetchone()[0],0)
    def test_tenant_a_only(self):self.tenant(F['tenant_a']);self.cur.execute('SELECT DISTINCT tenant_id::text FROM impact.programme_current');self.assertEqual(self.cur.fetchall(),[(F['tenant_a'],)])
    def test_hidden_object(self):self.tenant(F['tenant_a']);self.cur.execute('SELECT count(*) FROM impact.programme_current WHERE object_id=%s',(F['programme_b'],));self.assertEqual(self.cur.fetchone()[0],0)
    def test_revision_update_denied(self):
        self.tenant(F['tenant_a'])
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.cur.execute("UPDATE impact.object_revision SET payload='{}'")
    def test_audit_delete_denied(self):
        self.tenant(F['tenant_a'])
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.cur.execute('DELETE FROM impact.audit_event_current')
    def test_truncate_denied(self):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.cur.execute('TRUNCATE impact.programme_current')
    def test_partition_direct_access_denied(self):
        self.tenant(F['tenant_a'])
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.cur.execute('SELECT * FROM impact.observation_p00')
    def test_private_identifiers_denied(self):
        self.tenant(F['tenant_a'])
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):self.cur.execute('SELECT * FROM impact.participant_private')
    def test_foreign_tenant_reference_rejected(self):
        self.tenant(F['tenant_a']);self.cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):self.cur.execute('UPDATE impact.indicator_instance_current SET programme_id=%s',(F['programme_b'],))
    def test_wrong_object_kind_rejected(self):
        self.tenant(F['tenant_a']);self.cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):self.cur.execute('UPDATE impact.indicator_instance_current SET programme_id=%s',(F['evidence_a'],))
    def test_same_tenant_write_allowed(self):
        self.tenant(F['tenant_a']);self.cur.execute('UPDATE impact.programme_current SET title=%s WHERE object_id=%s',('temporary',F['mutable_programme']));self.assertEqual(self.cur.rowcount,1)
    def test_context_reset(self):
        self.tenant(F['tenant_a']);self.c.rollback();self.cur.execute('SET LOCAL ROLE impact_app');self.cur.execute('SELECT count(*) FROM impact.programme_current');self.assertEqual(self.cur.fetchone()[0],0)
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Database));sys.exit(0 if r.wasSuccessful() else 1)
