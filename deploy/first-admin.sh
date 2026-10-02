#!/usr/bin/env bash
# Show the owner's one-time sign-in details, in the owner's own console session only.
#
#   sudo /opt/impact/repo/deploy/first-admin.sh              show the temporary password while it
#                                                            has not yet been replaced
#   sudo /opt/impact/repo/deploy/first-admin.sh --reset      issue a new temporary password
#   sudo /opt/impact/repo/deploy/first-admin.sh --reset-totp as --reset, and also remove the
#                                                            account's authenticator app
#
# Meant for the DigitalOcean Web Console (Droplet -> Access -> Launch Droplet Console). The
# password is printed to this terminal and nowhere else: not to the deployment log, not to the
# status page. Once the owner has chosen a new password at first sign-in, running this again
# reveals nothing. There is no e-mail provider yet, so --reset is the account-recovery path.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

reset=""
case "${1:-}" in
"") ;;
--reset) reset="password" ;;
--reset-totp) reset="totp" ;;
*) die "usage: $0 [--reset | --reset-totp]" ;;
esac

require_root
require_compose_env
if [ ! -t 1 ] && [ "${IMPACT_ALLOW_NON_TTY:-}" != "1" ]; then
  die "refusing to print a password to something that is not a terminal"
fi

owner_email="$(env_value "$CONFIG_FILE" IMPACT_OWNER_EMAIL)"
owner_email="${owner_email:-$DEFAULT_OWNER_EMAIL}"
app_host="$(env_value "$COMPOSE_ENV" APP_HOST)"
auth_host="$(env_value "$COMPOSE_ENV" AUTH_HOST)"

status="$(compose run --rm -T idp-admin python deploy/keycloak_admin.py status --email "$owner_email" 2>/dev/null | last_json)"
[ -n "$status" ] || die "the identity provider did not answer; check https://$app_host/deploy-status.json"
[ "$(printf '%s' "$status" | json_field exists)" = "true" ] ||
  die "no account for $owner_email yet: the deployment has not finished (see https://$app_host/deploy-status.json)"

if [ -n "$reset" ]; then
  password="$(readable_password)"
  args=(reset --email "$owner_email")
  if [ "$reset" = "totp" ]; then args+=(--totp); fi
  result="$(IMPACT_TEMP_PASSWORD="$password" compose run --rm -T -e IMPACT_TEMP_PASSWORD idp-admin \
    python deploy/keycloak_admin.py "${args[@]}" 2>/dev/null | last_json)"
  [ "$(printf '%s' "$result" | json_field password_reset)" = "true" ] || die "the reset failed: $result"
  set_env_value "$SECRETS_FILE" OWNER_TEMP_PASSWORD "$password"
  log "issued a new temporary password for $owner_email (authenticator removed: $(printf '%s' "$result" | json_field totp_removed))" \
    >>"$STATE_DIR/admin-actions.log"
elif [ "$(printf '%s' "$status" | json_field temporary_password_pending)" != "true" ]; then
  box "Impact Platform (staging)" "" \
    "Address:    https://$app_host/" \
    "Username:   $owner_email" "" \
    "The owner account has already chosen its own password, so there is nothing to show." \
    "Forgot the password?          sudo $0 --reset" \
    "Lost the authenticator app?   sudo $0 --reset-totp"
  exit 0
fi

password="$(env_value "$SECRETS_FILE" OWNER_TEMP_PASSWORD)"
box "Impact Platform (staging) - your first sign-in" "" \
  "Address:              https://$app_host/" \
  "Username:             $owner_email" \
  "Temporary password:   $password"
cat <<EOF
  1. On your computer, open   https://$app_host/
     and choose "Sign in". You are sent to https://$auth_host/ .
  2. Username:                $owner_email
     Temporary password:      $password
  3. The sign-in service then asks for two things (in its own order):
     - an authenticator app: scan the QR code with Google Authenticator, Microsoft
       Authenticator or similar and type the 6-digit code; every sign-in asks for a code;
     - a new password (6 characters or more on this test server, not your e-mail address); it replaces the
       temporary one at once.
  4. You land in the platform as the platform operator (Tenant lifecycle).

  This password works once and is shown only here. Close this console when you are done.

EOF
