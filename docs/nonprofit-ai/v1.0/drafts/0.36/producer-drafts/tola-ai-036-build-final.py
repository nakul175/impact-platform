"""Private proposed explicit036 build producer; original035 producer was inline.

Default is NOT_RUN. --execute requires root's saved035 baseline and frozen lease.
Only strict TypeScript + the existing dual-entry Vite commands may establish PASS.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path('/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform')
EXPECTED_VERSION = {'build': '0.36.0', 'domain_api': '1.25.0', 'platform_api': '1.10.0', 'documentation_edition': '1.1', 'schema_rule': 'derived: the number of files in infrastructure/migrations (impact_api/version.py)'}
FROZEN_MIGRATIONS = {'0001_roles.sql': '5e75f33a46817c92888cb1c1077ce06887326e38f68d6db5576786705f0f39f7', '0002_domain.sql': '7cfcffcd735e7b7a2843cb675c67b2f0eb360a8e634fb1f0d220771367af5aa0', '0003_security.sql': '9bb472eb6481f95c83e755d6648928e7269958f647ddabf89ec9509bc4e9d148', '0004_application.sql': 'c3a6f63502127d4b7865f8035c8a7c84d0307323e7744f9c93dd8189825606a4', '0005_access_administration.sql': '3a5509cb2cbacc5473b83f3e0c9d70cd343f416ba49e6a02de38c73b2734260c', '0006_measurement_configuration.sql': '081b24b3927a426d4426912764d16c9a792f4e7b5ae84fffd8f2b1eab13e90ce', '0007_measurement_changes.sql': '15d8295c57ecc87fa0e7ab1b2881125bec151c13069f2d6ea6c8cb7465f15db0', '0008_period_governance.sql': '867df4f5da210533648944fbc244b6d35a8cda0aede44e2e95415ee0fb925950', '0009_reporting_packages.sql': '9d29b28d90814ed06cea352a0c35353fcb3f6f34d16e3e3727d40e546248525f', '0010_work_and_recalculation.sql': 'ae1179c228a7e5fa4f7ac7f0e4f42377003b76a9924e473981e52a97f72e24e7', '0011_controlled_publication.sql': 'c0a97842093f07d621e692e6cbc23923135719bfa751c24fa2c9c32827a14683', '0012_workspace_administration.sql': '5ef1bb4c71af91f7bf19fd3b1606c8354d7d3c640031b90ac78898e6cb032596', '0013_tenant_lifecycle.sql': '564e9c0858336297b379e6bb4930d8a92b3b499bf4d6b632f8a3ad994b2e3e5a', '0014_initial_access.sql': 'b91c517920bb28c77eea184e9dc40e717e3ed0e0db2a2bb7656c456de5d45468', '0015_recovery_contacts.sql': '2b721bd91480033d9b3c3e18f8d77e5e2bcb0f675dcf1e88cb33c60e6ebf9d42', '0016_authority_renewal.sql': '2c95596d9088fb2ec025266cffed824a787ec8df3d3dd4021fefe19cb09290cc', '0017_provider_logout.sql': '4378cafe2bacbf6266e0d18f5886966a29c0a53b2ba51566b7afc4c04c9c000b', '0018_worker_delivery.sql': 'bd2defdfb56f3332f0cdb1706fd330893497cc3eeb8f45f4277922f0eca9e8b7', '0019_results_framework.sql': 'e12728cf4bbb2ff544c75183ac9c5371b393f498f7d61ed791d8a08b356c4161', '0020_calculation_methods.sql': '357f7a80ed9b21b618cdf9209d09c00b7683fc69128fc4938c7e27728d51fa31', '0021_web_forms.sql': 'afd37bd9e4c5fbaf40d65ad0cb46da1ac8bb7b49adf7bb24ce37493ea11342f2', '0022_import_quality.sql': '7ea2f6f67331f02518ce538528cb06353d686835a5ff7c2849d271096e8002ac', '0023_evidence_objects.sql': 'aa6955e3d950925e9a79192d688b9eaed56bec16cd53702225ad5d4c292570fc', '0024_report_exports.sql': '2a162567e6414db5d349850bc0d279678203c830d7a3c4fef8751ce7fab8db9f', '0025_worker_grants.sql': 'e15906bfddde70bc978f93785dfec60ed60ddd45d0135d351a2584bbffbc5047', '0026_worker_job_grants.sql': 'c01bcd55621e71fd6e5bd3d11ac08f085eec8bd51efcefb25b8de11fded64310', '0027_privacy_execution.sql': 'b7fca9754e818ded1e856c66cf4c525aa6049bab924edfbc7e5f050b728e1e9d', '0028_usable_staging.sql': '2a7775799ee960728e21395d3d85c4027b5fe8f7e135853c4197ef3acf6f0c1c', '0029_operator_lifecycle.sql': 'de05d78b232cfea0ec5f75479f2f374fbfd8196c0df5a4694d871b73e68d4d41', '0030_security_privacy.sql': '5ea8601b29f10e1bc7d500a8f177a6aa6a95b9fcb9b094867e2c9366f453ec12', '0031_theory_of_change.sql': '2b0f3736515b77fc5657470d1a95fdfd87e560f4a6a5cc758a840ee86b80b4ac', '0032_forms_languages_rounds.sql': '999df25fb357cf91ef227240dfde6e42145e74abc1e4bf2867c0865374389b2b', '0033_application_executor.sql': 'a0e86eda72775b6a6f14e488be51bbdbcae31ec8dc41adf8137be9860fe4fc33', '0034_ai_advisory.sql': '5835d7e222cc56211463d006bd2d79411293f48f2424942babbde918cf894415', '0035_ai_adoption_plans.sql': '543e3ac6c3f0317cd4792c7cb86d318baca93efd270584940f1b9e0f88c45be5', '0036_reviewed_ceiling_widening.sql': '4e4bf01ebee650fb5c910c944e9ee6344f66c540d178f8c673bd54116710a464', '0037_ai_content_snapshots.sql': '668f0fd4e90e3548fcea922a088976e273e9b164cbdcb12fca97f79fca126d7e', '0038_human_advice_cases.sql': 'ace70f9e77a2636df7e0cf5f85f5ffd29de74af8efa94df6e5804077e5331e00', '0039_human_advice_anchor_availability.sql': '12fb7073f1f841965f6e8c5874444b48ae2da0c39f0e93dae820e7fbedd5b0f0', '0040_ai_plan_portability.sql': 'a4fa49f75b8734a4bb2ea3e9fa35572345714a74a8275381c1a0355756d00a89'}
DEPENDENCY_SHA256 = {'apps/web/package.json': '96cf9887560898ae6efe3a1c0d1af9093df84b34fa321270a1f977148571b185', 'apps/web/package-lock.json': 'ef11a662866b1f60e7cb6e8fe2d309b2ce1f557d3f2f397c6251402e7c4e5d7a'}
EXPECTED_SOURCE_NAMES = ['Makefile', 'VERSION.json', 'apps/api/impact_api/ai_enablement_catalog.py', 'apps/api/impact_api/ai_learning_content.py', 'apps/api/impact_api/ai_task_practice.py', 'apps/api/impact_api/main.py', 'apps/web/ai-walkthrough.html', 'apps/web/index.html', 'apps/web/package-lock.json', 'apps/web/package.json', 'apps/web/src/AIAdoptionWorkspace.tsx', 'apps/web/src/AIEnablement.tsx', 'apps/web/src/AIFictionalWalkthrough.tsx', 'apps/web/src/AIFictionalWalkthroughAdapter.ts', 'apps/web/src/AIGuidanceArchive.tsx', 'apps/web/src/AIHumanAdvice.tsx', 'apps/web/src/AIImpactEvidence.tsx', 'apps/web/src/AILearningLesson.tsx', 'apps/web/src/AIPlanExportAdapter.ts', 'apps/web/src/AIPlanPortability.tsx', 'apps/web/src/AIPlanReviewChecklist.tsx', 'apps/web/src/AIPlanReviewModel.ts', 'apps/web/src/AIPlanningTools.tsx', 'apps/web/src/AIPracticeStarter.tsx', 'apps/web/src/AIPracticeStarterModel.ts', 'apps/web/src/AIProcurementBrief.tsx', 'apps/web/src/AIProcurementPreview.tsx', 'apps/web/src/AIProcurementPreviewModel.ts', 'apps/web/src/AITaskPractice.tsx', 'apps/web/src/AIToolComparison.tsx', 'apps/web/src/AccessGate.tsx', 'apps/web/src/AccessUpgrade.tsx', 'apps/web/src/Accounts.tsx', 'apps/web/src/Administration.tsx', 'apps/web/src/AuditExport.tsx', 'apps/web/src/AuthorityRenewal.tsx', 'apps/web/src/Changes.tsx', 'apps/web/src/Configuration.tsx', 'apps/web/src/Dashboards.tsx', 'apps/web/src/Evidence.tsx', 'apps/web/src/Forms.tsx', 'apps/web/src/Imports.tsx', 'apps/web/src/InitialAccess.tsx', 'apps/web/src/Landing.tsx', 'apps/web/src/Operators.tsx', 'apps/web/src/PeriodGovernance.tsx', 'apps/web/src/Planning.tsx', 'apps/web/src/Portfolio.tsx', 'apps/web/src/Privacy.tsx', 'apps/web/src/RecoveryContacts.tsx', 'apps/web/src/ReferenceData.tsx', 'apps/web/src/ReportExports.tsx', 'apps/web/src/Rounds.tsx', 'apps/web/src/StatusBanner.tsx', 'apps/web/src/TenantLifecycle.tsx', 'apps/web/src/WorkCenter.tsx', 'apps/web/src/Workers.tsx', 'apps/web/src/WorkspaceSettings.tsx', 'apps/web/src/a11y.ts', 'apps/web/src/ai-enablement.css', 'apps/web/src/ai-plan-review.css', 'apps/web/src/ai-planning-tools.css', 'apps/web/src/ai-walkthrough-main.tsx', 'apps/web/src/ai-walkthrough.css', 'apps/web/src/main.tsx', 'apps/web/src/operations.ts', 'apps/web/src/styles.css', 'apps/web/src/vite-env.d.ts', 'apps/web/src/walkthrough-guidance.json', 'apps/web/tsconfig.json', 'apps/web/vite.config.ts', 'qualification/test_deploy_unit.py', 'scripts/run.py', 'scripts/smoke.py']

def qualification_guard(baseline_commit):
    """Future saved035 baseline, unchanged schema/dependencies, build-only delta."""
    import re
    if not isinstance(baseline_commit, str) or not re.fullmatch(r'[0-9a-f]{40}', baseline_commit):
        raise RuntimeError('Root-supplied actual saved0.35 baseline commit required')
    resolved = subprocess.check_output(['git','rev-parse',baseline_commit+'^{commit}'],cwd=ROOT,text=True).strip()
    if resolved != baseline_commit:
        raise RuntimeError('Baseline must identify the exact saved commit')
    subprocess.run(['git','merge-base','--is-ancestor',baseline_commit,'HEAD'],cwd=ROOT,check=True)
    baseline_version = json.loads(subprocess.check_output(['git','show',baseline_commit+':VERSION.json'],cwd=ROOT,text=True))
    expected_baseline = dict(EXPECTED_VERSION,build='0.35.0')
    if baseline_version != expected_baseline or json.loads((ROOT/'VERSION.json').read_text()) != EXPECTED_VERSION:
        raise RuntimeError('Only the reviewed build0.36 metadata delta is permitted')
    files = sorted((ROOT/'infrastructure/migrations').glob('*.sql'))
    if {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files} != FROZEN_MIGRATIONS:
        raise RuntimeError('Exact unchanged forty migrations required')
    for p in files:
        old = subprocess.check_output(['git','show',baseline_commit+':'+str(p.relative_to(ROOT))],cwd=ROOT)
        if hashlib.sha256(old).hexdigest() != FROZEN_MIGRATIONS[p.name]:
            raise RuntimeError('Current migration differs from the actual saved035 baseline')
    for name, expected in DEPENDENCY_SHA256.items():
        value = json.loads((ROOT/name).read_text())
        if value.get('version') != '0.36.0':
            raise RuntimeError('Web package root version must be0.36.0')
        value.pop('version')
        if 'packages' in value:
            if value['packages'][''].get('version') != '0.36.0':
                raise RuntimeError('Web lock root version must be0.36.0')
            value['packages'][''].pop('version')
        body = json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        if hashlib.sha256(body).hexdigest() != expected:
            raise RuntimeError('No dependency or non-version package metadata delta allowed')


def safe_evidence_file(path):
    evidence = (ROOT/'docs/evidence').resolve()
    if not path.resolve().is_relative_to(evidence) or any(p.is_symlink() for p in [path,*path.parents] if p.is_relative_to(ROOT)):
        raise RuntimeError('Evidence path must remain inside the owned non-symlink evidence tree')
    if path.exists() and not path.is_file():
        raise RuntimeError('Evidence target is not a regular file')


def prior_proof(target, preserved):
    safe_evidence_file(target);safe_evidence_file(preserved)
    exists=(target.exists(),preserved.exists())
    if exists == (False,False):
        return None
    if exists != (True,True) or target.read_bytes() != preserved.read_bytes():
        raise RuntimeError('Refuse asymmetric or mismatched prior qualification proof; preserve exact bytes first')
    return str(preserved.relative_to(ROOT))


def preserve_prior_outputs(evidence,prefix,archive):
    """Every pre-existing named full result needs an exact root-preserved copy."""
    prior=[]
    for entry in sorted(evidence.glob(prefix+'*')):
        if entry.is_symlink():raise RuntimeError('Named full evidence symlink refused')
        prior += [entry] if entry.is_file() else [p for p in entry.rglob('*') if p.is_file()]
    if not prior:
        if archive is not None:raise RuntimeError('No prior outputs exist for the supplied archive')
        return []
    if archive is None:raise RuntimeError('Preserve all prior named full outputs before rerun')
    if not archive.is_absolute():archive=evidence/archive
    if archive.is_symlink() or not archive.is_dir() or not archive.resolve().is_relative_to(evidence.resolve()):
        raise RuntimeError('Preserved full archive must be an owned evidence directory')
    preserved=[]
    for path in prior:
        safe_evidence_file(path)
        target=archive/path.relative_to(evidence)
        safe_evidence_file(target)
        if not target.is_file() or target.read_bytes()!=path.read_bytes():
            raise RuntimeError('Every existing named full report must have exact preserved bytes')
        preserved.append(str(target.relative_to(ROOT)))
    return preserved

NODE = '/Users/athena/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
COMMANDS = [[NODE,'node_modules/typescript/bin/tsc','--noEmit'],[NODE,'node_modules/vite/bin/vite.js','build']]
EXTRAS = ['Makefile','VERSION.json','apps/api/impact_api/ai_enablement_catalog.py','apps/api/impact_api/ai_learning_content.py','apps/api/impact_api/ai_task_practice.py','apps/api/impact_api/main.py','apps/web/ai-walkthrough.html','apps/web/index.html','apps/web/package-lock.json','apps/web/package.json','apps/web/tsconfig.json','apps/web/vite.config.ts','qualification/test_deploy_unit.py','scripts/run.py','scripts/smoke.py']
ASSET = re.compile(r'/assets/[A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:js|css)')


def sources():
    names = {ROOT/p for p in EXTRAS}
    names.update(p for p in (ROOT/'apps/web/src').rglob('*') if p.is_file() and p.suffix in {'.ts','.tsx','.css','.json'})
    if {str(p.relative_to(ROOT)) for p in names} != set(EXPECTED_SOURCE_NAMES) or len(names) != 74:
        raise RuntimeError('Exact closed74 build source names required')
    if any(p.is_symlink() or not p.is_file() for p in names):
        raise RuntimeError('Build source symlink or missing file refused')
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(names)}


class BuiltDocument(HTMLParser):
    """Inspect both exact local compiled entrypoint graphs without executing JS."""
    def __init__(self):
        super().__init__();self.assets={};self.roots=0;self.scripts=0;self.in_script=False

    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if len(values)!=len(attrs) or any(k.startswith('on') for k in values):
            raise RuntimeError('Duplicate or inline-event compiled entry attribute')
        if values.get('id')=='root':self.roots+=1
        if tag in {'iframe','object','embed','form','base'} or (tag=='meta' and values.get('http-equiv','').lower()=='refresh'):
            raise RuntimeError('Unexpected compiled entry embedded/navigation tag')
        for key in {'src','href','xlink:href','srcset','srcdoc','action','formaction','poster','data'}&values.keys():
            name=values[key] or ''
            if not ASSET.fullmatch(name) or '..' in name:
                raise RuntimeError('External/dev/unsafe compiled asset reference')
            if tag=='script' and key=='src' and values.get('type')=='module' and name.endswith('.js'):
                self.scripts+=1;kind='script'
            elif tag=='link' and key=='href' and values.get('rel') in {'stylesheet','modulepreload'}:
                kind='style' if values['rel']=='stylesheet' else 'script'
                if not name.endswith('.css' if kind=='style' else '.js'):
                    raise RuntimeError('Asset relation/extension mismatch')
            else:raise RuntimeError('Unexpected compiled resource reference')
            if name in self.assets or len(self.assets)>=16:
                raise RuntimeError('Repeated/excess compiled asset reference')
            self.assets[name]=kind
        if tag=='script':
            if not values.get('src'):raise RuntimeError('Inline compiled entry script refused')
            self.in_script=True

    def handle_endtag(self,tag):
        if tag=='script':self.in_script=False

    def handle_data(self,data):
        if self.in_script and data.strip():raise RuntimeError('Inline compiled script body refused')


def built_assets():
    dist=ROOT/'apps/web/dist'
    if dist.is_symlink() or not dist.is_dir():raise RuntimeError('Actual owned build output required')
    paths=sorted(dist.rglob('*'))
    if any(p.is_symlink() or not p.resolve().is_relative_to(dist.resolve()) for p in paths):
        raise RuntimeError('Build output symlink/path escape refused')
    files=[p for p in paths if p.is_file()]
    names={str(p.relative_to(dist)) for p in files}
    if len(files)!=8 or {'index.html','ai-walkthrough.html'}-names or len([n for n in names if n.startswith('assets/')])!=6:
        raise RuntimeError('Exact two HTML + six compiled asset files required; future036 eight-file assumption remains a qualification gate')
    if any(p.stat().st_size>10*1024*1024 for p in files):raise RuntimeError('Built asset size bound exceeded')
    if any(n not in {'index.html','ai-walkthrough.html'} and not ASSET.fullmatch('/'+n) for n in names):
        raise RuntimeError('Unreviewed build asset path/extension refused')
    references=set();entries={}
    for name in ['index.html','ai-walkthrough.html']:
        body=(dist/name).read_bytes()
        if len(body)>128*1024:raise RuntimeError('Compiled HTML byte bound exceeded')
        document=BuiltDocument();document.feed(body.decode('utf-8'));document.close()
        if document.roots!=1 or document.scripts!=1 or not any(v=='style' for v in document.assets.values()):
            raise RuntimeError('Each compiled entry needs one root/module and a stylesheet')
        references.update(document.assets)
        entries[name]=document.assets
    if references!={'/'+n for n in names if n.startswith('assets/')}:
        raise RuntimeError('Exact entrypoint asset graph differs from the six actual compiled assets')
    return {str(p.relative_to(dist)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},entries


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--baseline-commit');args=parser.parse_args()
    if not args.execute:
        print(json.dumps(dict(status='NOT_RUN',expected_source_count=74,expected_asset_count=8,commands=COMMANDS,baseline_commit_required=True)))
        return
    if Path.cwd().resolve()!=ROOT:raise RuntimeError('Run only in explicitly owned repository')
    qualification_guard(args.baseline_commit)
    evidence=ROOT/'docs/evidence';target=evidence/'sprint-0.36-web-build-source-proof.json'
    prior=prior_proof(target,evidence/'sprint-0.36-initial-full-source-qualification'/target.name)
    lock=open('/private/tmp/tola-ai-shared-qualification.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    try:
        before=sources();started=datetime.now(timezone.utc).isoformat();codes=[];assets={};graph={};error=None
        raw=Path('/private/tmp/tola-ai-036-build-final.log')
        try:
            with raw.open('x') as output:
                os.chmod(raw,0o600)
                for command in COMMANDS:
                    code=subprocess.run(command,cwd=ROOT/'apps/web',stdout=output,stderr=subprocess.STDOUT,check=False).returncode
                    codes.append(code)
                    if code:break
            if codes==[0,0]:assets,graph=built_assets()
        except (OSError,RuntimeError,UnicodeError) as caught:
            error=type(caught).__name__+': '+str(caught)[:240]
        after=sources();changes=[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
        result=0 if codes==[0,0] and not error and not changes and len(assets)==8 else 1
        proof=dict(status='PASS' if result==0 else 'FAIL',baseline_commit=args.baseline_commit,started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),exit_codes=codes,exit_code=result,commands=COMMANDS,scope='Exact strict TypeScript --noEmit and dual-entry Vite production build; explicit new producer based on root inline035 commands. No actualAPI/browser/hosted acceptance.',source_sha256_start=before,source_sha256_end=after,source_changed_during_run=changes,built_assets_sha256=assets,built_entry_asset_graph=graph,migration_sha256=FROZEN_MIGRATIONS,helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),raw_log_publication='NOT_PUBLISHED',preserved_initial_proof=prior,error=error)
        if raw.is_file():proof['raw_private_log_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
        target.write_text(json.dumps(proof,indent=2)+'\n')
        print(json.dumps(dict(exit_code=result,proof=str(target.relative_to(ROOT)),source_count=len(before),asset_count=len(assets))))
        raise SystemExit(result)
    finally:fcntl.flock(lock,fcntl.LOCK_UN)


if __name__=='__main__':main()
