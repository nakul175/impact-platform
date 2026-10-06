#!/bin/bash
# Sequential 26-mode browser run. One log + one evidence snapshot per mode; never stops on failure.
cd /home/claude/impact-platform
OUT=/tmp/claude-0/-home-claude/b5506d01-954b-5258-ba8c-af2eb1325fb6/scratchpad/browser26
modes="browser admin-browser measurement-browser planning-browser ai-enablement-browser ai-planning-browser ai-saved-review-browser ai-walkthrough-browser tola-ai-sprint-browser tola-ai-extension-browser ai-plan-export-browser dashboard-browser forms-browser reporting-browser workspace-browser tenant-browser bootstrap-browser recovery-browser renewal-browser import-browser evidence-browser export-browser requeue-browser a11y-browser operators-browser status-browser"
port=8300
: > $OUT/summary.txt
for m in $modes; do
  port=$((port+1)); mkdir -p $OUT/$m
  start=$(date +%s)
  if [ "$m" = status-browser ]; then export IMPACT_OPS_STATUS_FILE=$PWD/.local/status-browser/ops-status.json; mkdir -p .local/status-browser; fi
  IMPACT_PORT=$port timeout 2400 .venv/bin/python scripts/run.py $m > $OUT/$m/log.txt 2>&1
  rc=$?
  unset IMPACT_OPS_STATUS_FILE
  end=$(date +%s)
  git status --short docs/evidence | awk '{print $2}' | while read f; do [ -f "$f" ] && cp "$f" $OUT/$m/; done
  echo "$m rc=$rc secs=$((end-start))" >> $OUT/summary.txt
done
echo DONE >> $OUT/summary.txt
