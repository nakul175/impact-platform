from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,json
from pglast import parse_sql,parse_plpgsql
from pglast.stream import RawStream
out=Path('/private/tmp/tola-ai-portability-draft')
root=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
sql=(out/'0040_ai_plan_portability.sql').read_text()
ast=parse_sql(sql)
results=[]
for raw in ast:
    stmt=raw.stmt
    if type(stmt).__name__!='CreateFunctionStmt':continue
    name='.'.join(x.sval for x in stmt.funcname)
    language=next(x.arg.sval for x in stmt.options if x.defname=='language')
    try:
        if language=='plpgsql':parse_plpgsql(RawStream()(stmt))
        else:parse_sql(next(x.arg[0].sval for x in stmt.options if x.defname=='as'))
    except Exception as error:
        results.append(dict(function=name,result='PARSER_LIMITATION_REQUIRES_NATIVE_APPLICATION',parser_error_type=type(error).__name__,parser_error=str(error)))
    else:
        results.append(dict(function=name,result='BODY_SYNTAX_PARSED_ONLY'))
old=json.loads((root/'apps/api/impact_api/bootstrap_profile.json').read_text())
new=json.loads((out/'proposed-bootstrap-profile.json').read_text())
assert old['version']==new['version'] and old['purpose_bound']==new['purpose_bound']
assert all(set(old['roles'][r]) <= set(new['roles'][r]) for r in old['roles'])
delta={r:sorted(set(new['roles'][r])-set(old['roles'][r])) for r in new['roles'] if new['roles'][r]!=old['roles'][r]}
assert delta=={r:['ai.enablement.export'] for r in ['TENANT_ADMIN','MEL_ADMIN','PROGRAMME_MANAGER']}
assert 'DROP POLICY' not in sql
replaced=['.'.join(x.sval for x in raw.stmt.funcname) for raw in ast if type(raw.stmt).__name__=='CreateFunctionStmt' and raw.stmt.replace]
assert replaced==['impact.retention_purge_receipts','impact.retention_purge_receipts']
compile((out/'native_probe_helpers.py').read_text(),str(out/'native_probe_helpers.py'),'exec')
profile_hash=hashlib.sha256(json.dumps(new,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
proof=dict(recorded_at=datetime.now(timezone.utc).isoformat(),scope='Unregistered private filesystem draft: SQL/Python syntax and in-memory monotonic profile checks only. No migration application, database role execution, API/browser test or requirement acceptance.',sql_sha256=hashlib.sha256(sql.encode()).hexdigest(),profile_hash=profile_hash,profile_role_delta=delta,top_level_statement_count=len(ast),ast_statement_kinds=dict(Counter(type(r.stmt).__name__ for r in ast)),function_body_results=results,native_probes='PYTHON_COMPILED_ONLY',repository_product_edits=False,native_connection_attempted=False)
(out/'draft-validation.json').write_text(json.dumps(proof,indent=2)+'\n')
print({k:proof[k] for k in ['sql_sha256','profile_hash','top_level_statement_count','native_connection_attempted']})
print('Function syntax parsed:',sum(x['result']=='BODY_SYNTAX_PARSED_ONLY' for x in results),'parser limitations:',sum(x['result']!='BODY_SYNTAX_PARSED_ONLY' for x in results))
