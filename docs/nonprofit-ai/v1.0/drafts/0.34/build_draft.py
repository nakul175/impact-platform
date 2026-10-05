from pathlib import Path
import hashlib,json
root=Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
out=Path('/private/tmp/tola-ai-portability-draft')
profile=json.loads((root/'apps/api/impact_api/bootstrap_profile.json').read_text())
for role in ('TENANT_ADMIN','MEL_ADMIN','PROGRAMME_MANAGER'):
    profile['roles'][role]=sorted(set(profile['roles'][role])|{'ai.enablement.export'})
canonical=json.dumps(profile,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
digest=hashlib.sha256(canonical.encode()).hexdigest()
assert digest=='422b86a900e54a661f6c4a4a35ee8146a504ff7d026478e18e9fafe19e510d3f'
(out/'proposed-bootstrap-profile.json').write_text(json.dumps(profile,indent=2)+'\n')
header='''-- Unregistered0040 draft, outside repository; not project-applied or integration-qualified.
-- JSON-only INTERNAL_SELF export of one exact saved adoption-plan revision.
-- Register only after the implemented policy generates this exact target hash.
BEGIN;
SET LOCAL ROLE impact_owner;
-- Existing immutable0036 target and applied tenant ceilings remain unchanged.
-- Runtime impact_platform has SELECT only; owner migrations register new profiles.
INSERT INTO impact.platform_access_profile(profile_hash,manifest,source_migration)
 VALUES('%s',$profile_0040$%s$profile_0040$::jsonb,'0040_ai_plan_portability.sql');

'''%(digest,canonical)
(out/'0040_ai_plan_portability.sql').write_text(header+(out/'sql_body.txt').read_text())
print('Prepared profile hash:',digest)
print('SQL draft SHA256:',hashlib.sha256((out/'0040_ai_plan_portability.sql').read_bytes()).hexdigest())
