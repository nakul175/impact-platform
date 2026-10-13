#!/usr/bin/env python3
"""Independent saved-document/source review. No product/package tests or Native writes."""
import ast, collections, copy, datetime, hashlib, importlib.util, json, pathlib, re, subprocess, sys
sys.dont_write_bytecode = True
ROOT=pathlib.Path(__file__).resolve().parents[3]
REPO=ROOT/'work/imprana-framework-refinement-20261011'
OUT=ROOT/'outputs/imprana-standards-completion-20261011'
OWN=pathlib.Path(__file__).parent
PM=REPO/'docs/product/framework-v4-20261011/standards-completion'
QA=REPO/'docs/qa/standards-completion-20261011'
BASE='4472cc845b62c32ffd074d2afee49b5d32f98879'
PROJECT='2de29065-7bb5-46ca-9b8c-4c4ef66cc046'
checks=[]; pins={}; observations=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def textsha(v):return hashlib.sha256(v.encode()).hexdigest()
def load(p):
 pins[str(p.relative_to(ROOT))]={'sha256':sha(p),'bytes':p.stat().st_size}
 return json.loads(p.read_text())
def txt(p):
 pins[str(p.relative_to(ROOT))]={'sha256':sha(p),'bytes':p.stat().st_size}
 return p.read_text()
def check(n,ok,e=None):checks.append({'id':n,'passed':bool(ok),'evidence':e})
source=txt(OUT/'review_native_publication.py')
parsed=ast.parse(source)
spec=importlib.util.spec_from_file_location('read_only_native_compare',OUT/'review_native_publication.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
canonical=module.canonical
# Pure source comparison only: no corruption guard fixtures executed in this review.
canon_node=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='canonical')
canon_source=ast.get_source_segment(source,canon_node)
check('canonical_cosmetics_are_declared_and_literal_code_is_excluded', all(s in canon_source for s in ['if fence is None:', 'pieces = re.split', 'for index in range(0, len(pieces), 2)', 'code_source|evidence_artifact', 'https?', '.rstrip("\\n")']) and 'autolink' not in canon_source, {'observed_rules':'table delimiter spacing/dash lengths; unordered dash/star bullets; angle destinations around same HTTP URL; two explicit escaped labels; terminal LF only. Fenced/inline code excluded. No plain identifier generated-autolink removal.'})
guard_names=[n.slice.value for n in ast.walk(parsed) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='guards' and isinstance(n.slice,ast.Constant)]
main_ast=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='main')
guard_names+= [n.value for n in ast.walk(main_ast) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.endswith('_rejected')]
check('negative_guard_source_contains_13_declared_checks',len(set(guard_names))==13,{'guard_names':sorted(set(guard_names)),'execution':'Inspected direct-key and loop-tuple AST/source; not rerun under no-tests instruction.'})
check('native_comparer_has_full_prefix_marker_complete_append_and_named_field_guards', all(s in source for s in ['actual.startswith(old["description"])','canonical(actual) != canonical(expected)','actual.count("<!-- imprana:qa-v1.3:case-design:20261011 -->") != 1','old.get(field, sentinel) != new.get(field, sentinel)','set(original) != set(current)','duplicate issue identity','unselected description changed']),module.PROTECTED)

