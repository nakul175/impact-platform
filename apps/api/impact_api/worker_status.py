"""Operator liveness view of the workers: heartbeat rows only, platform operators only."""

from .domain import unavailable

# A running worker that has not beaten for this long is reported stale (default poll: 5 s).
STALE_AFTER_SECONDS = 60


class WorkerStatus:
    def __init__(self, lifecycle):
        self.lifecycle, self.db, self.s = lifecycle, lifecycle.db, lifecycle.s

    def directory(self, identity):
        if not self.s.platform_dsn:
            unavailable()
        with self.db.transaction(platform=True) as c:
            if not self.lifecycle.operator(c, identity):
                unavailable()
            # Staleness by the database clock, the same clock the worker stamps its beats with.
            rows = c.execute(
                "SELECT *,state<>'STOPPED' AND beat_at<statement_timestamp()-make_interval(secs=>%s) AS stale FROM ("
                "SELECT 'delivery' AS kind,worker_id AS id,build,state,started_at,beat_at,"
                "stopped_at,iterations,sent,retried,dead,NULL::bigint AS succeeded,"
                "NULL::bigint AS failed,failures FROM impact.worker_heartbeat "
                "UNION ALL SELECT 'application',executor_id,build,state,started_at,beat_at,"
                "stopped_at,iterations,NULL,NULL,NULL,succeeded,failed,failures "
                "FROM impact.executor_heartbeat) h ORDER BY beat_at DESC,id LIMIT 50",
                (STALE_AFTER_SECONDS,),
            ).fetchall()
        return {
            "stale_after_seconds": STALE_AFTER_SECONDS,
            "items": [
                {
                    "worker_id": row["id"],
                    "kind": row["kind"],
                    "build": row["build"],
                    "state": row["state"],
                    "started_at": row["started_at"].isoformat(),
                    "beat_at": row["beat_at"].isoformat(),
                    "stopped_at": row["stopped_at"].isoformat() if row["stopped_at"] else None,
                    "stale": row["stale"],
                    **{
                        key: row[key]
                        for key in [
                            "iterations",
                            "sent",
                            "retried",
                            "dead",
                            "succeeded",
                            "failed",
                            "failures",
                        ]
                    },
                }
                for row in rows
            ],
        }
