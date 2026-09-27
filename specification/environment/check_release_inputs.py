import json,os,re,sys
keys=['IMPACT_REGION','IMPACT_ALLOWED_REGIONS','IMPACT_PUBLIC_ORIGIN','IMPACT_OIDC_ISSUER','IMPACT_RUNTIME_SECRET_REFERENCE','IMPACT_PRIVACY_SECRET_REFERENCE','IMPACT_KMS_KEY_REFERENCE','IMPACT_ONCALL_ROUTE','IMPACT_RELEASE_EVIDENCE_FILE','IMPACT_POSTGRES_IMAGE','IMPACT_IDP_IMAGE']
missing=[k for k in keys if not os.environ.get(k)]
if missing:print(json.dumps({'status':'BLOCKED','missing_input_names':missing}));sys.exit(3)
errors=[]
if os.environ['IMPACT_REGION'] not in os.environ['IMPACT_ALLOWED_REGIONS'].split(','):errors.append('region outside allowed set')
for k in ['IMPACT_PUBLIC_ORIGIN','IMPACT_OIDC_ISSUER']:
 if not os.environ[k].startswith('https://') or '.invalid' in os.environ[k]:errors.append(k+' must identify actual HTTPS deployment')
for k in ['IMPACT_POSTGRES_IMAGE','IMPACT_IDP_IMAGE']:
 if not re.search(r'@sha256:[0-9a-f]{64}$',os.environ[k]):errors.append(k+' requires immutable digest')
try:
 with open(os.environ['IMPACT_RELEASE_EVIDENCE_FILE']) as f:e=json.load(f)
 for gate in ['database','integration','smoke','browser_accessibility','android','load_soak','restore','security','ai_evaluation']:
  if e.get(gate,{}).get('status')!='PASS' or not e.get(gate,{}).get('artifact_sha256'):errors.append('release evidence missing '+gate)
except (OSError,ValueError):errors.append('release evidence file unavailable or invalid')
print(json.dumps({'status':'FAIL' if errors else 'PASS','errors':errors}));sys.exit(1 if errors else 0)
