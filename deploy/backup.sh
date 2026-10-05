#!/bin/bash
# Nightly backup sets (the `backup` service of deploy/compose.yaml, running in the postgres:17 image).
# One set is everything a restore needs, written to the `backups` volume:
#
#   /backups/daily/YYYYMMDD/     one set per night; the newest KEEP_DAILY sets are kept
#     impact.dump                  pg_dump -Fc of the application database
#     keycloak.dump                pg_dump -Fc of the identity provider's database
#     globals.sql                  pg_dumpall --roles-only --no-role-passwords (the roles and
#                                  memberships the dumps' ownership and grants refer to; no password)
#     objects.tar                  the evidence object volume (read-only mount), taken AFTER the
#                                  database dumps so every object the dumps reference is in it
#     SHA256SUMS, manifest.json    sizes, SHA-256, schema version, commit, object count, checks
#   /backups/weekly/YYYYMMDD/    Sunday's set, hard-linked (no second copy); KEEP_WEEKLY kept
#
# A set is built in a hidden `.partial-*` directory, verified (pg_restore --list of each dump, a full
# read of the tar, `sha256sum --check` of every file) and only then renamed into place, so a listed
# set is always complete. A failed or refused attempt leaves the previous sets untouched.
#
# Disk guard: an attempt is refused (and reported) when the backup file system has less free space
# than max(MIN_FREE_MB, twice the newest set). Status goes to $STATUS_DIR/backup-status.json (a host
# directory, read by deploy/ops-check.sh into deploy-status.json); it holds no secret.
#
# `backup.sh --now` (docker compose exec backup /bin/bash /opt/backup/backup.sh --now) takes one set
# immediately and exits with its outcome. One set is taken at start when none exists for today.
# These sets sit on the same server: DigitalOcean's droplet backups are the only off-server copy.
set -euo pipefail

BACKUP_HOUR_UTC="${BACKUP_HOUR_UTC:-21}"
KEEP_DAILY="${KEEP_DAILY:-7}"
KEEP_WEEKLY="${KEEP_WEEKLY:-4}"
MIN_FREE_MB="${MIN_FREE_MB:-1024}"
ROOT="${BACKUP_ROOT:-/backups}"
OBJECTS_DIR="${OBJECTS_DIR:-/objects}"
STATUS_DIR="${STATUS_DIR:-/ops}"
COMMIT="${IMPACT_COMMIT:-unknown}"
DATABASES=(impact keycloak)
SET_NAME_PATTERN='[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'

log() { printf '%s backup: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }
# Only characters that need no JSON escaping (codes, names, numbers, timestamps).
plain() { printf '%s\n' "$(printf '%s' "$*" | tr -cd 'A-Za-z0-9 ._:/+-')" | cut -c1-200; }

# Free space (MiB) of the file system holding $1.
free_mb() { df -Pk "$1" | awk 'NR==2 {print int($4/1024)}'; }

# Complete sets of one tier, newest first (names only).
sets_in() {
  local dir=$1 entry
  [ -d "$dir" ] || return 0
  # The fixed eight-digit glob has no whitespace and matches complete names
  # only. Ignore symlinks, exactly as find's default -type d did.
  for entry in "$dir"/$SET_NAME_PATTERN; do
    [ -d "$entry" ] && [ ! -L "$entry" ] || continue
    printf '%s\n' "${entry##*/}"
  done | sort -r
}

file_bytes() {
  local bytes
  if ! bytes="$(stat -c %s "$1" 2>/dev/null)"; then
    bytes="$(stat -f %z "$1")" || return 1
  fi
  case "$bytes" in '' | *[!0-9]*) return 1;; esac
  printf '%s\n' "$bytes"
}

set_bytes() {
  local dir=$1 bytes
  # Preserve GNU du's existing byte accounting in the production image.
  if bytes="$(du -sb "$dir" 2>/dev/null)"; then
    bytes="$(printf '%s\n' "$bytes" | awk '{print $1}')"
    case "$bytes" in '' | *[!0-9]*) return 1;; esac
    printf '%s\n' "$bytes"
    return 0
  fi
  # BSD du lacks apparent-byte mode. A generated set has six distinct flat
  # files; sum the same logical stat sizes, including its directory metadata.
  find "$dir" -print0 | {
    local total=0 entry size
    while IFS= read -r -d '' entry; do
      size="$(file_bytes "$entry")" || return 1
      total=$((total + size))
    done
    printf '%s\n' "$total"
  }
}

# Size (MiB, rounded up) of the newest complete daily set, 0 when there is none.
newest_set_mb() {
  local newest
  newest="$(sets_in "$ROOT/daily" | head -n 1)"
  [ -n "$newest" ] || {
    echo 0
    return
  }
  du -sm "$ROOT/daily/$newest" | awk '{print $1}'
}

