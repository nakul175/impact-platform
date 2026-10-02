#!/usr/bin/env bash
# The server's alert check (systemd timer impact-ops-check.timer every 5 minutes, installed by
# deploy/update.sh; or by hand: sudo /opt/impact/repo/deploy/ops-check.sh).
#
# Collects, without contacting anything outside the server: the containers' states, the backup
# container's status (<impact home>/ops/backup-status.json), the last restore drill, free disk
# space of / and of Docker's data directory, and the API's operations summary (worker heartbeats,
# DEAD and unsent deliveries, unfinished jobs, schema), read with `python -m impact_api.ops_metrics`
# inside the running API container on its own platform connection. deploy/ops_alerts.py turns them
# into closed alert codes and writes <impact home>/ops/ops-status.json (also read by the operator-only
# GET /v1/platform/metrics) and the `operations` and `alerts` fields of deploy-status.json.
# No secret is read into or written by this script; nothing is sent anywhere (there is no paid
# monitoring service: the status page is the signal).
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

OPS_DIR="$IMPACT_HOME/ops"

# disk_json: free and total MB of / and of Docker's data directory.
disk_json() {
  local root docker_root
  root="$(df -Pk / | awk 'NR==2 {printf "{\"free_mb\":%d,\"total_mb\":%d}", $4/1024, $2/1024}')"
  docker_root="$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || true)"
  if [ -n "$docker_root" ] && [ -d "$docker_root" ]; then
    printf '{"root":%s,"docker":%s}' "$root" \
      "$(df -Pk "$docker_root" | awk 'NR==2 {printf "{\"free_mb\":%d,\"total_mb\":%d}", $4/1024, $2/1024}')"
  else
    printf '{"root":%s}' "$root"
  fi
}

main() {
  require_root
  require_compose_env
  mkdir -p "$OPS_DIR" "$STATE_DIR"
  chmod 755 "$OPS_DIR"
  exec 7>"$STATE_DIR/ops-check.lock"
  flock -w 120 7 || die "another operations check has held the lock for 2 minutes"
  work="$(mktemp -d)"
  trap 'rm -rf "$work"' EXIT
  compose ps --all --format json >"$work/containers.json" 2>/dev/null || echo "[]" >"$work/containers.json"
  if ! timeout 60 docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$COMPOSE_ENV" \
    exec -T api python -m impact_api.ops_metrics 2>/dev/null | last_json >"$work/app.json"; then
    echo '{"error":"API_NOT_REACHABLE"}' >"$work/app.json"
  fi
  [ -s "$work/app.json" ] || echo '{"error":"NO_SUMMARY"}' >"$work/app.json"
  disk_json >"$work/disk.json"
  python3 "$DEPLOY_DIR/ops_alerts.py" evaluate --ops-dir "$OPS_DIR" \
    --containers "$work/containers.json" --app "$work/app.json" --disk "$work/disk.json" \
    --secrets-file "$SECRETS_FILE" \
    --status-file "$STATUS_DIR/deploy-status.json" --status-file "$IMPACT_HOME/status.json"
}

main "$@"
