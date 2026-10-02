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
# GET /v1/platform/metrics and by GET /v1/status for every signed-in user) and the `operations` and
# `alerts` fields of deploy-status.json.
#
# Alert delivery (release 0.27): `ops_alerts.py notify` then sends NEW, CLEARED and (every
# ALERT_RENOTIFY_SECONDS, default 21600) REMINDER transitions, deduplicated by code and target in
# <impact home>/ops/alert-state.json, through the channels configured in config.env:
#   ALERT_WEBHOOK_URL      a generic JSON webhook (Slack-compatible `text`); ALERT_WEBHOOK_SECRET
#                          (config.env or secrets.env) signs each POST (X-Impact-Signature, HMAC-SHA256)
#   ALERT_EMAIL_TO         comma-separated addresses, sent through the worker's SMTP_* settings
#                          (a loopback SMTP host, the staging capture, is skipped)
# Without them nothing is sent and the status page remains the only signal. Secrets reach the
# notifier through its environment only and are never printed or written.
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
  notify_transitions
}

# Deliver alert transitions through the configured channels (see the header). The notifier's
# output names event kinds, codes and channel outcomes only.
notify_transitions() {
  local app_host webhook_secret smtp_password renotify
  app_host="$(env_value "$COMPOSE_ENV" APP_HOST)"
  renotify="$(env_value "$CONFIG_FILE" ALERT_RENOTIFY_SECONDS)"
  webhook_secret="$(env_value "$SECRETS_FILE" ALERT_WEBHOOK_SECRET)"
  [ -n "$webhook_secret" ] || webhook_secret="$(env_value "$CONFIG_FILE" ALERT_WEBHOOK_SECRET)"
  smtp_password="$(env_value "$CONFIG_FILE" SMTP_PASSWORD)"
  ALERT_WEBHOOK_URL="$(env_value "$CONFIG_FILE" ALERT_WEBHOOK_URL)" \
    ALERT_WEBHOOK_SECRET="$webhook_secret" \
    ALERT_EMAIL_TO="$(env_value "$CONFIG_FILE" ALERT_EMAIL_TO)" \
    SMTP_HOST="$(env_value "$CONFIG_FILE" SMTP_HOST)" \
    SMTP_PORT="$(env_value "$CONFIG_FILE" SMTP_PORT)" \
    SMTP_USERNAME="$(env_value "$CONFIG_FILE" SMTP_USERNAME)" \
    SMTP_PASSWORD="$smtp_password" \
    SMTP_FROM="$(env_value "$COMPOSE_ENV" SMTP_FROM)" \
    python3 "$DEPLOY_DIR/ops_alerts.py" notify --ops-dir "$OPS_DIR" \
    --renotify-seconds "${renotify:-21600}" \
    --deployment "${app_host:-$(hostname)}" \
    --status-url "${app_host:+https://$app_host/deploy-status.json}" ||
    log "WARNING: alert delivery failed (the status page is still current)"
}

main "$@"
