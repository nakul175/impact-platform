import { useEffect, useRef, useState, type FormEvent } from "react";
import type { Principal, RenewalState } from "./AuthorityRenewal";

type Profile = {
  version: string;
  roles: Record<string, string[]>;
  purpose_bound?: string[];
};
type CurrentAuthority = { version: string; principals: Principal[] };
type Preview = {
  tenant_id: string;
  tenant_revision: string;
  owner_identity_id: string;
  second_identity_id: string | null;
  authority_hash: string | null;
  profile_hash: string;
  target_manifest: Profile;
  current_manifest: CurrentAuthority | null;
  new_capabilities: string[];
  upgradable: boolean;
  reason_unavailable: string | null;
};
type Upgrade = {
  request_id: string;
  tenant_id: string;
  revision_id: string;
  operating_name: string;
  owner_identity_id: string;
  second_identity_id: string;
  state: RenewalState;
  current_manifest: CurrentAuthority;
  target_manifest: Profile;
  new_capabilities: string[];
  review_expires_at: string;
  accepted_at: string | null;
  approved_by: string | null;
  applied_at: string | null;
  reason: string;
};
type Directory = {
  operator: boolean;
  items: Upgrade[];
  next_cursor: string | null;
};
type Tenant = {
  tenant_id: string;
  operating_name: string;
  state: string;
  owner_identity_id: string;
};
type TenantDirectory = { items: Tenant[]; next_cursor: string | null };
type Action = "accept" | "approve" | "reject" | "cancel";
type Props = {
  request: (path: string, options?: RequestInit) => Promise<unknown>;
  explain: (error: unknown) => string;
  identity: string;
  close: () => void;
};
const base = "/v1/platform/access-upgrades";
const labels: Record<Action, string> = {
  accept: "Accept access proposal",
  approve: "Approve access extension",
  reject: "Reject access proposal",
  cancel: "Withdraw access proposal",
};
const reasons: Record<string, string> = {
  ACCESS_PROFILE_NOT_REGISTERED:
    "The deployed access profile needs platform registration before it can be proposed.",
  AUTHORITY_UNAVAILABLE:
    "Current delegated authority is unavailable. Restore valid access before proposing an extension.",
  SECOND_ADMIN_UNAVAILABLE:
    "Exactly one second administrator with current delegated authority is required.",
  TENANT_NOT_ACTIVE: "The organisation must be Active.",
  TENANT_NOT_READY:
    "Restore the organisation’s deployment, owner and recovery readiness checks.",
  RENEWAL_PENDING: "Complete or withdraw the pending authority renewal first.",
  ACCESS_UPGRADE_PENDING: "An access extension is already under review.",
  ACCESS_PROFILE_ALREADY_HELD:
    "The organisation already holds the available access profile.",
  ACCESS_PROFILE_INCOMPATIBLE:
    "The current authority cannot be safely extended to this profile. A platform operator must review the configuration.",
};
const when = (value: string | null) =>
  value ? new Date(value).toLocaleString() : "—";
const short = (value: string) => value.slice(0, 8) + "…" + value.slice(-4);
function AuthorityDetails({
  current,
  target,
  added,
}: {
  current: CurrentAuthority | null;
  target: Profile;
  added: string[];
}) {
  return (
    <>
      <p>
        Target access profile: <strong>{target.version}</strong>. {added.length}{" "}
        additional capabilities are proposed.
      </p>
      <details>
        <summary>Review the additional capabilities</summary>
        {added.length ? (
          <ul>
            {added.map((cap) => (
              <li key={cap}>
                <code>{cap}</code>
              </li>
            ))}
          </ul>
        ) : (
          <p>No additional capability is available.</p>
        )}
      </details>
      {current?.principals.map((p) => (
        <p key={p.principal_id}>
          Administrator <code>{short(p.identity_id)}</code>: current access ends{" "}
          {when(p.expires_at)}.
        </p>
      ))}
      <details>
        <summary>Review the target role templates</summary>
        {Object.entries(target.roles).map(([name, caps]) => (
          <section key={name}>
            <h4>{name.replaceAll("_", " ")}</h4>
            <ul>
              {caps.map((cap) => (
                <li key={cap}>
                  <code>{cap}</code>
                </li>
              ))}
            </ul>
          </section>
        ))}
        {!!target.purpose_bound?.length && (
          <p>
            Purpose-bound capabilities require separate, purpose-specific
            grants: {target.purpose_bound.join(", ")}.
          </p>
        )}
      </details>
    </>
  );
}

