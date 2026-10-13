#!/usr/bin/env python3
"""Deliberate-corruption guards using real preserved planning/native inputs."""
import copy
import csv
import json
import unittest
from pathlib import Path
import verify_refinement_publication as v

BASE=Path(__file__).resolve().parent.parent
REPO=BASE.parents[1]/'work/impact-platform-linear-planning'

class PublicationGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bi=v.read_json(BASE/'native-before/full-issues.json')
        cls.bd=v.read_json(BASE/'native-before/full-documents.json')
        cls.bp=v.read_json(BASE/'native-before/project.json')
        cls.plan=v.read_json(BASE/'native-publication-plan.json')
        with (REPO/'docs/backlog/backlog.csv').open(newline='') as f:
            cls.gh={r['ID']:r['Acceptance and rejection criteria (Gherkin)'] for r in csv.DictReader(f) if r['Status']!='Split'}
        cls.ai=copy.deepcopy(cls.bi);idx={i['id']:i for i in cls.ai['issues']}
        for p in cls.plan['issues']:idx[p['id']]['description']+=p['append']
        cls.ad=copy.deepcopy(cls.bd);di={d['id']:d for d in cls.ad}
        for p in cls.plan['documents']:di[p['id']]['content']+=p['append']
        cls.newid='11111111-1111-4111-8111-111111111111'
        cls.ad.append({'id':cls.newid,'title':cls.plan['overview']['title'],'content':cls.plan['overview']['content'],'archivedAt':None})
        cls.ap=copy.deepcopy(cls.bp);cls.ap['description']+=cls.plan['project_append']
        mi={m['id']:m for m in cls.ap['milestones']}
        for p in cls.plan['milestones']:mi[p['id']]['description']+=p['append']
        cls.ap['resources'].append({'id':cls.newid,'title':cls.plan['overview']['title'],'type':'document'})
        cls.ap['resourceCount']+=1

    def run_case(self,ai=None,ad=None,ap=None,policy=None):
        return v.verify(self.bi,ai or self.ai,self.plan,self.bd,ad or self.ad,self.bp,ap or self.ap,self.gh,policy)

    def assert_fails(self,result,code):
        self.assertEqual(result['result'],'FAIL');self.assertIn(code,[x['code'] for x in result['errors']])

    def test_exact_complete_positive(self):
        result=self.run_case();self.assertEqual(result['result'],'PASS',result['errors'][:5])
        self.assertEqual(result['counts']['original_scenarios'],1328)
        self.assertEqual(result['counts']['task_blocked_by_edges_after'],779)

    def test_source_gherkin_corruption_cannot_be_hidden_by_repeating_it_later(self):
        ai=copy.deepcopy(self.ai);i=next(i for i in ai['issues'] if v.CANONICAL.match(i['description'])[1]=='story')
        cid=v.CANONICAL.match(i['description'])[2];original=self.gh[cid]
        i['description']=i['description'].replace(original,original.replace('Then ','Then not ',1),1)+'\n\n```gherkin\n'+original+'\n```'
        result=self.run_case(ai=ai);self.assert_fails(result,'ORIGINAL_GHERKIN_CHANGED');self.assert_fails(result,'ORIGINAL_PREFIX_CHANGED')

    def test_metadata_changes_or_disappearing_fields_cannot_pass(self):
        for field,value in [('status','Done'),('parentId','APL-0'),('estimate',999),('cycle',{'id':'unauthorised-cycle'}),('assignee',{'id':'unauthorised-person'}),('labels',['Imprana Technical task','silently changed'])]:
            with self.subTest(field=field):
                ai=copy.deepcopy(self.ai);ai['issues'][0][field]=value
                self.assert_fails(self.run_case(ai=ai),'METADATA_CHANGED')

    def test_same_count_dependency_substitution_cannot_pass(self):
        ai=copy.deepcopy(self.ai);i=next(i for i in ai['issues'] if i['relations']['blockedBy'])
        i['relations']['blockedBy'][0]['id']='APL-0'
        result=self.run_case(ai=ai);self.assert_fails(result,'METADATA_CHANGED')
        self.assertEqual(result['counts']['task_blocked_by_edges_after'],779)

    def test_missing_append_history_or_milestone_damage_cannot_pass(self):
        ai=copy.deepcopy(self.ai);iid=self.plan['issues'][0]['id'];bi={i['id']:i for i in self.bi['issues']}
        next(i for i in ai['issues'] if i['id']==iid)['description']=bi[iid]['description']
        self.assert_fails(self.run_case(ai=ai),'APPEND_CONTENT_MISMATCH')
        ad=copy.deepcopy(self.ad);h=next(d for d in ad if d['id']=='37cd9321-6f7d-4df8-973d-557a199de68b');h['content']+='\nreplaced historical approval'
        self.assert_fails(self.run_case(ad=ad),'PROTECTED_HISTORY_DOCUMENT_CHANGED')
        ap=copy.deepcopy(self.ap);ap['milestones'][0]['targetDate']='2026-10-12'
        self.assert_fails(self.run_case(ap=ap),'METADATA_CHANGED')

    def test_known_platform_formatting_is_explicit_and_never_hides_substantive_change(self):
        ai=copy.deepcopy(self.ai);p=self.plan['issues'][0];i=next(i for i in ai['issues'] if i['id']==p['id'])
        before={i['id']:i for i in self.bi['issues']}[p['id']]['description']
        suffix=v.apply_known_transform(v.apply_known_transform(p['append'],'publication_comment_heading_blankline'),'remove_single_final_lf')
        i['description']=before+suffix
        self.assert_fails(self.run_case(ai=ai),'APPEND_CONTENT_MISMATCH')
        policy={'rules':[{'kind':'issues','ids':[p['id']],'transform':t,'evidence':'Synthetic guard for observed exact Linear marker/heading and final-LF change'} for t in ['publication_comment_heading_blankline','remove_single_final_lf']]}
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        i['description']=i['description'].replace('Planning recommendation','Planning  recommendation',1)
        self.assert_fails(self.run_case(ai=ai,policy=policy),'APPEND_CONTENT_MISMATCH')

    def test_one_observed_roadmap_table_rule_is_scoped_and_rejects_semantic_changes(self):
        did=v.ROADMAP_DOCUMENT;p=next(d for d in self.plan['documents'] if d['id']==did)
        bd=next(d for d in self.bd if d['id']==did)
        original='| --- | ---: | --- | --- |';observed='| -- | -- | -- | -- |'
        self.assertEqual(p['append'].splitlines().count(original),1)
        policy={'rules':[{'kind':'documents','ids':[did],'transform':t,'evidence':'Actual roadmap native readback, exactly one four-column alignment serialization'} for t in ['roadmap_exact_four_column_alignment_serialization','remove_single_final_lf']]}
        ad=copy.deepcopy(self.ad);row=next(d for d in ad if d['id']==did)
        row['content']=bd['content']+p['append'].replace(original,observed).removesuffix('\n')
        self.assert_fails(self.run_case(ad=ad),'APPEND_CONTENT_MISMATCH')
        self.assertEqual(self.run_case(ad=ad,policy=policy)['result'],'PASS')
        for old,new in [('368','369'),('proposed','approved')]:
            self.assertIn(old,p['append'])
            bad=copy.deepcopy(ad);d=next(d for d in bad if d['id']==did)
            d['content']=bd['content']+d['content'][len(bd['content']):].replace(old,new,1)
            self.assert_fails(self.run_case(ad=bad,policy=policy),'APPEND_CONTENT_MISMATCH')
        with self.assertRaises(ValueError):
            v.permitted_transforms({'rules':[{'kind':'issues','ids':['APL-279'],'transform':'roadmap_exact_four_column_alignment_serialization','evidence':'Invalid wider scope'}]},'issues','APL-279')
        with self.assertRaises(ValueError):v.apply_known_transform(original+'\n'+original+'\n','roadmap_exact_four_column_alignment_serialization')
        fence='```gherkin\n'+original+'\nThen 60 seconds\n```\n'
        self.assertEqual(v.apply_known_transform(fence,'roadmap_exact_four_column_alignment_serialization'),fence)
        self.assertEqual(v.apply_known_transform('| --- | ---: | --- |\n','roadmap_exact_four_column_alignment_serialization'),'| --- | ---: | --- |\n')

    def test_actual_six_new_suffix_observations_do_not_allow_semantic_or_scope_changes(self):
        policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json')
        ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        for partition,cids in [('partition-0-400',['FR-ACC-007','FR-AI-002','FR-AI-004']),('partition-1200-1553',['TASK-NFR-08-01','TASK-NFR-08-02','TASK-NFR-08-03'])]:
            for cid in cids:
                raw=v.read_json(BASE/'native-after'/partition/(cid+'.json'))
                if 'description' in raw:actual=raw
                else:actual=next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']))
                idx[actual['id']].update(actual)
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        for iid,old,new in [('APL-545','classify existing plan enrichment separately','approve existing plan enrichment separately'),('APL-531','TASK-FR-AI-002-03','TASK-FR-AI-002-04'),('APL-1832','AC-NFR-08-004','AC-NFR-08-005')]:
            bad=copy.deepcopy(ai);item=next(i for i in bad['issues'] if i['id']==iid);before=next(i for i in self.bi['issues'] if i['id']==iid)['description']
            suffix=item['description'][len(before):];self.assertIn(old,suffix);item['description']=before+suffix.replace(old,new,1)
            self.assert_fails(self.run_case(ai=bad,policy=policy),'APPEND_CONTENT_MISMATCH')
        for name in ['observed_three_supplement_heading_code_serialization','observed_empty_nfr08_source_label_space']:
            with self.assertRaises(ValueError):v.permitted_transforms({'rules':[{'kind':'issues','ids':['APL-279'],'transform':name,'evidence':'Invalid widened scope'}]},'issues','APL-279')
        for name,line in [('observed_three_supplement_heading_code_serialization',next(iter(v.FIXED_HEADING_SERIALIZATIONS))),('observed_empty_nfr08_source_label_space',v.EMPTY_NFR08_SOURCE_LINE)]:
            fence='```gherkin\n'+line+'\nThen 60 seconds\n```\n';self.assertEqual(v.apply_known_transform(fence,name),fence)
            with self.assertRaises(ValueError):v.apply_known_transform(line+'\n'+line+'\n',name)
        self.assertEqual(v.apply_known_transform(v.EMPTY_NFR08_SOURCE_LINE+'actual requirement \n','observed_empty_nfr08_source_label_space'),v.EMPTY_NFR08_SOURCE_LINE+'actual requirement \n')

    def test_all_185_observed_empty_source_labels_and_two_dq_cases_remain_strict(self):
        receipt=v.read_json(BASE/'verification-author/ACTUAL-185-EMPTY-LABEL-OBSERVATIONS-REVIEW.json')
        self.assertEqual(receipt['result'],'PASS');self.assertEqual(receipt['count'],185)
        policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json');ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        paths=[Path(x['native_raw_path']) for x in receipt['items']]+[BASE/'native-after/partition-0-400'/(cid+'.json') for cid in ['FR-DQ-001','FR-DQ-005']]
        for f in paths:
            raw=v.read_json(f);actual=raw if 'description' in raw else next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']));idx[actual['id']].update(actual)
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        for iid,old,new in [('APL-628','TASK-FR-DQ-001-03','TASK-FR-DQ-001-04'),('APL-633','classify existing plan enrichment separately','approve existing plan enrichment separately')]:
            bad=copy.deepcopy(ai);item=next(i for i in bad['issues'] if i['id']==iid);before=next(i for i in self.bi['issues'] if i['id']==iid)['description'];suffix=item['description'][len(before):];self.assertIn(old,suffix);item['description']=before+suffix.replace(old,new,1);self.assert_fails(self.run_case(ai=bad,policy=policy),'APPEND_CONTENT_MISMATCH')
        line=next(iter(v.OBSERVED_EMPTY_SOURCE_LINES));name='observed_exact_empty_source_label_space'
        self.assertEqual(v.apply_known_transform(line+'\n',name),line[:-1]+'\n')
        for altered in [line.replace('Original requirement','Original  requirement'),line+'explicit new requirement ',line.replace('bounded contribution','approved contribution')]:self.assertEqual(v.apply_known_transform(altered+'\n',name),altered+'\n')
        self.assertEqual(v.apply_known_transform('```gherkin\n'+line+'\n```\n',name),'```gherkin\n'+line+'\n```\n')
        with self.assertRaises(ValueError):v.permitted_transforms({'rules':[{'kind':'issues','ids':['APL-0'],'transform':name,'evidence':'Unobserved source ID'}]},'issues','APL-0')
        two=list(v.OBSERVED_EMPTY_SOURCE_LINES)[:2]
        with self.assertRaises(ValueError):v.apply_known_transform('\n'.join(two)+'\n',name)

    def test_additional13_exact_task_lines_and_two_actual_heading_cases(self):
        receipt=v.read_json(BASE/'verification-author/ACTUAL-13-EMPTY-LABEL-AND-TWO-HEADINGS-REVIEW.json');self.assertEqual(len(receipt['tasks']),13);self.assertEqual(len(receipt['headings']),2)
        policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json');ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        for item in receipt['tasks']+receipt['headings']:
            raw=v.read_json(item['raw_path']);actual=raw if 'description' in raw else next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']));idx[actual['id']].update(actual)
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        for item in [receipt['tasks'][0],receipt['tasks'][4],receipt['headings'][0]]:
            bad=copy.deepcopy(ai);i=next(i for i in bad['issues'] if i['id']==item['id']);before=next(i for i in self.bi['issues'] if i['id']==item['id'])['description'];suffix=i['description'][len(before):]
            old='Original requirement:' if item in receipt['tasks'] else 'Proposed verification duty';self.assertIn(old,suffix);i['description']=before+suffix.replace(old,old+' unauthorised',1)
            self.assert_fails(self.run_case(ai=bad,policy=policy),'APPEND_CONTENT_MISMATCH')

    def test_current_actual_duty_heading_readbacks_and_tampering_controls(self):
        receipt=v.read_json(BASE/'verification-author/CURRENT-DUTY-HEADING-OBSERVATIONS.json');self.assertEqual(receipt['result'],'PASS')
        policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json');ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        for item in receipt['items']:
            raw=v.read_json(item['native_path']);actual=raw if 'description' in raw else next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']));idx[actual['id']].update(actual)
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        for item in receipt['items']:
            old=item['exact_old_line'];fence='```gherkin\n'+old+'\n```\n';self.assertEqual(v.apply_known_transform(fence,'observed_fixed_supplement_heading_code_serialization'),fence)
        item=receipt['items'][-1];bad=copy.deepcopy(ai);row=next(i for i in bad['issues'] if i['id']==item['id']);before=next(i for i in self.bi['issues'] if i['id']==item['id'])['description'];suffix=row['description'][len(before):];new=item['exact_new_line'];self.assertIn(new,suffix);row['description']=before+suffix.replace(new,new.replace('-03`','-04`'),1);self.assert_fails(self.run_case(ai=bad,policy=policy),'APPEND_CONTENT_MISMATCH')
        for pending in receipt['pending']:self.assertNotIn(pending['id'],v.OBSERVED_FIXED_HEADING_IDS)

    def test_actual_ux004_classification_code_heading_and_semantic_rejection(self):
        receipt=v.read_json(BASE/'verification-author/ACTUAL-UX004-HEADING-REVIEW.json');self.assertEqual(receipt['result'],'PASS')
        raw=v.read_json(receipt['raw_path']);actual=raw if 'description' in raw else next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']));ai=copy.deepcopy(self.ai);row=next(i for i in ai['issues'] if i['id']==receipt['id']);row.update(actual);policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json');self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        before=next(i for i in self.bi['issues'] if i['id']==receipt['id'])['description'];suffix=row['description'][len(before):];row['description']=before+suffix.replace('AC-FR-UX-004-001','AC-FR-UX-004-999',1);self.assert_fails(self.run_case(ai=ai,policy=policy),'APPEND_CONTENT_MISMATCH')

    def test_explicit_fresh_document_collection_wrapper_preserves_records(self):
        self.assertEqual(self.run_case(ad={'documents':copy.deepcopy(self.ad)})['result'],'PASS')
        for invalid in [{'documents':'not full records'},{'items':self.ad},{'documents':self.ad,'ignored_extra':'unsupported container'}]:
            with self.assertRaises(ValueError):self.run_case(ad=invalid)
        bad=copy.deepcopy(self.ad);bad[0]['content']='changed old prefix'+bad[0]['content'];self.assert_fails(self.run_case(ad={'documents':bad}),'ORIGINAL_PREFIX_CHANGED')

    def test_final_actual_classification_headings_reject_words_numbers_and_fences(self):
        receipt=v.read_json(BASE/'verification-author/ACTUAL-FINAL-CLASSIFICATION-HEADINGS-REVIEW.json');self.assertEqual(receipt['result'],'PASS');self.assertEqual(len(receipt['items']),3)
        policy=v.read_json(BASE/'verification-author/DECLARED-ALL-OBJECT-FORMATTING-POLICY.json');ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        for item in receipt['items']:
            raw=v.read_json(item['raw_path']);actual=raw if 'description' in raw else next(json.loads(c['text']) for c in raw['content'] if c.get('type')=='text' and 'description' in json.loads(c['text']));idx[item['id']].update(actual)
            literal=item['exact_old_line'];fenced='```gherkin\n'+literal+'\n```\n';self.assertEqual(v.apply_known_transform(fenced,'observed_fixed_supplement_heading_code_serialization'),fenced)
            with self.assertRaises(ValueError):v.apply_known_transform(literal+'\n'+literal+'\n','observed_fixed_supplement_heading_code_serialization')
        self.assertEqual(self.run_case(ai=ai,policy=policy)['result'],'PASS')
        for item in receipt['items']:
            for old,new in [('classify','approve'),('-001','-999'),('-002','-999')]:
                bad=copy.deepcopy(ai);row=next(i for i in bad['issues'] if i['id']==item['id']);before=next(i for i in self.bi['issues'] if i['id']==item['id'])['description'];suffix=row['description'][len(before):]
                if old not in item['exact_new_line']:continue
                row['description']=before+suffix.replace(item['exact_new_line'],item['exact_new_line'].replace(old,new),1);self.assert_fails(self.run_case(ai=bad,policy=policy),'APPEND_CONTENT_MISMATCH')

    def test_planned_document_resource_timestamp_projection_is_bound_to_full_document(self):
        did=self.plan['documents'][0]['id'];ad=copy.deepcopy(self.ad);ap=copy.deepcopy(self.ap)
        doc=next(d for d in ad if d['id']==did);resource=next(r for r in ap['resources'] if r['id']==did);doc['updatedAt']='actual-new-time';resource['updatedAt']='actual-new-time'
        self.assertEqual(self.run_case(ad=ad,ap=ap)['result'],'PASS')
        resource['updatedAt']='arbitrary-unmatched-time';self.assert_fails(self.run_case(ad=ad,ap=ap),'PROJECT_DOCUMENT_TIMESTAMP_PROJECTION_MISMATCH')
        resource['updatedAt']=doc['updatedAt'];resource['title']='same-count renamed document';self.assert_fails(self.run_case(ad=ad,ap=ap),'EXISTING_PROJECT_RESOURCE_CHANGED')
        ap=copy.deepcopy(self.ap);old=next(r for r in ap['resources'] if r['id']=='37cd9321-6f7d-4df8-973d-557a199de68b');old['updatedAt']='changed historical timestamp';self.assert_fails(self.run_case(ap=ap),'EXISTING_PROJECT_RESOURCE_CHANGED')
        ap=copy.deepcopy(self.ap);link=next(r for r in ap['resources'] if r['id'] not in {d['id'] for d in self.ad});link['updatedAt']='invented link timestamp';self.assert_fails(self.run_case(ap=ap),'EXISTING_PROJECT_RESOURCE_CHANGED')

    def test_actual_three_readbacks_match_only_the_declared_supplement_syntax(self):
        actual=v.read_json(BASE/'native-after/initial-observed-readbacks.json')['issues']
        ai=copy.deepcopy(self.ai);idx={i['id']:i for i in ai['issues']}
        for i in actual:idx[i['id']].update(i)
        transforms=['publication_comment_heading_blankline','outside_fence_blankline_collapse','table_separator_three_to_two_dashes','table_trailing_cell_two_to_one_spaces','specific_missing_context_bracket_escape','leading_bold_code_emdash_heading','remove_single_final_lf']
        policy={'rules':[{'kind':'issues','ids':[i['id'] for i in actual],'transform':t,'evidence':'Actual initial-observed-readbacks.json for APL-279, APL-348 and APL-1016'} for t in transforms]}
        result=self.run_case(ai=ai,policy=policy);self.assertEqual(result['result'],'PASS',result['errors'][:5])
        changed=next(i for i in ai['issues'] if i['id']=='APL-348')
        for old,new in [('tenant A','tenant B'),('within 60 seconds','within 600 seconds')]:
            if old not in changed['description']:continue
            clone=copy.deepcopy(ai);item=next(i for i in clone['issues'] if i['id']=='APL-348');item['description']=item['description'].replace(old,new,1)
            self.assertEqual(self.run_case(ai=clone,policy=policy)['result'],'FAIL')
        fence='```gherkin\n<!-- imprana:bundle-v4.2:story:FAKE:20261011 -->\n### Literal source\n\n\nThen 60 is not 600\n```\n'
        for name in transforms[:-1]:self.assertEqual(v.apply_known_transform(fence,name),fence)

if __name__=='__main__':unittest.main(verbosity=2)