manifest=load(PM/'RECORD-MANIFEST.json'); rows=manifest['records']
records={x['id']:load(PM/x['path']) for x in rows}
artifact=load(PM/'ARTIFACT-MANIFEST.json')
epics={x['canonical_id']:x for x in load(REPO/'docs/product/framework-v4-20261011/epic-story-author/EPIC-REFINEMENT.json')}
stories={x['canonical_id']:x for x in load(REPO/'docs/product/framework-v4-20261011/epic-story-author/STORY-REFINEMENT.json')}
adapter=load(ROOT/'outputs/imprana-product-refinement-20261011/bundle-review/ROOT-REVIEWED-PLANNING-ADAPTER-V4.json')
elements={x['id']:x for x in adapter['elements']}
mapdoc=load(PM/'ELEMENT-ASSURANCE-MAP.json'); maps={x['element_id']:x for x in mapdoc['elements']}
requests=load(PM/'REVIEW-REQUEST-CONTRACTS.json')
sourcepins=load(PM/'SOURCE-PINS.json')
check('all55_original_scope_and_record_identities_exact',len(rows)==len(records)==55 and {x['scope_id'] for x in rows}==set(epics)|{'IMPRANA-CROSS-CUTTING'} and len(stories)==368)
record_errors=[];scope_errors=[];trust_errors=[]
for row in rows:
 d=records[row['id']];scope=d['planningScope']; rr=copy.deepcopy(d);rr['record']['contentHash']=None
 if sha(PM/row['path'])!=row['file_sha256'] or digest(rr)!=row['content_hash'] or d['record']['contentHash']!=row['content_hash'] or d['record']['id']!=row['id'] or d['record']['version']!=row['version']:record_errors.append(row['id'])
 if scope['scope_id']!='IMPRANA-CROSS-CUTTING':
  e=epics[scope['scope_id']]
  pairs={'included_story_ids':'included_story_ids','source_problem':'problem','proposed_outcome':'capability_outcome','source_contract':'shared_contract','excluded_scope':'excluded_scope_and_handoffs','risk_hypothesis':'riskiest_assumption','release_allocation':'release_allocation'}
  if any(scope[k]!=e[v] for k,v in pairs.items()) or any(stories[s]['epic_id']!=e['canonical_id'] for s in scope['included_story_ids']):scope_errors.append(row['id'])
 elif len(scope['included_story_ids'])!=368 or set(scope['included_story_ids'])!=set(stories):scope_errors.append(row['id'])
 if len(d['assuranceGroups'])!=7 or {g['id'] for g in d['assuranceGroups']}!={'AI-01','AI-02','AI-03','AI-04','AI-05','AI-06','AI-07'} or any(g['status']!='needs_input' or g['reviewReference'] is not None or g['assessedStage'] is not None for g in d['assuranceGroups']):trust_errors.append(row['id'])
 if d['externalReviewAndApprovalBoundary']!={'mode':'offline_advisory','trustedRegistryOrReviewServiceReference':None,'externalTrustAnchorEvidence':[],'approvalEvidence':[]} or d['record']['authorAuthoritySourceIds']:trust_errors.append(row['id'])
check('55_frozen_record_file_and_canonical_content_hashes_exact',not record_errors,record_errors)
check('every_scope_story_problem_contract_hypothesis_boundary_and_release_allocation_exact',not scope_errors,scope_errors)
check('all385_groups_needs_input_unassessed_zero_review_or_trust',not trust_errors,{'errors':trust_errors,'groups':sum(len(d['assuranceGroups']) for d in records.values())})
check('all24_original_inputs_and62_pm_members_unchanged',len(sourcepins['files'])==24 and all(sha(ROOT/x['path'])==x['sha256'] and (ROOT/x['path']).stat().st_size==x['bytes'] for x in sourcepins['files']) and len(artifact['files'])==62 and all(sha(PM/x['path'])==x['sha256'] and (PM/x['path']).stat().st_size==x['bytes'] for x in artifact['files']))
maperrors=[]
for k,e in elements.items():
 m=maps.get(k)
 if m is None or m['element_type']!=e['elementType'] or m['parent_id']!=e['parentId'] or m['source_ids']!=e['sourceIds'] or m['source_element_sha256']!=digest(e) or m['dependency_ids']!=e['dependencyIds'] or m['design_dependency_ids']!=e['designDependencyIds'] or m['source_pins']!={s:adapter['sourcePins'][s] for s in e['sourceIds']}:maperrors.append(k)
check('all2893_full_source_content_source_ids_parents_and_edges_preserved',len(elements)==len(maps)==2893 and set(elements)==set(maps) and not maperrors and sum(len(x['dependency_ids']) for x in maps.values())==779 and sum(len(x['design_dependency_ids']) for x in maps.values())==5508,{'errors':maperrors,'type_counts':dict(collections.Counter(e['elementType'] for e in elements.values()))})
releaseids={k for k,e in elements.items() if e['elementType']=='release_goal'}
check('original_story_release_goal_ids_exist_in_preserved_canonical_hierarchy',len(releaseids)==5 and all(x['release_goal_id'] in releaseids for x in stories.values()),sorted(releaseids))
check('56_requests20251_obligations_are_zero_actual_reviews',requests['definition_count']==len(requests['contracts'])==56 and requests['expanded_planning_gate_obligations']==sum(c['applicable_element_count'] for c in requests['contracts'])==20251 and requests['actual_reviews_created']==0 and all(c['status']=='requested evidence/independent review, not performed' for c in requests['contracts']))

