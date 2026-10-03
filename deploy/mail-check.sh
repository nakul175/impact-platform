#!/usr/bin/env bash
# Send one test e-mail through the configured provider and show the conversation (run by the owner
# in the server console after setting SMTP_* in /opt/impact/config.env or secrets.env and deploying):
#
#   sudo /opt/impact/repo/deploy/mail-check.sh you@example.org
#
# It runs deploy/mail_check.py inside the worker's own container, so it uses exactly the settings
# the worker uses (host, port, STARTTLS policy, credentials, From address) and the same network. The
# SMTP transcript is printed with every secret removed: the password and the username never appear,
# not even base64-encoded. The last line is a JSON summary; the exit code is 0 when the provider
# accepted the message, 1 when it refused, 2 for a configuration problem. Nothing is stored except
# one line in state/admin-actions.log (address and outcome, no transcript).
set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -eq 1 ] || die "usage: $0 <email>"
email="$1"
[[ "$email" =~ ^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$ ]] || die "not an e-mail address: $email"

require_root
require_compose_env

host="$(env_value "$COMPOSE_ENV" SMTP_HOST)"
log "sending a test message to $email through ${host:-the loopback capture (no provider configured)}"
set +e
compose run --rm -T \
  -v "$DEPLOY_DIR/mail_check.py:/app/deploy/mail_check.py:ro" \
  worker python deploy/mail_check.py --to "$email"
status=$?
set -e
case "$status" in
0) outcome="accepted by the provider" ;;
1) outcome="refused by the provider (see the transcript above)" ;;
*) outcome="not attempted: configuration problem (exit $status)" ;;
esac
mkdir -p "$STATE_DIR"
log "mail check to $email: $outcome" >>"$STATE_DIR/admin-actions.log"
log "mail check to $email: $outcome"
exit "$status"
