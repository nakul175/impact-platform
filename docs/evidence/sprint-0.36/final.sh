#!/bin/bash
cd /home/claude/impact-platform
S=/tmp/claude-0/-home-claude/b5506d01-954b-5258-ba8c-af2eb1325fb6/scratchpad
F=$S/final; : > $F/summary.txt
export PATH=/usr/lib/postgresql/16/bin:$PATH
snap() { d=$F/$1; mkdir -p $d; git status --short docs/evidence | awk '{print $2}' | while read f; do [ -f "$f" ] && cp "$f" $d/; done; }
step() { echo "$1 rc=$2" >> $F/summary.txt; }
make lint PYTHON=python3.12 > $F/lint.txt 2>&1; step lint $?
npm run build --prefix apps/web > $F/build.txt 2>&1; step build $?
(cd apps/web && npx tsc --noEmit -p . > $F/tsc.txt 2>&1); step tsc $?
for c in ai-plan-export-adapter-check ai-plan-review-model-check ai-practice-starter-model-check ai-walkthrough-adapter-check ai-procurement-preview-model-check; do
  node --experimental-strip-types tools/browser/$c.mjs > $F/pure-$c.txt 2>&1; step pure-$c $?
done
snap pure
$S/run26.sh > $S/run26-final.out 2>&1
cp -r $S/browser26 $F/browser26-final-run
step browser26 "see browser26-final-run/summary.txt"
psql -h 127.0.0.1 -p 55437 -U postgres -q -c "create database impact_test_c036d"
IMPACT_PORT=8371 IMPACT_FIXTURE_DSN="postgresql://postgres@127.0.0.1:55437/impact_test_c036d" IMPACT_UPGRADE_BASELINE=33 IMPACT_PG_BIN=/usr/lib/postgresql/16/bin .venv/bin/python scripts/run.py test --native > $F/native-final.txt 2>&1; step native $?
snap native
echo ALLDONE >> $F/summary.txt
