import { useEffect, useRef, useState, type FormEvent } from "react";

// Shapes mirror apps/api/impact_api/renewal_contracts.py (PRINCIPAL, MANIFEST, ITEM,
// DIRECTORY, AUTHORITY, RECEIPT) and the tenant directory rows this console reads.
export interface Principal {
  principal_id: string;
  identity_id: string;
  membership_id: string;
  scope_id: string;
  capabilities: string[];
  expires_at: string;
  assignment_ids: string[];
  grant_ids: string[];
}
export interface Manifest {
  version: string;
  authority_ids: string[];
  principals: Principal[];
}
export type RenewalState =
  | "Requested"
  | "Accepted"
  | "Applied"
  | "Rejected"
  | "Cancelled";
export type UnavailableReason =
  | "AUTHORITY_UNAVAILABLE"
  | "SECOND_ADMIN_UNAVAILABLE"
  | "TENANT_NOT_ACTIVE"
  | "TENANT_NOT_READY"
  | "RENEWAL_PENDING";
export interface Authority {
  tenant_id: string;
  tenant_revision: string;
  bootstrap_request_id: string | null;
  owner_identity_id: string;
  second_identity_id: string | null;
  authority_hash: string | null;
  earliest_expires_at: string | null;
  principals: Principal[];
  renewable: boolean;
  reason_unavailable: UnavailableReason | null;
}
export interface RenewalItem {
  request_id: string;
  tenant_id: string;
  revision_id: string;
  operating_name: string;
  bootstrap_request_id: string;
  owner_identity_id: string;
  second_identity_id: string;
  state: RenewalState;
  manifest: Manifest;
  authority_hash: string;
  previous_expires_at: string;
  expires_at: string;
  review_expires_at: string;
  reason: string;
  accepted_at: string | null;
  approved_by: string | null;
  applied_at: string | null;
}
export interface Directory {
  operator: boolean;
  items: RenewalItem[];
  next_cursor: string | null;
}
export type Receipt = RenewalItem & { operation_id: string };
interface TenantSummary {
  tenant_id: string;
  operating_name: string;
  state: string;
  owner_identity_id: string;
}
interface TenantDirectory {
  items: TenantSummary[];
  next_cursor: string | null;
}
type ReviewAction = "accept" | "approve" | "reject" | "cancel";

