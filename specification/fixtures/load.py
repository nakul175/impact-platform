"""Load a fresh disposable development/test database. Existing data is never removed."""
import os,sys
from pathlib import Path
def main():
    try:import psycopg
    except ImportError:print('BLOCKED: install environment/requirements.lock');return 3
    if os.environ.get('IMPACT_ALLOW_FIXTURE_LOAD')!='1':print('BLOCKED: explicit fixture-load flag required');return 3
    dsn=os.environ.get('IMPACT_FIXTURE_DSN')
    if not dsn:print('BLOCKED: IMPACT_FIXTURE_DSN required');return 3
    with psycopg.connect(dsn,autocommit=True) as c:
        c.execute("SELECT set_config('impact.allow_fixtures','true',false)")
        c.execute((Path(__file__).parent/'seed.sql').read_text(),prepare=False)
    print('PASS: fixture loaded into empty disposable database');return 0
if __name__=='__main__':sys.exit(main())
