import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";

type Item = {
  object_id: string;
  revision_id: string;
  state: string;
  [key: string]: any;
};
type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  Dialog: (p: {
    title: string;
    close: () => void;
    children: ReactNode;
  }) => ReactNode;
};
const sections = [
  ["role-templates", "Custom roles", "roles.manage"],
  ["access-groups", "Groups", "groups.read"],
  ["group-change-requests", "Group reviews", "groups.read"],
  ["organisation-units", "Organisation", "organisation-units.read"],
  ["renewal-requests", "Renewals", "memberships.read"],
  ["ownership-transfers", "Ownership", "memberships.read"],
];
const label = (r: Item) =>
  r.name ||
  r.display_name ||
  r.role_names?.join(", ") ||
  r.membership_id?.slice(0, 8) ||
  r.object_id.slice(0, 8);
const inDays = (days: number) =>
  new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);

export function WorkspaceSettings(props: Props) {
  const { base, capabilities, request, explain, Dialog } = props;
  const available = sections.filter((s) => capabilities.includes(s[2]));
  const [route, setRoute] = useState(available[0]?.[0] || ""),
    [page, setPage] = useState<any>(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0),
    [dialog, setDialog] = useState<{
      action: string | null;
      item?: Item;
    } | null>(null);
  const view = useRef("");
  view.current = base + route + tick;
  useEffect(() => {
    const permitted = sections.filter((s) => capabilities.includes(s[2]));
    setRoute((current) =>
      permitted.some((s) => s[0] === current)
        ? current
        : permitted[0]?.[0] || "",
    );
  }, [capabilities]);
  useEffect(() => {
    const controller = new AbortController();
    setPage(null);
    setError("");
    if (!route) return;
    setBusy(true);
    request(base + route + "?limit=50", { signal: controller.signal })
      .then((r) => {
        if (!controller.signal.aborted) setPage(r);
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      })
      .finally(() => {
        if (!controller.signal.aborted) setBusy(false);
      });
    return () => controller.abort();
  }, [base, route, tick]);
  const allowed = (cap: string) => capabilities.includes(cap);
  const createCap: Record<string, string> = {
    "role-templates": "roles.manage",
    "access-groups": "groups.manage",
    "organisation-units": "organisation-units.manage",
    "renewal-requests": "membership.renew.request",
    "ownership-transfers": "ownership.transfer",
  };
  async function more() {
    const snapshot = view.current;
    setBusy(true);
    try {
      const result = await request(
        base +
          route +
          "?limit=50&cursor=" +
          encodeURIComponent(page.next_cursor),
      );
      if (snapshot === view.current)
        setPage({ ...result, items: [...page.items, ...result.items] });
    } catch (e) {
      if (snapshot === view.current) setError(explain(e));
    } finally {
      if (snapshot === view.current) setBusy(false);
    }
  }
  if (!available.length)
    return <p>Your account has no workspace administration permissions.</p>;
  return (
    <section className="administration">
      <nav className="admin-tabs" aria-label="Workspace administration">
        {available.map(([key, title]) => (
          <button
            key={key}
            className={route === key ? "active" : ""}
            aria-current={route === key ? "page" : undefined}
            onClick={() => {
              setPage(null);
              setRoute(key);
              setNotice("");
            }}
          >
            {title}
          </button>
        ))}
      </nav>
      <div className="toolbar">
        <button className="secondary" onClick={() => setTick((n) => n + 1)}>
          Refresh settings
        </button>
        {allowed(createCap[route]) && (
          <button
            className="primary"
            onClick={() => setDialog({ action: null })}
          >
            {route === "renewal-requests"
              ? "Request renewal"
              : route === "ownership-transfers"
                ? "Nominate owner"
                : "Create " +
                  (route === "role-templates"
                    ? "role"
                    : route === "access-groups"
                      ? "group"
                      : "unit")}
          </button>
        )}
      </div>
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
      {route === "role-templates" && (
        <p className="muted">
          Roles define available capabilities. Assignments require a separate
          access review. Revising or retiring a role leaves existing assignments
          at their approved version.
        </p>
      )}
      {route === "organisation-units" && (
        <p className="muted">
          Codes are permanent. Moves take effect immediately and retain revision
          history. Existing exact-object scopes and programme assignments remain
          unchanged.
        </p>
      )}
      {route === "ownership-transfers" && (
        <p className="muted">
          The current owner nominates an existing eligible administrator.
          Acceptance transfers custody. Both people retain their separately
          approved access until it is explicitly reviewed.
        </p>
      )}
      {busy && !page ? (
        <p role="status">Loading settings…</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Record</th>
                <th>State</th>
                <th>Details</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {page?.items.map((row: Item) => (
                <tr key={row.object_id}>
                  <td>
                    <strong>{label(row)}</strong>
                    <small className="muted">{row.object_id}</small>
                  </td>
                  <td>{row.state}</td>
                  <td>
                    {route === "role-templates"
                      ? row.capabilities.join(", ")
                      : route === "access-groups"
                        ? `${row.membership_ids.length} members · ${row.bindings.length} role bindings`
                        : route === "organisation-units"
                          ? `${row.code} · ${row.parent_id ? "Parent " + row.parent_id.slice(0, 8) : "Root unit"}`
                          : row.reason}
                  </td>
                  <td>
                    <div className="row-actions">
                      {route === "role-templates" &&
                        ![
                          "AUTHOR",
                          "REVIEWER",
                          "PROGRAMME_MANAGER",
                          "ANALYST",
                          "EXTERNAL",
                          "TENANT_ADMIN",
                        ].includes(row.name) &&
                        allowed("roles.manage") && (
                          <>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "revise", item: row })
                              }
                            >
                              Revise role
                            </button>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "retire", item: row })
                              }
                            >
                              Retire role
                            </button>
                          </>
                        )}
                      {route === "access-groups" && row.state === "Active" && (
                        <>
                          {allowed("groups.request") && (
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "propose", item: row })
                              }
                            >
                              Propose access
                            </button>
                          )}
                          {allowed("groups.manage") && (
                            <>
                              <button
                                className="text"
                                disabled={!row.membership_ids.length}
                                onClick={() =>
                                  setDialog({
                                    action: "remove-member",
                                    item: row,
                                  })
                                }
                              >
                                Remove member
                              </button>
                              <button
                                className="text"
                                onClick={() =>
                                  setDialog({ action: "retire", item: row })
                                }
                              >
                                Retire group
                              </button>
                            </>
                          )}
                        </>
                      )}
                      {route === "organisation-units" &&
                        allowed("organisation-units.manage") && (
                          <>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "reparent", item: row })
                              }
                            >
                              Move unit
                            </button>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "rename", item: row })
                              }
                            >
                              Rename unit
                            </button>
                          </>
                        )}
                      {["group-change-requests", "renewal-requests"].includes(
                        route,
                      ) &&
                        row.state === "Requested" &&
                        allowed(
                          route === "group-change-requests"
                            ? "groups.approve"
                            : "membership.renew.approve",
                        ) && (
                          <>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "approve", item: row })
                              }
                            >
                              Review approval
                            </button>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "reject", item: row })
                              }
                            >
                              Reject
                            </button>
                          </>
                        )}
                      {route === "ownership-transfers" &&
                        row.state === "Requested" &&
                        allowed("ownership.transfer") && (
                          <>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "accept", item: row })
                              }
                            >
                              Accept ownership
                            </button>
                            <button
                              className="text"
                              onClick={() =>
                                setDialog({ action: "cancel", item: row })
                              }
                            >
                              Cancel nomination
                            </button>
                          </>
                        )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {page && !page.items.length && (
            <p className="empty">No records yet.</p>
          )}
        </div>
      )}
      {page?.next_cursor && (
        <button className="secondary" disabled={busy} onClick={more}>
          Load more settings
        </button>
      )}
      {dialog && (
        <Dialog
          title={
            dialog.action
              ? {
                  propose: "Propose group access",
                  reparent: "Move organisation unit",
                  approve: "Review approval",
                }[dialog.action] ||
                dialog.action[0].toUpperCase() + dialog.action.slice(1)
              : route === "role-templates"
                ? "Create custom role"
                : route === "renewal-requests"
                  ? "Request membership renewal"
                  : route === "ownership-transfers"
                    ? "Nominate workspace owner"
                    : "Create " +
                      (route === "access-groups"
                        ? "group"
                        : "organisation unit")
          }
          close={() => setDialog(null)}
        >
          <WorkspaceForm
            {...props}
            route={route}
            {...dialog}
            done={() => {
              setDialog(null);
              setTick((n) => n + 1);
              setNotice(
                "Saved. The decision and its revision history are recorded.",
              );
            }}
          />
        </Dialog>
      )}
    </section>
  );
}

