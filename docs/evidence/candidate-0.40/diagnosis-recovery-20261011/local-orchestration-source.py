from pathlib import Path
import subprocess,os,json,datetime,hashlib,shutil,secrets,socket,uuid,sys
project=Path(__file__).resolve().parents[2]
root=project/"work/imprana-diagnosis-20261011"
out=Path(__file__).resolve().parent/"diagnosis-recovery-run-1";out.mkdir(exist_ok=False)
pg=Path(__file__).resolve().parent/"installed/bin"
private=root/".local"/("native-10h-"+uuid.uuid4().hex[:8]);private.mkdir(mode=0o700)
cluster=private/"cluster";pw=private/"bootstrap-password";password=secrets.token_urlsafe(32);pw.write_text(password+"\n");pw.chmod(0o600)
sock=Path("/private/tmp")/("imprana-pg-"+uuid.uuid4().hex[:8]);sock.mkdir(mode=0o700)
with socket.socket() as s:s.bind(("127.0.0.1",0));port=s.getsockname()[1]
env=os.environ.copy();env["PATH"]=str(pg)+os.pathsep+env["PATH"]
receipt={"started_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),"engine":"native PostgreSQL 17.10, private loopback disposable cluster","runtime_path":str(pg),"cluster_path":str(cluster),"port":port,"upgrade_baseline":40,"production_data":False,"paid_resources":False,"source_pins":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((root/"apps/api").rglob("*.py"))+list((root/"qualification").glob("*.py"))+list((root/"infrastructure/migrations").glob("*.sql"))}}
(out/"RUN-RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
local_before={p.name for p in (root/".local").glob("test-*")}
for suffix in ["APP","IDENTITY","PLATFORM","WORKER","EXECUTOR","MIGRATOR"]:env["IMPACT_LOGIN_PASSWORD_"+suffix]=secrets.token_urlsafe(24)
before={str(p.relative_to(root)):p.read_bytes() for p in (root/"docs/evidence").rglob("*") if p.is_file()}
started=False;code=1
try:
 with (out/"initdb.log").open("w") as log:
  subprocess.run([str(pg/"initdb"),"-D",str(cluster),"-U","postgres","-A","scram-sha-256","--pwfile="+str(pw),"--locale=C","-E","UTF8"],stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
 pw.unlink()
 with (out/"cluster-start.log").open("w") as log:
  subprocess.run([str(pg/"pg_ctl"),"-D",str(cluster),"-l",str(private/"server.log"),"-o",f"-h 127.0.0.1 -p {port} -k {sock}","-w","start"],stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
 started=True
 env["PGPASSWORD"]=password
 subprocess.run([str(pg/"createdb"),"-h","127.0.0.1","-p",str(port),"-U","postgres","impact_test_imprana_10h"],env=env,check=True)
 env.pop("PGPASSWORD")
 env.update(IMPACT_FIXTURE_DSN=f"postgresql://postgres:{password}@127.0.0.1:{port}/impact_test_imprana_10h",IMPACT_PORT="8267",IMPACT_PG_BIN=str(pg),IMPACT_UPGRADE_BASELINE="40",PYTHONDONTWRITEBYTECODE="1")
 with (out/"native-full.log").open("w") as log:
  code=subprocess.call([str(project/"work/impact-platform/.venv/bin/python"),"-B","scripts/run.py","test","--native","--pytest-path","qualification/test_ai_diagnosis_native.py","--pytest-path","qualification/test_ai_diagnosis_recovery.py"],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
 if code==0:
  sys.path[:0]=[str(root/"scripts"),str(root/"apps/api")]
  import restore_drill,run as runner
  from provision_logins import passwords_from_env
  from native_upgrade_check import with_database
  import psycopg
  from psycopg import sql
  os.environ.update(env)
  os.environ["PYTHONPATH"]=str(root/"apps/api")
  fresh=[p for p in (root/".local").glob("test-*") if p.name not in local_before]
  assert len(fresh)==1
  source_local=fresh[0];state=json.loads((source_local/"restart-state.json").read_text())
  restored=restore_drill.run(env["IMPACT_FIXTURE_DSN"],env["IMPACT_FIXTURE_DSN"],passwords_from_env(env),pg_bin=str(pg),keep=True)
  target=restored["restored_database"];clone=private/"restored-api";clone.mkdir(mode=0o700)
  config=json.loads((source_local/"config.json").read_text())
  for key in ["app_dsn","identity_dsn","platform_dsn"]:config[key]=with_database(config[key],target)
  for name in ["private.pem","public.pem","restart-state.json"]:shutil.copyfile(source_local/name,clone/name);(clone/name).chmod(0o600)
  (clone/"config.json").write_text(json.dumps(config));(clone/"config.json").chmod(0o600)
  test_env=dict(env,PYTHONPATH=str(root/"apps/api"),IMPACT_TEST_LOCAL=str(clone),IMPACT_BASE_URL=config["public_origin"],IMPACT_NATIVE_TEST="1",IMPACT_REQUIRE_UNPRIVILEGED_DB="1",IMPACT_ENVIRONMENT="test",IMPACT_CONFIG_FILE=str(clone/"config.json"),IMPACT_FIXTURE_DSN=with_database(env["IMPACT_FIXTURE_DSN"],target),IMPACT_DIAGNOSIS_RESTORED_CHECK="1")
  api_env={k:v for k,v in test_env.items() if k not in runner.PRIVILEGED_ENV and not k.startswith("IMPACT_LOGIN_") and not k.startswith("PG")}
  api=None
  try:
   api,ready_seconds=runner.start_api(clone,api_env,config["public_origin"])
   with (out/"restored-api-check.log").open("w") as log:
    restored_code=subprocess.call([sys.executable,"-B","-m","pytest","qualification/test_ai_diagnosis_recovery.py","--junitxml="+str(out/"restored-api-tests.xml")],cwd=root,env=test_env,stdout=log,stderr=subprocess.STDOUT)
   receipt["restored_api"]={"exit_code":restored_code,"ready_seconds":ready_seconds,"runtime_requires_unprivileged_db":True,"read_exact_current_history_versions_and_replay":"PASS" if restored_code==0 else "FAIL","generic_restore":restored}
   code=code or restored_code
  finally:
   if api is not None:receipt["restored_api_stop"]=runner.stop_api(clone,api)
   with psycopg.connect(env["IMPACT_FIXTURE_DSN"],autocommit=True) as c:c.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(target)))
   receipt["restored_clone_dropped"]=True
finally:
 changed=[]
 for p in (root/"docs/evidence").rglob("*"):
  if not p.is_file():continue
  key=str(p.relative_to(root));current=p.read_bytes()
  if before.get(key)!=current:
   dest=out/"generated-evidence"/p.relative_to(root/"docs/evidence");dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(current);changed.append(key)
   if key in before:p.write_bytes(before[key])
   else:p.unlink()
 for key,content in before.items():
  p=root/key
  if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
 if started:
  with (out/"cluster-stop.log").open("w") as log:stop=subprocess.call([str(pg/"pg_ctl"),"-D",str(cluster),"-w","stop","-m","fast"],stdout=log,stderr=subprocess.STDOUT,env=env)
  receipt["cluster_stop_exit_code"]=stop
 if pw.exists():pw.unlink()
receipt.update(exit_code=code,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_evidence_restored=changed)
(out/"RUN-RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="source_pins"}));raise SystemExit(code)
