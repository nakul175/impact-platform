#!/usr/bin/env bash
# Weekly restore drill on the server (systemd timer impact-restore-drill.timer, installed by
# deploy/update.sh; or by hand: sudo /opt/impact/repo/deploy/restore-drill.sh [daily/YYYYMMDD]).
#
# Restores the newest backup set (or the one named) into throwaway containers of the Compose profile
# "drill" - a PostgreSQL with its own anonymous volume on its own internal network, which sees the
# backup sets read-only and nothing of the live database - then runs the checks of
# deploy/restore_check.py (object digests against the restored file_blob rows, migrator checksum
# pass, ownership and tenant fences, the identity provider's realm) and removes the containers and
# their volume again. Live data is never touched.
#
# The result goes to <impact home>/ops/restore-drill.json and, through deploy/ops-check.sh, into
# deploy-status.json: outcome, the set restored, how long the restore took end to end (the measured
# recovery time for a database of this size on this server) and how old the set was (the recovery
# point: at most 24 hours plus the time a failing nightly run goes unnoticed). Nothing secret is
# written; the drill database's password is generated per run and exists only in the containers'
# environment for the length of the drill.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

OPS_DIR="$IMPACT_HOME/ops"
RESULT_FILE="$OPS_DIR/restore-drill.json"

drill() { compose --profile drill "$@"; }

cleanup() {
  drill rm -s -f -v drill-db drill-check >/dev/null 2>&1 || true
}

# write_result <outcome> <started epoch> <restore json> <check json> <error>
write_result() {
  mkdir -p "$OPS_DIR"
  chmod 755 "$OPS_DIR"
  OUTCOME="$1" STARTED="$2" RESTORE="$3" CHECK="$4" ERROR="$5" FINISHED="$(date -u +%s)" \
    python3 "$DEPLOY_DIR/ops_alerts.py" drill-result "$RESULT_FILE"
}

main() {
  require_root
  require_compose_env
  local requested="${1:-}"
  if [ -n "$requested" ] && ! [[ "$requested" =~ ^(daily|weekly)/[0-9]{8}$ ]]; then
    die "usage: $0 [daily/YYYYMMDD | weekly/YYYYMMDD]"
  fi
  mkdir -p "$STATE_DIR"
  exec 8>"$STATE_DIR/restore-drill.lock"
  flock -n 8 || die "another restore drill is running"
  local started restore="" checked="" error=""
  started="$(date -u +%s)"
  DRILL_DB_PASSWORD="$(random_hex 24)"
  export DRILL_DB_PASSWORD
  trap cleanup EXIT
  cleanup
  log "restore drill: starting a throwaway database"
  if ! drill up -d drill-db >/dev/null; then
    error="DRILL_DATABASE_DID_NOT_START"
  else
    local waited=0
    until drill exec -T drill-db pg_isready -q -U postgres >/dev/null 2>&1; do
      if [ "$waited" -ge 120 ]; then
        error="DRILL_DATABASE_NOT_READY"
        break
      fi
      sleep 2
      waited=$((waited + 2))
    done
  fi
  if [ -z "$error" ]; then
    log "restore drill: restoring ${requested:-the newest set}"
    restore="$(drill exec -T drill-db /bin/bash /opt/drill/drill_restore.sh ${requested:+"$requested"} | last_json)" || true
    if [ -z "$restore" ] || [ "$(printf '%s' "$restore" | json_field result)" != "ok" ]; then
      error="RESTORE_FAILED"
    fi
  fi
  if [ -z "$error" ]; then
    local set
    set="$(printf '%s' "$restore" | json_field set)"
    log "restore drill: checking $set"
    checked="$(PGPASSWORD="$DRILL_DB_PASSWORD" drill run --rm -T -e PGPASSWORD drill-check \
      python deploy/restore_check.py --set "$set" | last_json)" || true
    if [ -z "$checked" ] || [ "$(printf '%s' "$checked" | json_field outcome)" != "PASS" ]; then
      error="CHECKS_FAILED"
    fi
  fi
  cleanup
  if [ -z "$error" ]; then
    write_result PASS "$started" "$restore" "$checked" ""
  else
    write_result FAIL "$started" "$restore" "$checked" "$error"
  fi
  log "restore drill: $(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["outcome"], "in", d["duration_seconds"], "s; set", d.get("set"), "aged", d.get("backup_age_hours"), "h", d.get("error") or "")' "$RESULT_FILE")"
  # Refresh deploy-status.json at once (best effort).
  "$DEPLOY_DIR/ops-check.sh" >/dev/null 2>&1 || true
  [ -z "$error" ]
}

main "$@"