type Props = {
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
  identity: string;
  close: () => void;
};
const base = "/v1/platform/authority-renewals";
const DAY = 86400000;
const labels: Record<ReviewAction, string> = {
  accept: "Accept renewal",
  approve: "Approve renewal",
  reject: "Reject renewal",
  cancel: "Withdraw proposal",
};
const confirmations: Record<ReviewAction | "propose", string> = {
  propose: "Confirm renewal proposal",
  accept: "Confirm acceptance",
  approve: "Confirm approval",
  reject: "Confirm rejection",
  cancel: "Confirm withdrawal",
};
const guidance: Record<ReviewAction, string> = {
  accept:
    "Confirm that you, as the second administrator, accept this renewal of the exact authority shown. An independent platform operator must still approve it before the review deadline; nothing changes until then.",
  approve:
    "Approval rechecks the pinned tenant, owner, readiness and authority manifest, then extends every pinned ceiling, grant and role assignment to the proposed expiry. It must come from a platform operator who is a different person from both administrators.",
  reject:
    "Rejection records the decision. Current authority and its expiry are unchanged.",
  cancel:
    "Withdrawal records the decision. Current authority and its expiry are unchanged; a fresh proposal can follow.",
};
const unavailable: Record<UnavailableReason, string> = {
  AUTHORITY_UNAVAILABLE:
    "initial access has not been applied, or the owner no longer holds current delegated authority in this tenant.",
  SECOND_ADMIN_UNAVAILABLE:
    "exactly one second administrator with current delegated authority is required.",
  TENANT_NOT_ACTIVE:
    "the tenant must be Active before its delegated authority can be renewed.",
  TENANT_NOT_READY:
    "the tenant no longer passes its readiness checks (deployment qualification, owner membership and verified recovery contact). Restore readiness before proposing a renewal.",
  RENEWAL_PENDING:
    "a renewal is already pending review. Complete, withdraw or reject it before proposing another.",
};
const states: Record<RenewalState, string> = {
  Requested: "awaiting the second administrator’s acceptance",
  Accepted: "awaiting independent platform operator approval",
  Applied:
    "every pinned ceiling, grant and assignment ends at the renewed expiry",
  Rejected: "rejected by a platform operator; authority unchanged",
  Cancelled: "withdrawn by the owner; authority unchanged",
};
const pendingStates: RenewalState[] = ["Requested", "Accepted"];
function mask(id: string | null | undefined) {
  return id ? id.slice(0, 8) + "…" + id.slice(-4) : "—";
}
function when(value: string | number | null | undefined) {
  return value ? new Date(value).toLocaleString() : "—";
}
function Principals({
  principals,
  owner,
}: {
  principals: Principal[];
  owner: string;
}) {
  return (
    <div className="renewal-principals">
      {principals.map((p) => (
        <details key={p.principal_id}>
          <summary>
            {p.identity_id === owner ? "Owner" : "Second administrator"}{" "}
            <code>{mask(p.identity_id)}</code>: {p.capabilities.length}{" "}
            capabilities, {p.grant_ids.length} grants, {p.assignment_ids.length}{" "}
            role assignments; expires {when(p.expires_at)}
          </summary>
          <ul>
            {p.capabilities.map((cap) => (
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
export function AuthorityRenewal({ request, explain, identity, close }: Props) {
  const [directory, setDirectory] = useState<Directory | null>(null);
  const [tenants, setTenants] = useState<TenantDirectory | null>(null);
  const [tenantId, setTenantId] = useState("");
  const [authority, setAuthority] = useState<Authority | null>(null);
  const [authorityNote, setAuthorityNote] = useState("");
  const [tick, setTick] = useState(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [proposing, setProposing] = useState(false);
  const [selected, setSelected] = useState<RenewalItem | null>(null);
  const [action, setAction] = useState<ReviewAction>("accept");
  const retry = useRef({ key: "", operation: "" });
  function preferred(items: TenantSummary[]) {
    const mine = items.filter((t) => t.owner_identity_id === identity);
    return (
      (
        mine.find((t) => t.state === "Active") ||
        mine[0] ||
        items.find((t) => t.state === "Active") ||
        items[0]
      )?.tenant_id || ""
    );
  }
  async function load(options?: RequestInit) {
    const [d, t] = await Promise.all([
      request(base, options) as Promise<Directory>,
      request("/v1/platform/tenants", options) as Promise<TenantDirectory>,
    ]);
    return { d, t };
  }
  async function refresh() {
    const { d, t } = await load();
    setDirectory(d);
    setTenants(t);
    setTenantId((current) =>
      t.items.some((x) => x.tenant_id === current)
        ? current
        : preferred(t.items),
    );
    setTick((n) => n + 1);
  }
  useEffect(() => {
    const c = new AbortController();
    load({ signal: c.signal })
      .then(({ d, t }) => {
        if (c.signal.aborted) return;
        setDirectory(d);
        setTenants(t);
        setTenantId((current) => current || preferred(t.items));
      })
      .catch((e) => {
        if (!c.signal.aborted) setError(explain(e));
      });
    return () => c.abort();
  }, []);
  useEffect(() => {
    setAuthority(null);
    setAuthorityNote("");
    if (!tenantId) return;
    const c = new AbortController();
    (
      request(`/v1/platform/tenants/${tenantId}/authority`, {
        signal: c.signal,
      }) as Promise<Authority>
    )
      .then((a) => {
        if (!c.signal.aborted) setAuthority(a);
      })
      .catch((e) => {
        if (!c.signal.aborted) setAuthorityNote(explain(e));
      });
    return () => c.abort();
  }, [tenantId, tick]);
  function dismiss() {
    setProposing(false);
    setSelected(null);
    setAction("accept");
    retry.current = { key: "", operation: "" };
  }
  const latest = authority?.principals.length
    ? Math.max(...authority.principals.map((p) => Date.parse(p.expires_at)))
    : 0;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    const data: Record<string, string> = {
      reason: String(form.get("reason") ?? ""),
    };
    let path: string, expected_revision: string;
    if (proposing) {
      if (!authority) return;
      const chosen = new Date(String(form.get("expires_at")));
      if (
        Number.isNaN(chosen.getTime()) ||
        chosen.getTime() <= latest ||
        chosen.getTime() > Date.now() + 90 * DAY
      ) {
        setError(
          `Choose an expiry after the current expiry (${when(latest)}) and within 90 days from now.`,
        );
        return;
      }
      data.second_identity_id = String(form.get("second_identity_id") ?? "");
      data.authority_hash = authority.authority_hash ?? "";
      data.expires_at = chosen.toISOString();
      path = `/v1/platform/tenants/${authority.tenant_id}/authority-renewal`;
      expected_revision = authority.tenant_revision;
    } else {
      if (!selected) return;
      path = `${base}/${selected.request_id}/actions/${action}`;
      expected_revision = selected.revision_id;
    }
    setBusy(true);
    try {
      // The operation ID is minted once per distinct payload and kept for the life of the
      // dialog, so a retry of the same change replays the original receipt exactly.
      const key = JSON.stringify([path, expected_revision, data]);
      if (retry.current.key !== key)
        retry.current = { key, operation: crypto.randomUUID() };
      const result = (await request(path, {
        method: "POST",
        body: JSON.stringify({
          operation_id: retry.current.operation,
          expected_revision,
          data,
        }),
      })) as Receipt;
      dismiss();
      await refresh();
      setNotice(
        `${result.operating_name}: authority renewal ${result.state}. Change saved.`,
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const pending = (directory?.items || []).filter((row) =>
    pendingStates.includes(row.state),
  );
  const history = (directory?.items || []).filter(
    (row) => !pendingStates.includes(row.state),
  );
  const canPropose =
    !!authority?.renewable && authority.owner_identity_id === identity;
  return (
    <main className="tenant-console">
      <button className="secondary" disabled={busy} onClick={close}>
        Back to tenant lifecycle
      </button>
      <h1>Authority renewal</h1>
      <p>
        Initial access gives the owner and the second administrator a delegation
        ceiling that ends within 90 days. The owner proposes a renewal that pins
        their exact current authority, the second administrator accepts it, and
        a platform operator independent of both approves it. Approval extends
        only the pinned ceilings, grants and role assignments: nothing revoked
        is restored and no capability is added.
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
          Refresh authority renewals
        </button>
        {tenants?.next_cursor && (
          <button
            className="secondary"
            disabled={busy}
            onClick={async () => {
              try {
                const t = (await request(
                  "/v1/platform/tenants?cursor=" + tenants.next_cursor,
                )) as TenantDirectory;
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
      <section
        className="panel renewal-authority"
        aria-label="Delegated authority"
      >
        <h2>Delegated authority</h2>
        {!tenants ? (
          <p role="status">Loading tenants…</p>
        ) : !tenants.items.length ? (
          <p>
            No managed tenants are available to you. Only a tenant’s owner and
            platform operators can inspect its delegated authority.
          </p>
        ) : (
          <>
            <label>
              Tenant
              <select
                aria-label="Tenant"
                value={tenantId}
                onChange={(e) => {
                  dismiss();
                  setTenantId(e.target.value);
                }}
              >
                {tenants.items.map((t) => (
                  <option key={t.tenant_id} value={t.tenant_id}>
                    {t.operating_name} ({t.state})
                  </option>
                ))}
              </select>
            </label>
            {authorityNote ? (
              <p>Delegated authority is not available: {authorityNote}</p>
            ) : !authority ? (
              <p role="status">Loading delegated authority…</p>
            ) : (
              <>
                <p>
                  Owner: <code>{mask(authority.owner_identity_id)}</code>
                  <br />
                  Second administrator:{" "}
                  <code>{mask(authority.second_identity_id)}</code>
                  <br />
                  Initial access request:{" "}
                  <code>{mask(authority.bootstrap_request_id)}</code>
                </p>
                <p>
                  Earliest ceiling expiry: {when(authority.earliest_expires_at)}
                  .
                </p>
                <p>
                  <strong>
                    {authority.renewable ? "Renewable" : "Not renewable"}
                  </strong>
                  {authority.reason_unavailable
                    ? " — " + unavailable[authority.reason_unavailable]
                    : ". The owner may propose an extension within 90 days."}
                </p>
                {authority.principals.length ? (
                  <Principals
                    principals={authority.principals}
                    owner={authority.owner_identity_id}
                  />
                ) : (
                  <p>No current delegated authority is recorded.</p>
                )}
                {canPropose && (
                  <div className="toolbar">
                    <button
                      className="primary"
                      disabled={busy}
                      onClick={() => {
                        dismiss();
                        setProposing(true);
                        setError("");
                      }}
                    >
                      Propose authority renewal
                    </button>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </section>
      <h2>Renewal reviews</h2>
      {!directory ? (
        <p role="status">Loading authority renewals…</p>
      ) : (
        <>
          {!directory.items.length ? (
            <p>No authority renewals are available.</p>
          ) : (
            !pending.length && <p>No renewal is pending review.</p>
          )}
          <div className="tenant-cards">
            {pending.map((row) => {
              const buttons: [ReviewAction, boolean][] = [
                [
                  "accept",
                  row.state === "Requested" &&
                    row.second_identity_id === identity,
                ],
                ["approve", row.state === "Accepted" && directory.operator],
                ["reject", directory.operator],
                ["cancel", row.owner_identity_id === identity],
              ];
              return (
                <article
                  className="panel"
                  key={row.request_id}
                  aria-label={row.operating_name + " authority renewal"}
                >
                  <h2>{row.operating_name}</h2>
                  <p>
                    <strong>{row.state}</strong> · {states[row.state]}.
                  </p>
                  <p>
                    Owner: <code>{mask(row.owner_identity_id)}</code>
                    <br />
                    Second administrator:{" "}
                    <code>{mask(row.second_identity_id)}</code>
                  </p>
                  <p>
                    Expiry: {when(row.previous_expires_at)} →{" "}
                    {when(row.expires_at)}. Review deadline:{" "}
                    {when(row.review_expires_at)}.
                  </p>
                  {row.accepted_at && (
                    <p>
                      Accepted by the second administrator:{" "}
                      {when(row.accepted_at)}.
                    </p>
                  )}
                  <p>Proposal reason: {row.reason}</p>
                  <Principals
                    principals={row.manifest.principals}
                    owner={row.owner_identity_id}
                  />
                  <div className="toolbar">
                    {buttons
                      .filter(([, show]) => show)
                      .map(([key]) => (
                        <button
                          key={key}
                          className="secondary"
                          disabled={busy}
                          onClick={() => {
                            dismiss();
                            setSelected(row);
                            setAction(key);
                            setError("");
                          }}
                        >
                          {labels[key]}
                        </button>
                      ))}
                  </div>
                </article>
              );
            })}
          </div>
          {!!history.length && (
            <section
              className="panel renewal-history"
              aria-label="Authority renewal history"
            >
              <h2>Renewal history</h2>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Tenant</th>
                      <th>Outcome</th>
                      <th>Expiry</th>
                      <th>Decision</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((row) => (
                      <tr key={row.request_id}>
                        <td data-label="Tenant">{row.operating_name}</td>
                        <td data-label="Outcome">
                          <strong>{row.state}</strong>
                        </td>
                        <td data-label="Expiry">
                          {when(row.previous_expires_at)} →{" "}
                          {when(row.expires_at)}
                        </td>
                        <td data-label="Decision">
                          {row.state === "Applied"
                            ? `Approved by ${mask(row.approved_by)} on ${when(row.applied_at)}`
                            : row.accepted_at
                              ? `Accepted ${when(row.accepted_at)}, then ${row.state.toLowerCase()}`
                              : states[row.state]}
                        </td>
                        <td data-label="Reason">{row.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
          {directory.next_cursor && (
            <button
              className="secondary"
              disabled={busy}
              onClick={async () => {
                try {
                  const d = (await request(
                    base + "?cursor=" + directory.next_cursor,
                  )) as Directory;
                  setDirectory({
                    ...d,
                    items: [...directory.items, ...d.items],
                  });
                } catch (e) {
                  setError(explain(e));
                }
              }}
            >
              Load more authority renewals
            </button>
          )}
        </>
      )}
      {(proposing || selected) && (
        <section className="panel" aria-label="Authority renewal change">
          <h2>
            {proposing
              ? "Propose authority renewal"
              : labels[action] + ": " + (selected?.operating_name ?? "")}
          </h2>
          {proposing ? (
            <p>
              The proposal pins the exact current authority of both
              administrators shown above. The second administrator must accept
              it, then a platform operator independent of both must approve it
              within seven days and before the current expiry. Nothing changes
              until approval.
            </p>
          ) : (
            selected && (
              <>
                <p>{guidance[action]}</p>
                <p>
                  Expiry: {when(selected.previous_expires_at)} →{" "}
                  {when(selected.expires_at)}. Review deadline:{" "}
                  {when(selected.review_expires_at)}.
                </p>
                <Principals
                  principals={selected.manifest.principals}
                  owner={selected.owner_identity_id}
                />
              </>
            )
          )}
          <form onSubmit={submit}>
            {proposing && (
              <>
                <label>
                  Second administrator identity UUID
                  <input
                    name="second_identity_id"
                    required
                    pattern="[0-9a-fA-F-]{36}"
                    defaultValue={authority?.second_identity_id ?? ""}
                    readOnly={!!authority?.second_identity_id}
                  />
                </label>
                <label>
                  New expiry
                  <input name="expires_at" type="datetime-local" required />
                </label>
                <p>
                  Choose an expiry after {when(latest)} and no later than{" "}
                  {when(Date.now() + 90 * DAY)}. Both administrators’ ceilings,
                  grants and role assignments will end at the new expiry; the
                  second administrator’s membership follows it and is never
                  shortened.
                </p>
              </>
            )}
            <label>
              Reason
              <textarea name="reason" required maxLength={1000} />
            </label>
            <div className="toolbar">
              <button type="submit" className="primary" disabled={busy}>
                {busy
                  ? "Saving…"
                  : confirmations[proposing ? "propose" : action]}
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={dismiss}
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
