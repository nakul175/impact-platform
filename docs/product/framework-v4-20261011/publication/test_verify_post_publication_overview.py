#!/usr/bin/env python3
"""Synthetic deliberate corruption guards; never a native publication PASS."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import verify_post_publication_overview as v

class PostPublicationGuards(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.before={'id':v.OVERVIEW_ID,'title':'Exact existing overview','content':'Exact frozen v1 content\n','archivedAt':None,'updatedAt':'old','createdAt':'fixed'}
        self.project={'uuid':'fixed-project','description':'Exact project body','resourceCount':14,'resources':[{'id':str(i),'type':'document','title':'Resource '+str(i)} for i in range(14)],'milestones':[{'id':str(i),'name':'Milestone '+str(i),'description':'exact','targetDate':None} for i in range(5)],'updatedAt':'old'}
        self.project['resources'][0]['id']=v.OVERVIEW_ID;self.project['resources'][0]['updatedAt']=self.before['updatedAt']
        self.marker='<!-- imprana:publication-verification:20261011:v2 -->';self.append='\n\n'+self.marker+'\nActual verification receipt; product tests remain unrun.\n'
        values={'issues':{'issues':[{'id':'APL-'+str(i),'uuid':'uuid-'+str(i)} for i in range(1553)]},'documents':{'documents':[self.before]+[{'id':'doc-'+str(i),'content':'exact'} for i in range(11)]},'project':self.project,'publication_plan':{'issues':[]},'policy':{'rules':[]},'verifier':'synthetic guard checker, not native execution'}
        baseline={}
        for key,value in values.items():
            path=self.base/(key+'.json');path.write_text(value if isinstance(value,str) else json.dumps(value));baseline[key]={'path':path.name,'sha256':v.sha(path.read_bytes())}
        report={'result':'PASS','errors':[],'counts':copy.deepcopy(v.REQUIRED_COUNTS),'input_pins':{target:{'sha256':baseline[key]['sha256']} for key,target in [('issues','after_issues'),('documents','after_docs'),('project','after_project'),('publication_plan','plan')]},'normalization_policy_pin':{'sha256':baseline['policy']['sha256']},'verifier_sha256':baseline['verifier']['sha256']}
        path=self.base/'report.json';path.write_text(json.dumps(report));baseline['report']={'path':path.name,'sha256':v.sha(path.read_bytes())}
        self.plan={'kind':v.KIND,'overview_id':v.OVERVIEW_ID,'marker':self.marker,'append':self.append,'baseline':baseline,'allowed_suffix_normalization':None}
        self.after=copy.deepcopy(self.before);self.after['content']+=self.append;self.after['updatedAt']='new';self.after_project=copy.deepcopy(self.project)
        self.after_project['resources'][0]['updatedAt']=self.after['updatedAt']

    def check(self,plan=None,overview=None,project=None):return v.verify(plan or self.plan,self.base,overview or self.after,project or self.after_project)
    def has(self,r,code):self.assertEqual(r['result'],'FAIL');self.assertIn(code,[e['code'] for e in r['errors']])

    def test_exact_positive_and_only_explicit_observed_final_lf(self):
        self.assertEqual(self.check()['result'],'PASS')
        overview={'content':[{'type':'text','text':json.dumps(self.after)}]};project={'content':[{'type':'text','text':json.dumps(self.after_project)}]};self.assertEqual(self.check(overview=overview,project=project)['result'],'PASS')
        after=copy.deepcopy(self.after);after['content']=after['content'][:-1];self.has(self.check(overview=after),'EXACT_DECLARED_V2_APPEND_MISMATCH')
        evidence=self.base/'observed-final-lf.json';evidence.write_text('{"actual_observation":"one final LF removed"}')
        plan=copy.deepcopy(self.plan);plan['allowed_suffix_normalization']={'name':'remove_single_final_lf','actual_observation_pin':{'path':evidence.name,'sha256':v.sha(evidence.read_bytes())}}
        self.assertEqual(self.check(plan=plan,overview=after)['result'],'PASS')
        plan['allowed_suffix_normalization']['name']='strip_all_whitespace'
        with self.assertRaises(ValueError):self.check(plan=plan)

    def test_prefix_word_number_and_duplicate_marker_damage_fails(self):
        for altered,code in [('Changed frozen v1 content\n'+self.append,'V1_OVERVIEW_PREFIX_CHANGED'),(self.before['content']+self.append.replace('unrun','passed'),'EXACT_DECLARED_V2_APPEND_MISMATCH'),(self.before['content']+self.append+'\n'+self.marker,'V2_MARKER_COUNT')]:
            after=copy.deepcopy(self.after);after['content']=altered;self.has(self.check(overview=after),code)
        after=copy.deepcopy(self.after);after['content']=after['content'].replace('v2 -->','v3 -->');self.has(self.check(overview=after),'V2_MARKER_COUNT')

    def test_overview_and_same_count_project_resource_or_milestone_damage_fails(self):
        after=copy.deepcopy(self.after);after['title']='silently renamed';self.has(self.check(overview=after),'OVERVIEW_METADATA_CHANGED')
        project=copy.deepcopy(self.after_project);project['resources'][1]['id']='same-count-substitution';self.has(self.check(project=project),'PROJECT_RESOURCE_SCOPE_CHANGED')
        project=copy.deepcopy(self.project);project['milestones'][0]['targetDate']='tomorrow';self.has(self.check(project=project),'PROJECT_MILESTONE_MEMBER_CHANGED')
        project=copy.deepcopy(self.project);project['description']+=' hidden change';self.has(self.check(project=project),'PROJECT_METADATA_OR_DESCRIPTION_CHANGED')
        project=copy.deepcopy(self.after_project);project['resources'][0]['updatedAt']='unmatched';self.has(self.check(project=project),'OVERVIEW_RESOURCE_TIMESTAMP_PROJECTION_MISMATCH')
        project=copy.deepcopy(self.after_project);project['resources'][1]['updatedAt']='unrelated document update';self.has(self.check(project=project),'PROJECT_RESOURCE_MEMBER_CHANGED')
        project=copy.deepcopy(self.after_project);project['resources'].reverse();project['milestones'].reverse();self.assertEqual(self.check(project=project)['result'],'PASS')

    def test_frozen_v1_pin_or_false_pass_counts_cannot_be_rewritten(self):
        p=self.base/'report.json';report=json.loads(p.read_text());report['result']='FAIL';p.write_text(json.dumps(report))
        with self.assertRaises(ValueError):self.check()
        plan=copy.deepcopy(self.plan);plan['baseline']['report']['sha256']=v.sha(p.read_bytes());self.has(self.check(plan=plan),'V1_ACTUAL_PASS_REQUIRED')
        report['result']='PASS';report['counts']['original_scenarios']=1327;p.write_text(json.dumps(report));plan['baseline']['report']['sha256']=v.sha(p.read_bytes());self.has(self.check(plan=plan),'V1_COUNT_MISMATCH')
        report['counts']['original_scenarios']=1328;report['input_pins']['after_issues']['sha256']='0'*64;p.write_text(json.dumps(report));plan['baseline']['report']['sha256']=v.sha(p.read_bytes());self.has(self.check(plan=plan),'V1_REPORT_INPUT_PIN_MISMATCH')

    def test_wrong_target_broad_plan_or_failed_native_readback_fails_closed(self):
        for field,value in [('overview_id','other-document'),('kind','other product')]:
            plan=copy.deepcopy(self.plan);plan[field]=value
            with self.assertRaises(ValueError):self.check(plan=plan)
        plan=copy.deepcopy(self.plan);plan['ignored_extra']='hidden instruction'
        with self.assertRaises(ValueError):self.check(plan=plan)
        with self.assertRaises(ValueError):self.check(overview={'isError':True,'content':[]})
        plan=copy.deepcopy(self.plan);plan['baseline']['issues']['path']='/tmp/unrelated.json'
        with self.assertRaises(ValueError):self.check(plan=plan)

if __name__=='__main__':unittest.main(verbosity=2)
