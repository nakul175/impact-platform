import { useEffect, useRef, useState, type ReactNode } from "react";
import { usePendingOperations } from "./operations";

const PURPOSE = "DATA_SUBJECT_REQUEST";
type Requester = (path: string, options?: RequestInit) => Promise<any>;
type Case = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  created_at: string;
  data: Record<string, any>;
};
type PlanEntry = {
  store: string;
  action: string;
  object_id: string;
  object_type: string;
  state: string;
  reason: string | null;
  hold_review_at: string | null;
};
type Plan = { plan_sha256: string; approved: boolean; entries: PlanEntry[] };
type Proof = {
  proof_id: string;
  job_id: string;
  data_class: string;
  action: string;
  retention_days: number;
  affected_count: number;
  items_sha256: string;
  executed_at: string;
};

/**
 * Data-subject requests and retention proof (v0.25 part B). Privacy-case grants are purpose-bound
 * (/me/access lists them under purpose_capabilities), so this panel is shown only to holders of
 * such a grant and names the purpose on every call; the server re-checks purpose, capability,
 * fresh assurance and approver independence each time.
 */
export function PrivacyPanel({
  base,
  capabilities,
  purposeCapabilities,
  request,
  explain,
  Dialog,
}: {
  base: string;
  capabilities: string[];
  purposeCapabilities: [string, string][];
  request: Requester;
  explain: (e: unknown) => string;
  Dialog: (p: {
    title: string;
    close: () => void;
    children: ReactNode;
  }) => ReactNode;
}) {
  const may = (cap: string) =>
    purposeCapabilities.some(([c, p]) => c === cap && p === PURPOSE);
  const [cases, setCases] = useState<Case[] | null>(null),
    [proofs, setProofs] = useState<Proof[] | null>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0),
    [dialog, setDialog] = useState<{ mode: string; item?: Case } | null>(null),
    [plan, setPlan] = useState<Plan | null>(null);
  const pending = usePendingOperations();
  const createId = useRef("");
  const query = "?purpose=" + PURPOSE;
  useEffect(() => {
    const c = new AbortController();
    if (may("privacy-cases.read"))
      request(base + "privacy-cases" + query + "&limit=50", {
        signal: c.signal,
      })
        .then((x) => !c.signal.aborted && setCases(x.items))
        .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    if (capabilities.includes("retention.read"))
      request(base + "retention-proofs", { signal: c.signal })
        .then((x) => !c.signal.aborted && setProofs(x.items))
        .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    return () => c.abort();
  }, [base, tick]);
  const governance = [
    "access-denials.read",
    "retention-policies.read",
    "retention-holds.read",
  ].some((cap) => capabilities.includes(cap));
  if (
    !may("privacy-cases.read") &&
    !capabilities.includes("retention.read") &&
    !governance
  )
    return null;

  async function act(item: Case, action: string, data: Record<string, any>) {
    const key = action + ":" + item.object_id;
    const body = { purpose: PURPOSE, ...data };
    setBusy(true);
    setError("");
    try {
      const receipt = await request(
        base + "privacy-cases/" + item.object_id + "/actions/" + action,
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: pending.id(key, body),
            expected_revision: item.revision_id,
            data: body,
          }),
        },
      );
      pending.done(key);
      setMessage("Request " + receipt.business_state.toLowerCase() + ".");
      setDialog(null);
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e)); /* the identifier is kept for an exact retry */
    } finally {
      setBusy(false);
    }
  }
  async function review(item: Case) {
    setPlan(null);
    setDialog({ mode: "plan", item });
    try {
      setPlan(
        await request(
          base + "privacy-cases/" + item.object_id + "/plan" + query,
        ),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  async function download(item: Case) {
    setError("");
    try {
      const response = await fetch(
        base + "privacy-cases/" + item.object_id + "/export" + query,
        { credentials: "same-origin" },
      );
      if (!response.ok) throw new Error((await response.json()).message);
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "data-subject-export-" + item.object_id + ".json";
      link.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(explain(e));
    }
  }
  async function create(form: HTMLFormElement) {
    const values = new FormData(form);
    const type = String(values.get("request_type"));
    const evidence = String(values.get("evidence_ids") || "")
      .split(/[\s,]+/)
      .filter(Boolean);
    const data: Record<string, any> = {
      request_type: type,
      subject_membership_id: String(values.get("subject")).trim(),
      reason: String(values.get("reason")),
      verification_note: String(values.get("verification")),
      purpose: PURPOSE,
      ...(type === "ERASURE" && evidence.length
        ? { evidence_ids: evidence }
        : {}),
    };
    createId.current ||= crypto.randomUUID();
    setBusy(true);
    setError("");
    try {
      await request(base + "privacy-cases", {
        method: "POST",
        body: JSON.stringify({ operation_id: createId.current, data }),
      });
      createId.current = "";
      setDialog(null);
      setMessage("Request recorded as a draft for independent approval.");
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const item = dialog?.item;
  return (
    <section className="readiness" aria-label="Privacy requests">
      <h3>Data-subject requests</h3>
      <p className="muted">
        Access and erasure requests about a member of this workspace. A
        different person from the one who recorded the request (and never the
        member concerned) approves the exact plan before it runs. Erasure keeps
        audit records and never changes approved official numbers.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {message && <p role="status">{message}</p>}
      {may("privacy-cases.draft.create") && (
        <button
          className="secondary"
          onClick={() => {
            createId.current = "";
            setDialog({ mode: "create" });
          }}
        >
          New request
        </button>
      )}
      {cases && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Data-subject requests</caption>
            <thead>
              <tr>
                <th scope="col">Type</th>
                <th scope="col">Member</th>
                <th scope="col">Status</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((c) => (
                <tr key={c.object_id}>
                  <td>{c.data.request_type}</td>
                  <td>
                    <code>
                      {String(c.data.subject_membership_id).slice(0, 8)}
                    </code>
                  </td>
                  <td>
                    {c.lifecycle_state}
                    {c.data.outcome
                      ? " · " +
                        c.data.outcome.replaceAll("_", " ").toLowerCase()
                      : ""}
                  </td>
                  <td>
                    <button className="secondary" onClick={() => review(c)}>
                      Plan
                    </button>
                    {["Approved", "Executing", "PartiallyCompleted"].includes(
                      c.lifecycle_state,
                    ) &&
                      may("privacy.execute") && (
                        <button
                          className="secondary"
                          disabled={busy}
                          onClick={() =>
                            act(c, "execute", {
                              approved_plan_hash: c.data.plan_sha256,
                            })
                          }
                        >
                          Execute
                        </button>
                      )}
                    {c.lifecycle_state === "Completed" &&
                      c.data.request_type === "ACCESS" &&
                      may("privacy.export") && (
                        <button
                          className="secondary"
                          onClick={() => download(c)}
                        >
                          Download export
                        </button>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {proofs && (
        <>
          <h3>Retention proof</h3>
          <div className="table-scroll">
            <table>
              <caption className="sr-only">
                Latest retention proof records
              </caption>
              <thead>
                <tr>
                  <th scope="col">Data class</th>
                  <th scope="col">Action</th>
                  <th scope="col">Items</th>
                  <th scope="col">SHA-256</th>
                  <th scope="col">When</th>
                </tr>
              </thead>
              <tbody>
                {proofs.slice(0, 12).map((p) => (
                  <tr key={p.proof_id}>
                    <td>{p.data_class.replaceAll("_", " ").toLowerCase()}</td>
                    <td>
                      {p.action} after {p.retention_days} d
                    </td>
                    <td>{p.affected_count}</td>
                    <td>
                      <code>{p.items_sha256.slice(0, 12)}…</code>
                    </td>
                    <td>{new Date(p.executed_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
      {capabilities.includes("retention-policies.read") && (
        <RetentionPolicies
          base={base}
          capabilities={capabilities}
          request={request}
          explain={explain}
        />
      )}
      {capabilities.includes("retention-holds.read") && (
        <RetentionHolds
          base={base}
          capabilities={capabilities}
          request={request}
          explain={explain}
        />
      )}
      {capabilities.includes("access-denials.read") && (
        <AccessDenied base={base} request={request} explain={explain} />
      )}
      {dialog?.mode === "create" && (
        <Dialog title="New data-subject request" close={() => setDialog(null)}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              create(e.currentTarget);
            }}
          >
            <label>
              Request type
              <select name="request_type" defaultValue="ACCESS">
                <option value="ACCESS">Access (export)</option>
                <option value="ERASURE">Erasure</option>
              </select>
            </label>
            <label>
              Member identifier
              <input name="subject" required pattern="[0-9a-fA-F-]{36}" />
            </label>
            <label>
              Reason
              <textarea name="reason" required maxLength={2000} />
            </label>
            <label>
              How the request was verified
              <textarea name="verification" required maxLength={2000} />
            </label>
            <label>
              Evidence the member uploaded that is their personal data (erasure
              only; identifiers, comma separated)
              <input name="evidence_ids" />
            </label>
            <div className="dialog-actions">
              <button disabled={busy}>Record request</button>
            </div>
          </form>
        </Dialog>
      )}
      {dialog?.mode === "plan" && item && (
        <Dialog title="Request plan" close={() => setDialog(null)}>
          {!plan ? (
            <p>Loading plan…</p>
          ) : (
            <>
              <p className="muted">
                Plan <code>{plan.plan_sha256.slice(0, 16)}…</code>
                {plan.entries.length === 0
                  ? item.data.request_type === "ACCESS"
                    ? " — an export of the member's data held here."
                    : " — nothing left to erase."
                  : ""}
              </p>
              {plan.entries.length > 0 && (
                <div className="table-scroll">
                  <table>
                    <caption className="sr-only">Store actions</caption>
                    <thead>
                      <tr>
                        <th scope="col">Store</th>
                        <th scope="col">Action</th>
                        <th scope="col">Record</th>
                        <th scope="col">State</th>
                      </tr>
                    </thead>
                    <tbody>
                      {plan.entries.map((e) => (
                        <tr key={e.store + e.object_id}>
                          <td>{e.store.replaceAll("_", " ").toLowerCase()}</td>
                          <td>{e.action.toLowerCase()}</td>
                          <td>
                            {e.object_type}{" "}
                            <code>{e.object_id.slice(0, 8)}</code>
                          </td>
                          <td>
                            {e.state}
                            {e.reason ? " (" + e.reason + ")" : ""}
                            {e.hold_review_at
                              ? " · review " +
                                new Date(e.hold_review_at).toLocaleDateString()
                              : ""}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {!plan.approved &&
                item.lifecycle_state === "Draft" &&
                may("privacy.approve") && (
                  <div className="dialog-actions">
                    <button
                      disabled={busy}
                      onClick={() =>
                        act(item, "approve", {
                          plan_sha256: plan.plan_sha256,
                          reason: "Plan reviewed",
                        })
                      }
                    >
                      Approve this plan
                    </button>
                  </div>
                )}
            </>
          )}
        </Dialog>
      )}
    </section>
  );
}

type Denial = {
  denial_id: string;
  principal_id: string;
  operation_id: string;
  capability: string;
  route: string;
  status: number;
  reason_code: string;
  occurrences: number;
  last_at: string;
  last_correlation_id: string;
};

/** Access denied (v0.27 denial auditing): refused authorisations of this workspace's members,
 * collapsed per principal, operation and reason inside a 300-second window. Read-only. */
function AccessDenied({
  base,
  request,
  explain,
}: {
  base: string;
  request: Requester;
  explain: (e: unknown) => string;
}) {
  const [items, setItems] = useState<Denial[] | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    const c = new AbortController();
    request(base + "access-denials?limit=100", { signal: c.signal })
      .then((x) => !c.signal.aborted && setItems(x.items))
      .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    return () => c.abort();
  }, [base]);
  return (
    <>
      <h3>Access denied</h3>
      <p className="muted">
        Authorisations the platform refused to members of this workspace
        (missing capability, hidden record, purpose or fresh sign-in required).
        Repeats within five minutes are counted on one line; these lines are
        also part of the audit export.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {items && items.length === 0 && (
        <p className="muted">No refusals recorded.</p>
      )}
      {items && items.length > 0 && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Access denied</caption>
            <thead>
              <tr>
                <th scope="col">Member</th>
                <th scope="col">Operation</th>
                <th scope="col">Reason</th>
                <th scope="col">Count</th>
                <th scope="col">Last seen</th>
                <th scope="col">Correlation</th>
              </tr>
            </thead>
            <tbody>
              {items.map((d) => (
                <tr key={d.denial_id}>
                  <td>
                    <code>{d.principal_id.slice(0, 8)}</code>
                  </td>
                  <td>
                    {d.operation_id} <span className="muted">({d.status})</span>
                  </td>
                  <td>{d.reason_code.replaceAll("_", " ").toLowerCase()}</td>
                  <td>{d.occurrences}</td>
                  <td>{new Date(d.last_at).toLocaleString()}</td>
                  <td>
                    <code>{d.last_correlation_id.slice(0, 8)}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

type Policy = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  data: Record<string, any>;
};
type ScheduleItem = {
  data_class: string;
  retention_days: number;
  action: string;
  source: string;
  policy_id: string | null;
};
const POLICY_CLASSES: [string, string, number, number][] = [
  ["OPERATION_RECEIPT", "Operation receipts", 7, 90],
  ["PRIVACY_EXPORT_PACKAGE", "Data-subject export packages", 1, 30],
  ["OUTBOX_RECIPIENT", "Sealed e-mail addresses", 7, 365],
  ["SECURITY_EVENT", "Access-denied records (audit window)", 365, 3650],
];

/** Tenant retention policies (v0.27): proposed per data class inside the class bounds, approved by
 * a different person, applied by the retention sweep from its next run. */
function RetentionPolicies({
  base,
  capabilities,
  request,
  explain,
}: {
  base: string;
  capabilities: string[];
  request: Requester;
  explain: (e: unknown) => string;
}) {
  const [policies, setPolicies] = useState<Policy[] | null>(null),
    [schedule, setSchedule] = useState<ScheduleItem[] | null>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0);
  const pending = usePendingOperations();
  const proposeId = useRef("");
  useEffect(() => {
    const c = new AbortController();
    request(base + "retention-policies?limit=50", { signal: c.signal })
      .then((x) => !c.signal.aborted && setPolicies(x.items))
      .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    if (capabilities.includes("retention.read"))
      request(base + "retention-schedule", { signal: c.signal })
        .then((x) => !c.signal.aborted && setSchedule(x.items))
        .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    return () => c.abort();
  }, [base, tick]);
  async function propose(form: HTMLFormElement) {
    const f = new FormData(form);
    const data = {
      data_class: String(f.get("data_class")),
      duration_days: Number(f.get("duration_days")),
      expiry_action:
        String(f.get("data_class")) === "OUTBOX_RECIPIENT"
          ? "REDACT"
          : "DELETE",
      reason: String(f.get("reason")),
    };
    if (!proposeId.current) proposeId.current = crypto.randomUUID();
    setBusy(true);
    setError("");
    try {
      await request(base + "retention-policies", {
        method: "POST",
        body: JSON.stringify({ operation_id: proposeId.current, data }),
      });
      proposeId.current = "";
      form.reset();
      setMessage("Policy proposed; a different person must approve it.");
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  async function approve(item: Policy) {
    const key = "approve-policy:" + item.object_id;
    const data = { reason: "Reviewed against the records schedule" };
    setBusy(true);
    setError("");
    try {
      await request(
        base + "retention-policies/" + item.object_id + "/actions/approve",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: pending.id(key, data),
            expected_revision: item.revision_id,
            data,
          }),
        },
      );
      pending.done(key);
      setMessage("Policy approved; the next retention sweep applies it.");
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h3>Retention policies</h3>
      <p className="muted">
        How long this workspace keeps each class of operational data. A policy
        is proposed by one person and approved by another; until then the
        platform&apos;s default applies. Access-denied records never fall below
        365 days.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {message && <p role="status">{message}</p>}
      {schedule && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Effective retention schedule</caption>
            <thead>
              <tr>
                <th scope="col">Data class</th>
                <th scope="col">Kept for</th>
                <th scope="col">Then</th>
                <th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((s) => (
                <tr key={s.data_class}>
                  <td>{s.data_class.replaceAll("_", " ").toLowerCase()}</td>
                  <td>{s.retention_days} days</td>
                  <td>{s.action.toLowerCase()}</td>
                  <td>
                    {s.source === "APPROVED_POLICY"
                      ? "approved policy"
                      : "platform default"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {policies && policies.length > 0 && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Retention policy proposals</caption>
            <thead>
              <tr>
                <th scope="col">Data class</th>
                <th scope="col">Days</th>
                <th scope="col">Status</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.object_id}>
                  <td>
                    {String(p.data.data_class)
                      .replaceAll("_", " ")
                      .toLowerCase()}
                  </td>
                  <td>{p.data.duration_days}</td>
                  <td>{p.lifecycle_state}</td>
                  <td>
                    {p.lifecycle_state === "Draft" &&
                      capabilities.includes("retention-policy.approve") && (
                        <button
                          className="secondary"
                          disabled={busy}
                          onClick={() => approve(p)}
                        >
                          Approve
                        </button>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {capabilities.includes("retention-policies.draft.create") && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            propose(e.currentTarget);
          }}
        >
          <label>
            Data class
            <select name="data_class" defaultValue="OPERATION_RECEIPT">
              {POLICY_CLASSES.map(([value, label, low, high]) => (
                <option key={value} value={value}>
                  {label} ({low}–{high} days)
                </option>
              ))}
            </select>
          </label>
          <label>
            Keep for (days)
            <input
              name="duration_days"
              type="number"
              min={1}
              max={3650}
              required
            />
          </label>
          <label>
            Reason for retention policy
            <input name="reason" required maxLength={2000} />
          </label>
          <button className="secondary" disabled={busy}>
            Propose policy
          </button>
        </form>
      )}
    </>
  );
}

type Hold = {
  hold_id: string;
  object_id: string;
  object_type: string;
  authority_reference: string;
  reason: string | null;
  review_at: string;
  placed_by: string | null;
  released_at: string | null;
};

/** Retention holds (v0.27): placed at once by a privacy officer or administrator, released only by
 * a different person; a held record is reported as HELD by every erasure plan. */
function RetentionHolds({
  base,
  capabilities,
  request,
  explain,
}: {
  base: string;
  capabilities: string[];
  request: Requester;
  explain: (e: unknown) => string;
}) {
  const [holds, setHolds] = useState<Hold[] | null>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0);
  const pending = usePendingOperations();
  const placeId = useRef("");
  useEffect(() => {
    const c = new AbortController();
    request(base + "retention-holds?limit=100", { signal: c.signal })
      .then((x) => !c.signal.aborted && setHolds(x.items))
      .catch((e) => e.name !== "AbortError" && setError(explain(e)));
    return () => c.abort();
  }, [base, tick]);
  async function place(form: HTMLFormElement) {
    const f = new FormData(form);
    const data = {
      object_id: String(f.get("object_id")).trim(),
      authority_reference: String(f.get("authority_reference")),
      reason: String(f.get("reason")),
      review_at: new Date(String(f.get("review_at"))).toISOString(),
    };
    if (!placeId.current) placeId.current = crypto.randomUUID();
    setBusy(true);
    setError("");
    try {
      await request(base + "retention-holds", {
        method: "POST",
        body: JSON.stringify({ operation_id: placeId.current, data }),
      });
      placeId.current = "";
      form.reset();
      setMessage("Hold placed.");
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  async function release(hold: Hold) {
    const key = "release-hold:" + hold.hold_id;
    const data = { reason: "Released after review" };
    setBusy(true);
    setError("");
    try {
      await request(
        base + "retention-holds/" + hold.hold_id + "/actions/release",
        {
          method: "POST",
          body: JSON.stringify({ operation_id: pending.id(key, data), data }),
        },
      );
      pending.done(key);
      setMessage("Hold released.");
      setTick((t) => t + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <h3>Retention holds</h3>
      <p className="muted">
        A hold keeps one record out of every erasure and retention action until
        a different person releases it.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {message && <p role="status">{message}</p>}
      {holds && holds.length > 0 && (
        <div className="table-scroll">
          <table>
            <caption className="sr-only">Retention holds</caption>
            <thead>
              <tr>
                <th scope="col">Record</th>
                <th scope="col">Authority</th>
                <th scope="col">Review</th>
                <th scope="col">Status</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {holds.map((h) => (
                <tr key={h.hold_id}>
                  <td>
                    {h.object_type} <code>{h.object_id.slice(0, 8)}</code>
                  </td>
                  <td>{h.authority_reference}</td>
                  <td>{new Date(h.review_at).toLocaleDateString()}</td>
                  <td>{h.released_at ? "Released" : "Active"}</td>
                  <td>
                    {!h.released_at &&
                      capabilities.includes("retention.release") && (
                        <button
                          className="secondary"
                          disabled={busy}
                          onClick={() => release(h)}
                        >
                          Release
                        </button>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {capabilities.includes("retention.hold") && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            place(e.currentTarget);
          }}
        >
          <label>
            Record identifier
            <input name="object_id" required pattern="[0-9a-fA-F-]{36}" />
          </label>
          <label>
            Authority reference
            <input name="authority_reference" required maxLength={200} />
          </label>
          <label>
            Reason for retention hold
            <input name="reason" required maxLength={2000} />
          </label>
          <label>
            Review on
            <input name="review_at" type="date" required />
          </label>
          <button className="secondary" disabled={busy}>
            Place hold
          </button>
        </form>
      )}
    </>
  );
}