summary=txt(REPO/'docs/product/framework-v4-20261011/PM-SCOPE-SUMMARIES-20261011.md')
intro=summary.split('\n## ',1)[0]
sections={m.group(1):m.group(0) for m in re.finditer(r'\n## ([^\n]+)\n(?:(?!\n## ).)*',summary,re.S)}
summaryerrors=[]
for row in rows:
 d=records[row['id']];scope=d['planningScope'];s='\n## '+row['scope_id']+'\n\nRecord: `'+row['id']+'`, draft version `'+row['version']+'`; exact file SHA-256 `'+row['file_sha256']+'`. Status: needs_input across all seven groups.\n'
 values=[('Source stories',', '.join(scope['included_story_ids'])),('Source problem',scope.get('source_problem',{}).get('text','Not established in this draft')),('Proposed outcome',scope.get('proposed_outcome','Not established')),('Source contract',scope.get('source_contract','Not established')),('Boundary/excluded scope',scope.get('excluded_scope','Not established'))]
 for label,value in values:s+='\n**'+label+':** '+value+'\n'
 for key,label in [('hypothesis','Proposed highest-consequence hypothesis'),('counter_hypothesis','Counter-hypothesis'),('method','Proposed learning method'),('decision_rule','Proposed decision rule'),('threshold_and_window','Threshold/window decision boundary')]:
  if scope.get('risk_hypothesis',{}).get(key):s+='\n**'+label+':** '+scope['risk_hypothesis'][key]+'\n'
 s+='\n**Existing source release allocation:** `'+json.dumps(scope.get('release_allocation',{}),sort_keys=True)+'`. Allocation is not an actual commitment.\n'
 s+='\n**Required actual review groups:** '+'; '.join(g['id']+' '+g['title']+' (needs_input)' for g in d['assuranceGroups'])+'\n'
 if sections.get(row['scope_id'])!=s:summaryerrors.append(row['scope_id'])
check('all55_readable_summary_sections_reconstruct_exactly_from_frozen_records',len(sections)==55 and set(sections)=={x['scope_id'] for x in rows} and not summaryerrors,summaryerrors)
check('summary_intro_is_proposal_no_research_owner_or_runtime_approval',all(s in intro for s in ['Source requirement synthesis is not observed research','All seven assurance groups on every record remain needs_input','actual reviews and trust are absent','no provider/data/owner/runtime decision is invented','Scope is only Imprana Commons','GitHub export remains pending']))

qa_plan=load(OUT/'native-qa-plan.json'); qa_after=load(OUT/'native-qa-save-readbacks.json')['results']
entry_plan=load(OUT/'native-integrated-doc-plan.json');entry_after=load(OUT/'native-integrated-doc-save-readbacks.json')
scoped_plan=load(OUT/'native-scoped-pm-plans.json');scoped_after=load(OUT/'native-scoped-pm-readbacks.json')
initial_doc_errors=[];document_rows=[]
for plan,after,titlekey,actualkey in [(qa_plan,qa_after,'title','content'),(entry_plan,entry_after,'title','actual'),(scoped_plan,scoped_after,'title','actual')]:
 for i,(expected,actual) in enumerate(zip(plan,after)):
  if expected['title']!=actual['title'] or canonical(expected['content'])!=canonical(actual[actualkey]) or actual['projectId']!=PROJECT:initial_doc_errors.append(actual['id'])
  document_rows.append({'id':actual['id'],'title':actual['title'],'expected_sha256':textsha(expected['content']),'actual_sha256':textsha(actual[actualkey]),'project_id':actual['projectId']})
check('ten_unique_initial_native_full_document_readbacks_match_source_plans',len(qa_plan)==len(qa_after)==5 and len(entry_plan)==len(entry_after)==2 and len(scoped_plan)==len(scoped_after)==3 and len({d['id'] for d in document_rows})==10 and not initial_doc_errors,{'errors':initial_doc_errors,'documents':document_rows})
native_sections={};dup=[]
for p in scoped_plan:
 found={m.group(1):m.group(0) for m in re.finditer(r'\n## ([^\n]+)\n(?:(?!\n## ).)*',p['content'],re.S)}
 for k,v in found.items():
  if k in native_sections:dup.append(k)
  native_sections[k]=v