function WorkspaceForm({
  base,
  request,
  explain,
  route,
  action,
  item,
  done,
}: Props & {
  route: string;
  action: string | null;
  item?: Item;
  done: () => void;
}) {
  const [options, setOptions] = useState<Record<string, Item[]>>({}),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [loading, setLoading] = useState(true);
  const [caps, setCaps] = useState<string[]>(item?.capabilities || []),
    [members, setMembers] = useState<string[]>(item?.membership_ids || []);
  const retry = useRef<{ signature: string; id: string } | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    const routes: string[] = [];
    if (
      (route === "role-templates" && action !== "retire") ||
      action === "propose"
    )
      routes.push("role-templates");
    if (action === "propose")
      routes.push("access-scopes", "membership-directory");
    if (
      action === "remove-member" ||
      (!action && ["renewal-requests", "ownership-transfers"].includes(route))
    )
      routes.push("membership-directory");
    if (route === "organisation-units" && action !== "rename")
      routes.push("organisation-units");
    async function all(path: string) {
      const rows: Item[] = [];
      let cursor: string | null = null;
      do {
        const result = await request(
          base +
            path +
            "?limit=100" +
            (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
          { signal: controller.signal },
        );
        rows.push(...result.items);
        cursor = result.next_cursor;
        if (rows.length > 5000)
          throw Error(
            "Too many choices. Narrow the workspace before continuing.",
          );
      } while (cursor);
      return rows;
    }
    Promise.all(routes.map(async (r) => [r, await all(r)] as const))
      .then((entries) => {
        if (!controller.signal.aborted) setOptions(Object.fromEntries(entries));
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const f = new FormData(e.currentTarget),
      text = (k: string) => String(f.get(k) || "");
    let data: Record<string, any> = { reason: text("reason") },
      target = route,
      verb = action;
    if (route === "role-templates" && action !== "retire")
      data = { ...data, name: text("name"), capabilities: caps };
    if (route === "access-groups" && !action) data.name = text("name");
    if (action === "remove-member") data.membership_id = text("membership_id");
    if (action === "propose") {
      target = "group-change-requests";
      verb = null;
      data = {
        ...data,
        group_id: item!.object_id,
        expected_group_revision: item!.revision_id,
        membership_ids: members,
        bindings: text("role_template_id")
          ? [
              {
                role_template_id: text("role_template_id"),
                scope_ids: [text("scope_id")],
                expires_at: text("expires_at") + "T23:59:59Z",
              },
            ]
          : [],
      };
    }
    if (route === "organisation-units") {
      if (!action) data.code = text("code");
      if (action !== "reparent") data.name = text("name");
      if (action !== "rename") data.parent_id = text("parent_id") || null;
    }
    if (
      !action &&
      ["renewal-requests", "ownership-transfers"].includes(route)
    ) {
      const selected = options["membership-directory"].find(
        (r) => r.object_id === text("membership_id"),
      )!;
      data = {
        ...data,
        membership_id: selected.object_id,
        expected_membership_revision: selected.revision_id,
      };
      if (route === "renewal-requests")
        data.expires_at = text("expires_at") + "T23:59:59Z";
    }
    const payload = {
        ...(verb ? { expected_revision: item!.revision_id } : {}),
        data,
      },
      signature = JSON.stringify(payload);
    if (retry.current?.signature !== signature)
      retry.current = { signature, id: crypto.randomUUID() };
    try {
      await request(
        base + target + (verb ? `/${item!.object_id}/actions/${verb}` : ""),
        {
          method: "POST",
          body: JSON.stringify({ operation_id: retry.current.id, ...payload }),
        },
      );
      done();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  const roleChoices = options["role-templates"] || [],
    memberChoices = (options["membership-directory"] || []).filter((r) =>
      action === "remove-member"
        ? item!.membership_ids.includes(r.object_id)
        : !["Revoked", "Suspended"].includes(r.state),
    );
  const capChoices = [
    ...new Set([
      ...caps,
      ...roleChoices.flatMap((r) => r.capabilities as string[]),
    ]),
  ].sort();
  if (loading) return <p role="status">Loading current choices…</p>;
  return (
    <form onSubmit={submit}>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {item && (
        <p className="muted">
          Current record: {label(item)} · {item.state}
        </p>
      )}
      {((route === "role-templates" && action !== "retire") ||
        (route === "access-groups" && !action) ||
        (route === "organisation-units" && action !== "reparent")) && (
        <label>
          Name
          <input
            name="name"
            required
            maxLength={120}
            defaultValue={item?.name || ""}
          />
        </label>
      )}
      {route === "role-templates" && action !== "retire" && (
        <fieldset>
          <legend>Capabilities</legend>
          <p className="muted">
            Select capabilities from existing role templates. Your current
            delegation authority is checked when saving.
          </p>
          <div className="choice-grid">
            {capChoices.map((cap) => (
              <label key={cap}>
                <input
                  type="checkbox"
                  checked={caps.includes(cap)}
                  onChange={(e) =>
                    setCaps(
                      e.target.checked
                        ? [...caps, cap]
                        : caps.filter((c) => c !== cap),
                    )
                  }
                />
                {cap}
              </label>
            ))}
          </div>
        </fieldset>
      )}
      {route === "organisation-units" && !action && (
        <label>
          Stable code
          <input
            name="code"
            required
            maxLength={64}
            pattern="[A-Z][A-Z0-9_-]*"
            placeholder="REGION_NORTH"
          />
        </label>
      )}
      {route === "organisation-units" && action !== "rename" && (
        <>
          <label>
            Parent unit
            <select
              name="parent_id"
              aria-label="Parent unit"
              defaultValue={item?.parent_id || ""}
            >
              <option value="">Root unit</option>
              {(options["organisation-units"] || [])
                .filter(
                  (r) =>
                    r.object_id !== item?.object_id && r.state === "Active",
                )
                .map((r) => (
                  <option key={r.object_id} value={r.object_id}>
                    {r.code} · {r.name}
                  </option>
                ))}
            </select>
          </label>
          {action === "reparent" && (
            <p>
              This changes the current reporting hierarchy. Descendants move
              with the unit. Historic revisions, explicit grants and programme
              assignments are preserved. Cycles and excessive depth are
              rejected.
            </p>
          )}
        </>
      )}
      {(action === "remove-member" ||
        (!action &&
          ["renewal-requests", "ownership-transfers"].includes(route))) && (
        <label>
          Member
          <select
            name="membership_id"
            aria-label="Member"
            required
            defaultValue=""
          >
            <option value="" disabled>
              Select member
            </option>
            {memberChoices
              .filter((r) => action === "remove-member" || !r.owner)
              .map((r) => (
                <option value={r.object_id} key={r.object_id}>
                  {r.display_name} · {r.state}
                </option>
              ))}
          </select>
        </label>
      )}
      {action === "propose" && (
        <>
          <p>
            This proposal replaces the complete group membership and role
            bindings when an independent administrator approves it. The existing{" "}
            {item?.bindings.length || 0} bindings are replaced by the selection
            below.
          </p>
          <fieldset>
            <legend>Group members</legend>
            <div className="choice-grid">
              {memberChoices.map((r) => (
                <label key={r.object_id}>
                  <input
                    type="checkbox"
                    checked={members.includes(r.object_id)}
                    onChange={(e) =>
                      setMembers(
                        e.target.checked
                          ? [...members, r.object_id]
                          : members.filter((m) => m !== r.object_id),
                      )
                    }
                  />
                  {r.display_name}
                </label>
              ))}
            </div>
          </fieldset>
          <label>
            Role binding
            <select
              name="role_template_id"
              aria-label="Role binding"
              defaultValue=""
            >
              <option value="">No access binding</option>
              {roleChoices.map((r) => (
                <option key={r.object_id} value={r.object_id}>
                  {r.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Scope
            <select name="scope_id" aria-label="Scope" required>
              {(options["access-scopes"] || []).map((r) => (
                <option key={r.object_id} value={r.object_id}>
                  {r.title}
                </option>
              ))}
            </select>
          </label>
        </>
      )}
      {((route === "renewal-requests" && !action) || action === "propose") && (
        <label>
          Access end date (UTC)
          <input
            type="date"
            name="expires_at"
            required
            min={inDays(1)}
            max={inDays(89)}
            defaultValue={inDays(action === "propose" ? 10 : 30)}
          />
        </label>
      )}
      {route === "renewal-requests" && action !== "reject" && (
        <p className="warning">
          Renewal removes existing direct grants and group access, and requires
          a new sign-in. A separate access request must restore any required
          permissions. Schedules do not resume automatically.
        </p>
      )}
      {route === "ownership-transfers" && (
        <p>
          The successor must already have tenant administration and delegation
          authority. Nomination expires after seven days. Custody transfer
          grants no additional access to participant data. Unavailable-owner
          recovery is not available in this build.
        </p>
      )}
      {action === "approve" && (
        <p>
          Requested by {item?.requested_by}. Reason: {item?.reason}.{" "}
          {item?.membership_ids &&
            `Affected members: ${item.membership_ids.join(", ")}. Roles: ${item.role_names.join(", ")}.`}{" "}
          {item?.expires_at && `New expiry: ${item.expires_at}.`} You must be
          independent of the requester and affected members.
        </p>
      )}
      {action === "approve" &&
        item?.bindings?.map((binding: any, index: number) => (
          <div className="panel" key={index}>
            <strong>{binding.role_name}</strong>
            <p>Scopes: {binding.scope_ids.join(", ")}</p>
            <p>Expires: {binding.expires_at}</p>
            <p>Capabilities: {binding.capabilities.join(", ")}</p>
          </div>
        ))}
      {action === "retire" && (
        <p>
          {route === "role-templates"
            ? "The role will no longer be available for new assignments. Existing assignments keep their approved permissions."
            : "All permissions supplied by this group will be removed immediately."}
        </p>
      )}
      <label>
        Reason
        <textarea name="reason" required maxLength={2000} rows={3} />
      </label>
      <button
        className="primary"
        disabled={
          busy ||
          (route === "role-templates" && action !== "retire" && !caps.length)
        }
      >
        {busy
          ? "Saving…"
          : action === "approve"
            ? "Approve reviewed change"
            : "Save change"}
      </button>
    </form>
  );
}

export function AccountPanel({
  request,
  explain,
}: Pick<Props, "request" | "explain">) {
  const [preferences, setPreferences] = useState<any>(null),
    [sessions, setSessions] = useState<any>(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0),
    [confirm, setConfirm] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      request("/auth/preferences", { signal: controller.signal }),
      request("/auth/sessions", { signal: controller.signal }),
    ])
      .then(([p, s]) => {
        if (!controller.signal.aborted) {
          setPreferences(p);
          setSessions(s);
          document.documentElement.dataset.reducedMotion = String(
            p.reduced_motion,
          );
        }
      })
      .catch((e) => {
        if (!controller.signal.aborted) setError(explain(e));
      });
    return () => controller.abort();
  }, [tick]);
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setBusy(true);
    setError("");
    try {
      const p = await request("/auth/preferences", {
        method: "PUT",
        body: JSON.stringify({
          expected_revision: preferences.revision_id,
          display_name: f.get("display_name"),
          language: "en",
          timezone: f.get("timezone"),
          reduced_motion: f.has("reduced_motion"),
        }),
      });
      setPreferences(p);
      window.dispatchEvent(
        new CustomEvent("impact:preferences", { detail: p }),
      );
      document.documentElement.dataset.reducedMotion = String(p.reduced_motion);
      setNotice("Preferences saved.");
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  async function revoke() {
    setBusy(true);
    setError("");
    try {
      const result = await request(
        confirm === "all"
          ? "/auth/sessions/revoke-all"
          : `/auth/sessions/${confirm}/revoke`,
        { method: "POST" },
      );
      if (result.signed_out) window.location.reload();
      else {
        setConfirm(null);
        setTick((n) => n + 1);
        setNotice("Session revoked.");
      }
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="account-settings">
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
      {preferences && (
        <div className="panel">
          <h2>Personal preferences</h2>
          <form onSubmit={save} key={preferences.revision_id || "new"}>
            <label>
              Display name
              <input
                name="display_name"
                required
                maxLength={120}
                defaultValue={preferences.display_name}
              />
            </label>
            <label>
              Time zone
              <input
                name="timezone"
                required
                maxLength={80}
                defaultValue={preferences.timezone}
                placeholder="Europe/London"
              />
            </label>
            <p className="muted">
              Interface language: English. Your verified sign-in identity is
              managed by your organisation.
            </p>
            <label>
              <input
                type="checkbox"
                name="reduced_motion"
                defaultChecked={preferences.reduced_motion}
              />{" "}
              Reduce motion
            </label>
            <button className="primary" disabled={busy}>
              Save preferences
            </button>
          </form>
        </div>
      )}
      {sessions && (
        <div className="panel">
          <h2>Signed-in sessions</h2>
          <p>
            Sessions expire after 15 minutes without a request, or eight hours
            after sign-in. Device labels describe the browser and are not
            identity evidence.
          </p>
          <button className="secondary" onClick={() => setTick((n) => n + 1)}>
            Refresh sessions
          </button>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Signed in</th>
                  <th>Last active</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {sessions.items.map((s: any) => (
                  <tr key={s.session_id}>
                    <td>
                      {s.device_label}
                      {s.current && " · This session"}
                    </td>
                    <td>
                      {new Date(s.created_at).toLocaleString("en", {
                        timeZone: preferences?.timezone || "UTC",
                      })}
                    </td>
                    <td>
                      {new Date(s.last_seen_at).toLocaleString("en", {
                        timeZone: preferences?.timezone || "UTC",
                      })}
                    </td>
                    <td>
                      <button
                        className="text"
                        onClick={() => setConfirm(s.session_id)}
                      >
                        Revoke session
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button className="secondary" onClick={() => setConfirm("all")}>
            Sign out all sessions
          </button>
          {confirm && (
            <div role="alert">
              <p>
                {confirm === "all"
                  ? "This signs you out everywhere in this application and rejects tokens from earlier authentications."
                  : "Revoke this browser session now?"}{" "}
                A sign-in within the last five minutes is required.
              </p>
              <button disabled={busy} onClick={revoke}>
                Confirm revocation
              </button>
              <button className="text" onClick={() => setConfirm(null)}>
                Cancel
              </button>
            </div>
          )}
          {sessions.provider_account_url ? (
            <p>
              <a href={sessions.provider_account_url} rel="noreferrer">
                Manage MFA, passkeys and recovery with your organisation
              </a>
            </p>
          ) : (
            <p className="muted">
              Your organisation has not configured an account recovery link.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
