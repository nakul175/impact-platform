"""Deterministic design references. Production identity, storage and policy adapters remain separate."""
import hashlib,json,math
PART_SIZE=1048576

def canonical(value):
    """Project canonical profile: closed DTOs, Unicode preserved, decimals as strings, no floats."""
    def check(x):
        if isinstance(x,float):raise ValueError('binary float not permitted in command hash')
        if isinstance(x,dict):
            if not all(isinstance(k,str) for k in x):raise ValueError('nonstring key')
            for v in x.values():check(v)
        elif isinstance(x,list):
            for v in x:check(v)
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def upload_manifest(expected_bytes,parts,purpose='EVIDENCE_MEDIA'):
    maximum=25000000 if purpose=='EVIDENCE_MEDIA' else 100000000
    if type(expected_bytes) is not int or not 1<=expected_bytes<=maximum:raise ValueError('size')
    count=math.ceil(expected_bytes/PART_SIZE)
    if len(parts)!=count:raise ValueError('missing or extra part')
    for i,p in enumerate(parts,1):
        if p['part_number']!=i:raise ValueError('noncontiguous order')
        size=PART_SIZE if i<count else expected_bytes-PART_SIZE*(count-1)
        if p['bytes']!=size:raise ValueError('part size')
        digest=p['sha256']
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('digest')
    return hashlib.sha256(canonical(parts)).hexdigest()

def part_replay(existing,incoming,state='OPEN',authorised=True):
    if not authorised:return 'DENIED'
    if state!='OPEN':return 'SEALED'
    if existing is None:return 'ACCEPT'
    return 'REPLAY' if existing==incoming else 'CONFLICT'

def evaluate(rule,context):
    """Context is trusted server-derived input, never a caller-owned request DTO."""
    if rule['capability']=='public':return 'ALLOW'
    if not context.get('authenticated'):return 'AUTH_REQUIRED'
    if rule['operation_id']=='accept_invitation':
        return 'ALLOW' if all(context.get(k) for k in ['intended_invitee','valid_invitation','inviter_still_authorised']) else 'POLICY_DENIED'
    if not context.get('tenant_match'):return 'RESOURCE_UNAVAILABLE'
    if not context.get('membership_active') or not context.get('membership_unexpired'):return 'RESOURCE_UNAVAILABLE'
    if not context.get('tenant_allows_operation'):return 'POLICY_DENIED'
    if rule['capability'] not in context.get('grants',[]):return 'POLICY_DENIED'
    if not context.get('scope_match'):return 'RESOURCE_UNAVAILABLE'
    if not context.get('classification_allowed'):return 'POLICY_DENIED'
    if rule['purpose_required'] and not context.get('purpose_allowed'):return 'POLICY_DENIED'
    if not context.get('epochs_current'):return 'POLICY_DENIED'
    limit=rule['fresh_assurance_seconds']
    if limit is not None and (context.get('assurance_age_seconds') is None or not 0<=context['assurance_age_seconds']<=limit):return 'ASSURANCE_REQUIRED'
    if rule['independence_required'] and context.get('natural_actor_id') in context.get('material_author_ids',[]):return 'INDEPENDENCE_REQUIRED'
    if not context.get('lifecycle_allows'):return 'STATE_TRANSITION_DENIED'
    if not context.get('revision_matches'):return 'CONFLICT_VERSION'
    return 'ALLOW'