check('three_native_scoped_documents_18_18_19_cover_all55_full_exact_sections', [p['recordCount'] for p in scoped_plan]==[18,18,19] and not dup and native_sections==sections,{'record_counts':[p['recordCount'] for p in scoped_plan],'duplicates':dup})
index=load(OUT/'native-pm-index-link-append.json');recon=load(OUT/'native-pm-index-link-append-reconciliation.json')
bef=index['before'];aft=index['after'];correct_expected=bef['content']+index['addition'];marker='<!-- imprana:pm-scoped-intakes:20261011 -->'
metadata_diff=[k for k in set(bef)|set(aft) if k not in {'content','updatedAt'} and bef.get(k,object())!=aft.get(k,object())]
check('pm_index_initial_false_composer_observation_retained_and_exact_native_baseline_reconciled',index['verified'] is False and recon['verified'] is True and aft['content'].startswith(bef['content']) and canonical(aft['content'])==canonical(correct_expected) and aft['content'].count(marker)==1 and not metadata_diff and recon['beforeId']==bef['id'],{'initial_verified':index['verified'],'original_prefix_byte_exact':aft['content'].startswith(bef['content']),'complete_append_normalized_equal':canonical(aft['content'])==canonical(correct_expected),'metadata_differences':metadata_diff,'qualification':recon['qualification'],'correct_expected_sha256':textsha(correct_expected),'actual_sha256':textsha(aft['content'])})
observations.append({'id':'PM_INDEX_FALSE_COMPOSER_HISTORY','disposition':'Retained genuine false observation; resolved only by composing actual pre-append Native baseline plus authorized appendix. No internal newline normalization waiver or prefix change.'})
check('pm_index_append_links_exact_three_scoped_native_documents',all(d['url'] in index['addition'] for d in scoped_after))
final_expected=load(OUT/'native-final-ten-document-expected.json');final_docs=load(OUT/'native-final-ten-document-fresh.json')
own_expected={a['id']:(p['content'],p['title']) for plans,afters in [(qa_plan,qa_after),(entry_plan,entry_after),(scoped_plan,scoped_after)] for p,a in zip(plans,afters)}
own_expected[bef['id']]=(correct_expected,bef['title'])
finaldocerrors=[]
for d in final_docs:
 if d['id'] not in own_expected or d['title']!=own_expected[d['id']][1] or d['projectId']!=PROJECT or canonical(d['actual'])!=canonical(own_expected[d['id']][0]):finaldocerrors.append(d['id'])
check('final_fresh_ten_complete_native_documents_match_independently_reconstructed_sources',len(final_docs)==len({d['id'] for d in final_docs})==10 and {d['id'] for d in final_docs}==set(own_expected) and not finaldocerrors,{'errors':finaldocerrors,'final_expected_plan_ids_match':{d['id'] for d in final_expected}==set(own_expected)})

coverage=load(QA/'proposed-registers/ACTUAL-COVERAGE-SUMMARY.json')
raw=load(OUT/'source/proposed-registers/structure.stdout.json');negative=load(OUT/'source/proposed-registers/negative-release-record.stdout.json')
fields=['planned_coverage','validated_coverage','required_completion','selected_pass_rate','unknown_applicability','selected_unique_runs','result_counts','freshness_counts']
check('actual3786_structure_and3794_release_diagnostics_preserved',len(raw['errors'])==coverage['structure_errors']==3786 and len(negative['errors'])==coverage['release_errors']==3794 and coverage['real_structure_exit']==coverage['real_release_record_exit']==1 and all(sha(ROOT/coverage[k]['path'])==coverage[k]['sha256'] for k in ['checker_stdout','negative_checker_stdout','unchanged_checker']))
check('planned1328_never_upgrades_validated_zero_runs_zero_unknown1328',all(coverage['actual_coverage_fields'][k]==raw[k]==negative[k] for k in fields) and raw['planned_coverage']=={'numerator':1328,'denominator':1328,'ratio':1.0} and raw['validated_coverage']=={'numerator':0,'denominator':1328,'ratio':0.0} and raw['required_completion']['numerator']==0 and raw['selected_unique_runs']==0 and raw['unknown_applicability']==1328 and raw['result_counts']['NOT_RUN']==1328 and raw['freshness_counts']['UNASSESSED']==1328 and coverage['accepted_bindings']==coverage['design_tests_executed']==0 and coverage['case_modes']=={'MANUAL':66,'AUTO':1262})

