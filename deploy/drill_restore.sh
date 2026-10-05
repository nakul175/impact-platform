#!/bin/bash
# Restore one backup set into the throwaway drill database (runs inside the `drill-db` container of
# the restore drill; see deploy/restore-drill.sh). Never run against the live database: this
# container has no route to it and only a read-only view of the backup sets.
#
#   drill_restore.sh [SET]    SET is daily/YYYYMMDD or weekly/YYYYMMDD; default the newest complete
#                             set of either tier (the one with the latest name)
#
# Steps, each timed: sha256sum --check of the set, roles from globals.sql (the cluster's own
# `postgres` role skipped), createdb impact and keycloak, pg_restore --exit-on-error of both dumps.
# Prints one JSON line: {"set": ..., "manifest": {...}, "seconds": {...}, "result": "ok"|"failed"}.
set -euo pipefail

ROOT="${BACKUP_ROOT:-/backups}"
export PGUSER="${PGUSER:-postgres}"

plain() { printf '%s\n' "$(printf '%s' "$*" | tr -cd 'A-Za-z0-9 ._:/+-')" | cut -c1-200; }

# Newest complete set: the greatest YYYYMMDD among daily/ and weekly/ that has a manifest.
latest_set() {
  local best="" name tier entry
  for tier in daily weekly; do
    [ -d "$ROOT/$tier" ] || continue
    for entry in "$ROOT/$tier"/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]; do
      [ -d "$entry" ] && [ ! -L "$entry" ] || continue
      name="${entry##*/}"
      [ -n "$name" ] && [ -s "$ROOT/$tier/$name/manifest.json" ] || continue
      if [ -z "$best" ] || [ "$name" \> "${best#*/}" ]; then best="$tier/$name"; fi
    done
  done
  printf '%s' "$best"
}

timings=""
result="failed"
failed_step=""
set_name=""
selected_dir=""
finish() {
  local manifest="null"
  if [ -n "$selected_dir" ] && [ -s "$selected_dir/manifest.json" ]; then manifest="$(tr -d '\n' <"$selected_dir/manifest.json")"; fi
  printf '{"set":"%s","result":"%s","failed_step":"%s","seconds":{%s},"manifest":%s}\n' \
    "$(plain "$set_name")" "$result" "$(plain "$failed_step")" "${timings#,}" "$manifest"
}
trap finish EXIT

timed() {
  local name=$1 started ended
  shift
  failed_step="$name"
  started="$(clock_seconds)"
  "$@"
  ended="$(clock_seconds)"
  timings="$timings,\"$name\":$(awk -v a="$started" -v b="$ended" 'BEGIN {printf "%.2f", b - a}')"
}

clock_seconds() {
  local value
  value="$(date +%s.%N)"
  case "$value" in
    *[!0-9.]* | *.*.*) date +%s;;
    *) printf '%s\n' "$value";;
  esac
}

verify_checksums() {
  (cd "$1" && sha256sum --check --quiet --strict SHA256SUMS)
}

roles() {
  # pg_dumpall --roles-only also lists the bootstrap superuser, which this cluster already has.
  grep -v -E '^(CREATE|ALTER) ROLE postgres( |;)' "$1" | psql -X -q -v ON_ERROR_STOP=1 -d postgres >/dev/null
}

restore() {
  local db=$1 dump=$2
  createdb "$db"
  pg_restore --exit-on-error --no-password -d "$db" "$dump"
}

# Over TCP: on first start the image initialises with a socket-only server, then restarts it.
until pg_isready -q -h 127.0.0.1; do sleep 1; done
set_name="${1:-$(latest_set)}"
case "$set_name" in
daily/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9] | weekly/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;;
*)
  failed_step="no_backup_set"
  exit 1
  ;;
esac
dir="$ROOT/$set_name"
[ -d "$dir" ] && [ ! -L "$dir" ] && [ -s "$dir/manifest.json" ] || {
  failed_step="manifest_missing"
  exit 1
}
selected_dir="$dir"
timed verify_checksums verify_checksums "$dir"
timed roles roles "$dir/globals.sql"
timed restore_impact restore impact "$dir/impact.dump"
timed restore_identity_provider restore keycloak "$dir/keycloak.dump"
failed_step=""
result="ok"
