import { useEffect, useRef, useState, type FormEvent } from "react";

type Props = {
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  identity: string;
  close: () => void;
};
const base = "/v1/platform/access-bootstraps";
function Capabilities({ roles }: { roles: Record<string, string[]> }) {
  return (
    <div>
      {Object.entries(roles).map(([name, caps]) => (
        <details key={name}>
          <summary>
            {name.replaceAll("_", " ")}: {caps.length} capabilities
          </summary>
          <ul>
            {caps.map((cap) => (
              <li key={cap}>
                <code>{cap}</code>
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
export function InitialAccess({ request, explain, identity, close }: Props) {
  const [directory, setDirectory] = useState<any>(null);
  const [tenants, setTenants] = useState<any>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const [action, setAction] = useState("");
  const [roles, setRoles] = useState(["PROGRAMME_MANAGER"]);
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
    const controller = new AbortController();
    Promise.all([
      request(base, { signal: controller.signal }),
      request("/v1/platform/tenants", { signal: controller.signal }),
    ])
      .then(([d, t]) => {
        if (!controller.signal.aborted) {
          setDirectory(d);
          setTenants(t);
        }
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      });
    return () => controller.abort();
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    try {
      const tenant = creating
        ? tenants.items.find((t: any) => t.tenant_id === form.get("tenant_id"))
        : null;
      const data: any = { reason: form.get("reason") };
      if (creating)
        Object.assign(data, {
          second_identity_id: form.get("second_identity_id"),
          profile_hash: directory.profile_hash,
          role_names: roles,
          expires_at: new Date(String(form.get("expires_at"))).toISOString(),
        });
      const path = creating
        ? `/v1/platform/tenants/${tenant.tenant_id}/access-bootstrap`
        : `${base}/${selected.request_id}/actions/${action}`;
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
        `${result.operating_name}: initial access ${result.state}. Change saved.`,
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const eligible = (tenants?.items || []).filter(
    (t: any) =>
      t.state === "Active" &&
      t.owner_identity_id === identity &&
      !directory?.items.some(
        (r: any) =>
          r.tenant_id === t.tenant_id &&
          ["Requested", "Accepted", "Applied"].includes(r.state),
      ),
  );
  return (
    <main className="tenant-console">
      <button className="secondary" disabled={busy} onClick={close}>
        Back to tenant lifecycle
      </button>
      <h1>Initial access</h1>
      <p>
        The owner and a second administrator receive time-limited administration
        access. Their delegation ceiling is the exact capability list reviewed
        here, across all workspace records. Business access requires a separate
        grant request and independent approval.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {notice && (
        <div role="status" className="success">
          {notice}
        </div>
      )}
      <div className="toolbar">
        <button
          className="secondary"
          disabled={busy}
          onClick={() => refresh().catch((e) => setError(explain(e)))}
        >
          Refresh initial access
        </button>
        {!!eligible.length && (
          <button
            className="primary"
            disabled={busy}
            onClick={() => {
              setCreating(true);
              setSelected(null);
              setError("");
            }}
          >
            Propose initial access
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
            Load more eligible tenants
          </button>
        )}
      </div>
      {!directory ? (
        <p role="status">Loading access reviews…</p>
      ) : (
        <>
          {!directory.items.length && (
            <p>No initial access reviews are available.</p>
          )}
          <div className="tenant-cards">
            {directory.items.map((row: any) => (
              <article
                className="panel"
                key={row.request_id}
                aria-label={row.operating_name + " initial access"}
              >
                <h2>{row.operating_name}</h2>
                <p>
                  <strong>{row.state}</strong>
                </p>
                <p>
                  Owner: <code>{row.owner_identity_id}</code>
                  <br />
                  Second administrator: <code>{row.second_identity_id}</code>
                </p>
                <p>
                  Access and delegation end:{" "}
                  {new Date(row.expires_at).toLocaleString()}. Review deadline:{" "}
                  {new Date(row.review_expires_at).toLocaleString()}.
                </p>
                <p>Proposal reason: {row.reason}</p>
                <p>
                  TENANT ADMIN is granted to both administrators. The remaining
                  roles are delegation ceilings only.
                </p>
                <Capabilities roles={row.manifest.roles} />
                {row.state === "Applied" && (
                  <p>
                    Initial access is provisioned. Return to the workspace and
                    select this tenant. Use People &amp; access to request
                    business access for the second administrator; the owner can
                    approve it independently.
                  </p>
                )}
                <div className="toolbar">
                  {[
                    [
                      "accept",
                      "Accept administrator role",
                      row.state === "Requested" &&
                        row.second_identity_id === identity,
                    ],
                    [
                      "approve",
                      "Approve initial access",
                      row.state === "Accepted" && directory.operator,
                    ],
                    [
                      "reject",
                      "Reject initial access",
                      ["Requested", "Accepted"].includes(row.state) &&
                        directory.operator,
                    ],
                    [
                      "cancel",
                      "Withdraw proposal",
                      ["Requested", "Accepted"].includes(row.state) &&
                        row.owner_identity_id === identity,
                    ],
                  ]
                    .filter(([, , show]) => show)
                    .map(([key, label]) => (
                      <button
                        className="secondary"
                        key={String(key)}
                        disabled={busy}
                        onClick={() => {
                          setSelected(row);
                          setAction(String(key));
                          setCreating(false);
                          setError("");
                        }}
                      >
                        {String(label)}
                      </button>
                    ))}
                </div>
              </article>
            ))}
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
              Load more access reviews
            </button>
          )}
        </>
      )}
      {(creating || selected) && (
        <section className="panel" aria-label="Initial access change">
          <h2>
            {creating
              ? "Propose initial access"
              : action + " initial access: " + selected.operating_name}
          </h2>
          {creating ? (
            <p>
              Choose a registered person with a verified identity. They must
              accept this proposal, then an independent platform operator must
              approve it within seven days. No invitation email is sent.
            </p>
          ) : (
            <>
              <p>
                Review the exact package below. Approval requires an operator
                who is a different person from both administrators. This
                one-time provision cannot be repeated after access is revoked.
              </p>
              <p>
                Access expires: {new Date(selected.expires_at).toLocaleString()}
              </p>
              <Capabilities roles={selected.manifest.roles} />
            </>
          )}
          <form onSubmit={submit}>
            {creating && (
              <>
                <label>
                  Tenant
                  <select name="tenant_id" aria-label="Tenant" required>
                    {eligible.map((t: any) => (
                      <option key={t.tenant_id} value={t.tenant_id}>
                        {t.operating_name}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Second administrator identity UUID
                  <input
                    name="second_identity_id"
                    required
                    pattern="[0-9a-fA-F-]{36}"
                  />
                </label>
                <label>
                  Access expiry
                  <input name="expires_at" type="datetime-local" required />
                </label>
                <p>
                  Choose a future expiry within 90 days. Both administrators’
                  grants and delegation authority end then; the second
                  administrator’s membership also expires. Delegation renewal is
                  not available in this release.
                </p>
                <fieldset>
                  <legend>Business roles permitted for later delegation</legend>
                  {Object.keys(directory.profile.roles)
                    .filter((name) => name !== "TENANT_ADMIN")
                    .map((name) => (
                      <label key={name} className="check-row">
                        <input
                          type="checkbox"
                          checked={roles.includes(name)}
                          onChange={(e) =>
                            setRoles(
                              e.target.checked
                                ? [...roles, name].sort()
                                : roles.filter((r) => r !== name),
                            )
                          }
                        />
                        {name.replaceAll("_", " ")}
                      </label>
                    ))}
                </fieldset>
                <Capabilities
                  roles={Object.fromEntries(
                    ["TENANT_ADMIN", ...roles].map((name) => [
                      name,
                      directory.profile.roles[name],
                    ]),
                  )}
                />
              </>
            )}
            <label>
              Reason
              <textarea name="reason" required maxLength={1000} />
            </label>
            <div className="toolbar">
              <button
                type="submit"
                className="primary"
                disabled={busy || (creating && !roles.length)}
              >
                {busy ? "Saving…" : "Confirm initial access change"}
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
