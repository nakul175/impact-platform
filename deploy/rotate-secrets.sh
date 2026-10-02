#!/usr/bin/env bash
# Rotate or retire the application's own secrets on the staging server without printing a value.
#
#   sudo /opt/impact/repo/deploy/rotate-secrets.sh status
#   sudo /opt/impact/repo/deploy/rotate-secrets.sh rotate --family cookie|invitation|delivery|provisioner|all \
#        [--grace-days N] [--reason TEXT] [--dry-run]
#   sudo /opt/impact/repo/deploy/rotate-secrets.sh retire --family F (--kid K | --all-previous | --expired) \
#        [--reason TEXT] [--dry-run]
#
# Edits /opt/impact/secrets.env (and the compose.env the containers start from) atomically through
# scripts/rotate_secrets.py, holding the same lock as deploy/update.sh so an automatic update cannot
# interleave, then recreates the api container (and the worker when the invitation or delivery
# family changed) so they read the new keyring. The output names key ids (kids) only. A rotation
# keeps the old secret in IMPACT_<FAMILY>_SECRET_PREVIOUS until it is retired; see
# docs/current/DEPLOYMENT-GUIDE.md "Rotating the application secrets".
#
# The provisioner family (v0.27) is the `impact-provisioner` client secret shared with Keycloak: it
# has no grace list. The new value is written to the env files first, then Keycloak is re-aligned
# to it through deploy/keycloak_admin.py rotate-provisioner (inside the idp-admin job, which reads
# compose.env), then the api is recreated. Should the re-alignment fail, the files already hold the
# new value and the next deploy/update.sh run re-aligns the provider itself (its "account
# provisioning client" step); until then account creation answers PROVIDER_ADMIN_UNAVAILABLE.
#
# The identity provider's token-signing keys are Keycloak's and are rotated in Keycloak (the API
# verifies bearer tokens through the realm JWKS by kid); database login passwords are not covered.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

container_health() {
  local id
  id="$(compose ps -q "$1" 2>/dev/null | head -n 1)"
  [ -n "$id" ] || {
    echo "absent"
    return
  }
  docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$id"
}

[ $# -ge 1 ] || die "usage: $0 status | rotate --family F [...] | retire --family F [...] (see the header)"
require_root
umask 077
[ -r "$SECRETS_FILE" ] || die "$SECRETS_FILE is missing: the first deployment has not run yet"
command -v python3 >/dev/null || die "python3 is required on the host"

dry_run=""
for argument in "$@"; do
  if [ "$argument" = "--dry-run" ]; then dry_run=1; fi
done
command=$1
shift
# rotate_secrets.py takes --dry-run before the command.
args=()
for argument in "$@"; do
  if [ "$argument" != "--dry-run" ]; then args+=("$argument"); fi
done
global=(--env-file "$SECRETS_FILE")
if [ -f "$COMPOSE_ENV" ]; then global+=(--sync-to "$COMPOSE_ENV"); fi
if [ -n "$dry_run" ]; then global+=(--dry-run); fi

mkdir -p "$STATE_DIR"
exec 9>"$STATE_DIR/update.lock"
flock -w 600 9 || die "deploy/update.sh is still running; try again later"

result="$(python3 "$REPO_DIR/scripts/rotate_secrets.py" "${global[@]}" "$command" "${args[@]}")"
printf '%s\n' "$result"
if [ "$command" = "status" ] || [ -n "$dry_run" ]; then
  exit 0
fi

require_compose_env
realign="$(printf '%s' "$result" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin).get("provider_realign", [])))')"
if [ -n "$realign" ]; then
  log "re-aligning the identity provider: $realign"
  provider="$(compose run --rm -T idp-admin python deploy/keycloak_admin.py rotate-provisioner 2>/dev/null | last_json)" || true
  log "provider: $provider"
  [ -n "$provider" ] && [ -z "$(printf '%s' "$provider" | json_field error)" ] ||
    die "the identity provider was not re-aligned; the files hold the new secret and the next deploy/update.sh run re-aligns it (see the header)"
fi
services="$(printf '%s' "$result" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin).get("restart_required", [])))')"
if [ -z "$services" ]; then
  log "nothing to restart"
  exit 0
fi
log "recreating: $services"
# shellcheck disable=SC2086  # service names are single words
compose up -d --no-deps --force-recreate $services
for service in $services; do
  waited=0
  while :; do
    state="$(container_health "$service")"
    if [ "$state" = "healthy" ] || { [ "$service" = "worker" ] && [ "$state" = "running" ]; }; then
      log "$service is $state"
      break
    fi
    if [ "$waited" -ge 180 ]; then
      die "$service is still '$state' after 180s; the previous secrets are kept in grace, see the deployment guide"
    fi
    sleep 5
    waited=$((waited + 5))
  done
done
log "rotation applied; values made with the grace keys keep working until they are retired"
