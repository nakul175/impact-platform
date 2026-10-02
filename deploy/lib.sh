#!/usr/bin/env bash
# Shared helpers for deploy/update.sh and the owner and operations scripts in deploy/. Sourced, not
# run. Paths default to the server layout and can be moved with IMPACT_HOME (the CI stack does).
# shellcheck disable=SC2034  # variables are used by the scripts that source this file

IMPACT_HOME="${IMPACT_HOME:-/opt/impact}"
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$DEPLOY_DIR/.." && pwd)"
COMPOSE_FILE="$DEPLOY_DIR/compose.yaml"
SECRETS_FILE="$IMPACT_HOME/secrets.env"
CONFIG_FILE="$IMPACT_HOME/config.env"
COMPOSE_ENV="$IMPACT_HOME/compose.env"
STATUS_DIR="$IMPACT_HOME/public"
CA_DIR="$IMPACT_HOME/ca"
STATE_DIR="$IMPACT_HOME/state"
OPS_DIR="$IMPACT_HOME/ops"
PROJECT="impact"
DEFAULT_OWNER_EMAIL="nakul.jain@aplyd.com"
DEFAULT_OWNER_FIRST_NAME="Nakul"
DEFAULT_OWNER_LAST_NAME="Jain"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
die() {
  log "ERROR: $*" >&2
  exit 1
}

compose() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" --env-file "$COMPOSE_ENV" "$@"
}

# Value of KEY in an env file (KEY=value lines, no quoting); empty when absent.
env_value() {
  local file=$1 key=$2
  [ -r "$file" ] || return 0
  sed -n "s/^${key}=//p" "$file" | tail -n 1
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    die "run this as root (sudo $0)"
  fi
}

require_compose_env() {
  [ -r "$COMPOSE_ENV" ] || die "$COMPOSE_ENV is missing: the first deployment has not run yet"
}

# One random secret of hex characters (safe inside URLs and env files without quoting).
random_hex() {
  local bytes=$1
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex "$bytes"
  else
    python3 -c "import secrets,sys; print(secrets.token_hex(int(sys.argv[1])))" "$bytes"
  fi
}

# A temporary password a person can type from a console: five groups of four characters.
readable_password() {
  python3 -c "import secrets; a='abcdefghjkmnpqrstuvwxyz23456789'; print('-'.join(''.join(secrets.choice(a) for _ in range(4)) for _ in range(5)))"
}

# Replace (or add) KEY=value in a 0600 env file without printing the value.
set_env_value() {
  local file=$1 key=$2 value=$3 tmp
  tmp="$(mktemp "${file}.XXXXXX")"
  chmod 600 "$tmp"
  if [ -f "$file" ]; then
    grep -v "^${key}=" "$file" >"$tmp" || true
  fi
  printf '%s=%s\n' "$key" "$value" >>"$tmp"
  mv -f "$tmp" "$file"
}

# Last line of a job's output that parses as a JSON object, or nothing.
last_json() {
  python3 -c '
import json, sys
found = ""
for line in sys.stdin:
    line = line.strip()
    if line.startswith("{"):
        try:
            json.loads(line)
            found = line
        except ValueError:
            pass
print(found)
'
}

# A plain box around the given lines, for the owner's console (no colours, ASCII only).
box() {
  local line width=0 rule
  for line in "$@"; do
    if [ "${#line}" -gt "$width" ]; then width=${#line}; fi
  done
  rule="$(printf '%*s' $((width + 4)) '' | tr ' ' '-')"
  printf '\n  +%s+\n' "$rule"
  for line in "$@"; do
    printf '  |  %-*s  |\n' "$width" "$line"
  done
  printf '  +%s+\n\n' "$rule"
}

# The keycloak_admin.py `list` JSON (stdin) as a plain table for the owner's console.
format_user_listing() {
  python3 -c '
import json, sys
data = json.loads(sys.stdin.read() or "{}")
users = data.get("users", [])
def status(u):
    if not u.get("enabled"):
        return "switched off (cannot sign in)"
    if u.get("locked"):
        return "temporarily locked after wrong passwords (reset-user.sh lifts it)"
    if u.get("temporary_password_pending"):
        return "has not signed in yet (one-time password not used)"
    if not u.get("totp_configured"):
        return "signed in, but no authenticator app set up yet"
    return "active, authenticator app set up"
rows = [(u.get("email") or "", u.get("name") or "", status(u)) for u in users]
w1 = max([len("E-MAIL")] + [len(r[0]) for r in rows])
w2 = max([len("NAME")] + [len(r[1]) for r in rows])
print()
print("  Sign-in accounts on this deployment: %d" % len(rows))
print()
print("  %-*s  %-*s  %s" % (w1, "E-MAIL", w2, "NAME", "STATUS"))
for r in rows:
    print("  %-*s  %-*s  %s" % (w1, r[0], w2, r[1], r[2]))
if data.get("truncated"):
    print("  (only the first 500 accounts are shown)")
print()
'
}

# Field of a JSON object read from stdin ("" when absent).
json_field() {
  python3 -c '
import json, sys
text = sys.stdin.read().strip()
value = json.loads(text).get(sys.argv[1], "") if text else ""
print("true" if value is True else "false" if value is False else value)
' "$1"
}
