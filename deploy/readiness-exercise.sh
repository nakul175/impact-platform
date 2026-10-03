#!/usr/bin/env bash
# Readiness exercise (release 0.27, VF-SUP-001 / VF-OBS-001): rehearses, on the server or in the CI
# container stack, that a critical failure is alerted, delivered and cleared, and records the
# evidence in <impact home>/ops/readiness-exercise.json.
#
#   sudo /opt/impact/repo/deploy/readiness-exercise.sh
#
# Steps (each timed, each PASS or FAIL in the record):
#   1. baseline        the alert check runs; the live alert codes are recorded
#   2. worker stopped  `compose stop worker`, then the alert check must raise WORKER_STALE and
#                      CONTAINER_UNHEALTHY (worker) and the notifier must record them as active
#                      (alert-state.json), delivering NEW through the configured channels
#   3. worker started  `compose start worker`, then repeated checks until both alerts have cleared
#                      (the notifier delivers CLEARED); the time to clear is recorded
#   4. disk simulation an evaluation against a scratch copy of the operations directory with a
#                      synthetic nearly-full file system must raise DISK_LOW, deliver it as NEW
#                      labelled "<deployment> (exercise)", and clear it on the next evaluation;
#                      the live status files are never touched by this step
#
# The live worker is stopped for about one check (seconds); queued deliveries wait and are sent
# when it is back. Run it in a quiet period. Nothing here reads or prints a secret: the notifier
# gets the configured channels through ops-check.sh's own mechanism (config.env / secrets.env).
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

OPS_DIR="$IMPACT_HOME/ops"
RECORD="$OPS_DIR/readiness-exercise.json"
MAX_CLEAR_CHECKS="${MAX_CLEAR_CHECKS:-30}"

steps_json=""
exercise_failed=0
scratch=""

record_step() { # name outcome seconds detail-json
  local entry
  entry="$(printf '{"step":"%s","outcome":"%s","seconds":%s,"detail":%s}' "$1" "$2" "$3" "$4")"
  steps_json="${steps_json:+$steps_json,}$entry"
  log "step $1: $2 (${3}s)"
  [ "$2" = "PASS" ] || exercise_failed=1
}

alert_codes() { # file -> JSON array of codes
  python3 -c 'import json,sys; print(json.dumps(sorted(a["code"] for a in json.load(open(sys.argv[1]))["alerts"])))' "$1"
}

has_codes() { # file code...
  python3 - "$@" <<'PY'
import json, sys
codes = {a["code"] for a in json.load(open(sys.argv[1]))["alerts"]}
sys.exit(0 if set(sys.argv[2:]) <= codes else 1)
PY
}

lacks_codes() { # file code...
  python3 - "$@" <<'PY'
import json, sys
codes = {a["code"] for a in json.load(open(sys.argv[1]))["alerts"]}
sys.exit(0 if not (set(sys.argv[2:]) & codes) else 1)
PY
}

active_keys() { # state file -> JSON array of active keys
  python3 -c 'import json,sys
try:
    print(json.dumps(sorted(json.load(open(sys.argv[1])).get("active", {}))))
except (OSError, ValueError):
    print("[]")' "$1"
}

