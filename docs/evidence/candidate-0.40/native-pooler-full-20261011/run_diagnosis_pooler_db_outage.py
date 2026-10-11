from pathlib import Path
import subprocess,os,json,datetime,hashlib,shutil,secrets,socket,uuid,shlex
project=Path(__file__).resolve().parents[2]
root=project/"work/imprana-diagnosis-20261011"
out=Path(__file__).resolve().parent/"diagnosis-pooler-db-outage-run-1";out.mkdir(exist_ok=False)
pg=Path(__file__).resolve().parent/"installed/bin"
private=root/".local"/("native-10h-"+uuid.uuid4().hex[:8]);private.mkdir(mode=0o700)
cluster=private/"cluster";pw=private/"bootstrap-password";password=secrets.token_urlsafe(32);pw.write_text(password+"\n");pw.chmod(0o600)
sock=Path("/private/tmp")/("imprana-pg-"+uuid.uuid4().hex[:8]);sock.mkdir(mode=0o700)
with socket.socket() as s:s.bind(("127.0.0.1",0));port=s.getsockname()[1]
env=os.environ.copy();env["PATH"]=str(project/"outputs/imprana-pooler-runtime-20261011/installed/bin")+os.pathsep+str(pg)+os.pathsep+env["PATH"]
receipt={"started_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"source_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),"engine":"native PostgreSQL 17.10, private loopback disposable cluster","runtime_path":str(pg),"cluster_path":str(cluster),"port":port,"upgrade_baseline":45,"production_data":False,"paid_resources":False,"source_pins":{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/"scripts/run.py", root/"scripts/pooler.py"]+list((root/"apps/api").rglob("*.py"))+list((root/"qualification").glob("*.py"))+list((root/"infrastructure/migrations").glob("*.sql"))+list((root/"docs/engineering/delivery-system-20261011").glob("*.CANDIDATE.sql"))}}
receipt["pooler_binary_sha256"]=hashlib.sha256((project/"outputs/imprana-pooler-runtime-20261011/installed/bin/pgbouncer").read_bytes()).hexdigest()
(out/"RUN-RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
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
 env.update(IMPACT_FIXTURE_DSN=f"postgresql://postgres:{password}@127.0.0.1:{port}/impact_test_imprana_10h",IMPACT_PORT="8372",IMPACT_PG_BIN=str(pg),IMPACT_UPGRADE_BASELINE="45",PYTHONDONTWRITEBYTECODE="1")
 env["IMPACT_DB_STOP_COMMAND"]=shlex.join([str(pg/"pg_ctl"),"-D",str(cluster),"-w","-t","60","stop","-m","fast"])
 env["IMPACT_DB_START_COMMAND"]=shlex.join([str(pg/"pg_ctl"),"-D",str(cluster),"-l",str(private/"server.log"),"-o",f"-h 127.0.0.1 -p {port} -k {sock}","-w","-t","60","start"])
 with (out/"native-restart.log").open("w") as log:
  code=subprocess.call([str(project/"work/impact-platform/.venv/bin/python"),"-B","scripts/run.py","test","--native","--pooler","pgbouncer","--perf","--skip-upgrade-check","--skip-restart-check","--skip-restore-drill","--pytest-path","qualification/test_native_nonfunctional.py::test_native_database_restart_api_and_worker_recover_without_restart_and_receipts_hold"],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
finally:
 directories=[d for d in (root/".local").glob("test-*") if d.stat().st_mtime >= datetime.datetime.fromisoformat(receipt["started_at"]).timestamp()]
 if directories:
  latest=max(directories,key=lambda path:path.stat().st_mtime)
  for name in ["perf-tests.xml","database-restart.json"]:
   extra=latest/name
   if extra.exists():shutil.copy2(extra,out/name)
  for extra in latest.glob("*restart-worker*.log"):
   shutil.copy2(extra,out/extra.name)
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
receipt["source_pins_stable"] = all(hashlib.sha256((root/key).read_bytes()).hexdigest()==value for key,value in receipt["source_pins"].items())
receipt.update(exit_code=code,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),historical_evidence_restored=changed)
(out/"RUN-RECEIPT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({k:v for k,v in receipt.items() if k!="source_pins"}));raise SystemExit(code)
