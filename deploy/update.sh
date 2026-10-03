#!/usr/bin/env bash
# Bring this server to the commit checked out in the repository; run as root by
# /usr/local/bin/impact-sync after it resets /opt/impact/repo to origin/main.
#
# Idempotent, on a fresh server and on every later run: generates the secrets once, derives the
# host names, builds the application image once per commit, provisions and migrates the database,
# starts the stack, imports the identity-provider realm when absent, creates the owner's provider
# account and the first platform operator when absent, waits for health and writes the status file
# (also served at https://<app host>/deploy-status.json). It never prints a secret.
# See docs/current/DEPLOYMENT-GUIDE.md.
set -euo pipefail

# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

CURRENT_STEP="start"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COMMIT=""
RUN_LOG=""

step() {
  CURRENT_STEP=$1
  log "== $1"
}

# ---------------------------------------------------------------------------------------------
# Status file: commit, time, outcome, containers and URLs; the log tail is scrubbed of every
# value in secrets.env before it is written. Never a secret.
write_status() {
  local result=$1
  mkdir -p "$STATUS_DIR"
  local containers="[]"
  if [ -r "$COMPOSE_ENV" ]; then
    containers="$(compose ps --all --format json 2>/dev/null || echo "[]")"
  fi
  RESULT="$result" STEP="$CURRENT_STEP" COMMIT="$COMMIT" STARTED_AT="$STARTED_AT" \
    APP_HOST="${APP_HOST:-}" AUTH_HOST="${AUTH_HOST:-}" CONTAINERS="$containers" \
    RUN_LOG="$RUN_LOG" SECRETS_FILE="$SECRETS_FILE" TLS_MODE="${CADDY_TLS_MODE:-}" \
    OPERATOR="${OPERATOR_OUTCOME:-}" SCHEMA="${SCHEMA_VERSION:-}" OPS_FILE="$OPS_DIR/ops-status.json" \
    python3 - "$STATUS_DIR/deploy-status.json" "$IMPACT_HOME/status.json" <<'PY'
import json, os, sys, tempfile
from datetime import datetime, timezone

raw = os.environ["CONTAINERS"].strip()
try:
    rows = json.loads(raw) if raw.startswith("[") else [json.loads(l) for l in raw.splitlines() if l.strip()]
except ValueError:
    rows = []
services = {}
for row in rows:
    services[row.get("Service") or row.get("Name")] = {
        "state": row.get("State"),
        "health": row.get("Health") or None,
        "image": (row.get("Image") or "").split("@")[0],
    }
secrets = []
try:
    for line in open(os.environ["SECRETS_FILE"]):
        if "=" in line:
            value = line.split("=", 1)[1].strip()
            if len(value) >= 8:
                secrets.append(value)
except OSError:
    pass
tail = []
if os.environ["RUN_LOG"]:
    try:
        tail = open(os.environ["RUN_LOG"], errors="replace").read().splitlines()[-40:]
    except OSError:
        tail = []
cleaned = []
for line in tail:
    for value in secrets:
        line = line.replace(value, "[redacted]")
    cleaned.append(line[:400])
app, auth = os.environ["APP_HOST"], os.environ["AUTH_HOST"]
# The last operations check (deploy/ops-check.sh, every 5 minutes): kept across deployments.
try:
    ops = json.load(open(os.environ["OPS_FILE"]))
except (OSError, ValueError):
    ops = {}
document = {
    "result": os.environ["RESULT"],
    "step": os.environ["STEP"],
    "commit": os.environ["COMMIT"],
    "started_at": os.environ["STARTED_AT"],
    "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "environment": "staging",
    "urls": {
        "application": "https://" + app + "/" if app else None,
        "identity_provider": "https://" + auth + "/realms/impact" if auth else None,
    },
    "tls": os.environ["TLS_MODE"] or None,
    "schema_version": os.environ["SCHEMA"] or None,
    "first_operator": os.environ["OPERATOR"] or None,
    "services": services,
    "operations": ops.get("operations"),
    "alerts": ops.get("alerts", []),
    "log_tail": cleaned,
}
for target in sys.argv[1:]:
    directory = os.path.dirname(target)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".status-")
    with os.fdopen(fd, "w") as handle:
        json.dump(document, handle, indent=2)
        handle.write("\n")
    os.chmod(tmp, 0o644)
    os.replace(tmp, target)
PY
}

on_exit() {
  local code=$?
  if [ "$code" -ne 0 ]; then
    log "update FAILED at step: $CURRENT_STEP (exit $code)"
    write_status failed || true
  fi
}
trap on_exit EXIT

