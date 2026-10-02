import { useEffect, useRef, useState } from "react";

type Request = (path: string, options?: RequestInit) => Promise<any>;
type Notice = { code: string; severity: string; message: string };
type ServiceStatus = {
  state: "OK" | "DEGRADED";
  poll_seconds?: number;
  notices: Notice[];
  detail?: any;
};
// Catalogue text for conditions the status call itself cannot report in a 200 body (the database
// and the identity provider are required by every authenticated request) and for an unreachable
// server. Every other message comes from the server's closed catalogue (impact_api/status.py).
const OUTAGES: Record<string, Notice> = {
  DATABASE_UNAVAILABLE: {
    code: "DATABASE_UNAVAILABLE",
    severity: "critical",
    message:
      "The database is unavailable. Nothing can be read or saved until it is back; work already saved is safe.",
  },
  IDENTITY_PROVIDER_UNAVAILABLE: {
    code: "IDENTITY_PROVIDER_UNAVAILABLE",
    severity: "critical",
    message:
      "Sign-in is unavailable while the identity provider is unreachable. Sessions that are already open continue.",
  },
  SERVICE_UNAVAILABLE: {
    code: "SERVICE_UNAVAILABLE",
    severity: "critical",
    message:
      "The service is temporarily unavailable. Please wait a moment before trying again.",
  },
  UNREACHABLE: {
    code: "UNREACHABLE",
    severity: "critical",
    message:
      "The server cannot be reached. Check your connection; work already saved is safe.",
  },
};
const MIN_POLL = 60_000;
const MAX_POLL = 600_000;

export function useServiceStatus(request: Request) {
  const [status, setStatus] = useState<ServiceStatus | null>(null);
  const [outage, setOutage] = useState<Notice | null>(null);
  const failures = useRef(0);
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let delay = MIN_POLL;
    const controller = new AbortController();
    async function poll() {
      try {
        const result = await request("/v1/status", {
          signal: controller.signal,
        });
        if (cancelled) return;
        failures.current = 0;
        delay = Math.max(MIN_POLL, (result.poll_seconds || 60) * 1000);
        setStatus(result);
        setOutage(null);
      } catch (e: any) {
        if (cancelled || controller.signal.aborted) return;
        failures.current += 1;
        // Back off while the server is failing; name the outage after a second failure in a
        // row (one dropped request is not an outage), at once when the server says why.
        delay = Math.min(delay * 2, MAX_POLL);
        const reason = e && typeof e.reason === "string" ? e.reason : "";
        if (OUTAGES[reason]) setOutage(OUTAGES[reason]);
        else if (e && e.code === "SERVICE_UNAVAILABLE")
          setOutage(OUTAGES.SERVICE_UNAVAILABLE);
        else if (e && e.code === "AUTH_REQUIRED") setOutage(null);
        else if (failures.current >= 2) setOutage(OUTAGES.UNREACHABLE);
      }
      if (!cancelled) timer = setTimeout(poll, delay);
    }
    poll();
    return () => {
      cancelled = true;
      controller.abort();
      if (timer) clearTimeout(timer);
    };
  }, [request]);
  return { status, outage };
}

// Shown to every signed-in person while something is degraded (VF-AVL-002): plain-language
// notices from a closed catalogue, never a reason code, login, tenant or address. Platform
// operators can open the detail the server adds for them (alert codes, counts, who is on call).
export function StatusBanner({ request }: { request: Request }) {
  const { status, outage } = useServiceStatus(request);
  const [open, setOpen] = useState(false);
  const notices: Notice[] = outage ? [outage] : status?.notices || [];
  if (!notices.length) return null;
  const critical = notices.some((n) => n.severity === "critical");
  const detail = outage ? null : status?.detail;
  return (
    <div
      className={
        "status-banner " +
        (critical ? "status-banner-critical" : "status-banner-warning")
      }
      role="status"
      aria-live="polite"
      aria-label="Service notice"
      data-state={outage ? "OUTAGE" : status?.state}
    >
      <div className="status-banner-body">
        <strong>Service notice:</strong>
        <ul>
          {notices.map((n) => (
            <li key={n.code} data-code={n.code}>
              {n.message}
            </li>
          ))}
        </ul>
        {detail && (
          <button
            type="button"
            className="text"
            aria-expanded={open}
            aria-controls="status-detail"
            onClick={() => setOpen((o) => !o)}
          >
            {open ? "Hide details" : "Details for operators"}
          </button>
        )}
      </div>
      {detail && open && <StatusDetail detail={detail} id="status-detail" />}
    </div>
  );
}

export function onCallLine(rota: any): string {
  if (!rota || rota.status === "NOT_CONFIGURED")
    return "No on-call rota is configured for this deployment.";
  if (rota.status === "MISSING")
    return "No on-call rota is published yet (ops/on-call.json is missing).";
  if (rota.status === "INVALID")
    return "The published on-call rota could not be read (ops/on-call.json is not valid).";
  const p = rota.primary || {};
  const parts = [p.name, p.role ? `(${p.role})` : "", p.contact, p.hours]
    .filter(Boolean)
    .join(" · ");
  const secondary = rota.secondary?.name
    ? `; second: ${rota.secondary.name}${rota.secondary.contact ? " · " + rota.secondary.contact : ""}`
    : "";
  return (
    `On call: ${parts}${secondary}` +
    (rota.expired ? " (rota past its valid-until date)" : "")
  );
}

export function StatusDetail({ detail, id }: { detail: any; id?: string }) {
  const workers = detail.workers;
  const ops = detail.operations;
  return (
    <div className="status-detail" id={id}>
      <p>
        <strong>Observed:</strong>{" "}
        {detail.sources?.length
          ? detail.sources.join(", ")
          : "nothing degraded"}
        {workers
          ? ` · workers running ${workers.running} (fresh ${workers.running_fresh}` +
            (workers.newest_beat_age_seconds != null
              ? `, newest beat ${Math.round(workers.newest_beat_age_seconds)} s ago)`
              : ")")
          : ""}
        {detail.deliveries?.dead != null
          ? ` · failed deliveries ${detail.deliveries.dead}, held ${detail.deliveries.held}`
          : ""}
        {detail.storage
          ? ` · evidence storage ${detail.storage.free_mb} MB free`
          : ""}
      </p>
      <p>
        <strong>Server alerts:</strong>{" "}
        {ops === null || ops === undefined
          ? "no operations check is configured"
          : ops.stale
            ? "the last operations check is older than 30 minutes" +
              (ops.checked_at ? ` (${ops.checked_at})` : "")
            : ops.alerts.length
              ? ""
              : "none at " + ops.checked_at}
      </p>
      {ops && !ops.stale && ops.alerts.length > 0 && (
        <ul className="status-alerts">
          {ops.alerts.map((a: any, i: number) => (
            <li key={a.code + a.target + i}>
              <code>{a.code}</code> {a.severity}
              {a.target ? ` · ${a.target}` : ""} — {a.message}
            </li>
          ))}
        </ul>
      )}
      <p className="status-on-call">{onCallLine(detail.on_call)}</p>
    </div>
  );
}
