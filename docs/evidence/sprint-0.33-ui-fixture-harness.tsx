import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import {AIEnablementPanel} from '/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/AIEnablement.tsx';
import '/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/styles.css';
const ids={plan:'11111111-1111-4111-8111-111111111111',head:'22222222-2222-4222-8222-222222222222',committed:'33333333-3333-4333-8333-333333333333',later:'44444444-4444-4444-8444-444444444444',programme:'55555555-5555-4555-8555-555555555555',period:'66666666-6666-4666-8666-666666666666',indicator:'77777777-7777-4777-8777-777777777777',actor:'88888888-8888-4888-8888-888888888888',second:'99999999-9999-4999-8999-999999999999',member:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',case:'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'};
const plan={object_id:ids.plan,revision_id:ids.head,business_state:'Draft',data:{title:'Synthetic saved parent plan',profile:{sector:'GENERAL',team_size:5,goal:'Synthetic saved organisation goal',data_readiness:'BASIC',ai_experience:'NONE',sensitive_data:false},solution_ids:[],learning_completed:[],procurement:{requirements:'',data_boundary:'',budget_notes:'',vendor_questions:''},pilot:{success_measure:'',completed_actions:[]},planning:{cost_comparison:null,pilot_evaluation:null,task_practice:null},content_versions:{catalog:'synthetic-v1',solutions:'synthetic-v1'}}};
const catalog={content_version:'synthetic-v1',advisory_available:false,journey:[],use_cases:[],learning_paths:[],procurement_criteria:[],marketplace_status:{status:'UNVERIFIED',explanation:'Synthetic catalogue only'}};
const value={value_state:'PRESENT',displayed_value:'46.36',numerator:'51',denominator:'110',calculated_at:'2026-10-05T10:00:00Z',reason_code:null};
const card={indicator_id:ids.indicator,indicator_label:'Synthetic governed outcome',unit:'%',official:value,provisional:{...value,displayed_value:'47.00'},target:null,baseline:null,status:{status:'ON_TRACK',compared_with:'OFFICIAL',attainment_percent:'92.72',reason_code:null},coverage:{source:'CLOSE_SNAPSHOT',applicability:'APPLICABLE',approval_percent:'50.00',expected_count:4,required_count:4,approved_count:2,pending_count:1,missing_count:1,reason_code:null},freshness:{stale:true,stale_reasons:[],source_check:'CHECKED',checked_at:'2026-10-05T10:00:00Z'}};
const evidence={object_id:ids.plan,revision_id:ids.head,status:'LINKED',reference:{programme_id:ids.programme,indicator_id:ids.indicator,period_id:ids.period,interpretation_note:'Synthetic note',snapshot_id:ids.plan,snapshot_revision:ids.head,snapshot_version:1},reference_status:{programme:'CURRENT',indicator:'CURRENT',definition:'CURRENT',period:'CURRENT',calendar:'CURRENT',snapshot:'CURRENT'},programme_title:'Synthetic private programme label',period:{period_code:'Synthetic Q1',period_state:'Locked',starts_at:'2026-01-01T00:00:00Z',ends_at:'2026-04-01T00:00:00Z'},indicator:card,stale_rule:'Synthetic freshness rule',disclaimer:'The evidence link does not establish that AI caused an impact result.'};
const qa=window.qa={ids,plan,evidence,calls:[],receipts:{},props:null,update:null,mode:'linked',loseNext:false,laterEdit:false,failCanonical:false,holdNext:false,held:[],cases:[],caseHistory:[],caseReceipts:{},loseNextAdvice:false,denyPeers:false,secondCanReadPlan:false};

const adviceStamp='2026-10-05T10:00:00Z';
function adviceProject(item){const copy=structuredClone(item);copy.context_current=item.data.context_plan_revision===qa.plan.revision_id;if(qa.props.principalId===ids.second&&item.business_state==='Open')copy.problem=null;return copy;}
function adviceCurrent(){const item=qa.cases[0];if(!item||(qa.props.principalId===ids.second&&['Closed','Cancelled'].includes(item.business_state)))throw {code:'RESOURCE_UNAVAILABLE'};return item;}
async function request(path,options={}){
 const call={path,method:options.method||'GET',body:options.body?JSON.parse(options.body):null,actor:qa.props.principalId};qa.calls.push(call);

 if(path.includes('/ai-enablement/human-advice')){
  if(call.method==='POST'){
   if(qa.caseReceipts[call.body.operation_id])return structuredClone(qa.caseReceipts[call.body.operation_id]);
   let item;if(!path.includes('/actions/')){qa.caseHistory=[];item={object_id:crypto.randomUUID(),revision_id:crypto.randomUUID(),business_state:'Open',context_current:true,problem:call.body.data.problem,data:{...call.body.data,requester_principal_id:ids.actor,adviser_principal_id:ids.second,declaration:null,assignment:null,notes:[],advice:null,closure:null,cancellation:null}};qa.cases=[item];}
   else {item=adviceCurrent();const action=path.split('/').at(-1),data=call.body.data;item.revision_id=crypto.randomUUID();if(action==='declare-scope')item.data.declaration={...data,declared_at:adviceStamp};if(action==='assign'){item.data.assignment={...data,assigned_at:adviceStamp};item.business_state='Assigned';}if(action==='advise'){item.data.advice={text:data.advice,actions:data.actions.map(v=>({...v,action_id:crypto.randomUUID()})),advised_at:adviceStamp};item.business_state='AdviceDraft';}if(action==='close'){item.data.closure={...data,closed_at:adviceStamp};item.business_state='Closed';}if(action==='cancel'){item.data.cancellation={...data,cancelled_at:adviceStamp};item.business_state='Cancelled';}}
   qa.caseHistory.unshift(structuredClone(item));const receipt={operation_id:call.body.operation_id,object_id:item.object_id,revision_id:item.revision_id,business_state:item.business_state,saved_at:adviceStamp,correlation_id:ids.case};qa.caseReceipts[call.body.operation_id]=receipt;if(qa.loseNextAdvice){qa.loseNextAdvice=false;throw new TypeError('Synthetic advice response lost');}return receipt;
  }
  if(path.includes('/eligible-peers?')){if(qa.denyPeers||!qa.props.capabilities.includes('memberships.read'))throw {code:'RESOURCE_UNAVAILABLE'};return {items:[{membership_id:ids.member,display_name:'Synthetic eligible organisation member'}],next_cursor:null};}
  if(path.includes('/revisions?')){adviceCurrent();return {items:qa.caseHistory.map((item,index)=>({revision_id:item.revision_id,revision_number:qa.caseHistory.length-index,saved_at:adviceStamp})),next_cursor:null};}
  if(path.includes('/revisions/')){adviceCurrent();return adviceProject(qa.caseHistory.find(item=>item.revision_id===path.split('/').at(-1)));}
  if(qa.cases[0]&&path.includes(qa.cases[0].object_id))return adviceProject(adviceCurrent());
  return {items:qa.cases.filter(item=>qa.props.principalId!==ids.second||!['Closed','Cancelled'].includes(item.business_state)).map(adviceProject),next_cursor:null};
 }
 if(qa.holdNext&&path.endsWith('/impact-reference/result')){qa.holdNext=false;const captured=structuredClone(qa.evidence);return new Promise(resolve=>qa.held.push(()=>resolve(captured)));}
 if(path.endsWith('/impact-reference')&&call.method==='PUT'){
  if(qa.receipts[call.body.operation_id])return structuredClone(qa.receipts[call.body.operation_id]);
  qa.plan.revision_id=ids.committed;qa.evidence.revision_id=ids.committed;
  const receipt={operation_id:call.body.operation_id,object_id:ids.plan,revision_id:ids.committed,business_state:'Draft',saved_at:'2026-10-05T10:00:00Z',correlation_id:ids.plan};qa.receipts[call.body.operation_id]=receipt;
  if(qa.laterEdit){qa.plan.revision_id=ids.later;qa.evidence.revision_id=ids.later;qa.plan.data.title='Synthetic later canonical title';}
  if(qa.loseNext){qa.loseNext=false;throw new TypeError('Synthetic response lost');}return receipt;
 }
 if(path.endsWith('/impact-reference/result')){if(qa.mode==='hidden'||qa.props.principalId===ids.second)throw {code:'RESOURCE_UNAVAILABLE',message:'Unavailable'};return structuredClone(qa.evidence);}
 if(path.endsWith('/ai-enablement/catalog'))return structuredClone(catalog);
 if(path.endsWith('/ai-enablement/solutions'))return {content_version:'synthetic-v1',checked_on:'2026-10-05',explanation:'Synthetic only',solutions:[],comparison_criteria:[]};
 if(path.includes('/ai-enablement/plans?'))return {items:qa.props.principalId===ids.second&&!qa.secondCanReadPlan?[]:[structuredClone(qa.plan)],next_cursor:null};
 if(path.endsWith('/ai-enablement/plans/'+ids.plan)){
  if(call.method==='PUT'){qa.plan.data=structuredClone(call.body.data);qa.plan.revision_id=crypto.randomUUID();qa.evidence.revision_id=qa.plan.revision_id;return {operation_id:call.body.operation_id,object_id:ids.plan,revision_id:qa.plan.revision_id,business_state:'Draft',saved_at:'2026-10-05T10:00:00Z',correlation_id:ids.plan};}
  if(qa.failCanonical){qa.failCanonical=false;throw {code:'RESOURCE_UNAVAILABLE',message:'Synthetic current plan unavailable'};}return structuredClone(qa.plan);
 }
 if(path.includes('/programmes?'))return {items:[{object_id:ids.programme,revision_id:ids.head,data:{title:'Synthetic private programme label',starts_at:'2026-01-01T00:00:00Z',ends_at:'2027-01-01T00:00:00Z'}}],next_cursor:null};
 if(path.includes('/periods?'))return {items:[{object_id:ids.period,revision_id:ids.head,data:{code:'Synthetic Q1',starts_at:'2026-01-01T00:00:00Z',ends_at:'2026-04-01T00:00:00Z'}}],next_cursor:null};
 if(path.includes('/dashboard?'))return {indicators:[card],next_cursor:null};
 throw Error('Unexpected synthetic request: '+path);
}
function Dialog({title,close,children}){return <section role="dialog" aria-label={title}><h2>{title}</h2>{children}<button type="button" onClick={close}>Close dialog</button></section>;}
function App(){const[props,setProps]=useState({base:'/v1/tenants/synthetic/',principalId:ids.actor,sessionIdentity:'synthetic-session-a',capabilities:['ai.enablement.read','ai.enablement.manage']});qa.props=props;qa.update=change=>setProps(previous=>({...previous,...change}));return <AIEnablementPanel key={props.base+props.sessionIdentity+props.principalId} {...props} request={request} explain={error=>error.message||'Synthetic request failed'} Dialog={Dialog}/>;}
createRoot(document.getElementById('root')).render(<App/>);
