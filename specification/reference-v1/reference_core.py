"""Executable design reference, not a production service or security boundary.

Expected values in fixtures/vectors.json are independently fixed examples.
Production implementations must run the same contracts with real infrastructure.
"""
import hashlib, json, re
from datetime import datetime
from decimal import Decimal, localcontext, ROUND_HALF_UP

class ContractError(ValueError):
    def __init__(self, code): self.code=code; super().__init__(code)

def number(value):
    if not isinstance(value,str) or not re.fullmatch(r'-?(0|[1-9][0-9]{0,25})(\.[0-9]{1,12})?',value):
        raise ContractError('VALIDATION_FAILED')
    return Decimal(value)

def display(value,places=2):
    if type(places) is not int or not 0<=places<=6: raise ContractError('VALIDATION_FAILED')
    with localcontext() as c:
        c.prec=60
        return format(Decimal(value).quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP),'f')

def stored(value):
    with localcontext() as c:
        c.prec=60
        result=Decimal(value).quantize(Decimal('0.000000000001'),rounding=ROUND_HALF_UP)
        if abs(result)>=Decimal('1e26'):raise ContractError('LIMIT_EXCEEDED')
        return format(result,'f')

def total(values):
    with localcontext() as c:
        c.prec=60
        result=sum((number(v) for v in values),Decimal(0))
        if abs(result)>=Decimal('1e26'): raise ContractError('LIMIT_EXCEEDED')
        return format(result,'f')

def pooled(pairs):
    with localcontext() as c:
        c.prec=60
        parsed=[(number(n),number(d)) for n,d in pairs]
        if any(n<0 or d<0 or (d>0 and n>d) for n,d in parsed): raise ContractError('VALIDATION_FAILED')
        n=sum((x[0] for x in parsed),Decimal(0)); d=sum((x[1] for x in parsed),Decimal(0))
        if not d:return {'state':'UNDEFINED','value':None,'reason':'ZERO_DENOMINATOR'}
        value=n/d*100
        return {'state':'PRESENT','value':stored(value),'display':display(value,2),'numerator':format(n,'f'),'denominator':format(d,'f')}

def divide(n,d):
    with localcontext() as c:
        c.prec=60; a=number(n); b=number(d)
        return None if not b else stored(a/b)

def unique_reach(groups):
    return None if any(g is None for g in groups) else len(set().union(*[set(g) for g in groups]))

def cumulative(values,zero_start=False):
    nums=[number(v) for v in values]
    return {'end':format(nums[-1],'f') if nums else None,'increments':[format(v-(nums[i-1] if i else Decimal(0)),'f') for i,v in enumerate(nums)] if zero_start else None}

def higher(actual,target):
    a=number(actual); t=number(target)
    if t<=0:raise ContractError('UNDEFINED_RESULT')
    with localcontext() as c:c.prec=60; return display(a/t*100,2)

def lower(actual,target):
    a=number(actual);t=number(target)
    return {'achieved':a<=t,'deviation':format(a-t,'f')}

def in_range(actual,low,high):
    a=number(actual);lo=number(low);hi=number(high)
    if lo>hi:raise ContractError('VALIDATION_FAILED')
    return lo<=a<=hi

def coverage(approved,expected):
    if type(approved) is not int or type(expected) is not int or not 0<=approved<=expected:raise ContractError('VALIDATION_FAILED')
    if not expected:return {'state':'NOT_APPLICABLE','percent':None,'partial':False}
    with localcontext() as c:c.prec=60; return {'state':'PRESENT','percent':display(Decimal(approved)/expected*100,2),'partial':approved<expected}

def weighted(values,weights):
    vals=[number(v) for v in values]; ws=[number(w) for w in weights]
    with localcontext() as c:
        c.prec=60
        if len(vals)!=len(ws) or any(w<0 for w in ws) or sum(ws)!=1:raise ContractError('VALIDATION_FAILED')
        return display(sum(v*w for v,w in zip(vals,ws)),2)

