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
  if (!may("privacy-cases.read") && !capabilities.includes("retention.read"))
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
                    ? " · " + c.data.outcome.replaceAll("_", " ").toLowerCase()
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
                      <button className="secondary" onClick={() => download(c)}>
                        Download export
                      </button>
                    )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {proofs && (
        <>
          <h3>Retention proof</h3>
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
        </>
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
                          {e.object_type} <code>{e.object_id.slice(0, 8)}</code>
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
