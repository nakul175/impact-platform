#!/usr/bin/env bash
# Give one more person a sign-in on this deployment (run by the owner in the server console):
#
#   sudo /opt/impact/repo/deploy/add-user.sh person@example.org "First" "Last"   (names required:
#   the identity provider asks for them otherwise, and the platform shows them)
#
# Creates the person's identity-provider account (e-mail as username, a temporary password that
# must be replaced at first sign-in, an authenticator app required) and registers that account as
# a platform identity with no authority at all. What the person may then do is decided only
# through the platform's own reviewed procedures: an operator names them as a tenant owner, a
# tenant administrator invites them, and so on. The temporary password is printed to this
# terminal once and is not stored; hand it over in person or by a channel you trust.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -eq 3 ] || die "usage: $0 <email> <first name> <last name>"
email="$1"
first="$2"
last="$3"
[[ "$email" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]] || die "not an e-mail address: $email"

require_root
require_compose_env
if [ ! -t 1 ] && [ "${IMPACT_ALLOW_NON_TTY:-}" != "1" ]; then
  die "refusing to print a password to something that is not a terminal"
fi
auth_host="$(env_value "$COMPOSE_ENV" AUTH_HOST)"
app_host="$(env_value "$COMPOSE_ENV" APP_HOST)"

password="$(readable_password)"
account="$(IMPACT_TEMP_PASSWORD="$password" compose run --rm -T -e IMPACT_TEMP_PASSWORD idp-admin \
  python deploy/keycloak_admin.py user --email "$email" --first-name "$first" --last-name "$last" \
  2>/dev/null | last_json)"
subject="$(printf '%s' "$account" | json_field subject)"
[ -n "$subject" ] || die "the account could not be created: $account"
created="$(printf '%s' "$account" | json_field created)"

identity="$(compose run --rm -T operator-bootstrap python scripts/bootstrap_operator.py identity \
  --issuer "https://$auth_host/realms/impact" --subject "$subject" 2>/dev/null | last_json)"
[ -n "$(printf '%s' "$identity" | json_field identity_id)" ] || die "the identity could not be registered: $identity"
log "added $email (provider account created: $created; identity $(printf '%s' "$identity" | json_field identity_id))" \
  >>"$STATE_DIR/admin-actions.log"

if [ "$created" != "true" ]; then
  cat <<EOF

$email already had an account; it is registered as a platform identity. No password was changed.

EOF
  exit 0
fi
cat <<EOF

  Account created for $email
  Sign in at:           https://$app_host/
  Temporary password:   $password
  At first sign-in they choose their own password and set up an authenticator app.
  They can sign in, but hold no authority until one is given through the platform.

EOF
