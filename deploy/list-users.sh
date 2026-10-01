#!/usr/bin/env bash
# List everyone who has a sign-in on this deployment (run by the owner in the server console):
#
#   sudo /opt/impact/repo/deploy/list-users.sh
#
# Shows, per account: e-mail, name, whether it can sign in, whether its one-time password is still
# waiting to be replaced, whether an authenticator app is set up and whether it is temporarily
# locked after wrong passwords. No password is shown or stored. What a person may do inside the
# platform is not listed here: that is decided by the platform's own reviewed procedures.
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -eq 0 ] || die "usage: $0"
require_root
require_compose_env

listing="$(compose run --rm -T idp-admin python deploy/keycloak_admin.py list 2>/dev/null | last_json)"
[ -n "$listing" ] || die "the sign-in service did not answer; check https://$(env_value "$COMPOSE_ENV" APP_HOST)/deploy-status.json"
error="$(printf '%s' "$listing" | json_field error)"
[ -z "$error" ] || die "the sign-in service refused the listing: $error"
printf '%s' "$listing" | format_user_listing