export function AccessUpgrade({ request, explain, identity, close }: Props) {
  const [directory, setDirectory] = useState<Directory | null>(null);
  const [tenants, setTenants] = useState<TenantDirectory | null>(null);
  const [tenantId, setTenantId] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [tick, setTick] = useState(0);
  const [proposing, setProposing] = useState(false);
  const [selected, setSelected] = useState<Upgrade | null>(null);
  const [action, setAction] = useState<Action>("accept");
  const retry = useRef({ key: "", operation: "" });
  const epoch = useRef(0);
  const directoryEpoch = useRef(0);
  function dismiss() {
    setProposing(false);
    setSelected(null);
    retry.current = { key: "", operation: "" };
  }
  async function load(options?: RequestInit) {
    const [d, t] = await Promise.all([
      request(base, options),
      request("/v1/platform/tenants", options),
    ]);
    return { d: d as Directory, t: t as TenantDirectory };
  }
  function apply({ d, t }: { d: Directory; t: TenantDirectory }) {
    setDirectory(d);
    setTenants(t);
    setTenantId((current) =>
      t.items.some((t) => t.tenant_id === current)
        ? current
        : t.items.find(
            (t) => t.owner_identity_id === identity && t.state === "Active",
          )?.tenant_id ||
          t.items[0]?.tenant_id ||
          "",
    );
  }
  useEffect(() => {
    const controller = new AbortController();
    const current = ++directoryEpoch.current;
    load({ signal: controller.signal })
      .then((result) => {
        if (!controller.signal.aborted && current === directoryEpoch.current)
          apply(result);
      })
      .catch((e) => {
        if (!controller.signal.aborted && current === directoryEpoch.current)
          setError(explain(e));
      });
    return () => {
      controller.abort();
      ++epoch.current;
      ++directoryEpoch.current;
    };
  }, []);
  useEffect(() => {
    setPreview(null);
    dismiss();
    if (!tenantId) return;
    const controller = new AbortController();
    (
      request(`/v1/platform/tenants/${tenantId}/access-upgrade-preview`, {
        signal: controller.signal,
      }) as Promise<Preview>
    )
      .then((result) => {
        if (!controller.signal.aborted) setPreview(result);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      });
    return () => controller.abort();
  }, [tenantId, tick]);
  async function refresh() {
    const current = ++directoryEpoch.current;
    try {
      const result = await load();
      if (current !== directoryEpoch.current) return;
      apply(result);
      dismiss();
      setTick((n) => n + 1);
    } catch (e) {
      if (current === directoryEpoch.current) throw e;
    }
  }
  async function manualRefresh() {
    if (busy) return;
    const current = epoch.current;
    setBusy(true);
    setError("");
    try {
      await refresh();
    } catch (e) {
      if (current === epoch.current) setError(explain(e));
    } finally {
      if (current === epoch.current) setBusy(false);
    }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const reason = String(
      new FormData(event.currentTarget).get("reason") || "",
    );
    const data: Record<string, string> = { reason };
    let path: string, expected_revision: string;
    if (proposing) {
      if (
        !preview?.upgradable ||
        !preview.second_identity_id ||
        !preview.authority_hash
      )
        return;
      Object.assign(data, {
        second_identity_id: preview.second_identity_id,
        authority_hash: preview.authority_hash,
        profile_hash: preview.profile_hash,
      });
      path = `/v1/platform/tenants/${preview.tenant_id}/access-upgrade`;
      expected_revision = preview.tenant_revision;
    } else {
      if (!selected) return;
      path = `/v1/platform/tenants/${selected.tenant_id}/access-upgrades/${selected.request_id}/actions/${action}`;
      expected_revision = selected.revision_id;
    }
    const key = JSON.stringify([path, expected_revision, data]);
    if (retry.current.key !== key)
      retry.current = { key, operation: crypto.randomUUID() };
    const current = epoch.current;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = (await request(path, {
        method: "POST",
        body: JSON.stringify({
          operation_id: retry.current.operation,
          expected_revision,
          data,
        }),
      })) as Upgrade;
      if (current !== epoch.current) return;
      dismiss();
      setNotice(
        `${result.operating_name}: access proposal ${result.state}. Change saved.`,
      );
      await refresh();
    } catch (e) {
      if (current === epoch.current) setError(explain(e));
    } finally {
      if (current === epoch.current) setBusy(false);
    }
  }
  async function moreReviews() {
    if (!directory?.next_cursor || busy) return;
    const current = directoryEpoch.current;
    setBusy(true);
    try {
      const page = (await request(
        base + "?cursor=" + encodeURIComponent(directory.next_cursor),
      )) as Directory;
      if (current !== directoryEpoch.current) return;
      setDirectory((old) => ({
        ...page,
        items: [
          ...(old?.items || []),
          ...page.items.filter(
            (item) =>
              !old?.items.some(
                (previous) => previous.request_id === item.request_id,
              ),
          ),
        ],
      }));
    } catch (e) {
      if (current === directoryEpoch.current) setError(explain(e));
    } finally {
      if (current === directoryEpoch.current) setBusy(false);
    }
  }
  async function moreTenants() {
    if (!tenants?.next_cursor || busy) return;
    const current = directoryEpoch.current;
    setBusy(true);
    try {
      const page = (await request(
        "/v1/platform/tenants?cursor=" +
          encodeURIComponent(tenants.next_cursor),
      )) as TenantDirectory;
      if (current !== directoryEpoch.current) return;
      setTenants((old) => ({
        ...page,
        items: [
          ...(old?.items || []),
          ...page.items.filter(
            (item) =>
              !old?.items.some(
                (previous) => previous.tenant_id === item.tenant_id,
              ),
          ),
        ],
      }));
    } catch (e) {
      if (current === directoryEpoch.current) setError(explain(e));
    } finally {
      if (current === directoryEpoch.current) setBusy(false);
    }
  }
  return (
    <main className="tenant-console">
      <button className="secondary" disabled={busy} onClick={close}>
        Back to tenant lifecycle
      </button>
      <h1>Extend organisation access</h1>
      <p>
        The owner proposes an extension to the current access profile. The named
        second administrator accepts the exact proposal, then an independent
        platform operator approves it. Each decision requires a fresh sign-in
        assurance.
      </p>
      <p>
        Approval makes the reviewed capabilities available through the existing
        delegation model. Access keeps its current expiry; this proposal does
        not renew it.
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
          onClick={() => void manualRefresh()}
        >
          Refresh access proposals
        </button>
      </div>
      <section className="panel" aria-label="Available access extension">
        <h2>Available access extension</h2>
        {tenants?.items.length ? (
          <label>
            Organisation
            <select
              value={tenantId}
              disabled={busy}
              onChange={(e) => setTenantId(e.target.value)}
            >
              {tenants.items.map((t) => (
                <option key={t.tenant_id} value={t.tenant_id}>
                  {t.operating_name} · {t.state}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <p>No organisation is available for you to propose an extension.</p>
        )}
        {tenants?.next_cursor && (
          <button
            className="secondary"
            disabled={busy}
            onClick={() => void moreTenants()}
          >
            Load more organisations
          </button>
        )}
        {tenantId && !preview && (
          <p role="status">Loading the current access profile…</p>
        )}
        {preview && (
          <>
            <p>
              {preview.upgradable
                ? "The owner can propose this access extension."
                : reasons[preview.reason_unavailable || ""] ||
                  "An access extension is unavailable."}
            </p>
            <AuthorityDetails
              current={preview.current_manifest}
              target={preview.target_manifest}
              added={preview.new_capabilities}
            />
            {preview.upgradable && preview.owner_identity_id === identity && (
              <button
                className="primary"
                disabled={busy}
                onClick={() => {
                  dismiss();
                  setProposing(true);
                  setError("");
                }}
              >
                Propose access extension
              </button>
            )}
          </>
        )}
      </section>
      <h2>Access reviews</h2>
      {!directory ? (
        <p role="status">Loading access reviews…</p>
      ) : !directory.items.length ? (
        <p>No access proposals are available.</p>
      ) : (
        <div className="tenant-cards">
          {directory.items.map((row) => {
            const pending = ["Requested", "Accepted"].includes(row.state);
            const buttons: [Action, boolean][] = [
              [
                "accept",
                row.state === "Requested" &&
                  row.second_identity_id === identity,
              ],
              ["approve", row.state === "Accepted" && directory.operator],
              ["reject", pending && directory.operator],
              ["cancel", pending && row.owner_identity_id === identity],
            ];
            return (
              <article
                className="panel"
                key={row.request_id}
                aria-label={row.operating_name + " access proposal"}
              >
                <h3>{row.operating_name}</h3>
                <p>
                  <strong>{row.state}</strong>
                  {row.state === "Requested"
                    ? " · awaiting the second administrator"
                    : row.state === "Accepted"
                      ? " · awaiting independent operator approval"
                      : ""}
                  .
                </p>
                <p>
                  Owner: <code>{short(row.owner_identity_id)}</code>. Second
                  administrator: <code>{short(row.second_identity_id)}</code>.
                  Review deadline: {when(row.review_expires_at)}.
                </p>
                <p>Proposal reason: {row.reason}</p>
                {row.applied_at && (
                  <p>
                    Applied {when(row.applied_at)} by operator{" "}
                    <code>{short(row.approved_by || "")}</code>.
                  </p>
                )}
                <AuthorityDetails
                  current={row.current_manifest}
                  target={row.target_manifest}
                  added={row.new_capabilities}
                />
                <div className="toolbar">
                  {buttons
                    .filter(([, show]) => show)
                    .map(([value]) => (
                      <button
                        className="secondary"
                        key={value}
                        disabled={busy}
                        onClick={() => {
                          dismiss();
                          setSelected(row);
                          setAction(value);
                          setError("");
                        }}
                      >
                        {labels[value]}
                      </button>
                    ))}
                </div>
              </article>
            );
          })}
        </div>
      )}
      {directory?.next_cursor && (
        <button
          className="secondary"
          disabled={busy}
          onClick={() => void moreReviews()}
        >
          Load more access reviews
        </button>
      )}
      {(proposing || selected) && (
        <section className="panel" aria-label="Access extension decision">
          <h2>{proposing ? "Propose access extension" : labels[action]}</h2>
          <p>
            Organisation:{" "}
            {selected?.operating_name ||
              tenants?.items.find((tenant) => tenant.tenant_id === tenantId)
                ?.operating_name ||
              "Unavailable"}
            .
            {selected && (
              <>
                {" "}
                Proposal: <code>{short(selected.request_id)}</code>.
              </>
            )}
          </p>
          <p>
            {proposing
              ? "The proposal pins the current authority, administrators and target profile shown above. Both reviewers must decide before the review deadline. Capabilities become available only after approval."
              : action === "approve"
                ? "Confirm that you reviewed the exact capability extension and are a different person from both administrators. Approval rechecks their current authority and the target profile."
                : action === "accept"
                  ? "Confirm that you are the named second administrator and accept the exact capability extension. An independent operator must still approve it."
                  : "Record this decision for the proposal."}
          </p>
          {selected && (
            <AuthorityDetails
              current={selected.current_manifest}
              target={selected.target_manifest}
              added={selected.new_capabilities}
            />
          )}
          <form
            key={
              proposing
                ? `proposal:${tenantId}`
                : `${selected?.request_id}:${action}`
            }
            onSubmit={submit}
          >
            <label>
              Reason
              <textarea name="reason" required maxLength={1000} />
            </label>
            <div className="dialog-actions">
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Saving…" : "Confirm decision"}
              </button>
              <button
                className="secondary"
                type="button"
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
