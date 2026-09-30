#!/bin/bash
# Nightly logical backups of the application and identity-provider databases (the `backup` service
# of deploy/compose.yaml, running in the postgres:17 image). Writes custom-format dumps
# (pg_dump -Fc) to the `backups` volume:
#
#   /backups/daily/<db>-YYYYMMDD.dump     one per night, the newest KEEP_DAILY kept per database
#   /backups/weekly/<db>-YYYYMMDD.dump    Sunday's dump copied here, the newest KEEP_WEEKLY kept
#
# A dump is written to a temporary name and renamed only after pg_restore --list reads it back.
# One dump is taken at start when none exists for today, so a fresh server has one at once.
# These dumps sit on the same server; DigitalOcean's daily droplet backups are the off-server copy.
set -euo pipefail

BACKUP_HOUR_UTC="${BACKUP_HOUR_UTC:-21}"
KEEP_DAILY="${KEEP_DAILY:-7}"
KEEP_WEEKLY="${KEEP_WEEKLY:-4}"
DATABASES=(impact keycloak)
ROOT=/backups

log() { printf '%s backup: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

prune() {
  local dir=$1 keep=$2 db=$3
  # Newest first by the date in the name; everything after the first $keep goes.
  find "$dir" -maxdepth 1 -name "${db}-*.dump" -printf '%f\n' | sort -r | tail -n "+$((keep + 1))" |
    while read -r name; do
      rm -f -- "${dir:?}/${name}"
      log "pruned ${dir}/${name}"
    done
}

dump_all() {
  local day weekday
  day=$(date -u +%Y%m%d)
  weekday=$(date -u +%u)
  mkdir -p "$ROOT/daily" "$ROOT/weekly"
  chmod 700 "$ROOT" "$ROOT/daily" "$ROOT/weekly"
  for db in "${DATABASES[@]}"; do
    local target="$ROOT/daily/${db}-${day}.dump" partial="$ROOT/daily/.${db}-${day}.partial"
    umask 077
    if pg_dump -Fc --no-password -d "$db" -f "$partial" && pg_restore --list "$partial" >/dev/null; then
      mv -f "$partial" "$target"
      log "wrote $target ($(stat -c %s "$target") bytes)"
      if [ "$weekday" = "7" ]; then
        cp -f "$target" "$ROOT/weekly/${db}-${day}.dump"
        log "kept weekly copy of $db"
      fi
    else
      rm -f "$partial"
      log "FAILED to dump $db"
    fi
    prune "$ROOT/daily" "$KEEP_DAILY" "$db"
    prune "$ROOT/weekly" "$KEEP_WEEKLY" "$db"
  done
  date -u +%Y-%m-%dT%H:%M:%SZ >"$ROOT/last-run"
}

seconds_until_next_run() {
  local now target
  now=$(date -u +%s)
  target=$(date -u -d "today ${BACKUP_HOUR_UTC}:00" +%s)
  if [ "$target" -le "$now" ]; then
    target=$(date -u -d "tomorrow ${BACKUP_HOUR_UTC}:00" +%s)
  fi
  echo $((target - now))
}

until pg_isready -q; do sleep 5; done
if [ ! -e "$ROOT/daily/impact-$(date -u +%Y%m%d).dump" ]; then
  dump_all
fi
while true; do
  wait_seconds=$(seconds_until_next_run)
  log "next run in ${wait_seconds}s (daily at ${BACKUP_HOUR_UTC}:00 UTC)"
  sleep "$wait_seconds"
  dump_all
done
