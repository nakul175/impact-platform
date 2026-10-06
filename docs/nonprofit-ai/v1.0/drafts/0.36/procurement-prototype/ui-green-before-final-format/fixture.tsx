import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/styles.css";
import "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/src/ai-enablement.css";
import { AIAdoptionWorkspace } from "./AIAdoptionWorkspace";
import "./fixture.css";
import type { Catalog, Profile } from "./AIEnablement";
const clone = <T,>(value: T): T => structuredClone(value);
const profile: Profile = { sector:"GENERAL",team_size:5,goal:"Review invented Café messages\nKeep human review",data_readiness:"BASIC",ai_experience:"EXPERIMENTING",sensitive_data:false };
const catalog: Catalog = { content_version:"invented-catalog-v1",advisory_available:false,journey:[],use_cases:[],learning_paths:[{id:"foundation",title:"Invented foundation",steps:[],lessons:[{key:"known-lesson",title:"Invented lesson",lesson:"Invented reading",exercise:"Invented exercise",check:{question:"Human review?",options:["Yes","No"],answer:0,explanation:"Invented test"}}]}],procurement_criteria:[{id:"boundary",title:"Data boundary",questions:["What is retained?","How is data deleted?"]}],marketplace_status:{status:"DRAFT",explanation:"Synthetic fixture only"} };
const solutions = {content_version:"invented-solutions-v1",checked_on:"2026-10-05",explanation:"Synthetic fixture",solutions:["first","second"].map((id,index)=>({id,name:index===0?"First Café":"Second supplied tool",provider:"Invented",category:"GENERAL_ASSISTANT",use_case_ids:[],description:"Invented fixture",deployment:"Hosted",commercial_model:"Verify",nonprofit_offer:"Verify",api_available:"Verify",source_urls:[],verification_notes:[],data_review_questions:[index===0?"Who can access it?":"What can be exported?"]})),comparison_criteria:[]};
const seed={object_id:"aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",revision_id:"bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",business_state:"Draft",data:{title:"Private procurement source",profile,solution_ids:["first","second"],learning_completed:["known-lesson"],procurement:{requirements:"Own Café\nrequirements",data_boundary:"Own approved boundary notes",budget_notes:"Own budget notes",vendor_questions:"Own supplier questions"},pilot:{success_measure:"Existing manual pilot criterion",completed_actions:["DEFINE_GOAL"]},planning:{cost_comparison:null,pilot_evaluation:null,task_practice:{template_id:"invented-task",brief:"Existing invented brief",draft:"Own exact learner Café\ndraft",review_notes:"Own exact review notes",checked_steps:["own-step"]}},content_versions:{catalog:catalog.content_version,solutions:solutions.content_version}}};
let row=clone(seed), calls:{path:string;method:string;body?:any}[]=[], hold=false, held=false, release:(()=>void)|null=null,lost=false;
const receipts=new Map<string,any>();
async function request(path:string,options:RequestInit={}) {
 const method=options.method||"GET",body=options.body?JSON.parse(String(options.body)):undefined;calls.push({path,method,...(body?{body}:{})});
 if(path.endsWith("/solutions"))return clone(solutions);
 if(path.includes("plans?limit"))return {items:[clone(row)],next_cursor:null};
 if(path.includes("/revisions?"))return {items:[],next_cursor:null};
 if(path.endsWith("/plans/"+row.object_id)){
  if(method==="PUT"){
   if(hold){hold=false;held=true;await new Promise<void>(resolve=>{release=resolve;});held=false;}
   if(receipts.has(body.operation_id))return clone(receipts.get(body.operation_id));
   row={...row,revision_id:crypto.randomUUID(),data:{...body.data,content_versions:row.data.content_versions}};const receipt={object_id:row.object_id,revision_id:row.revision_id,business_state:"Draft"};receipts.set(body.operation_id,receipt);
   if(lost){lost=false;throw {code:"SERVICE_UNAVAILABLE",reason:"Synthetic lost save response"};}return clone(receipt);
  }
  return clone(row);
 }
 throw {code:"RESOURCE_UNAVAILABLE",reason:"Synthetic fixture has no response"};
}
function Dialog({title,close,children}:{title:string;close:()=>void;children:React.ReactNode}){return <div role="dialog" aria-label={title}>{children}<button type="button" onClick={close}>Close</button></div>;}
function App(){const [currentProfile,setProfile]=useState(clone(profile)),[currentCatalog,setCatalog]=useState(clone(catalog)),[canManage,setManage]=useState(true),[principal,setPrincipal]=useState("invented-editor");Object.assign(window,{fixture:{calls:()=>clone(calls),row:()=>clone(row),seed:()=>clone(seed),profile:()=>clone(currentProfile),patchProfile:(patch:Partial<Profile>)=>setProfile(previous=>({...previous,...patch})),catalog:()=>clone(currentCatalog),setCatalog,canManage:setManage,principal:setPrincipal,holdSave:()=>{hold=true;},saveHeld:()=>held,loseSave:()=>{lost=true;},releaseSave:()=>{release?.();release=null;}}});return <main className="ai-enablement"><h1>Private procurement preview</h1><h2>Adoption planning fixture</h2><p>Synthetic in-memory request responses only. No actual API or current authority proof.</p><AIAdoptionWorkspace base="/v1/tenants/invented/" principalId={principal} sessionIdentity="invented-session" request={request} explain={error=>String((error as any).reason||error)} capabilities={canManage?["ai.enablement.read","ai.enablement.manage"]:["ai.enablement.read"]} profile={currentProfile} catalog={currentCatalog} onLoadProfile={setProfile} Dialog={Dialog}/></main>;}
createRoot(document.getElementById("root")!).render(<App/>);
