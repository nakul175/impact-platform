import { useEffect, useRef, useState, type FormEvent } from "react";

type Props = {
  development: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  identity: string;
  close: () => void;
};
const base = "/v1/platform/recovery-contacts";
const labels: Record<string, string> = {
  verify: "Verify my recovery contact",
  approve: "Approve recovery contact",
  reject: "Reject nomination",
  cancel: "Withdraw nomination",
  decline: "Decline nomination",
  revoke: "Revoke recovery contact",
};
export function RecoveryContacts({
  development,
  request,
  explain,
  identity,
  close,
}: Props) {
  const [directory, setDirectory] = useState<any>(null);
  const [tenants, setTenants] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [creating, setCreating] = useState(false);
  const [tenantId, setTenantId] = useState("");
  const [selected, setSelected] = useState<any>(null);
  const [action, setAction] = useState("");
  const retry = useRef({ key: "", operation: "" });
  async function refresh() {
    const [d, t] = await Promise.all([
      request(base),
      request("/v1/platform/tenants"),
    ]);
    setDirectory(d);
    setTenants(t);
  }
  useEffect(() => {
    const c = new AbortController();
    Promise.all([
      request(base, { signal: c.signal }),
      request("/v1/platform/tenants", { signal: c.signal }),
    ])
      .then(([d, t]) => {
        if (!c.signal.aborted) {
          setDirectory(d);
          setTenants(t);
        }
      })
      .catch((e) => {
        if (!c.signal.aborted) setError(explain(e));
      });
    return () => c.abort();
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    try {
      const tenant = creating
        ? tenants.items.find((t: any) => t.tenant_id === tenantId)
        : null;
      const data: any = { reason: form.get("reason") };
      if (creating)
        Object.assign(data, {
          nominee_identity_id: form.get("nominee_identity_id"),
          expected_contact_revision: tenant.recovery_contact.revision_id,
          expires_at: new Date(String(form.get("expires_at"))).toISOString(),
        });
      const path = creating
        ? `/v1/platform/tenants/${tenantId}/recovery-contacts`
        : `${base}/${selected.contact_id}/actions/${action}`;
      const expected_revision = (tenant || selected).revision_id;
      const key = JSON.stringify([path, expected_revision, data]);
      if (retry.current.key !== key)
        retry.current = { key, operation: crypto.randomUUID() };
      const result = await request(path, {
        method: "POST",
        body: JSON.stringify({
          operation_id: retry.current.operation,
          expected_revision,
          data,
        }),
      });
      setCreating(false);
      setSelected(null);
      retry.current = { key: "", operation: "" };
      await refresh();
      setNotice(
        `${result.operating_name}: recovery contact ${result.state}. Change saved.`,
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const eligible = (tenants?.items || []).filter(
    (t: any) =>
      t.owner_identity_id === identity &&
      ["Provisioning", "Active", "Suspended"].includes(t.state),
  );
  const chosen = eligible.find((t: any) => t.tenant_id === tenantId);
  return (
    <main className="tenant-console">
      <button className="secondary" disabled={busy} onClick={close}>
        Back to tenant lifecycle
      </button>
      <h1>Recovery contacts</h1>
      {development && (
        <p className="demo-note">
          Development workspace: identity verification is synthetic.
        </p>
      )}
      <p>
        Nominate one primary contact, obtain their confirmation, then have an
        independent platform operator approve it. A contact receives no
        workspace access and cannot reset an account or transfer ownership.
      </p>
      <p>
        Verification uses the nominated person’s existing verified account and
        recent MFA-backed sign-in. This release does not send email or SMS
        challenges.
      </p>
      {error && (
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
          className="secondary"
          disabled={busy}
          onClick={() => refresh().catch((e) => setError(explain(e)))}
        >
          Refresh recovery contacts
        </button>
        {!!eligible.length && (
          <button
            className="primary"
            disabled={busy}
            onClick={() => {
              setCreating(true);
              setSelected(null);
              setTenantId(eligible[0].tenant_id);
              setError("");
            }}
          >
            Nominate recovery contact
          </button>
        )}
        {tenants?.next_cursor && (
          <button
            className="secondary"
            disabled={busy}
            onClick={async () => {
              try {
                const t = await request(
                  "/v1/platform/tenants?cursor=" + tenants.next_cursor,
                );
                setTenants({ ...t, items: [...tenants.items, ...t.items] });
              } catch (e) {
                setError(explain(e));
              }
            }}
          >
            Load more tenants
          </button>
        )}
      </div>
      {!directory ? (
        <p role="status">Loading recovery contacts…</p>
      ) : (
        <>
          {!directory.items.length && (
            <p>No recovery contacts are available.</p>
          )}
          <div className="tenant-cards">
            {directory.items.map((row: any) => {
              const owner = tenants?.items.some(
                (t: any) =>
                  t.tenant_id === row.tenant_id &&
                  t.owner_identity_id === identity,
              );
              const nominee = row.nominee_identity_id === identity;
              const pending = ["Nominated", "Verified"].includes(row.state);
              const buttons = [
                ["verify", row.state === "Nominated" && nominee],
                ["approve", row.state === "Verified" && directory.operator],
                ["reject", pending && directory.operator],
                ["cancel", pending && owner],
                ["decline", pending && nominee],
                [
                  "revoke",
                  row.state === "Active" &&
                    (owner || nominee || directory.operator),
                ],
              ];
              return (
                <article
                  className="panel"
                  key={row.contact_id}
                  aria-label={`${row.operating_name} recovery contact ${row.display_name}`}
                >
                  <h2>{row.operating_name}</h2>
                  <p>
                    <strong>{row.state}</strong> · {row.display_name}
                  </p>
                  <p>
                    {row.email_mask}
                    <br />
                    Identity: <code>{row.nominee_identity_id}</code>
                  </p>
                  <p>
                    Eligible for readiness:{" "}
                    {row.verification.eligible ? "Yes" : "No"}
                    {row.state === "Active" && !row.verification.eligible
                      ? " — " +
                        row.verification.reason
                          .replaceAll("_", " ")
                          .toLowerCase()
                      : ""}
                    .
                  </p>
                  <p>
                    Expires: {new Date(row.expires_at).toLocaleString()}. Review
                    deadline: {new Date(row.review_expires_at).toLocaleString()}
                    .
                  </p>
                  {row.verified_at && (
                    <p>
                      Account confirmed:{" "}
                      {new Date(row.verified_at).toLocaleString()}. Independent
                      approval is required within 24 hours of confirmation.
                    </p>
                  )}
                  {row.approved_at && (
                    <p>
                      Approved: {new Date(row.approved_at).toLocaleString()}
                      <br />
                      Reviewer: <code>{row.approved_by}</code>
                    </p>
                  )}
                  {row.replaces_contact_id && (
                    <p>
                      This nomination replaces or renews an earlier contact only
                      after approval.
                    </p>
                  )}
                  <p>Nomination reason: {row.reason}</p>
                  <div className="toolbar">
                    {buttons
                      .filter(([, show]) => show)
                      .map(([key]) => (
                        <button
                          key={String(key)}
                          className="secondary"
                          disabled={busy}
                          onClick={() => {
                            setSelected(row);
                            setAction(String(key));
                            setCreating(false);
                            setError("");
                          }}
                        >
                          {labels[String(key)]}
                        </button>
                      ))}
                  </div>
                </article>
              );
            })}
          </div>
          {directory.next_cursor && (
            <button
              className="secondary"
              disabled={busy}
              onClick={async () => {
                try {
                  const d = await request(
                    base + "?cursor=" + directory.next_cursor,
                  );
                  setDirectory({
                    ...d,
                    items: [...directory.items, ...d.items],
                  });
                } catch (e) {
                  setError(explain(e));
                }
              }}
            >
              Load more recovery contacts
            </button>
          )}
        </>
      )}
      {(creating || selected) && (
        <section className="panel" aria-label="Recovery contact change">
          <h2>{creating ? "Nominate recovery contact" : labels[action]}</h2>
          {!creating && (
            <>
              <p>
                {selected.operating_name}: {selected.display_name} ·{" "}
                {selected.email_mask}
              </p>
              <p>Expires: {new Date(selected.expires_at).toLocaleString()}.</p>
              <p>
                {action === "revoke"
                  ? "Revocation removes this contact from readiness immediately. It blocks future activation or reactivation until an eligible contact is approved. It does not suspend current business access."
                  : action === "verify"
                    ? "Confirm that you accept this tenant’s recovery-contact nomination using the displayed registered account. No account recovery rights or workspace permissions are granted."
                    : "Approval must come from a different person from the owner and contact. The existing contact remains in place until replacement approval succeeds."}
              </p>
            </>
          )}
          <form onSubmit={submit}>
            {creating && (
              <>
                <label>
                  Tenant
                  <select
                    aria-label="Tenant"
                    required
                    value={tenantId}
                    onChange={(e) => setTenantId(e.target.value)}
                  >
                    {eligible.map((t: any) => (
                      <option key={t.tenant_id} value={t.tenant_id}>
                        {t.operating_name}
                      </option>
                    ))}
                  </select>
                </label>
                <p>
                  {chosen?.recovery_contact.contact_id
                    ? "An existing contact is recorded. This nomination will replace or renew it after verification and independent approval."
                    : "No active recovery contact is recorded for this tenant."}
                </p>
                <label>
                  Nominated contact identity UUID
                  <input
                    name="nominee_identity_id"
                    required
                    pattern="[0-9a-fA-F-]{36}"
                  />
                </label>
                <label>
                  Contact expiry
                  <input name="expires_at" type="datetime-local" required />
                </label>
                <p>
                  Choose an expiry within 90 days. The contact must confirm
                  within seven days; approval must follow within 24 hours. To
                  renew verification, nominate the same identity again and
                  complete the review.
                </p>
              </>
            )}
            <label>
              Reason
              <textarea name="reason" required maxLength={1000} />
            </label>
            <div className="toolbar">
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Saving…" : "Confirm recovery contact change"}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => {
                  setCreating(false);
                  setSelected(null);
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}
    </main>
  );
}
