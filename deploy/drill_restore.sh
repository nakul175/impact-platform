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

plain() { printf '%s' "$*" | tr -cd 'A-Za-z0-9 ._:/+-' | cut -c1-200; }

# Newest complete set: the greatest YYYYMMDD among daily/ and weekly/ that has a manifest.
latest_set() {
  local best="" name tier
  for tier in daily weekly; do
    [ -d "$ROOT/$tier" ] || continue
    while read -r name; do
      [ -n "$name" ] && [ -s "$ROOT/$tier/$name/manifest.json" ] || continue
      if [ -z "$best" ] || [ "$name" \> "${best#*/}" ]; then best="$tier/$name"; fi
    done < <(find "$ROOT/$tier" -mindepth 1 -maxdepth 1 -type d -name '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]' -printf '%f\n')
  done
  printf '%s' "$best"
}

timings=""
result="failed"
failed_step=""
set_name=""
finish() {
  local manifest="null"
  if [ -n "$set_name" ] && [ -s "$ROOT/$set_name/manifest.json" ]; then manifest="$(tr -d '\n' <"$ROOT/$set_name/manifest.json")"; fi
  printf '{"set":"%s","result":"%s","failed_step":"%s","seconds":{%s},"manifest":%s}\n' \
    "$(plain "$set_name")" "$result" "$(plain "$failed_step")" "${timings#,}" "$manifest"
}
trap finish EXIT

timed() {
  local name=$1 started ended
  shift
  failed_step="$name"
  started="$(date +%s.%N)"
  "$@"
  ended="$(date +%s.%N)"
  timings="$timings,\"$name\":$(awk -v a="$started" -v b="$ended" 'BEGIN {printf "%.2f", b - a}')"
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

until pg_isready -q; do sleep 1; done
set_name="${1:-$(latest_set)}"
case "$set_name" in
daily/[0-9]* | weekly/[0-9]*) ;;
*)
  failed_step="no_backup_set"
  exit 1
  ;;
esac
dir="$ROOT/$set_name"
[ -s "$dir/manifest.json" ] || {
  failed_step="manifest_missing"
  exit 1
}
timed verify_checksums bash -c "cd '$dir' && sha256sum --check --quiet --strict SHA256SUMS"
timed roles roles "$dir/globals.sql"
timed restore_impact restore impact "$dir/impact.dump"
timed restore_identity_provider restore keycloak "$dir/keycloak.dump"
failed_step=""
result="ok"