main() {
  require_root
  require_compose_env
  mkdir -p "$OPS_DIR"
  local started t0 t1 codes detail
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # 1. baseline
  t0=$(date +%s)
  "$DEPLOY_DIR/ops-check.sh" >/dev/null
  t1=$(date +%s)
  codes="$(alert_codes "$OPS_DIR/ops-status.json")"
  record_step baseline PASS $((t1 - t0)) "{\"alerts\":$codes}"

  # 2. worker stopped -> alerted
  t0=$(date +%s)
  compose stop worker >/dev/null 2>&1
  "$DEPLOY_DIR/ops-check.sh" >/dev/null
  t1=$(date +%s)
  codes="$(alert_codes "$OPS_DIR/ops-status.json")"
  detail="{\"alerts\":$codes,\"active\":$(active_keys "$OPS_DIR/alert-state.json")}"
  if has_codes "$OPS_DIR/ops-status.json" WORKER_STALE CONTAINER_UNHEALTHY &&
    python3 -c 'import json,sys; a=json.load(open(sys.argv[1])).get("active",{}); sys.exit(0 if "WORKER_STALE|" in a and "CONTAINER_UNHEALTHY|worker" in a else 1)' "$OPS_DIR/alert-state.json"; then
    record_step worker_stopped PASS $((t1 - t0)) "$detail"
  else
    record_step worker_stopped FAIL $((t1 - t0)) "$detail"
  fi

  # 3. worker started -> cleared
  t0=$(date +%s)
  compose start worker >/dev/null 2>&1
  local i cleared=0
  for i in $(seq 1 "$MAX_CLEAR_CHECKS"); do
    "$DEPLOY_DIR/ops-check.sh" >/dev/null
    if lacks_codes "$OPS_DIR/ops-status.json" WORKER_STALE CONTAINER_UNHEALTHY; then
      cleared=1
      break
    fi
    sleep 5
  done
  t1=$(date +%s)
  codes="$(alert_codes "$OPS_DIR/ops-status.json")"
  detail="{\"alerts\":$codes,\"checks\":$i,\"active\":$(active_keys "$OPS_DIR/alert-state.json")}"
  if [ "$cleared" = 1 ] &&
    python3 -c 'import json,sys; a=json.load(open(sys.argv[1])).get("active",{}); sys.exit(1 if "WORKER_STALE|" in a or "CONTAINER_UNHEALTHY|worker" in a else 0)' "$OPS_DIR/alert-state.json"; then
    record_step worker_started PASS $((t1 - t0)) "$detail"
  else
    record_step worker_started FAIL $((t1 - t0)) "$detail"
  fi

  # 4. disk simulation in a scratch copy (the live status files are not touched)
  t0=$(date +%s)
  scratch="$(mktemp -d)"
  trap 'rm -rf "${scratch:-}"' EXIT
  cp "$OPS_DIR/backup-status.json" "$scratch/" 2>/dev/null || true
  cp "$OPS_DIR/restore-drill.json" "$scratch/" 2>/dev/null || true
  compose ps --all --format json >"$scratch/containers.json" 2>/dev/null || echo "[]" >"$scratch/containers.json"
  echo '{"workers":{"running_fresh":1,"stale_after_seconds":120,"newest_beat_age_seconds":1},"deliveries":{"dead":0,"unsent":0},"jobs":{"unfinished":0},"schema_version":0,"schema_expected":0}' >"$scratch/app.json"
  echo '{"root":{"free_mb":700,"total_mb":80000}}' >"$scratch/disk-low.json"
  echo '{"root":{"free_mb":40000,"total_mb":80000}}' >"$scratch/disk-ok.json"
  local app_host
  app_host="$(env_value "$COMPOSE_ENV" APP_HOST)"
  python3 "$DEPLOY_DIR/ops_alerts.py" evaluate --ops-dir "$scratch" --containers "$scratch/containers.json" \
    --app "$scratch/app.json" --disk "$scratch/disk-low.json" --secrets-file "$SECRETS_FILE" >/dev/null
  local low_codes
  low_codes="$(alert_codes "$scratch/ops-status.json")"
  OPS_DIR="$scratch" notify_exercise "${app_host:-$(hostname)} (exercise)" >"$scratch/notify-low.json"
  python3 "$DEPLOY_DIR/ops_alerts.py" evaluate --ops-dir "$scratch" --containers "$scratch/containers.json" \
    --app "$scratch/app.json" --disk "$scratch/disk-ok.json" --secrets-file "$SECRETS_FILE" >/dev/null
  OPS_DIR="$scratch" notify_exercise "${app_host:-$(hostname)} (exercise)" >"$scratch/notify-ok.json"
  t1=$(date +%s)
  detail="{\"alerts_low\":$low_codes,\"delivery_low\":$(cat "$scratch/notify-low.json"),\"delivery_cleared\":$(cat "$scratch/notify-ok.json")}"
  if has_codes "$scratch/ops-status.json" DISK_LOW; then
    record_step disk_simulation FAIL $((t1 - t0)) "$detail"
  elif python3 -c 'import json,sys; sys.exit(0 if "DISK_LOW" in json.loads(sys.argv[1]) else 1)' "$low_codes" &&
    python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if any(e["event"]=="NEW" and "DISK_LOW" in e["codes"] for e in d["events"]) else 1)' "$scratch/notify-low.json" &&
    python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if any(e["event"]=="CLEARED" and "DISK_LOW" in e["codes"] for e in d["events"]) else 1)' "$scratch/notify-ok.json"; then
    record_step disk_simulation PASS $((t1 - t0)) "$detail"
  else
    record_step disk_simulation FAIL $((t1 - t0)) "$detail"
  fi

  python3 - "$RECORD" "$started" "$exercise_failed" "$steps_json" <<'PY'
import json, sys, datetime
path, started, failed, steps = sys.argv[1:5]
record = {
    "schema": "impact-readiness-exercise-v1",
    "started_at": started,
    "finished_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "outcome": "FAIL" if failed == "1" else "PASS",
    "steps": json.loads("[" + steps + "]"),
}
with open(path, "w") as handle:
    json.dump(record, handle, indent=2, sort_keys=True)
    handle.write("\n")
print(json.dumps({"outcome": record["outcome"], "steps": [(s["step"], s["outcome"], s["seconds"]) for s in record["steps"]]}))
PY
  chmod 644 "$RECORD"
  [ "$exercise_failed" = 0 ]
}

# The notifier with the channels ops-check.sh configures, against $OPS_DIR (the scratch copy).
notify_exercise() {
  local webhook_secret renotify
  webhook_secret="$(env_value "$SECRETS_FILE" ALERT_WEBHOOK_SECRET)"
  [ -n "$webhook_secret" ] || webhook_secret="$(env_value "$CONFIG_FILE" ALERT_WEBHOOK_SECRET)"
  renotify="$(env_value "$CONFIG_FILE" ALERT_RENOTIFY_SECONDS)"
  ALERT_WEBHOOK_URL="$(env_value "$CONFIG_FILE" ALERT_WEBHOOK_URL)" \
    ALERT_WEBHOOK_SECRET="$webhook_secret" \
    ALERT_EMAIL_TO="$(env_value "$CONFIG_FILE" ALERT_EMAIL_TO)" \
    SMTP_HOST="$(env_value "$CONFIG_FILE" SMTP_HOST)" \
    SMTP_PORT="$(env_value "$CONFIG_FILE" SMTP_PORT)" \
    SMTP_USERNAME="$(env_value "$CONFIG_FILE" SMTP_USERNAME)" \
    SMTP_PASSWORD="$(env_value "$CONFIG_FILE" SMTP_PASSWORD)" \
    SMTP_FROM="$(env_value "$COMPOSE_ENV" SMTP_FROM)" \
    python3 "$DEPLOY_DIR/ops_alerts.py" notify --ops-dir "$OPS_DIR" \
    --renotify-seconds "${renotify:-21600}" --deployment "$1"
}

main "$@"
