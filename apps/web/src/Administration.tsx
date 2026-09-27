import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";

type Requester = (path: string, options?: RequestInit) => Promise<any>;
type Item = {
  object_id: string;
  revision_id: string;
  state: string;
  [key: string]: any;
};
type Page = { items: Item[]; next_cursor: string | null };
type Props = {
  base: string;
  capabilities: string[];
  request: Requester;
  explain: (e: unknown) => string;
  Dialog: (p: {
    title: string;
    close: () => void;
    children: ReactNode;
  }) => ReactNode;
};
const sections = [
  ["membership-directory", "Members", "memberships.read"],
  ["member-invitations", "Invitations", "member-invitations.read"],
  ["access-requests", "Access requests", "access-requests.read"],
  ["access-scopes", "Scopes", "access-scopes.read"],
  ["role-templates", "Role templates", "role-templates.read"],
];
const inDays = (days: number) =>
  new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);

export function AdministrationPanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const [route, setRoute] = useState("membership-directory"),
    [page, setPage] = useState<Page | null>(null),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0),
    [dialog, setDialog] = useState<{ mode: string; item?: Item } | null>(null),
    [link, setLink] = useState("");
  const currentView = useRef("");
  currentView.current = `${base}:${route}:${tick}`;
  const allowed = (cap: string) => capabilities.includes(cap);
  useEffect(() => {
    const controller = new AbortController();
    setPage(null);
    setError("");
    setBusy(true);
    request(base + route + "?limit=50", { signal: controller.signal })
      .then((result) => {
        if (!controller.signal.aborted) setPage(result);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      })
      .finally(() => {
        if (!controller.signal.aborted) setBusy(false);
      });
    return () => controller.abort();
  }, [base, route, tick]);
  async function more() {
    if (!page?.next_cursor) return;
    const view = currentView.current;
    setBusy(true);
    try {
      const next = await request(
        base +
          route +
          "?limit=50&cursor=" +
          encodeURIComponent(page.next_cursor),
      );
      if (currentView.current === view)
        setPage({ ...next, items: [...page.items, ...next.items] });
    } catch (e) {
      if (currentView.current === view) setError(explain(e));
    } finally {
      if (currentView.current === view) setBusy(false);
    }
  }
  function completed(result: any) {
    setDialog(null);
    setTick((x) => x + 1);
    if (result.invitation_url) {
      setLink(result.invitation_url);
      setMessage(
        "Invitation created. No email has been sent; deliver the link through an approved channel.",
      );
    } else setMessage("Saved. Access and policy versions have been updated.");
  }
  const name = (r: Item) =>
    r.display_name ||
    r.email_mask ||
    r.title ||
    r.name ||
    r.role_name + " access request";
  return (
    <section className="administration">
      <div
        className="admin-tabs"
        role="tablist"
        aria-label="Access administration"
      >
        {sections
          .filter((s) => allowed(s[2]))
          .map(([key, title]) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={route === key}
              className={route === key ? "selected" : ""}
              onClick={() => {
                if (route !== key) {
                  setPage(null);
                  setBusy(true);
                }
                setRoute(key);
                setMessage("");
                setLink("");
              }}
            >
              {title}
            </button>
          ))}
      </div>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {message && (
        <div className="success" role="status">
          {message}
        </div>
      )}
      {link && (
        <div className="panel invite-link">
          <h2>Invitation link</h2>
          <p>
            This link expires and can be accepted once by the verified intended
            account. It does not create a login account.
          </p>
          <label>
            Copy invitation link
            <textarea
              readOnly
              aria-label="Copy invitation link"
              value={link}
              onFocus={(e) => e.target.select()}
            />
          </label>
          <button className="secondary" onClick={() => setLink("")}>
            Hide link
          </button>
        </div>
      )}
      <div className="panel">
        <div className="panel-toolbar">
          <div>
            <h2>{sections.find((s) => s[0] === route)?.[1]}</h2>
            <small>
              {page?.items.length || 0} records loaded · current workspace only
            </small>
          </div>
          <div className="toolbar-actions">
            {route === "member-invitations" && allowed("member.invite") && (
              <button
                className="primary"
                onClick={() => setDialog({ mode: "invite" })}
              >
                Invite member
              </button>
            )}
            {route === "access-scopes" && allowed("access-scopes.create") && (
              <button
                className="primary"
                onClick={() => setDialog({ mode: "scope" })}
              >
                Create scope
              </button>
            )}
            <button
              className="secondary"
              onClick={() => setTick((x) => x + 1)}
              disabled={busy}
            >
              Refresh access
            </button>
          </div>
        </div>
        <p className="admin-scroll-hint">
          On narrow screens, scroll the table horizontally to reach all actions.
        </p>
        <div
          className="table-wrap"
          role="region"
          aria-label="Access records, horizontally scrollable"
          tabIndex={0}
        >
          <table>
            <thead>
              <tr>
                <th>
                  {route === "membership-directory" ? "Member" : "Record"}
                </th>
                <th>Status / scope</th>
                <th>Access</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {page?.items.map((item) => (
                <tr key={item.object_id}>
                  <td>
                    <strong>{name(item)}</strong>
                    <small className="record-id">
                      {route === "membership-directory"
                        ? item.email_mask
                        : item.object_id.slice(0, 8)}
                    </small>
                  </td>
                  <td>
                    <span
                      className={"badge " + (item.state || "").toLowerCase()}
                    >
                      {item.state || item.scope_type}
                    </span>
                    {item.owner && (
                      <span className="badge">Protected owner</span>
                    )}
                  </td>
                  <td>
                    {item.roles?.join(", ") ||
                      item.role_name ||
                      `${item.capabilities?.length ?? item.object_ids?.length ?? 0} ${item.capabilities ? "capabilities" : "objects"}`}
                    {item.expires_at && (
                      <small className="record-id">
                        Until {new Date(item.expires_at).toLocaleDateString()}
                      </small>
                    )}
                  </td>
                  <td>
                    <button
                      className="secondary"
                      onClick={() => setDialog({ mode: "inspect", item })}
                    >
                      View{" "}
                      {route === "membership-directory" ? "member" : "details"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {busy && !page ? (
          <div className="empty" role="status">
            Loading access records…
          </div>
        ) : !page?.items.length ? (
          <div className="empty">No records in this section.</div>
        ) : null}
        <div className="panel-footer">
          <span>Role changes require an independent administrator.</span>
          {page?.next_cursor && (
            <button className="secondary" disabled={busy} onClick={more}>
              Load more access records
            </button>
          )}
        </div>
      </div>
      {dialog && (
        <Dialog
          title={
            dialog.mode === "inspect"
              ? name(dialog.item!)
              : {
                  invite: "Invite a member",
                  scope: "Create an object scope",
                  request: "Request a role",
                  suspend: "Suspend membership",
                  reactivate: "Reactivate membership",
                  revoke: "Revoke membership",
                  resend: "Reissue invitation",
                  cancel: "Revoke invitation",
                  approve: "Approve access request",
                  reject: "Reject access request",
                  revokeGrant: "Revoke a capability",
                }[dialog.mode] || "Access change"
          }
          close={() => setDialog(null)}
        >
          {dialog.mode === "inspect" ? (
            <>
              <dl className="fields">
                {Object.entries(dialog.item!)
                  .filter(([k]) => !["grants", "capabilities"].includes(k))
                  .map(([k, v]) => (
                    <div key={k} className="admin-detail-row">
                      <dt>{k.replaceAll("_", " ")}</dt>
                      <dd>
                        {Array.isArray(v)
                          ? v.join(", ")
                          : v === null
                            ? "—"
                            : String(v)}
                      </dd>
                    </div>
                  ))}
              </dl>
              {dialog.item?.capabilities && (
                <div className="capability-list">
                  {dialog.item.capabilities.map((c: string) => (
                    <code key={c}>{c}</code>
                  ))}
                </div>
              )}
              {dialog.item?.owner && (
                <p className="footnote">
                  The designated owner cannot be suspended, revoked, or
                  reassigned through ordinary administration. Custody transfer
                  requires a separate governed workflow.
                </p>
              )}
              <div className="dialog-actions">
                {route === "membership-directory" && !dialog.item?.owner && (
                  <>
                    {dialog.item?.state === "Active" &&
                      allowed("membership.suspend") && (
                        <button
                          className="secondary"
                          onClick={() =>
                            setDialog({ ...dialog, mode: "suspend" })
                          }
                        >
                          Suspend member
                        </button>
                      )}
                    {dialog.item?.state === "Suspended" &&
                      allowed("membership.reactivate") && (
                        <button
                          className="secondary"
                          onClick={() =>
                            setDialog({ ...dialog, mode: "reactivate" })
                          }
                        >
                          Reactivate member
                        </button>
                      )}
                    {["Active", "Suspended"].includes(dialog.item!.state) &&
                      allowed("membership.revoke") && (
                        <button
                          className="danger"
                          onClick={() =>
                            setDialog({ ...dialog, mode: "revoke" })
                          }
                        >
                          Revoke member
                        </button>
                      )}
                    {dialog.item?.state === "Active" &&
                      allowed("grant.request") && (
                        <button
                          className="primary"
                          onClick={() =>
                            setDialog({ ...dialog, mode: "request" })
                          }
                        >
                          Request role change
                        </button>
                      )}
                  </>
                )}
                {route === "member-invitations" &&
                  ["Invited", "Expired"].includes(dialog.item!.state) &&
                  allowed("member.invite") && (
                    <>
                      <button
                        className="secondary"
                        onClick={() => setDialog({ ...dialog, mode: "resend" })}
                      >
                        Reissue link
                      </button>
                      <button
                        className="danger"
                        onClick={() => setDialog({ ...dialog, mode: "cancel" })}
                      >
                        Revoke invitation
                      </button>
                    </>
                  )}
                {route === "access-requests" &&
                  dialog.item?.state === "Requested" &&
                  allowed("grant.approve") && (
                    <>
                      <button
                        className="secondary"
                        onClick={() => setDialog({ ...dialog, mode: "reject" })}
                      >
                        Reject request
                      </button>
                      <button
                        className="primary"
                        onClick={() =>
                          setDialog({ ...dialog, mode: "approve" })
                        }
                      >
                        Approve request
                      </button>
                    </>
                  )}
              </div>
              {dialog.item?.grants?.length > 0 && (
                <section className="grant-list">
                  <h3>Current grants</h3>
                  <p className="footnote">
                    A role label is explanatory. These exact grants determine
                    authority.
                  </p>
                  {dialog.item!.grants.map((grant: any) => (
                    <div key={grant.object_id}>
                      <span>
                        <code>{grant.capability}</code>
                        <small>Scope {grant.scope_id.slice(0, 8)}</small>
                      </span>
                      {allowed("grant.revoke") && !dialog.item?.owner && (
                        <button
                          className="text"
                          onClick={() =>
                            setDialog({ mode: "revokeGrant", item: grant })
                          }
                        >
                          Revoke grant
                        </button>
                      )}
                    </div>
                  ))}
                </section>
              )}
            </>
          ) : (
            <AdminForm
              key={dialog.mode + (dialog.item?.object_id || "")}
              mode={dialog.mode}
              item={dialog.item}
              base={base}
              request={request}
              explain={explain}
              completed={completed}
            />
          )}
        </Dialog>
      )}
    </section>
  );
}

function AdminForm({
  mode,
  item,
  base,
  request,
  explain,
  completed,
}: {
  mode: string;
  item?: Item;
  base: string;
  request: Requester;
  explain: (e: unknown) => string;
  completed: (r: any) => void;
}) {
  const [roles, setRoles] = useState<Item[]>([]),
    [scopes, setScopes] = useState<Item[]>([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const operation = useRef(crypto.randomUUID()),
    invitationExpiry = useRef(
      new Date(Date.now() + 6 * 86400000).toISOString(),
    );
  useEffect(() => {
    if (!["invite", "request"].includes(mode)) return;
    const controller = new AbortController();
    Promise.all(
      ["role-templates", "access-scopes"].map((r) =>
        request(base + r + "?limit=100", { signal: controller.signal }),
      ),
    )
      .then(([r, s]) => {
        setRoles(r.items);
        setScopes(s.items);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      });
    return () => controller.abort();
  }, [mode]);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(e.currentTarget),
      get = (k: string) => String(form.get(k) || "");
    let target = "",
      data: any = { reason: get("reason") };
    let expected = item?.revision_id;
    if (mode === "invite") {
      target = "member-invitations";
      data = {
        ...data,
        email: get("email"),
        role_template_id: get("role"),
        scope_ids: [get("scope")],
        external: true,
        expires_at: invitationExpiry.current,
        membership_expires_at: new Date(
          get("expires") + "T23:59:59Z",
        ).toISOString(),
      };
    } else if (mode === "scope") {
      target = "access-scopes";
      data = {
        ...data,
        title: get("title"),
        object_ids: get("objects")
          .split(/[\s,]+/)
          .filter(Boolean),
      };
    } else if (mode === "request") {
      target = "access-requests";
      expected = undefined;
      data = {
        ...data,
        membership_id: item!.object_id,
        expected_membership_revision: item!.revision_id,
        role_template_id: get("role"),
        scope_ids: [get("scope")],
        expires_at: new Date(get("expires") + "T23:59:59Z").toISOString(),
      };
    } else if (["suspend", "reactivate", "revoke"].includes(mode))
      target = "memberships/" + item!.object_id + "/actions/" + mode;
    else if (["resend", "cancel"].includes(mode))
      target =
        "member-invitations/" +
        item!.object_id +
        "/actions/" +
        (mode === "cancel" ? "revoke" : "resend");
    else if (mode === "revokeGrant")
      target = "grants/" + item!.object_id + "/actions/revoke";
    else target = "access-requests/" + item!.object_id + "/actions/" + mode;
    try {
      const response = await request(base + target, {
        method: "POST",
        body: JSON.stringify({
          operation_id: operation.current,
          ...(expected ? { expected_revision: expected } : {}),
          data,
        }),
      });
      completed(response);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {mode === "invite" && (
        <>
          <p className="muted">
            Invite an externally managed, verified account. Membership lasts at
            most 90 days. Invitation delivery is manual in this build.
          </p>
          <label>
            Verified account email
            <input
              name="email"
              type="email"
              autoComplete="off"
              maxLength={254}
              required
              placeholder="colleague@example.org"
            />
          </label>
        </>
      )}
      {["invite", "request"].includes(mode) && (
        <>
          <label>
            Role template
            <select
              name="role"
              aria-label="Role template"
              required
              defaultValue=""
            >
              <option value="" disabled>
                Select a role
              </option>
              {roles
                .filter((r) => mode !== "invite" || !r.administrative)
                .map((r) => (
                  <option key={r.object_id} value={r.object_id}>
                    {r.name}
                  </option>
                ))}
            </select>
          </label>
          <label>
            Access scope
            <select
              name="scope"
              aria-label="Access scope"
              required
              defaultValue=""
            >
              <option value="" disabled>
                Select the permitted scope
              </option>
              {scopes.map((s) => (
                <option key={s.object_id} value={s.object_id}>
                  {s.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Access expires (UTC)
            <input
              type="date"
              name="expires"
              required
              min={inDays(7)}
              max={inDays(89)}
              defaultValue={inDays(30)}
            />
          </label>
          <p className="footnote">
            The issuer's delegation ceiling and membership expiry also apply.
            The server rejects grants outside those bounds.
          </p>
        </>
      )}
      {mode === "request" && (
        <p className="footnote">
          This adds a time-bounded role assignment; it does not remove existing
          grants. A different eligible administrator must approve it. The target
          member cannot approve their own access.
        </p>
      )}
      {mode === "scope" && (
        <>
          <label>
            Scope name
            <input name="title" maxLength={120} required />
          </label>
          <label>
            Object identifiers
            <textarea
              name="objects"
              required
              placeholder="UUIDs separated by commas or new lines"
            />
          </label>
          <p className="footnote">
            Scopes contain exact existing records in this workspace. They do not
            automatically include related records or future objects.
          </p>
        </>
      )}
      {["suspend", "revoke", "reactivate", "revokeGrant"].includes(mode) && (
        <div className="admin-warning">
          {mode === "reactivate"
            ? "Reactivation requires a fresh sign-in. It does not resume paused jobs or schedules."
            : mode === "revoke"
              ? "Revocation permanently closes this membership and revokes its grants. Pending invitations and queued work are stopped; historical attribution is retained."
              : mode === "suspend"
                ? "Suspension stops new access immediately. A later reactivation requires a fresh sign-in."
                : "This removes the exact capability grant. Other active grants can still permit the same capability."}
        </div>
      )}
      {mode === "approve" && (
        <p className="footnote">
          Approval applies the exact requested role, scope and expiry. Both your
          authority and the requester's authority are checked again.
        </p>
      )}
      <label>
        Reason
        <textarea
          name="reason"
          required
          maxLength={2000}
          placeholder="Record the reason for this access change"
        />
      </label>
      <div className="dialog-actions">
        <button
          className={
            ["revoke", "cancel", "revokeGrant"].includes(mode)
              ? "danger"
              : "primary"
          }
          disabled={busy}
        >
          {busy
            ? "Saving…"
            : {
                invite: "Create invitation",
                scope: "Create scope",
                request: "Submit access request",
                suspend: "Confirm suspension",
                reactivate: "Confirm reactivation",
                revoke: "Confirm revocation",
                resend: "Reissue invitation",
                cancel: "Confirm invitation revocation",
                approve: "Confirm approval",
                reject: "Confirm rejection",
                revokeGrant: "Confirm grant revocation",
              }[mode]}
        </button>
      </div>
    </form>
  );
}

export function readInvitation() {
  try {
    if (!location.hash.startsWith("#invite=")) return null;
    const value = JSON.parse(decodeURIComponent(location.hash.slice(8)));
    if (
      typeof value.tenant_id === "string" &&
      typeof value.token === "string" &&
      value.token.length <= 512
    )
      return value;
    return null;
  } catch {
    return null;
  }
}
export function JoinInvitation({
  invitation,
  request,
  explain,
  complete,
  logout,
}: {
  invitation: { tenant_id: string; token: string };
  request: Requester;
  explain: (e: unknown) => string;
  complete: () => Promise<void>;
  logout: () => void;
}) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const operation = useRef(crypto.randomUUID());
  async function accept() {
    setBusy(true);
    setError("");
    try {
      await request(
        "/v1/tenants/" +
          encodeURIComponent(invitation.tenant_id) +
          "/invitation-acceptances",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: operation.current,
            data: { invitation_token: invitation.token },
          }),
        },
      );
      await complete();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="join-page">
      <section className="panel">
        <span className="eyebrow">WORKSPACE INVITATION</span>
        <h1>Join the workspace</h1>
        <p>
          Acceptance is bound to your verified identity and the exact approved
          role, scope and expiry. A forwarded link cannot grant access to
          another account.
        </p>
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        <div className="dialog-actions">
          <button className="secondary" onClick={logout}>
            Use another account
          </button>
          <button className="primary" disabled={busy} onClick={accept}>
            {busy ? "Accepting…" : "Accept invitation"}
          </button>
        </div>
      </section>
    </main>
  );
}