# ---------------------------------------------------------------------------------------------
container_health() {
  local id
  id="$(compose ps -q "$1" 2>/dev/null | head -n 1)"
  [ -n "$id" ] || {
    echo "absent"
    return
  }
  docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$id"
}

wait_for() {
  local service=$1 wanted=$2 seconds=$3 waited=0 state
  while :; do
    state="$(container_health "$service")"
    if [ "$state" = "$wanted" ]; then
      log "$service is $state"
      return 0
    fi
    if [ "$waited" -ge "$seconds" ]; then
      log "$service is still '$state' after ${seconds}s"
      compose logs --no-color --tail 40 "$service" || true
      return 1
    fi
    sleep 5
    waited=$((waited + 5))
  done
}

ensure_secret() {
  local key=$1 bytes=$2
  if [ -z "$(env_value "$SECRETS_FILE" "$key")" ]; then
    set_env_value "$SECRETS_FILE" "$key" "$(random_hex "$bytes")"
    log "generated $key"
  fi
}

# Host units: the 5-minute alert check, the weekly restore drill and log rotation for the logs this
# package writes on the host. Rewritten only when their content changes; IMPACT_HOST_UNITS=0 skips.
render_host_units() {
  local dir=$1
  cat >"$dir/impact-ops-check.service" <<EOF
[Unit]
Description=Impact Platform operations check (alerts into deploy-status.json)
After=docker.service

[Service]
Type=oneshot
Environment=IMPACT_HOME=$IMPACT_HOME
ExecStart=$DEPLOY_DIR/ops-check.sh
Nice=10
TimeoutStartSec=5min
StandardOutput=append:/var/log/impact-ops.log
StandardError=append:/var/log/impact-ops.log
EOF
  cat >"$dir/impact-ops-check.timer" <<EOF
[Unit]
Description=Impact Platform operations check every 5 minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF
  cat >"$dir/impact-restore-drill.service" <<EOF
[Unit]
Description=Impact Platform weekly restore drill (throwaway containers; live data untouched)
After=docker.service

[Service]
Type=oneshot
Environment=IMPACT_HOME=$IMPACT_HOME
ExecStart=$DEPLOY_DIR/restore-drill.sh
Nice=10
TimeoutStartSec=2h
StandardOutput=append:/var/log/impact-restore-drill.log
StandardError=append:/var/log/impact-restore-drill.log
EOF
  cat >"$dir/impact-restore-drill.timer" <<EOF
[Unit]
Description=Impact Platform restore drill every Sunday after the nightly backup

[Timer]
OnCalendar=Sun *-*-* 23:15:00 UTC
RandomizedDelaySec=15min
Persistent=true

[Install]
WantedBy=timers.target
EOF
  cat >"$dir/logrotate" <<EOF
# Impact Platform host logs (written by deploy/update.sh; regenerated on every deployment).
# An su directive in every stanza: Ubuntu's /var/log is root:syslog 0775, and without an su
# directive logrotate refuses the group-writable parent ("insecure permissions"), skips the logs
# and exits 1 whenever this file is run on its own.
/var/log/impact-deploy.log /var/log/impact-ops.log /var/log/impact-restore-drill.log {
  su root root
  weekly
  maxsize 20M
  rotate 8
  compress
  delaycompress
  missingok
  notifempty
  copytruncate
}
$STATE_DIR/admin-actions.log {
  su root root
  monthly
  rotate 24
  compress
  missingok
  notifempty
  copytruncate
}
EOF
}

install_host_units() {
  if [ "${IMPACT_HOST_UNITS:-1}" != "1" ] || [ ! -d /run/systemd/system ] || ! command -v systemctl >/dev/null; then
    log "host units: skipped (no systemd, or IMPACT_HOST_UNITS=0)"
    return 0
  fi
  local rendered name changed=0
  rendered="$(mktemp -d)"
  render_host_units "$rendered"
  for name in impact-ops-check.service impact-ops-check.timer impact-restore-drill.service impact-restore-drill.timer; do
    if ! cmp -s "$rendered/$name" "/etc/systemd/system/$name"; then
      install -m 644 "$rendered/$name" "/etc/systemd/system/$name"
      changed=1
    fi
  done
  if [ -d /etc/logrotate.d ]; then
    install -m 644 "$rendered/logrotate" /etc/logrotate.d/impact
  fi
  rm -rf "$rendered"
  if [ "$changed" = 1 ]; then
    systemctl daemon-reload
    log "host units: installed or updated"
  fi
  systemctl enable --now impact-ops-check.timer impact-restore-drill.timer >/dev/null 2>&1 ||
    log "host units: the timers could not be enabled"
}