# The space an attempt needs: twice the newest set, never less than MIN_FREE_MB.
required_mb() {
  local last
  last="$(newest_set_mb)"
  if [ $((last * 2)) -gt "$MIN_FREE_MB" ]; then echo $((last * 2)); else echo "$MIN_FREE_MB"; fi
}

json_list() {
  local first=1 item
  printf '['
  for item in "$@"; do
    [ "$first" = 1 ] || printf ','
    printf '"%s"' "$(plain "$item")"
    first=0
  done
  printf ']'
}

# write_status <result> <reason> <set> <bytes> <free> <required>: atomically, with the last success.
write_status() {
  local result=$1 reason=$2 set=$3 bytes=$4 free=$5 required=$6 tmp last="null"
  mkdir -p "$STATUS_DIR"
  if [ -s "$STATUS_DIR/backup-last-success.json" ]; then last="$(cat "$STATUS_DIR/backup-last-success.json")"; fi
  tmp="$(mktemp "$STATUS_DIR/.backup-status.XXXXXX")"
  # shellcheck disable=SC2046  # word splitting of the set lists is intended
  {
    printf '{"format":1,"attempted_at":"%s","result":"%s","reason":"%s","set":"%s",' \
      "$(now_iso)" "$(plain "$result")" "$(plain "$reason")" "$(plain "$set")"
    printf '"bytes":%d,"free_mb":%d,"required_mb":%d,"keep_daily":%d,"keep_weekly":%d,' \
      "${bytes:-0}" "${free:-0}" "${required:-0}" "$KEEP_DAILY" "$KEEP_WEEKLY"
    printf '"daily_sets":%s,"weekly_sets":%s,"last_success":%s}\n' \
      "$(json_list $(sets_in "$ROOT/daily"))" "$(json_list $(sets_in "$ROOT/weekly"))" "$last"
  } >"$tmp"
  chmod 644 "$tmp"
  mv -f "$tmp" "$STATUS_DIR/backup-status.json"
}

prune() {
  local dir=$1 keep=$2
  sets_in "$dir" | tail -n "+$((keep + 1))" | while read -r name; do
    rm -rf -- "${dir:?}/${name}"
    log "pruned ${dir}/${name}"
  done
}

# Flat dumps of the earlier layout (<db>-YYYYMMDD.dump) age out with the same horizons.
prune_legacy() {
  find "$ROOT/daily" -maxdepth 1 -type f -name '*.dump' -mtime "+$KEEP_DAILY" -delete 2>/dev/null || true
  find "$ROOT/weekly" -maxdepth 1 -type f -name '*.dump' -mtime "+$((KEEP_WEEKLY * 7))" -delete 2>/dev/null || true
}

file_entry() {
  local dir=$1 name=$2 bytes digest
  bytes="$(file_bytes "$dir/$name")" || return 1
  digest="$(sha256sum "$dir/$name" | awk '{print $1}')" || return 1
  printf '{"name":"%s","bytes":%d,"sha256":"%s"}' "$name" "$bytes" "$digest"
}

# verify_set <dir>: every dump lists, the tar reads to the end, every checksum matches.
verify_set() {
  local dir=$1 db
  for db in "${DATABASES[@]}"; do
    pg_restore --list "$dir/$db.dump" >/dev/null || return 1
  done
  tar --list --file "$dir/objects.tar" >/dev/null || return 1
  (cd "$dir" && sha256sum --check --quiet --strict SHA256SUMS) || return 1
}

