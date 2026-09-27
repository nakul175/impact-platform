"""Run design reference or implementation-facing qualification tests.
Exit 0 = all executed tests passed; 1 = failure; 3 = blocked/skipped requirements.
"""
import argparse, json, os, sys, time, unittest
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('suite',choices=['reference','integration','smoke']);p.add_argument('--report',required=True);args=p.parse_args()
report_target=Path(args.report).resolve()
os.chdir(Path(__file__).resolve().parent)
loader=unittest.TestLoader();suite=loader.discover('tests',pattern='test_'+args.suite+'.py')
planned=suite.countTestCases();started=time.time();result=unittest.TextTestRunner(verbosity=2).run(suite)
status='Fail' if result.failures or result.errors else ('Blocked' if result.skipped or result.testsRun!=planned else 'Pass')
report={'suite':args.suite,'status':status,'planned':planned,'executed':result.testsRun,'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),'duration_seconds':round(time.time()-started,3),'product_validated':False,'scope':'Design reference only' if args.suite=='reference' else 'Configured API assertions only; not full release qualification','run_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'details':{'failed':[str(t) for t,_ in result.failures],'errors':[str(t) for t,_ in result.errors],'blocked':[{'test':str(t),'reason':r} for t,r in result.skipped]}}
target=report_target;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2))
sys.exit(0 if status=='Pass' else 3 if status=='Blocked' else 1)
