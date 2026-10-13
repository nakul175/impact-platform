#!/usr/bin/env python3
"""Read-only, fail-closed check of one declared post-v1 overview receipt append.

This does not rerun or replace the complete v1 publication verification. The
caller must first freeze its actual PASS report and all listed v1 inputs. No
network, native mutation, Git mutation, or application test is performed here.
"""
import argparse
import copy
import datetime
import hashlib
import json
import re
from pathlib import Path

OVERVIEW_ID='61b8c340-13f3-4d51-8c6f-bfc23a6660a5'
KIND='Imprana Commons post-publication overview receipt v2'
BASELINE_KEYS={'report','issues','documents','project','publication_plan','policy','verifier'}
REQUIRED_COUNTS={'issues_before':1553,'issues_after':1553,'issue_types':{'epic':54,'story':368,'task':1131},'original_scenarios':1328,'task_blocked_by_edges_before':779,'task_blocked_by_edges_after':779,'updated_documents':10,'protected_history_documents':1,'new_overview_documents':1,'milestones':5,'missing_given_supplements':37,'supplementary_assertion_classifications':7,'qualification_duty_supplements':13,'in_review_before':4,'in_review_after':4,'nonmissing_estimates_before':10,'nonmissing_estimates_after':10}

def sha(data):
    return hashlib.sha256(data.encode('utf-8') if isinstance(data,str) else data).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text())

def full_native_object(value, required_field):
    if isinstance(value,dict) and value.get('isError') is True:raise ValueError('An errored native response is not a full readback.')
    if isinstance(value,dict) and required_field in value and (required_field!='content' or isinstance(value['content'],str)):return value
    if not isinstance(value,dict) or value.get('isError') is True:raise ValueError('A successful full native readback is required.')
    candidates=[]
    for part in value.get('content',[]):
        if isinstance(part,dict) and part.get('type')=='text':
            try:item=json.loads(part.get('text',''))
            except (ValueError,TypeError):continue
            if isinstance(item,dict) and required_field in item:candidates.append(item)
    if len(candidates)!=1:raise ValueError('Exactly one complete native object is required.')
    return candidates[0]

def index_exact(rows,label):
    if not isinstance(rows,list):raise ValueError(label+' must be a full-record list.')
    result={}
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'] or row['id'] in result:raise ValueError(label+' has a missing or duplicate ID.')
        result[row['id']]=copy.deepcopy(row)
    return result

def resolve_input(base,spec):
    if not isinstance(spec,dict) or set(spec)!={'path','sha256'} or not isinstance(spec['path'],str) or not re.fullmatch(r'[0-9a-f]{64}',str(spec['sha256'])):raise ValueError('Each baseline pin requires exactly path and SHA256.')
    path=Path(spec['path']);path=path.resolve() if path.is_absolute() else (base/path).resolve()
    if not path.is_relative_to(base.resolve()):raise ValueError('Frozen v1 inputs must remain inside this evidence output root.')
    if not path.is_file() or sha(path.read_bytes())!=spec['sha256']:raise ValueError('Frozen v1 input missing or changed: '+str(path))
    return path

