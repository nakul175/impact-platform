import React, { useEffect, useState, useRef, type FormEvent } from "react";
import { InitialAccess } from "./InitialAccess";
import { RecoveryContacts } from "./RecoveryContacts";
import { AuthorityRenewal } from "./AuthorityRenewal";
import { AccessUpgrade } from "./AccessUpgrade";
import { Workers } from "./Workers";
import { StatusBanner } from "./StatusBanner";
import { Operators } from "./Operators";

export type DialogComponent = React.ComponentType<{
  title: string;
  close: () => void;
  children: React.ReactNode;
}>;
type Props = {
  development: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  identity: string;
  close: () => void;
  logout: () => void;
  Dialog: DialogComponent;
};
export function TenantLifecycle({
  development,
  request,
  explain,
  identity,
  close,
  logout,
  Dialog,
}: Props) {
  const [directory, setDirectory] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [action, setAction] = useState("");
  const [creating, setCreating] = useState(false);
  const [initialAccess, setInitialAccess] = useState(false);
  const [recoveryContacts, setRecoveryContacts] = useState(false);
  const [authorityRenewal, setAuthorityRenewal] = useState(false);
  const [accessUpgrade, setAccessUpgrade] = useState(false);
  const [people, setPeople] = useState<any[]>([]);
  const retry = useRef({ key: "", operation: "" });
  useEffect(() => {
    if (!creating) return;
    // Registered people (operators only): the owner is chosen by name, not typed as a UUID.
    request("/v1/platform/operators")
      .then((r) => setPeople(r.identities || []))
      .catch(() => setPeople([]));
  }, [creating]);
  const base = "/v1/platform/tenants";
  // The change form opens as a modal dialog from the card that was clicked (v0.27): before,
  // it rendered at the foot of the page, below the operators, workers and deliveries panels.
  const open = creating || Boolean(selected);
  const actionLabels: Record<string, string> = {
    "accept-owner": "Accept ownership",
    activate: "Activate tenant",
    suspend: "Suspend tenant",
    reactivate: "Reactivate tenant",
    "begin-closure": "Begin closure",
  };
  function cancel() {
    if (busy) return;
    setCreating(false);
    setSelected(null);
    setAction("");
    setError("");
  }
  async function refresh(after?: string) {
    const result = await request(
      base + (after ? "?cursor=" + encodeURIComponent(after) : ""),
    );
    setDirectory((old: any) =>
      after ? { ...result, items: [...old.items, ...result.items] } : result,
    );
    return result;
  }
  useEffect(() => {
    let mounted = true;
    request(base)
      .then((r) => {
        if (mounted) setDirectory(r);
      })
      .catch((e) => {
        if (mounted) setError(explain(e));
      });
    return () => {
      mounted = false;
    };
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    const data: any = { reason: form.get("reason") };
    if (creating)
      Object.assign(data, {
        operating_name: form.get("operating_name"),
        owner_identity_id: form.get("owner_identity_id"),
        qualification_id: form.get("qualification_id"),
        reporting_zone: form.get("reporting_zone"),
        retention_days: Number(form.get("retention_days")),
        privacy_reference: form.get("privacy_reference"),
      });
    try {
      const path = creating
        ? base
        : `${base}/${selected.tenant_id}/actions/${action}`;
      const key = JSON.stringify([path, selected?.revision_id, data]);
      if (retry.current.key !== key)
        retry.current = { key, operation: crypto.randomUUID() };
      const result = await request(path, {
        method: "POST",
        body: JSON.stringify({
          operation_id: retry.current.operation,
          ...(!creating ? { expected_revision: selected.revision_id } : {}),
          data,
        }),
      });
      setSelected(null);
      setCreating(false);
      setAction("");
      retry.current = { key: "", operation: "" };
      await refresh();
      setNotice(`${result.operating_name}: ${result.state}. Change saved.`);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  if (recoveryContacts)
    return (
      <RecoveryContacts
        development={development}
        request={request}
        explain={explain}
        identity={identity}
        close={() => {
          setRecoveryContacts(false);
          refresh().catch((e) => setError(explain(e)));
        }}
      />
    );
  if (initialAccess)
    return (
      <InitialAccess
        request={request}
        explain={explain}
        identity={identity}
        close={() => setInitialAccess(false)}
      />
    );
  if (accessUpgrade)
    return (
      <AccessUpgrade
        request={request}
        explain={explain}
        identity={identity}
        close={() => {
          setAccessUpgrade(false);
          refresh().catch((e) => setError(explain(e)));
        }}
      />
    );
  if (authorityRenewal)
    return (
      <AuthorityRenewal
        request={request}
        explain={explain}
        identity={identity}
        close={() => {
          setAuthorityRenewal(false);
          refresh().catch((e) => setError(explain(e)));
        }}
      />
    );
  return (
    <main className="tenant-console">
      <div className="toolbar">
        <button className="secondary" onClick={close}>
          Back to workspace
        </button>
        <button className="secondary" onClick={logout}>
          Sign out
        </button>
      </div>
      <h1>Tenant lifecycle</h1>
      <StatusBanner request={request} />
      <button className="secondary" onClick={() => setRecoveryContacts(true)}>
        Recovery contacts
      </button>
      <button className="secondary" onClick={() => setInitialAccess(true)}>
        Initial access
      </button>
      <button className="secondary" onClick={() => setAuthorityRenewal(true)}>
        Authority renewal
      </button>
      <button className="secondary" onClick={() => setAccessUpgrade(true)}>
        Extend organisation access
      </button>
      <p>
        Review ownership and deployment policy before activation. Ownership does
        not grant programme-data access.
      </p>
      {error && !open && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="success" role="status">
          {notice}
        </div>
      )}
      <div className="toolbar">
        <button
          disabled={busy}
          className="secondary"
          onClick={() => refresh().catch((e) => setError(explain(e)))}
        >
          Refresh tenants
        </button>
        {directory?.operator && (
          <button
            className="primary"
            onClick={() => {
              setCreating(true);
              setSelected(null);
              setError("");
            }}
          >
            Request tenant
          </button>
        )}
      </div>
      {!directory ? (
        <p role="status">Loading tenant requests…</p>
      ) : (
        <>
          <p>
            {directory.operator
              ? "Platform operator: configuration access only."
              : "Only your nominated ownership requests are shown."}
          </p>
          {!directory.items.length && <p>No tenant requests are available.</p>}
          <div className="tenant-cards">
            {directory.items.map((row: any) => (
              <article
                className="panel"
                key={row.tenant_id}
                aria-label={row.operating_name}
              >
                <h2>{row.operating_name}</h2>
                <p>
                  <strong>{row.state}</strong> · {row.region} ·{" "}
                  {row.reporting_zone}
                </p>
                <p>
                  Retention: {row.retention_days} days, then review. Policy:{" "}
                  {row.privacy_reference}
                </p>
                <p>
                  Owner identity: <code>{row.owner_identity_id}</code>
                </p>
                <p>
                  Impact: {row.impact.unfinished_jobs} unfinished jobs;{" "}
                  {row.impact.active_schedules} active schedules;{" "}
                  {row.impact.unsent_events} undelivered notices or emails;{" "}
                  {row.impact.retention_holds} retention holds.
                </p>
                <details>
                  <summary>Readiness checks</summary>
                  <ul>
                    {Object.entries(row.readiness).map(([key, value]) => (
                      <li key={key}>
                        {key.replaceAll("_", " ")}: {value ? "Pass" : "Pending"}
                      </li>
                    ))}
                  </ul>
                </details>
                <div className="toolbar">
                  {row.state === "Requested" &&
                    row.owner_identity_id === identity && (
                      <button
                        className="primary"
                        onClick={() => {
                          setSelected(row);
                          setAction("accept-owner");
                          setCreating(false);
                        }}
                      >
                        Accept ownership
                      </button>
                    )}
                  {directory.operator &&
                    [
                      ["Provisioning", "activate", "Activate tenant"],
                      ["Active", "suspend", "Suspend tenant"],
                      ["Suspended", "reactivate", "Reactivate tenant"],
                    ]
                      .filter(([state]) => state === row.state)
                      .map(([, key, label]) => (
                        <button
                          key={key}
                          className="secondary"
                          onClick={() => {
                            setSelected(row);
                            setAction(key);
                            setCreating(false);
                          }}
                        >
                          {label}
                        </button>
                      ))}
                  {directory.operator &&
                    ["Active", "Suspended"].includes(row.state) && (
                      <button
                        className="secondary"
                        onClick={() => {
                          setSelected(row);
                          setAction("begin-closure");
                          setCreating(false);
                        }}
                      >
                        Begin closure
                      </button>
                    )}
                </div>
              </article>
            ))}
          </div>
          {directory.next_cursor && (
            <button
              className="secondary"
              onClick={() =>
                refresh(directory.next_cursor).catch((e) =>
                  setError(explain(e)),
                )
              }
            >
              Load more tenants
            </button>
          )}
          <Operators
            request={request}
            explain={explain}
            changed={() => refresh().catch((e) => setError(explain(e)))}
          />
          {directory.operator && (
            <Workers request={request} explain={explain} />
          )}
        </>
      )}
      {open && (
        <Dialog
          title={
            creating
              ? "New tenant request"
              : (actionLabels[action] || action.replaceAll("-", " ")) +
                ": " +
                selected.operating_name
          }
          close={cancel}
        >
          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}
          {!creating && (
            <p>
              {action === "accept-owner"
                ? "Accept the displayed configuration. An independent operator must activate it. No data access is granted."
                : action === "activate" || action === "reactivate"
                  ? "Activation requires current deployment evidence and an operator independent of the requester and nominated owner. Held work is not resumed."
                  : "This blocks tenant access and holds background deliveries. Beginning closure does not delete data and cannot be reversed in this release."}
            </p>
          )}
          <form onSubmit={submit}>
            {creating && (
              <>
                <label>
                  Operating name
                  <input name="operating_name" required maxLength={200} />
                </label>
                {people.length ? (
                  <label>
                    Organisation owner (a different person from you)
                    <select
                      name="owner_identity_id"
                      aria-label="Organisation owner"
                      required
                      defaultValue=""
                    >
                      <option value="" disabled>
                        Select the person who will own it
                      </option>
                      {people
                        .filter((p: any) => p.identity_id !== identity)
                        .map((p: any) => (
                          <option
                            key={p.identity_id}
                            value={p.identity_id}
                            disabled={!p.signed_in}
                          >
                            {p.display_name} {p.email_mask || ""}
                            {p.signed_in ? "" : " (must sign in once first)"}
                          </option>
                        ))}
                    </select>
                  </label>
                ) : (
                  <label>
                    Nominated owner identity reference
                    <input
                      name="owner_identity_id"
                      required
                      pattern="[0-9a-fA-F-]{36}"
                    />
                  </label>
                )}
                <label>
                  Qualified deployment
                  <select
                    name="qualification_id"
                    aria-label="Qualified deployment"
                    required
                  >
                    <option value="">Select deployment</option>
                    {directory.qualifications.map((q: any) => (
                      <option
                        key={q.qualification_id}
                        value={q.qualification_id}
                      >
                        {q.region} / {q.environment} / {q.privacy_reference}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Reporting time zone
                  <input
                    name="reporting_zone"
                    defaultValue="Asia/Kolkata"
                    required
                    maxLength={80}
                  />
                </label>
                <label>
                  Retention days
                  <input
                    name="retention_days"
                    type="number"
                    min={1}
                    max={36500}
                    defaultValue={365}
                    required
                  />
                </label>
                <label>
                  Privacy policy reference
                  <input name="privacy_reference" required maxLength={300} />
                </label>
                <p>
                  The owner must already have a verified registered identity.
                  This request sends no email. Local deployment fixtures are not
                  production qualification.
                </p>
              </>
            )}
            <label>
              Reason
              <textarea name="reason" required maxLength={1000} />
            </label>
            <div className="dialog-actions">
              <button type="submit" className="primary" disabled={busy}>
                {busy ? "Saving…" : "Confirm tenant change"}
              </button>
              <button
                type="button"
                disabled={busy}
                className="secondary"
                onClick={cancel}
              >
                Cancel
              </button>
            </div>
          </form>
        </Dialog>
      )}
    </main>
  );
}
