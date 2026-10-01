#!/usr/bin/env bash
# Give a person a new one-time password (run by the owner in the server console):
#
#   sudo /opt/impact/repo/deploy/reset-user.sh person@example.org          forgotten password
#   sudo /opt/impact/repo/deploy/reset-user.sh person@example.org --totp   also remove their
#                                                                          authenticator app (lost phone)
#
# The person must choose a new password at their next sign-in (and, with --totp, set up an
# authenticator app again). A temporary lock after wrong passwords is lifted too. The one-time
# password is printed to this console only: never to a log, a file or the status page. Hand it
# over yourself. There is no e-mail provider yet, so this is the account-recovery path.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

totp=""
if [ $# -eq 2 ] && [ "$2" = "--totp" ]; then
  totp="--totp"
elif [ $# -ne 1 ]; then
  die "usage: $0 <email> [--totp]"
fi
email="$1"
[[ "$email" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]] || die "not an e-mail address: $email"

require_root
require_compose_env
if [ ! -t 1 ] && [ "${IMPACT_ALLOW_NON_TTY:-}" != "1" ]; then
  die "refusing to print a password to something that is not a terminal"
fi
app_host="$(env_value "$COMPOSE_ENV" APP_HOST)"

password="$(readable_password)"
args=(reset --email "$email")
if [ -n "$totp" ]; then args+=(--totp); fi
result="$(IMPACT_TEMP_PASSWORD="$password" compose run --rm -T -e IMPACT_TEMP_PASSWORD idp-admin \
  python deploy/keycloak_admin.py "${args[@]}" 2>/dev/null | last_json)"
if [ "$(printf '%s' "$result" | json_field password_reset)" != "true" ]; then
  die "the reset failed: $(printf '%s' "$result" | json_field error) (list accounts with: sudo $DEPLOY_DIR/list-users.sh)"
fi
removed="$(printf '%s' "$result" | json_field totp_removed)"
log "reset the password of $email (authenticators removed: ${removed:-0})" >>"$STATE_DIR/admin-actions.log"

lines=(
  "New one-time password for $email"
  ""
  "Sign in at:          https://$app_host/"
  "Username:            $email"
  "One-time password:   $password"
  ""
  "At the next sign-in they choose a new password."
)
if [ -n "$totp" ]; then
  lines+=("Their authenticator app was removed: they set up a new one at sign-in.")
fi
lines+=("This password is shown only here. Hand it over yourself.")
box "${lines[@]}"