def period_contains(event,start,end):
    try:e,s,t=[datetime.fromisoformat(v.replace('Z','+00:00')) for v in (event,start,end)]
    except ValueError:raise ContractError('VALIDATION_FAILED')
    if any(x.tzinfo is None for x in (e,s,t)) or s>=t:raise ContractError('VALIDATION_FAILED')
    return s<=e<t

def value_contract(state,value):
    if state=='PRESENT':return format(number(value),'f')
    if state not in {'MISSING','NOT_COLLECTED','NOT_APPLICABLE','INVALID','UNDEFINED'} or value is not None:raise ContractError('VALIDATION_FAILED')
    return None

def approve(actor,authors,active,candidate,current,decisions=None,quorum=1):
    if not active:raise ContractError('POLICY_DENIED')
    if actor in authors:raise ContractError('INDEPENDENCE_REQUIRED')
    if candidate!=current:raise ContractError('CONFLICT_VERSION')
    if type(quorum) is not int or quorum<1:raise ContractError('VALIDATION_FAILED')
    return len(set(decisions or [])|{actor})>=quorum

def offline_allowed(elapsed,restricted=False,anchor=True,revoked=False):
    return type(elapsed) in (int,float) and anchor and not revoked and 0<=elapsed<(28800 if restricted else 86400)

def canonical_hash(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def replay(previous_hash,payload_hash,current_access=True):
    if not current_access:raise ContractError('POLICY_DENIED')
    if previous_hash!=payload_hash:raise ContractError('CONFLICT_OPERATION')
    return 'ORIGINAL_RECEIPT'

def revision(expected,current):
    if expected!=current:raise ContractError('CONFLICT_VERSION')
    return True

def row_accounting(parsed,outcomes):
    if type(parsed) is not int or parsed<0 or len(outcomes)!=6 or any(type(n) is not int or n<0 for n in outcomes):raise ContractError('VALIDATION_FAILED')
    return parsed==sum(outcomes)

def text_limit(text,limit):
    if not isinstance(text,str) or any(0xD800<=ord(x)<=0xDFFF for x in text) or len(text)>limit:raise ContractError('VALIDATION_FAILED')
    return True

def dependency_order(edges):
    nodes=set(edges)|{d for deps in edges.values() for d in deps};out=[];visiting=set();done=set()
    def visit(n):
        if n in visiting:raise ContractError('VALIDATION_FAILED')
        if n in done:return
        visiting.add(n)
        for d in sorted(edges.get(n,[])):visit(d)
        visiting.remove(n);done.add(n);out.append(n)
    for n in sorted(nodes):visit(n)
    return out

def public_cells(cells,threshold=5):
    """Conservative example for one additive row, not a general inference engine."""
    if any(type(c) is not int or c<0 for c in cells) or type(threshold) is not int or threshold<1:raise ContractError('VALIDATION_FAILED')
    if any(0<c<threshold for c in cells):return {'cells':[None]*len(cells),'total':None}
    return {'cells':cells,'total':sum(cells)}

def median(values):
    nums=sorted(number(v) for v in values)
    if not nums:return None
    with localcontext() as c:
        c.prec=60;n=len(nums)
        return display(nums[n//2] if n%2 else (nums[n//2-1]+nums[n//2])/2,2)

def currency(amount,rate):
    with localcontext() as c:
        c.prec=60;a=number(amount);r=number(rate)
        if r<=0:raise ContractError('VALIDATION_FAILED')
        return stored(a*r)

def contribution_sum(contributions,unit):
    unique={}
    for identity,value,source_unit in contributions:
        if source_unit!=unit:raise ContractError('INCOMPATIBLE_MEASURE')
        if identity in unique and unique[identity]!=value:raise ContractError('CONFLICT_VERSION')
        unique[identity]=value
    return total(list(unique.values()))