def verify(plan,base,after_overview,after_project):
    errors=[]; normalizations=[];pins={}
    def fail(code,**detail):errors.append({'code':code,**detail})
    expected_keys={'kind','overview_id','marker','append','baseline','allowed_suffix_normalization'}
    if not isinstance(plan,dict) or set(plan)!=expected_keys:raise ValueError('Use the exact declared v2 delta plan schema.')
    if plan['kind']!=KIND or plan['overview_id']!=OVERVIEW_ID:raise ValueError('Only the one existing Imprana overview is permitted.')
    marker=plan['marker'];append=plan['append']
    if not isinstance(marker,str) or not re.fullmatch(r'<!-- imprana:publication-verification:20261011:v2 -->',marker):raise ValueError('The v2 receipt marker is fixed and explicit.')
    if not isinstance(append,str) or not append.startswith('\n\n') or append.count(marker)!=1:raise ValueError('One separately marked exact append is required.')
    baseline=plan['baseline']
    if not isinstance(baseline,dict) or set(baseline)!=BASELINE_KEYS:raise ValueError('All seven immutable v1 input pins are required.')
    for name,spec in baseline.items():
        path=resolve_input(base,spec);pins[name]={'path':str(path),'sha256':spec['sha256']}
    report=read_json(pins['report']['path'])
    if report.get('result')!='PASS' or report.get('errors')!=[]:fail('V1_ACTUAL_PASS_REQUIRED')
    for key,value in REQUIRED_COUNTS.items():
        if report.get('counts',{}).get(key)!=value:fail('V1_COUNT_MISMATCH',field=key,expected=value,actual=report.get('counts',{}).get(key))
    # The frozen PASS must itself bind the exact complete input snapshot hashes.
    report_keys={'issues':'after_issues','documents':'after_docs','project':'after_project','publication_plan':'plan'}
    for name,key in report_keys.items():
        if report.get('input_pins',{}).get(key,{}).get('sha256')!=pins[name]['sha256']:fail('V1_REPORT_INPUT_PIN_MISMATCH',input=name)
    if report.get('normalization_policy_pin',{}).get('sha256')!=pins['policy']['sha256']:fail('V1_REPORT_POLICY_PIN_MISMATCH')
    if report.get('verifier_sha256')!=pins['verifier']['sha256']:fail('V1_REPORT_VERIFIER_PIN_MISMATCH')
    issues=read_json(pins['issues']['path'])
    if not isinstance(issues,dict) or set(issues)!={'issues'} or len(index_exact(issues['issues'],'v1 issues'))!=1553:fail('V1_COMPLETE_ISSUES_REQUIRED')
    olddocs=read_json(pins['documents']['path'])
    if isinstance(olddocs,dict) and set(olddocs)=={'documents'}:olddocs=olddocs['documents']
    documents=index_exact(olddocs,'v1 documents')
    if len(documents)!=12 or OVERVIEW_ID not in documents:fail('V1_COMPLETE_DOCUMENTS_REQUIRED')
    old=documents.get(OVERVIEW_ID,{})
    current=full_native_object(after_overview,'content');current_project=full_native_object(after_project,'resources')
    if old.get('id')!=current.get('id') or current.get('id')!=OVERVIEW_ID:fail('OVERVIEW_ID_CHANGED')
    before=old.get('content');actual=current.get('content')
    if not isinstance(before,str) or not isinstance(actual,str):fail('OVERVIEW_CONTENT_TYPE')
    else:
        if marker in before:fail('V2_ALREADY_PRESENT_IN_FROZEN_V1')
        if actual.count(marker)!=1:fail('V2_MARKER_COUNT',actual=actual.count(marker))
        if not actual.startswith(before):fail('V1_OVERVIEW_PREFIX_CHANGED')
        normal=plan['allowed_suffix_normalization']
        if normal is not None:
            if not isinstance(normal,dict) or set(normal)!={'name','actual_observation_pin'} or normal.get('name')!='remove_single_final_lf':raise ValueError('Only separately observed single-final-LF removal may be declared.')
            evidence=resolve_input(base,normal['actual_observation_pin'])
        if actual!=before+append:
            if normal is not None and append.endswith('\n') and actual==before+append[:-1]:normalizations.append({'name':'remove_single_final_lf','observation_path':str(evidence),'sha256':sha(evidence.read_bytes())})
            else:fail('EXACT_DECLARED_V2_APPEND_MISMATCH')
    volatile={'content','updatedAt','updatedBy'}
    if {k:v for k,v in old.items() if k not in volatile}!={k:v for k,v in current.items() if k not in volatile}:fail('OVERVIEW_METADATA_CHANGED')
    oldproject=read_json(pins['project']['path'])
    for label,obj in [('v1',oldproject),('after',current_project)]:
        if obj.get('resourceCount')!=14 or len(index_exact(obj.get('resources'),label+' resources'))!=14:fail('PROJECT_RESOURCE_COUNT',capture=label)
        if len(index_exact(obj.get('milestones'),label+' milestones'))!=5:fail('PROJECT_MILESTONE_COUNT',capture=label)
    old_resources=index_exact(oldproject.get('resources'),'v1 resources');new_resources=index_exact(current_project.get('resources'),'after resources')
    if set(old_resources)!=set(new_resources) or OVERVIEW_ID not in old_resources:fail('PROJECT_RESOURCE_SCOPE_CHANGED')
    for rid,resource in old_resources.items():
        if rid not in new_resources:continue
        next_resource=new_resources[rid]
        if rid==OVERVIEW_ID:
            for capture,item,document in [('v1',resource,old),('after',next_resource,current)]:
                if not isinstance(item.get('updatedAt'),str) or not item['updatedAt'] or item['updatedAt']!=document.get('updatedAt'):fail('OVERVIEW_RESOURCE_TIMESTAMP_PROJECTION_MISMATCH',capture=capture)
            if {k:v for k,v in resource.items() if k!='updatedAt'}!={k:v for k,v in next_resource.items() if k!='updatedAt'}:fail('PROJECT_RESOURCE_MEMBER_CHANGED',id=rid)
        elif resource!=next_resource:fail('PROJECT_RESOURCE_MEMBER_CHANGED',id=rid)
    if index_exact(oldproject.get('milestones'),'v1 milestones')!=index_exact(current_project.get('milestones'),'after milestones'):fail('PROJECT_MILESTONE_MEMBER_CHANGED')
    excluded={'updatedAt','resources','milestones'}
    if {k:v for k,v in oldproject.items() if k not in excluded}!={k:v for k,v in current_project.items() if k not in excluded}:fail('PROJECT_METADATA_OR_DESCRIPTION_CHANGED')
    for name,spec in baseline.items():
        try:resolve_input(base,spec)
        except ValueError as exc:fail('FROZEN_V1_INPUT_CHANGED_DURING_CHECK',input=name,message=str(exc))
    return {'result':'PASS' if not errors else 'FAIL','scope':'Read-only check of one exact post-v1 overview receipt append and fresh captured overview/project preservation. Frozen v1 report and inputs remain unchanged. Other live objects are not re-read or requalified; no application tests, Ready/Done, owner acceptance or release clearance is established.','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overview_id':OVERVIEW_ID,'counts':{'overview_appends':1,'project_resources':14,'milestones':5,'frozen_v1_inputs':7},'baseline_pins':pins,'observed_suffix_normalizations':normalizations,'errors':errors}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,default=Path(__file__).resolve().parent.parent);p.add_argument('--plan',type=Path,required=True);p.add_argument('--after-overview',type=Path,required=True);p.add_argument('--after-project',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    protected={a.plan.resolve(),a.after_overview.resolve(),a.after_project.resolve()}
    report={'result':'FAIL','errors':[]}
    try:
        plan=read_json(a.plan)
        for spec in plan.get('baseline',{}).values():
            if isinstance(spec,dict) and 'path' in spec:protected.add((Path(spec['path']) if Path(spec['path']).is_absolute() else a.base/str(spec['path'])).resolve())
        normal=plan.get('allowed_suffix_normalization')
        if isinstance(normal,dict):
            spec=normal.get('actual_observation_pin',{})
            if isinstance(spec,dict) and 'path' in spec:protected.add((Path(spec['path']) if Path(spec['path']).is_absolute() else a.base/str(spec['path'])).resolve())
        if a.output.resolve() in protected:raise ValueError('Report output must not overwrite any input or frozen v1 evidence.')
        report=verify(plan,a.base,read_json(a.after_overview),read_json(a.after_project));report['input_pins']={name:{'path':str(path.resolve()),'sha256':sha(path.read_bytes())} for name,path in [('delta_plan',a.plan),('fresh_overview',a.after_overview),('fresh_project',a.after_project)]};report['checker_sha256']=sha(Path(__file__).read_bytes())
    except Exception as exc:report['result']='FAIL';report.setdefault('errors',[]).append({'code':'MISSING_OR_INVALID_EVIDENCE','message':str(exc)})
    if a.output.resolve() in protected:print(json.dumps(report,indent=2));return 1
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'result':report['result'],'errors':len(report['errors']),'report':str(a.output)},indent=2));return 0 if report['result']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
