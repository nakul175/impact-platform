"""Apply checksummed migrations to an explicitly supplied PostgreSQL 17 database."""
import hashlib,json,os,sys,re
from pathlib import Path

def main():
    try:import psycopg
    except ImportError:print('BLOCKED: install environment/requirements.lock');return 3
    dsn=os.environ.get('IMPACT_MIGRATION_DSN')
    if not dsn:print('BLOCKED: IMPACT_MIGRATION_DSN is required');return 3
    folder=Path(__file__).parent/'migrations'
    files=sorted(folder.glob('*.sql'))
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute('SHOW server_version_num');version=int(cur.fetchone()[0])
            if not 170000<=version<180000:raise RuntimeError('This migration baseline requires PostgreSQL 17')
            cur.execute('SELECT pg_advisory_lock(93812044)')
            try:
                cur.execute("SELECT to_regclass('impact.schema_migration')")
                present=cur.fetchone()[0] is not None
                applied={}
                if present:
                    cur.execute('SELECT version,sha256 FROM impact.schema_migration');applied=dict(cur.fetchall())
                for f in files:
                    number=int(f.name[:4]);digest=hashlib.sha256(f.read_bytes()).hexdigest()
                    if number in applied:
                        if applied[number]!=digest:raise RuntimeError('Migration checksum mismatch at '+f.name)
                        continue
                    sql=re.sub(r'^BEGIN;\s*','',f.read_text(),count=1)
                    sql=re.sub(r'\s*COMMIT;\s*$','',sql,count=1)
                    # 0001 starts with a comment. Remove only the standalone transaction boundary.
                    sql=re.sub(r'^BEGIN;\s*$','',sql,count=1,flags=re.M)
                    with conn.transaction():
                        cur.execute(sql,prepare=False)
                        cur.execute('INSERT INTO impact.schema_migration(version,sha256) VALUES(%s,%s)',(number,digest))
                print(json.dumps({'status':'PASS','migration_versions':[int(f.name[:4]) for f in files],'postgresql_version_number':version}))
            finally:cur.execute('SELECT pg_advisory_unlock(93812044)')
    return 0

if __name__=='__main__':sys.exit(main())