public_ipv4() {
  curl -sf --max-time 5 http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address || true
}

# ---------------------------------------------------------------------------------------------
main() {
  require_root
  umask 077
  mkdir -p "$IMPACT_HOME" "$STATE_DIR" "$STATUS_DIR" "$CA_DIR" "$OPS_DIR"
  chmod 700 "$IMPACT_HOME" "$STATE_DIR"
  # Public certificates only (CI's internal root); the API container reads them as a non-root user.
  # The operations directory holds status files only (backup, drill, alerts; never a secret).
  chmod 755 "$STATUS_DIR" "$CA_DIR" "$OPS_DIR"
  exec 9>"$STATE_DIR/update.lock"
  if ! flock -n 9; then
    log "another update is running; nothing to do"
    exit 0
  fi
  RUN_LOG="$STATE_DIR/last-run.log"
  exec > >(tee "$RUN_LOG") 2>&1

  step "host preparation"
  # The temporary key-publishing service of the server's first boot must not hold port 80.
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files impact-pubkey.service >/dev/null 2>&1; then
    systemctl disable --now impact-pubkey.service >/dev/null 2>&1 || true
  fi
  command -v docker >/dev/null || die "docker is not installed"
  docker compose version >/dev/null || die "the docker compose plugin is not installed"
  command -v python3 >/dev/null || die "python3 is required on the host"
  COMMIT="${IMPACT_COMMIT:-$(git -c safe.directory="$REPO_DIR" -C "$REPO_DIR" rev-parse HEAD 2>/dev/null || true)}"
  [ -n "$COMMIT" ] || die "cannot determine the commit of $REPO_DIR"
  local tag="${COMMIT:0:12}"
  log "deploying commit $COMMIT"

  step "secrets"
  touch "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  ensure_secret POSTGRES_PASSWORD 32
  ensure_secret IMPACT_LOGIN_PASSWORD_APP 32
  ensure_secret IMPACT_LOGIN_PASSWORD_IDENTITY 32
  ensure_secret IMPACT_LOGIN_PASSWORD_PLATFORM 32
  ensure_secret IMPACT_LOGIN_PASSWORD_WORKER 32
  ensure_secret IMPACT_LOGIN_PASSWORD_MIGRATOR 32
  ensure_secret KEYCLOAK_DB_PASSWORD 32
  ensure_secret KEYCLOAK_ADMIN_PASSWORD 32
  ensure_secret IMPACT_COOKIE_SECRET 48
  ensure_secret IMPACT_INVITATION_SECRET 48
  ensure_secret IMPACT_DELIVERY_SECRET 48
  # v0.26a: the client secret of the realm's account-provisioning service account (user management
  # only), with which the API creates sign-in accounts from the control plane.
  ensure_secret IMPACT_PROVISIONER_SECRET 48
  if [ -z "$(env_value "$SECRETS_FILE" OWNER_TEMP_PASSWORD)" ]; then
    set_env_value "$SECRETS_FILE" OWNER_TEMP_PASSWORD "$(readable_password)"
    log "generated OWNER_TEMP_PASSWORD"
  fi

  step "configuration"
  if [ -r "$CONFIG_FILE" ]; then
    log "reading overrides from $CONFIG_FILE"
  fi
  APP_HOST="$(env_value "$CONFIG_FILE" IMPACT_APP_HOST)"
  AUTH_HOST="$(env_value "$CONFIG_FILE" IMPACT_AUTH_HOST)"
  if [ -z "$APP_HOST" ]; then
    local ip
    ip="$(public_ipv4)"
    [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
      die "no public IPv4 from the DigitalOcean metadata service; set IMPACT_APP_HOST in $CONFIG_FILE"
    APP_HOST="${ip//./-}.sslip.io"
  fi
  AUTH_HOST="${AUTH_HOST:-auth.$APP_HOST}"
  CADDY_TLS_MODE="$(env_value "$CONFIG_FILE" CADDY_TLS_MODE)"
  CADDY_TLS_MODE="${CADDY_TLS_MODE:-acme}"
  case "$CADDY_TLS_MODE" in acme | internal) ;; *) die "CADDY_TLS_MODE must be acme or internal" ;; esac
  local owner_email owner_first owner_last acme_email smtp_from region privacy recovery
  owner_email="$(env_value "$CONFIG_FILE" IMPACT_OWNER_EMAIL)"
  owner_email="${owner_email:-$DEFAULT_OWNER_EMAIL}"
  owner_first="$(env_value "$CONFIG_FILE" IMPACT_OWNER_FIRST_NAME)"
  owner_first="${owner_first:-$DEFAULT_OWNER_FIRST_NAME}"
  owner_last="$(env_value "$CONFIG_FILE" IMPACT_OWNER_LAST_NAME)"
  owner_last="${owner_last:-$DEFAULT_OWNER_LAST_NAME}"
  acme_email="$(env_value "$CONFIG_FILE" ACME_EMAIL)"
  smtp_from="$(env_value "$CONFIG_FILE" SMTP_FROM)"
  region="$(env_value "$CONFIG_FILE" IMPACT_REGION)"
  privacy="$(env_value "$CONFIG_FILE" IMPACT_PRIVACY_REFERENCE)"
  recovery="$(env_value "$CONFIG_FILE" IMPACT_RECOVERY_REFERENCE)"
  log "application https://$APP_HOST  identity provider https://$AUTH_HOST  TLS $CADDY_TLS_MODE"

  local ca_bundle=""
  if [ "$CADDY_TLS_MODE" = "internal" ]; then
    ca_bundle="/etc/impact-ca/bundle.pem"
  fi
  local tmp
  tmp="$(mktemp "$COMPOSE_ENV.XXXXXX")"
  chmod 600 "$tmp"
  {
    grep -E '^[A-Z0-9_]+=' "$SECRETS_FILE" | grep -v '^OWNER_TEMP_PASSWORD='
    printf 'IMPACT_TAG=%s\n' "$tag"
    printf 'APP_HOST=%s\nAUTH_HOST=%s\nCADDY_TLS_MODE=%s\n' "$APP_HOST" "$AUTH_HOST" "$CADDY_TLS_MODE"
    printf 'ACME_EMAIL=%s\n' "${acme_email:-$owner_email}"
    printf 'SMTP_FROM=%s\n' "${smtp_from:-impact@$APP_HOST}"
    printf 'IMPACT_STATUS_DIR=%s\nIMPACT_CA_DIR=%s\nIMPACT_CA_BUNDLE=%s\n' "$STATUS_DIR" "$CA_DIR" "$ca_bundle"
    printf 'IMPACT_OPS_DIR=%s\n' "$OPS_DIR"
    for key in SMTP_HOST SMTP_PORT SMTP_USERNAME SMTP_PASSWORD SMTP_STARTTLS SMTP_CA_FILE \
      EMAIL_RATE_LIMIT EMAIL_TENANT_RATE_LIMIT EMAIL_RATE_WINDOW_SECONDS BACKUP_HOUR_UTC BACKUP_MIN_FREE_MB; do
      local value
      value="$(env_value "$CONFIG_FILE" "$key")"
      if [ -n "$value" ]; then printf '%s=%s\n' "$key" "$value"; fi
    done
  } >"$tmp"
  mv -f "$tmp" "$COMPOSE_ENV"
  install_host_units

  if [ "$(cat "$STATE_DIR/last-success" 2>/dev/null || true)" = "$COMMIT" ] &&
    [ "$(container_health api)" = "healthy" ] && [ "$(container_health keycloak)" = "healthy" ] &&
    [ "$(container_health caddy)" = "healthy" ] && [ "$(container_health worker)" = "running" ]; then
    step "unchanged"
    log "commit $COMMIT is already deployed and healthy"
    OPERATOR_OUTCOME="$(cat "$STATE_DIR/operator" 2>/dev/null || true)"
    SCHEMA_VERSION="$(cat "$STATE_DIR/schema" 2>/dev/null || true)"
    write_status ok
    return 0
  fi

  step "image build"
  if docker image inspect "impact-platform:$tag" >/dev/null 2>&1; then
    log "image impact-platform:$tag already built"
  else
    compose build --pull api
  fi

  step "database"
  compose up -d postgres
  wait_for postgres healthy 180
  local prepared
  prepared="$(compose run --rm -T migrate | tee /dev/stderr | last_json)"
  [ -n "$prepared" ] || die "the database job printed no summary"
  SCHEMA_VERSION="$(printf '%s' "$prepared" | json_field schema_version)"
  printf '%s\n' "$SCHEMA_VERSION" >"$STATE_DIR/schema"
  log "schema version $SCHEMA_VERSION"

  step "edge"
  compose up -d caddy
  wait_for caddy healthy 120
  if [ "$CADDY_TLS_MODE" = "internal" ]; then
    local waited=0
    until compose cp caddy:/data/caddy/pki/authorities/local/root.crt "$CA_DIR/caddy-root.crt" >/dev/null 2>&1; do
      [ "$waited" -lt 60 ] || die "Caddy's internal root certificate did not appear"
      sleep 2
      waited=$((waited + 2))
    done
    cat "$CA_DIR/caddy-root.crt" /etc/ssl/certs/ca-certificates.crt >"$CA_DIR/bundle.pem" 2>/dev/null ||
      cp "$CA_DIR/caddy-root.crt" "$CA_DIR/bundle.pem"
    chmod 644 "$CA_DIR/bundle.pem" "$CA_DIR/caddy-root.crt"
  fi

  step "services"
  compose up -d --remove-orphans
  wait_for keycloak healthy 420

  step "identity provider realm"
  local realm
  realm="$(compose run --rm -T idp-admin python deploy/keycloak_admin.py realm \
    --file deploy/keycloak/realm-staging.json | tee /dev/stderr | last_json)" || true
  log "realm: $realm"
  [ -n "$realm" ] && [ -z "$(printf '%s' "$realm" | json_field error)" ] || die "realm import failed"

  step "account provisioning client"
  local provisioner
  provisioner="$(compose run --rm -T idp-admin python deploy/keycloak_admin.py provisioner |
    tee /dev/stderr | last_json)" || true
  log "provisioner: $provisioner"
  [ -n "$provisioner" ] && [ -z "$(printf '%s' "$provisioner" | json_field error)" ] ||
    die "the account provisioning client could not be set up"

  step "owner account"
  local account subject
  account="$(IMPACT_TEMP_PASSWORD="$(env_value "$SECRETS_FILE" OWNER_TEMP_PASSWORD)" \
    compose run --rm -T -e IMPACT_TEMP_PASSWORD idp-admin python deploy/keycloak_admin.py user \
    --email "$owner_email" --first-name "$owner_first" --last-name "$owner_last" | tee /dev/stderr | last_json)" || true
  log "owner account: $account"
  subject="$(printf '%s' "$account" | json_field subject)"
  [ -n "$subject" ] || die "the owner's provider account could not be created"

  step "first platform operator"
  local operator status=0
  operator="$(compose run --rm -T operator-bootstrap python scripts/bootstrap_operator.py operator \
    --issuer "https://$AUTH_HOST/realms/impact" --subject "$subject" \
    --required-acr "urn:impact:acr:mfa" \
    --region "${region:-do-blr1}" \
    --privacy-reference "${privacy:-staging-privacy-notice-v1}" \
    --recovery-reference "${recovery:-DigitalOcean daily droplet backups and nightly pg_dump on the server}" \
    --reference "First platform operator: deployment owner $owner_email, bootstrapped by deploy/update.sh at commit ${COMMIT:0:12}" |
    last_json)" || status=$?
  log "operator bootstrap: $operator"
  OPERATOR_OUTCOME="$(printf '%s' "$operator" | json_field outcome)"
  if [ "$status" -ne 0 ] && [ "$OPERATOR_OUTCOME" != "refused" ]; then
    die "the operator bootstrap failed"
  fi
  printf '%s\n' "$OPERATOR_OUTCOME" >"$STATE_DIR/operator"

  step "health"
  wait_for api healthy 240
  wait_for caddy healthy 60
  wait_for worker running 60
  wait_for mailsink running 30
  wait_for backup running 30

  step "cleanup"
  # Keep the image of this commit and of the two before it (for a quick rollback build-free).
  docker image ls impact-platform --format '{{.CreatedAt}}\t{{.Tag}}' | sort -r | awk 'NR>3 {print $2}' |
    while read -r old; do
      if [ "$old" != "$tag" ]; then docker image rm "impact-platform:$old" >/dev/null 2>&1 || true; fi
    done
  docker image prune -f >/dev/null 2>&1 || true

  step "done"
  printf '%s\n' "$COMMIT" >"$STATE_DIR/last-success"
  # Fill the status file's operations and alerts at once instead of at the next timer run.
  "$DEPLOY_DIR/ops-check.sh" >/dev/null 2>&1 || log "operations check failed (the timer retries)"
  write_status ok
  log "deployed $COMMIT; status at https://$APP_HOST/deploy-status.json"
}

main "$@"