sourcefreeze=load(OUT/'source/SOURCE-FREEZE-RECEIPT.json')
proposedfreeze=load(OUT/'source/proposed-registers/FINAL-PROPOSED-REGISTER-FREEZE.json')
casefreeze=load(OUT/'cases/ACTUAL-CASE-DESIGN-VALIDATION.json')
freezeerrors=[]
for label,members,parent in [('source',sourcefreeze['files'],QA/'source-registers'),('proposed',proposedfreeze['actual_files'],ROOT),('cases',casefreeze['files_pinned'],ROOT)]:
 for member in members:
  path=pathlib.Path(member['path']);path=path if path.is_absolute() else parent/path
  if not path.is_file() or sha(path)!=member['sha256'] or ('bytes' in member and path.stat().st_size!=member['bytes']):freezeerrors.append({'group':label,'path':str(path)})
check('all25_source394_proposed375_case_frozen_artifacts_unchanged',not freezeerrors and len(sourcefreeze['files'])==25 and len(proposedfreeze['actual_files'])==394 and len(casefreeze['files_pinned'])==375,freezeerrors)

before=load(OUT/'native-full-target-before.json');fullplan=load(OUT/'native-story-full-plan.json')
fullafter=load(OUT/'native-final-full-targets.json'); combined=load(OUT/'native-final-combined.json')
backlog=load(OUT/'native-final-all-metadata.json')
appends=load(QA/'case-design/LINEAR-STORY-QA-APPENDS.json')
before_map={x['id']:x for x in before['issues']};before_targets={x['id']:x for x in before['targetFullRows']};aftertargets={x['id']:x for x in fullafter['rows']}
planerrors=[]
for p in fullplan:
 frozen=appends['stories'][p['storyId']]
 if p['append']!=frozen['append'] or p['criterionIds']!=frozen['criterion_ids'] or p['expectedDescription']!=before_map[p['id']]['description']+'\n\n'+frozen['append']:planerrors.append(p['storyId'])
check('all368_native_story_plans_match_frozen1328_source_case_appendices',len(fullplan)==len(appends['stories'])==368 and sum(len(p['criterionIds']) for p in fullplan)==1328 and not planerrors,planerrors)
# Independent actual-readback comparisons. Pure comparison does not execute guard fixtures.
comparison=module.review(before['issues'],combined['issues'],fullplan,final_docs)
check('all368_saved_fresh_full_story_prefixes_and_appendices_match_exact_contract',not comparison['errors'] and len(aftertargets)==len(before_targets)==368 and all(aftertargets[k]['description']==next(x for x in combined['issues'] if x['id']==k)['description'] for k in aftertargets),{'errors':comparison['errors'],'targets':comparison['updated_story_count'],'issues':comparison['issues'],'unselected_issues':comparison['unselected_issues']})
full_metadata=[];compared=0
for identity,old in before_targets.items():
 new=aftertargets[identity]
 for k in set(old)|set(new):
  if k in {'description','updatedAt'}:continue
  compared+=1
  if k not in old or k not in new or old[k]!=new[k]:full_metadata.append({'id':identity,'field':k})
check('full_target_named_metadata_preserved_without_absent_field_inference',not full_metadata and compared==11418,{'compared_field_values':compared,'differences':full_metadata,'assignment_cycle_captured':any(k in x for x in before_targets.values() for k in ['assignee','assigneeId','cycle','cycleId'])})
first=load(OUT/'native-first-target-full-prefix-reconciliation.json')
priorpath=ROOT/first['priorFullCapturePath'];prior=load(priorpath)['issues'];priorrow=next(x for x in prior if x['id']==first['id'])
check('first_target_prior_complete_prefix_proof_exact_and_fresh_capture_limit_disclosed',first['currentOriginalPrefix']==priorrow['description']==before_map[first['id']]['description'] and 'Fresh pre-save full capture was not obtained' in first['disposition'] and first==before['firstTargetRecovery'], {'id':first['id'],'prefix_sha256':textsha(first['currentOriginalPrefix']),'prior_capture':first['priorFullCapturePath'],'disposition':first['disposition']})
rootactual=load(OUT/'ACTUAL-FINAL-NATIVE-PUBLICATION-REVIEW.json');rootmeta=load(OUT/'ACTUAL-TARGET-FULL-METADATA-COMPARISON.json')
check('root_report_explicit_limits_and13_historical_guards_honest',rootactual['status']=='PASS' and not rootactual['errors'] and len(rootactual['guard_checks'])==13 and all(rootactual['guard_checks'].values()) and rootactual['issues']==1553 and rootactual['updated_story_count']==368 and len(rootactual['documents'])==10 and 'Unselected descriptions are list excerpts only' in rootactual['scope'] and 'Assignee/cycle not requested or certified' in rootactual['omitted_fields'] and 'live relations need a separate capture' in rootactual['relationships'] and rootmeta['compared_field_values']==compared and not rootmeta['differences'] and not rootmeta['omitted'])