# take_set: one complete, verified set or a non-zero exit (status written either way).
take_set() {
  local day weekday stamp work target started free required schema objects bytes postgres
  day="$(date -u +%Y%m%d)"
  weekday="$(date -u +%u)"
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  started="$(now_iso)"
  umask 077
  mkdir -p "$ROOT/daily" "$ROOT/weekly"
  chmod 700 "$ROOT" "$ROOT/daily" "$ROOT/weekly"
  # A partial directory left by an interrupted attempt is never a backup.
  find "$ROOT/daily" -mindepth 1 -maxdepth 1 -type d -name '.partial-*' -exec rm -rf {} + 2>/dev/null || true
  free="$(free_mb "$ROOT")"
  required="$(required_mb)"
  if [ "$free" -lt "$required" ]; then
    log "REFUSED: ${free} MiB free on the backup disk, ${required} MiB required"
    write_status refused DISK_LOW "$day" 0 "$free" "$required"
    return 1
  fi
  work="$ROOT/daily/.partial-$stamp"
  mkdir -m 700 "$work"
  local step=""
  if ! {
    step=dump_impact && pg_dump -Fc --no-password -d impact -f "$work/impact.dump" &&
      step=dump_keycloak && pg_dump -Fc --no-password -d keycloak -f "$work/keycloak.dump" &&
      step=roles && pg_dumpall --roles-only --no-role-passwords --no-password -f "$work/globals.sql" &&
      step=schema_version && schema="$(psql -Atq --no-password -d impact -c 'SELECT max(version) FROM impact.schema_migration')" &&
      step=objects && mkdir -p "$OBJECTS_DIR" &&
      COPYFILE_DISABLE=1 tar --create --file "$work/objects.tar" --directory "$OBJECTS_DIR" --exclude='.incoming-*' . &&
      step=checksums && (cd "$work" && sha256sum impact.dump keycloak.dump globals.sql objects.tar >SHA256SUMS) &&
      step=verify && verify_set "$work"
  }; then
    rm -rf -- "$work"
    log "FAILED at step $step"
    write_status failed "STEP_FAILED_$step" "$day" 0 "$free" "$required"
    return 1
  fi
  objects="$(tar --list --verbose --file "$work/objects.tar" | grep -c '^-' || true)"
  postgres="$(psql -Atq --no-password -d impact -c 'SHOW server_version' | awk '{print $1}')"
  local entries=() name entry
  for name in impact.dump keycloak.dump globals.sql objects.tar; do
    if ! entry="$(file_entry "$work" "$name")"; then
      rm -rf -- "$work"
      write_status failed STEP_FAILED_manifest "$day" 0 "$free" "$required"
      return 1
    fi
    entries+=("$entry")
  done
  if ! {
    printf '{"format":1,"set":"%s","created_at":"%s","finished_at":"%s",' "$day" "$started" "$(now_iso)"
    printf '"commit":"%s","schema_version":%d,"postgres":"%s",' "$(plain "$COMMIT")" "${schema:-0}" "$(plain "$postgres")"
    printf '"files":[%s,%s,%s,%s],' "${entries[0]}" "${entries[1]}" "${entries[2]}" "${entries[3]}"
    printf '"objects":{"files":%d},' "$objects"
    printf '"verified":{"pg_restore_list":true,"tar_read":true,"sha256":true}}\n'
  } >"$work/manifest.json"; then
    rm -rf -- "$work"
    write_status failed STEP_FAILED_manifest "$day" 0 "$free" "$required"
    return 1
  fi
  if ! bytes="$(set_bytes "$work")"; then
    rm -rf -- "$work"
    write_status failed STEP_FAILED_set_size "$day" 0 "$free" "$required"
    return 1
  fi
  target="$ROOT/daily/$day"
  if [ -e "$target" ]; then
    # A second set the same day (--now) replaces the first only once it is complete.
    mv -f "$target" "$ROOT/daily/.replaced-$stamp"
    mv "$work" "$target"
    rm -rf -- "$ROOT/daily/.replaced-$stamp"
  else
    mv "$work" "$target"
  fi
  log "wrote set $target ($bytes bytes, schema $schema, $objects objects)"
  if [ "$weekday" = "7" ]; then
    rm -rf -- "${ROOT:?}/weekly/$day"
    cp -al "$target" "$ROOT/weekly/$day"
    log "kept weekly set $day"
  fi
  prune "$ROOT/daily" "$KEEP_DAILY"
  prune "$ROOT/weekly" "$KEEP_WEEKLY"
  prune_legacy
  mkdir -p "$STATUS_DIR"
  {
    printf '{"set":"%s","finished_at":"%s","bytes":%d,' "$day" "$(now_iso)" "$bytes"
    printf '"schema_version":%d,"commit":"%s","objects":%d}\n' "${schema:-0}" "$(plain "$COMMIT")" "$objects"
  } >"$STATUS_DIR/.backup-last-success.tmp"
  mv -f "$STATUS_DIR/.backup-last-success.tmp" "$STATUS_DIR/backup-last-success.json"
  write_status ok "" "$day" "$bytes" "$(free_mb "$ROOT")" "$required"
}

seconds_until_next_run() {
  local now target hour
  [[ "$BACKUP_HOUR_UTC" =~ ^[0-9]{1,2}$ ]] && [ "$BACKUP_HOUR_UTC" -le 23 ] || return 1
  hour=$((10#$BACKUP_HOUR_UTC))
  now=$(date -u +%s)
  # POSIX epoch days are UTC: retain the same next scheduled hour without
  # GNU date -d, local-time parsing or an additional runtime dependency.
  target=$((now - now % 86400 + hour * 3600))
  if [ "$target" -le "$now" ]; then
    target=$((target + 86400))
  fi
  echo $((target - now))
}

main() {
  until pg_isready -q; do sleep 5; done
  if [ "${1:-}" = "--now" ]; then
    take_set
    return
  fi
  if [ ! -d "$ROOT/daily/$(date -u +%Y%m%d)" ]; then
    take_set || true
  fi
  while true; do
    wait_seconds=$(seconds_until_next_run)
    log "next run in ${wait_seconds}s (daily at ${BACKUP_HOUR_UTC}:00 UTC)"
    sleep "$wait_seconds"
    take_set || true
  done
}

# Sourced by the unit tests with BACKUP_LIBRARY=1: functions only.
if [ "${BACKUP_LIBRARY:-}" != "1" ]; then
  main "$@"
fi