overview=load(OUT/'native-overview-final-append-readback.json');ob=overview['before'];oa=overview['after']
overviewdiff=[k for k in set(ob)|set(oa) if k not in {'content','updatedAt'} and ob.get(k,object())!=oa.get(k,object())]
check('existing_overview_original7140_prefix_and_one_complete_exact_addition_preserved',len(ob['content'])==7140 and oa['content'].startswith(ob['content']) and overview['expected']==ob['content']+overview['addition'] and canonical(oa['content'])==canonical(overview['expected']) and oa['content'].count('<!-- imprana:pm-qa-standards-completion:20261011 -->')==1 and oa['project']['id']==PROJECT and not overviewdiff,{'old_prefix_sha256':textsha(ob['content']),'expected_sha256':textsha(overview['expected']),'actual_sha256':textsha(oa['content']),'metadata_differences':overviewdiff})
check('overview_factual_qualifiers_match_actual_counts_and_capture_limits',all(x in overview['addition'] for x in ['2,893 planning elements','55 shared draft assurance records','56 reusable review-request contracts','1,328 original active acceptance scenarios across 368 stories','All 385 assurance groups remain needs_input','actual authentic reviews are zero','accepted bindings and completed runs are zero','3,786 structure errors and 3,794 negative release-mode errors','Unselected 1,185 issue descriptions','assignee/cycle fields were omitted','not a fabricated fresh pre-save full capture','does not claim a new all-live-relationship capture','no broad autolink waiver','human approval, Ready/Done, product PASS, deployment or new spending authority']))
readme=txt(QA/'README.md');adoption=txt(QA/'ADOPTION-CONTRACT.md');publication=txt(QA/'publication/README.md')
check('readme_and_adoption_keep_authoring_scope_authority_bindings_and_enforcement_open',all(x in readme for x in ['zero validated bindings and zero completed runs','3,786 actual binding errors','3,794 errors','Applicability remains UNKNOWN','Do not relabel planned automation as MANUAL','No product run','No completion percentage']) and all(x in adoption for x in ['docs/CODEOWNERS','NOT_VERIFIED','source-owner','NOT_READY','Main auto-deploys','no planned case implies execution']))
texts=[readme,adoption,summary,publication]+[x['actual'] for x in final_docs]+[overview['addition']]
check('no_unrelated_product_scope_in_reviewed_documentation',not any(re.search(r'\b(?:saha|health\s+saha|patient|msme)\b',x,re.I) for x in texts))
check('publication_prose_capture_limits_no_product_or_human_certification',all(x in publication for x in ['not product tests','first target','Assignee/cycle','1,185','zero accepted bindings/completed runs','Parser-generated autolinks were never normalized away']))

tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=REPO,text=True).splitlines()
allowed={'docs/product/framework-v4-20261011/START-HERE.md','docs/DOCUMENTATION-INDEX.md'};protected=[p for p in tracked if p not in allowed]
changed=subprocess.check_output(['git','diff','--name-only',BASE,'--',*protected],cwd=REPO,text=True).splitlines()
check('all1910_original_protected_tracked_sources_history_code_unchanged',len(protected)==1910 and not changed,{'baseline':BASE,'protected_files':len(protected),'changed':changed})
rootintegrity=load(OUT/'ROOT-INTEGRATION-PREPUBLICATION-CHECK.json')
check('actual_root_prepublication_receipt_is_limited_document_evidence',rootintegrity['status']=='PASS' and not rootintegrity['errors'] and all(x['pass'] for x in rootintegrity['checks']) and 'no product runs, owner approvals, deployment' in rootintegrity['scope'])
# Root has copied only compact receipts; inspect and verify every copy against its original.
copychecks=[];copy_errors=[]
for dir,filename in [(QA/'review','REVIEW-COPY-MANIFEST.json'),(QA/'publication','PUBLICATION-COPY-MANIFEST.json')]:
 obj=load(dir/filename)
 for member in obj['members']:
  dest=REPO/member['destination'] if 'destination' in member else dir/member['file']
  if not dest.is_file() or sha(dest)!=member['sha256'] or dest.stat().st_size!=member['bytes']:
   copy_errors.append({'destination':str(dest),'error':'copy hash or byte length differs'})
  if 'source' in member:
   origin=OUT/member['source']
   if member['source']=='ROOT-INTEGRATION-PREPUBLICATION-CHECK.json' and 'prior_prepublication_source_retained_at' in obj:
    origin=OUT/obj['prior_prepublication_source_retained_at']
    observations.append({'id':'DECLARED_FIRST_PREPUBLICATION_COPY_HISTORY','historical_source':str(origin.relative_to(ROOT)),'sha256':sha(origin),'disposition':'Original published prepublication proof remains exact against explicitly declared retained history; current later document-integrity proof is a different retained observation.'})
   if not origin.is_file() or origin.read_bytes()!=dest.read_bytes():
    copy_errors.append({'destination':str(dest),'source':str(origin),'error':'original copy differs'})
  elif 'compact_derived_from' in member:
   derived=load(dest);copychecks.append({'compact':str(dest.relative_to(ROOT)),'fields':derived})
  copychecks.append({'destination':str(dest.relative_to(ROOT)),'sha256':sha(dest),'source':member.get('source',member.get('compact_derived_from'))})
check('all17_review_and_publication_copies_byte_exact_or_declared_compact_derivation',len(copychecks)==18 and not copy_errors,{'members':17,'errors':copy_errors})
compact=load(QA/'publication/ACTUAL-OVERVIEW-APPEND-VERIFICATION.json')
check('compact_overview_receipt_binds_actual_full_readback_hashes',compact.get('verified') is True and compact.get('original_prefix_byte_exact') is True and compact.get('marker_count')==1 and compact['before_sha256']==textsha(ob['content']) and compact['after_sha256']==textsha(oa['content']) and compact['addition_sha256']==textsha(overview['addition']) and compact['raw_evidence_sha256']==sha(OUT/'native-overview-final-append-readback.json') and compact['id']==oa['id'] and compact['project_id']==PROJECT,compact)
observations.append({'id':'THIS_REVIEW_SECOND_ADAPTER_OBSERVATION','path':str((OWN/'SECOND-REVIEWER-ADAPTER-OBSERVATION.json').relative_to(ROOT)),'sha256':sha(OWN/'SECOND-REVIEWER-ADAPTER-OBSERVATION.json'),'disposition':'Preserved reviewer schema/path assumption failures. Compact overview uses verified/original_prefix_byte_exact/marker_count and is now fully tied to actual hashes; dated first prepublication copy binds its explicitly declared immutable historical source rather than newer same-named active output. No shared source edits.'})
observations.append({'id':'THIS_REVIEW_FIRST_ADAPTER_OBSERVATION','path':str((OWN/'FIRST-REVIEWER-ADAPTER-OBSERVATION.json').relative_to(ROOT)),'sha256':sha(OWN/'FIRST-REVIEWER-ADAPTER-OBSERVATION.json'),'disposition':'Preserved first review adapter failures: AST reader originally counted only ten direct keys, omitting three loop-declared corruption guard names; factual qualifier reader expected lowercase unselected where actual text correctly begins Unselected. Only reviewer helper was corrected; Native/repository sources unchanged.'})

def literal_code_projection(text):
 result=[];block=[];fence=None
 for line in text.splitlines(keepends=True):
  if fence:
   block.append(line)
   if re.fullmatch(r' {0,3}'+re.escape(fence[0])+r'{'+str(fence[1])+r',}[ \t]*(?:\n)?',line):
    result.append(('fenced',''.join(block)));block=[];fence=None
   continue
  f=re.match(r'^ {0,3}(`{3,}|~{3,})',line)
  if f:
   fence=(f[1][0],len(f[1]));block=[line];continue
  at=0
  while at<len(line):
   opener=re.search(r'`+',line[at:])
   if not opener:break
   start=at+opener.start();end=at+opener.end();size=len(opener[0]);close=None
   for tick in re.finditer(r'`+',line[end:]):
    if len(tick[0])==size:close=(end+tick.start(),end+tick.end());break
   if close is None:at=end;continue
   result.append(('inline',line[start:close[1]]));at=close[1]
 if block:result.append(('unclosed_fenced',''.join(block)))
 return result
literal_errors=[]
for doc in final_docs:
 if literal_code_projection(own_expected[doc['id']][0])!=literal_code_projection(doc['actual']):literal_errors.append(doc['id'])
for item in fullplan:
 actual=aftertargets[item['id']]['description'][len(before_map[item['id']]['description']):]
 if literal_code_projection('\n\n'+item['append'])!=literal_code_projection(actual):literal_errors.append(item['id'])
check('all378_actual_doc_and_story_appendix_literal_code_projections_exact',not literal_errors,{'documents':10,'stories':368,'differences':literal_errors,'method':'Independent fence-length-aware and exact matching backtick-run projection of retained observations, not test fixtures.'})
c_lane=load(OUT/'native-lane-c/FINAL-RECEIPT.json');d_lane=load(OUT/'native-lane-d/FINAL-JOURNAL.json');rootrepair=load(OUT/'native-APL-429-auto-link-repair.json')
d_repairs=[x['id'] for x in d_lane['rows'] if x['repairs']]
c_repaired=[x['id'] for x in c_lane['readbacks'] if x['repair_count']>0]
repair_ids={'APL-429'}|set(c_repaired)|set(d_repairs)
check('publication21_distinct_actual_repair_story_count_matches_retained_lane_evidence',c_lane['actual_counts']['concrete_source_autolink_repairs']==len(c_repaired)==9 and len(d_repairs)==len(set(d_repairs))==11 and rootrepair['before']['id']==rootrepair['after']['id']=='APL-429' and len(repair_ids)==21,{'root_repaired_story':'APL-429','lane_c_repaired_stories':c_repaired,'lane_d_repaired_stories':d_repairs,'count':len(repair_ids),'qualification':'Actual concrete source failures/patches retained; whole final prefixes independently raw exact.'})

report={'record':'IMPRANA-FINAL-INDEPENDENT-DOCUMENT-INTEGRATION-REVIEW','recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'disposition':'PASS_DOCUMENT_SOURCE_AND_PUBLICATION_INTEGRITY_ONLY' if all(c['passed'] for c in checks) else 'FINDINGS','reviewer':'Separate AI documentation/source reviewer; no authenticated human/owner authority asserted','scope':{'records':55,'groups':385,'scoped_summary_sections':55,'elements':2893,'original_criteria':1328,'native_stories':368,'native_documents':10,'overview_appendix':1,'selected_full_metadata_values':compared,'unselected_descriptions':'1185 list excerpts only','actual_package_or_product_tests_run_by_this_review':0,'Native_writes':0,'repo_writes':0},'checks':checks,'failed_checks':[x['id'] for x in checks if not x['passed']],'observations':observations,'source_pins':pins,'copy_manifest_discovery':copychecks,'helper':{'path':str(pathlib.Path(__file__).relative_to(ROOT)),'sha256':sha(pathlib.Path(__file__))},'limits':['Saved/fresh full captures are reviewed as actual retained observations; this reviewer made no new Native request and claims no later live-state freshness.','All PM scopes and QA case/binding/applicability decisions remain drafts/unknown. No qualified human/source-owner/trust/release approval is authenticated.','No package/product/runtime/CI/provider tests or regression guards were executed; the 13 historical corruption guard results were read and their source independently inspected.','Full source prefixes are raw byte exact; observed Markdown cosmetics are limited to nonliteral presentation of authorized appendices/documents. Generated autolinks are not normalized away.','Assignee/cycle were omitted in both captures and are not inferred as backend null; unselected complete descriptions/live all-task edges are not independently certified.','PASS means bounded source/document integrity only: not favorable assurance, runtime qualification, percentage, Ready/Done, deployment, new spend or export authority.']}
path=OWN/'FINAL-INDEPENDENT-DOCUMENTATION-INTEGRATION-REVIEW.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'disposition':report['disposition'],'checks':len(checks),'passed':sum(c['passed'] for c in checks),'failures':report['failed_checks'],'receipt':str(path.relative_to(ROOT)),'sha256':sha(path)},indent=2))
