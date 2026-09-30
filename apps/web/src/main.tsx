import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { ChangesPanel } from "./Changes";
import { PeriodGovernancePanel } from "./PeriodGovernance";
import { PlanningPanel } from "./Planning";
import { FormsPanel } from "./Forms";
import { WorkCenterPanel } from "./WorkCenter";
import { WorkspaceSettings, AccountPanel } from "./WorkspaceSettings";
import { TenantLifecycle } from "./TenantLifecycle";
import {
  ConfigurationPanel,
  ProgrammeReadiness,
  CoverageSummary,
} from "./Configuration";
import {
  AdministrationPanel,
  JoinInvitation,
  readInvitation,
} from "./Administration";
type RecordRow = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  classification: string;
  updated_at: string;
  data: Record<string, any>;
};
type Tenant = { tenant_id: string; name: string };
type Session = {
  identity_id: string;
  csrf_token: string;
  tenants: Tenant[];
  preferences?: { display_name: string; reduced_motion: boolean };
};
type Page = {
  items: RecordRow[];
  next_cursor: string | null;
  scope_label: string;
};
type Access = { capabilities: string[] };
let csrf = "";
class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public reason?: string,
  ) {
    super(message);
  }
}
async function api(path: string, options: RequestInit = {}): Promise<any> {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.method && options.method !== "GET"
        ? { "X-CSRF-Token": csrf }
        : {}),
      ...options.headers,
    },
  });
  const data = await response.json();
  if (response.status === 401 && path.startsWith("/v1/"))
    window.dispatchEvent(new Event("impact:reauthentication"));
  if (!response.ok)
    throw new ApiError(data.code, data.message, data.reason_code);
  return data;
}
const nav = [
  ["programmes", "Portfolio", "◫"],
  ["observations", "Measurement", "↗"],
  ["configuration", "Measurement setup", "⚙"],
  ["planning", "Results framework", "◇"],
  ["forms", "Forms", "☰"],
  ["changes", "Change requests", "⇄"],
  ["period-governance", "Period close", "▣"],
  ["work", "My work", "◷"],
  ["workflows", "Review queue", "✓"],
  ["calculated-results", "Results", "▥"],
  ["reports", "Reports", "▤"],
  ["memberships", "People & access", "⊙"],
  ["workspace-settings", "Workspace settings", "⚙"],
  ["account", "My account", "◉"],
] as const;
const titles: Record<string, [string, string]> = {
  "workspace-settings": [
    "Workspace settings",
    "Govern roles, groups, organisation structure and workspace custody.",
  ],
  account: [
    "My account",
    "Manage personal preferences and signed-in sessions.",
  ],
  changes: [
    "Change requests",
    "Correct measurements, amend plans and reassign responsibilities with independent review.",
  ],
  "period-governance": [
    "Period close",
    "Freeze official results, inspect locked snapshots and govern restatements.",
  ],
  work: [
    "My work",
    "Resolve assigned recalculations and acknowledge safe in-app notices.",
  ],
  forms: [
    "Forms",
    "Design, review and publish forms, then collect responses as observations.",
  ],
  planning: [
    "Results framework",
    "Plan results, place indicators and govern targets against actuals.",
  ],
  configuration: [
    "Measurement setup",
    "Build approved definitions, indicator assignments and collection plans.",
  ],
  programmes: [
    "Programme portfolio",
    "A shared view of the programmes behind your impact.",
  ],
  observations: [
    "Measurement",
    "Capture evidence. Build a trustworthy picture of change.",
  ],
  workflows: [
    "Review queue",
    "Independent decisions, tied to the exact submitted version.",
  ],
  "calculated-results": [
    "Results & learning",
    "Understand the numbers, coverage, and sources behind each result.",
  ],
  reports: [
    "Reports",
    "Keep narratives connected to the evidence they describe.",
  ],
  memberships: [
    "People & access",
    "Inspect workspace memberships and your current permissions.",
  ],
};
function label(r: RecordRow) {
  return (
    r.data.title ||
    r.data.name ||
    r.data.source_key ||
    r.data.code ||
    r.data.heading ||
    r.data.sections?.[0]?.heading ||
    r.data.local_applicability ||
    (r.data.identity_id
      ? "Member " + r.data.identity_id.slice(0, 8)
      : r.data.displayed_value
        ? "Result · " + r.data.displayed_value
        : r.data.candidate_id
          ? "Review · " + r.data.candidate_id.slice(0, 8)
          : "Record " + r.object_id.slice(0, 8))
  );
}
function Badge({ value }: { value: string }) {
  return (
    <span className={"badge " + value.toLowerCase()}>
      {value.replaceAll("_", " ")}
    </span>
  );
}
function ErrorBox({ error }: { error: string }) {
  return error ? (
    <div className="error" role="alert">
      {error}
    </div>
  ) : null;
}
function explain(e: unknown) {
  if (e instanceof ApiError) {
    if (
      e.code === "ASSURANCE_REQUIRED" ||
      ["REAUTHENTICATION_REQUIRED", "FRESH_MFA_REQUIRED"].includes(
        e.reason || "",
      )
    )
      return "Sign out and sign in again. This action requires recent authentication.";
    if (e.reason === "CONFIGURATION_NOT_IMPLEMENTED")
      return "This calculation method cannot be used with the chosen measurement type and time semantic. Choose a supported combination.";
    if (e.reason === "INVALID_DISAGGREGATION")
      return "Each dimension and category code must be unique, and UNSPECIFIED is reserved.";
    if (e.reason === "INVALID_DIMENSION_VALUES")
      return "Dimension codes must belong to the indicator's approved disaggregation scheme; exhaustive dimensions need a code and only multiselect dimensions accept several codes separated by |.";
    if (e.reason === "INVALID_MEASUREMENT_VALUE")
      return "The value does not satisfy the approved measurement contract (for example a count must be a whole number, an event count must be 1, and ratios need both components).";
    if (e.reason === "NUMERIC_OVERFLOW")
      return "The result exceeds the qualified numeric range and was not calculated.";
    if (e.reason === "CHANNEL_ADDRESS_MISMATCH")
      return "That address is not the verified email address of your registered account. Enter the address you sign in with.";
    if (e.reason === "CHANNEL_CODE_INVALID")
      return "That code is not correct. Check the latest email and try again; the code locks after five wrong attempts.";
    if (e.reason === "CHANNEL_CODE_ATTEMPTS_EXCEEDED")
      return "Too many wrong codes. This code is locked; request a new code.";
    if (e.reason === "CHANNEL_CODE_EXPIRED")
      return "This code has expired. Request a new code.";
    if (e.reason === "CHANNEL_CODE_USED")
      return "This code has already been used. Your email address is already confirmed.";
    if (e.reason === "CHANNEL_CHALLENGE_CLOSED")
      return "This code is no longer valid. Request a new code.";
    if (e.reason === "CHANNEL_REQUEST_LIMIT")
      return "Too many codes were requested in the last hour. Try again later.";
    if (e.reason === "DELIVERY_NOT_CONFIGURED")
      return "Email delivery is not configured for this deployment.";
    if (e.reason === "PLATFORM_OPERATOR_REQUIRED")
      return "Only an independent platform operator can perform this review.";
    if (e.reason === "AUTHORITY_UNAVAILABLE")
      return "Delegated authority is not available for renewal. Initial access must be applied and the owner must still hold its administration ceiling.";
    if (e.reason === "RENEWAL_PENDING")
      return "An authority renewal is already pending. Complete, withdraw or reject it before proposing another.";
    if (e.reason === "RENEWAL_EXPIRED")
      return "This renewal review has expired. Withdraw or reject it, then propose a fresh renewal.";
    if (
      ["AUTHORITY_CHANGED", "RENEWAL_CONTEXT_CHANGED"].includes(e.reason || "")
    )
      return "The delegated authority, tenant or owner record changed after this proposal was pinned. Refresh the authority panel; withdraw or reject the proposal and review a fresh one.";
    if (e.reason === "INVALID_RENEWAL_TRANSITION")
      return "This renewal has already been decided or is not ready for that action. Refresh the list before continuing.";
    if (e.reason === "OPERATION_REUSE")
      return "This operation was already submitted with different content, or its receipt has expired. Close the form and submit the change again.";
    if (e.reason === "OWNER_UNAVAILABLE")
      return "The tenant owner’s custody membership is no longer active. Only the current owner can propose or withdraw a renewal.";
    if (e.reason === "DELEGATION_NOT_PERMITTED")
      return "The requested role, scope or expiry exceeds your delegated authority.";
    if (e.reason === "INITIAL_ACCESS_ALREADY_PROVISIONED")
      return "Initial access has already been provisioned. Use access administration for later changes.";
    if (e.reason === "INITIAL_ACCESS_PENDING")
      return "An initial access proposal already exists. Complete, withdraw or reject it before proposing another.";
    if (e.reason === "INITIAL_ACCESS_EXPIRED")
      return "This review has expired. Withdraw or reject it, then create a fresh proposal.";
    if (
      ["INITIAL_ACCESS_CONTEXT_CHANGED", "ACCESS_PROFILE_CHANGED"].includes(
        e.reason || "",
      )
    )
      return "The tenant configuration or access profile changed. Withdraw or reject this proposal and review a new one.";
    if (e.reason === "SECOND_ADMIN_UNAVAILABLE")
      return "Choose a different eligible administrator. Existing or inactive memberships cannot be restored through initial access, and a renewal requires a second administrator who still holds delegated authority.";
    if (e.reason === "GRANT_EXPIRY_BOUNDS")
      return "Choose an expiry in the future, after any current expiry, and within 90 days.";
    if (e.reason === "RECOVERY_EXPIRY_BOUNDS")
      return "Choose a contact expiry in the future and within 90 days.";
    if (e.reason === "RECOVERY_PENDING")
      return "A recovery nomination is already pending. Complete, withdraw or reject it before nominating again.";
    if (
      ["RECOVERY_REVIEW_EXPIRED", "RECOVERY_VERIFICATION_STALE"].includes(
        e.reason || "",
      )
    )
      return "This nomination or verification has expired. Withdraw or reject it, then nominate and verify again.";
    if (
      ["RECOVERY_CONTACT_CHANGED", "RECOVERY_CONTEXT_CHANGED"].includes(
        e.reason || "",
      )
    )
      return "The tenant, owner or current contact changed. Refresh the records; withdraw or reject any pending nomination before submitting a replacement.";
    if (e.reason === "RECOVERY_IDENTITY_CHANGED")
      return "The nominated account’s verified contact changed. Create a fresh nomination for the current verified account.";
    if (e.reason === "RECOVERY_VERIFICATION_REVOKED")
      return "The nominated account’s authentication was revoked. A fresh nomination and verification are required.";
    if (e.reason === "RECOVERY_TENANT_UNAVAILABLE")
      return "Recovery contacts can be configured after ownership acceptance and before closure.";
    if (e.reason === "TENANT_NOT_ACTIVE")
      return "The tenant must be active before initial access or an authority renewal can be proposed, accepted or approved.";
    if (e.reason === "TENANT_NOT_READY")
      return "The tenant no longer passes its deployment and ownership checks. Review tenant readiness before continuing.";
    if (e.reason === "LAST_OWNER_PROTECTED")
      return "The designated workspace owner cannot be removed through ordinary administration.";
    if (e.code === "INVITATION_UNAVAILABLE")
      return "The invitation is invalid, expired, already used, or belongs to a different verified account.";
    if (e.reason === "INDEPENDENCE_REQUIRED")
      return "An independent reviewer must decide on this record. You contributed to its content.";
    if (e.reason === "PLAN_INDICATOR_CHANGED")
      return "The indicator configuration changed after this plan was submitted. Return the plan for review, or restore the configuration pinned by its approval.";
    if (e.reason === "PLAN_ALREADY_APPROVED")
      return "An approved plan already exists for this indicator and period. Approved plan amendments are not available in this release.";
    if (e.reason === "ASSIGNMENT_INELIGIBLE")
      return "The assigned collector or reviewer no longer has the required active membership and permissions.";
    if (e.reason === "UNBOUND_NARRATIVE_NUMBER")
      return "Replace every narrative number with its approved binding placeholder before submission.";
    if (e.reason === "UNKNOWN_NARRATIVE_BINDING")
      return "A narrative placeholder does not match a metric bound in the same section.";
    if (e.reason === "APPROVED_DISCLOSURE_REQUIRED")
      return "Choose an independently approved disclosure for this exact report revision.";
    if (e.reason === "ACTIVE_PUBLICATION_REQUIRED")
      return "This report revision has no active controlled publication to withdraw.";
    if (e.code === "CONFLICT_VERSION")
      return "Someone changed this record. Close it and refresh before saving again.";
    return (
      e.message +
      (e.reason ? " (" + e.reason.replaceAll("_", " ").toLowerCase() + ")" : "")
    );
  }
  return e instanceof Error ? e.message : "The request could not be completed.";
}
function App() {
  const [tenantConsole, setTenantConsole] = useState(false);
  const [invitation, setInvitation] = useState(readInvitation);
  const [session, setSession] = useState<Session | null>(null),
    [loading, setLoading] = useState(true),
    [tenant, setTenant] = useState(""),
    [development, setDevelopment] = useState(false),
    [error, setError] = useState("");
  async function refresh() {
    const s = await api("/auth/me");
    csrf = s.csrf_token;
    setError("");
    setSession(s);
    document.documentElement.dataset.reducedMotion = String(
      s.preferences?.reduced_motion || false,
    );
    setTenant((current) =>
      s.tenants.some((t: Tenant) => t.tenant_id === current)
        ? current
        : s.tenants[0]?.tenant_id || "",
    );
  }
  useEffect(() => {
    const preferencesChanged = (event: Event) => {
      const preferences = (event as CustomEvent).detail;
      setSession((previous) =>
        previous ? { ...previous, preferences } : previous,
      );
    };
    window.addEventListener("impact:preferences", preferencesChanged);
    const reauthenticate = () => {
      csrf = "";
      setSession(null);
      setTenantConsole(false);
      setTenant("");
      setError("Your session requires a fresh sign-in before continuing.");
    };
    window.addEventListener("impact:reauthentication", reauthenticate);
    api("/auth/mode")
      .then((x) => setDevelopment(x.development))
      .catch(() => {});
    refresh()
      .catch((e) => {
        if (e.code !== "AUTH_REQUIRED") setError(explain(e));
      })
      .finally(() => setLoading(false));
    return () => {
      window.removeEventListener("impact:preferences", preferencesChanged);
      window.removeEventListener("impact:reauthentication", reauthenticate);
    };
  }, []);
  async function logout() {
    try {
      const result = await api("/auth/logout", { method: "POST" });
      csrf = "";
      setSession(null);
      // With a live identity provider the provider session is ended too: the browser visits
      // its logout endpoint, which returns to the platform's front page.
      if (result?.logout_url) window.location.assign(result.logout_url);
    } catch (e) {
      setError(explain(e));
    }
  }
  if (loading) return <div className="loading">Opening your workspace…</div>;
  if (!session)
    return (
      <Login development={development} refresh={refresh} initialError={error} />
    );
  if (invitation)
    return (
      <JoinInvitation
        invitation={invitation}
        request={api}
        explain={explain}
        logout={logout}
        complete={async () => {
          await refresh();
          history.replaceState(null, "", location.pathname);
          setInvitation(null);
        }}
      />
    );
  if (tenantConsole)
    return (
      <TenantLifecycle
        request={api}
        development={development}
        explain={explain}
        identity={session.identity_id}
        logout={logout}
        close={() => {
          setTenantConsole(false);
          refresh().catch((e) => setError(explain(e)));
        }}
      />
    );
  if (!session.tenants.length)
    return (
      <main className="join-page">
        <section className="panel">
          <h1>No active workspace</h1>
          <p>
            Open your invitation link after signing in with the intended
            verified account.
          </p>
          <button className="secondary" onClick={logout}>
            Sign out
          </button>
          <button className="secondary" onClick={() => setTenantConsole(true)}>
            Tenant lifecycle
          </button>
        </section>
      </main>
    );
  return (
    <div className="app">
      <Workspace
        key={tenant}
        tenant={tenant}
        session={session}
        setTenant={setTenant}
        logout={logout}
        development={development}
        openTenants={() => setTenantConsole(true)}
      />
    </div>
  );
}
function Login({
  development,
  refresh,
  initialError,
}: {
  development: boolean;
  refresh: () => Promise<void>;
  initialError: string;
}) {
  const [error, setError] = useState(initialError),
    [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const f = new FormData(e.currentTarget);
    try {
      await api("/auth/development-login", {
        method: "POST",
        body: JSON.stringify({
          username: f.get("username"),
          password: f.get("password"),
        }),
      });
      await refresh();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="login">
      <section className="login-story">
        <a className="brand" href="/">
          impact<span>.</span>
        </a>
        <div>
          <span className="eyebrow">FROM EVIDENCE TO UNDERSTANDING</span>
          <h1>
            Make change
            <br />
            measurable.
          </h1>
          <p>
            Bring your programmes, evidence, and decisions into one shared
            workspace.
          </p>
          <div className="rings" aria-hidden="true">
            <i />
            <i />
            <i />
          </div>
        </div>
        <p className="small">Clarity at every step.</p>
      </section>
      <section className="login-form">
        <div>
          <span className="eyebrow">YOUR MEASUREMENT WORKSPACE</span>
          <h2>Welcome back</h2>
          <p className="muted">Sign in to continue your work.</p>
          <ErrorBox error={error} />
          {development ? (
            <form onSubmit={submit}>
              <label>
                Username
                <input
                  name="username"
                  autoComplete="username"
                  required
                  autoFocus
                />
              </label>
              <label>
                Password
                <input
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                />
              </label>
              <button className="primary" disabled={busy}>
                {busy ? "Signing in…" : "Sign in →"}
              </button>
              <p className="footnote">
                Development workspace · use the credentials generated during
                setup. All sample records are synthetic.
              </p>
            </form>
          ) : (
            <a className="primary button" href="/auth/login">
              Continue with your organisation →
            </a>
          )}
        </div>
      </section>
    </main>
  );
}
function Workspace({
  tenant,
  session,
  setTenant,
  logout,
  development,
  openTenants,
}: {
  tenant: string;
  session: Session;
  setTenant: (t: string) => void;
  logout: () => void;
  development: boolean;
  openTenants: () => void;
}) {
  const [route, setRoute] = useState("programmes"),
    [access, setAccess] = useState<Access>({ capabilities: [] }),
    [page, setPage] = useState<Page | null>(null),
    [query, setQuery] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [tick, setTick] = useState(0),
    [dialog, setDialog] = useState<{ mode: string; row?: RecordRow } | null>(
      null,
    ),
    [toast, setToast] = useState("");
  const request = useRef<AbortController | null>(null);
  const base = "/v1/tenants/" + tenant + "/";
  const allowed = (cap: string) => access.capabilities.includes(cap);
  useEffect(() => {
    const c = new AbortController();
    setAccess({ capabilities: [] });
    if (tenant)
      api(base + "me/access", { signal: c.signal })
        .then((a) => {
          if (c.signal.aborted) return;
          setAccess(a);
          if (
            !a.capabilities.includes("programmes.read") &&
            a.capabilities.includes("memberships.read")
          )
            setRoute((current) =>
              current === "programmes" ? "memberships" : current,
            );
        })
        .catch((e) => {
          if (e.name !== "AbortError") setError(explain(e));
        });
    return () => c.abort();
  }, [tenant]);
  async function loadMore() {
    if (!page?.next_cursor) return;
    setBusy(true);
    try {
      const more = await api(
        base +
          route +
          "?limit=50&cursor=" +
          encodeURIComponent(page.next_cursor),
      );
      setPage({ ...more, items: [...page.items, ...more.items] });
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    request.current?.abort();
    const c = new AbortController();
    request.current = c;
    setPage(null);
    setError("");
    setBusy(true);
    if (
      !tenant ||
      route === "memberships" ||
      route === "workspace-settings" ||
      route === "account" ||
      route === "configuration" ||
      route === "planning" ||
      route === "forms" ||
      route === "changes" ||
      route === "period-governance" ||
      route === "work"
    ) {
      setBusy(false);
      return;
    }
    api(base + route + "?limit=50", { signal: c.signal })
      .then((result) => {
        if (!c.signal.aborted) setPage(result);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      })
      .finally(() => {
        if (!c.signal.aborted) setBusy(false);
      });
    return () => c.abort();
  }, [route, tenant, tick]);
  function completed(message: string) {
    setDialog(null);
    setToast(message);
    setTick((t) => t + 1);
  }
  const rows = (page?.items || []).filter((r) =>
    (label(r) + " " + r.lifecycle_state + " " + r.object_id)
      .toLowerCase()
      .includes(query.toLowerCase()),
  );
  const [title, description] = titles[route];
  return (
    <>
      <aside className="sidebar">
        <a className="brand" href="/">
          impact<span>.</span>
        </a>
        <div className="workspace-label">MEASUREMENT WORKSPACE</div>
        <nav aria-label="Main navigation">
          {nav.map(([key, name, icon]) => (
            <button
              key={key}
              className={route === key ? "active" : ""}
              onClick={() => {
                setRoute(key);
                setQuery("");
                setToast("");
              }}
              aria-current={route === key ? "page" : undefined}
            >
              <span aria-hidden="true">{icon}</span>
              {name}
              {key === "workflows" && <span className="nav-dot" />}
            </button>
          ))}
          <button onClick={openTenants}>Tenant lifecycle</button>
        </nav>
        <div className="sidebar-bottom">
          <span className="avatar">IM</span>
          <div>
            <strong>
              {session.preferences?.display_name || "Impact workspace"}
            </strong>
            <small>Evidence you can trace</small>
          </div>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <span className="breadcrumb">
            Workspace <span>/</span> {nav.find((x) => x[0] === route)?.[1]}
          </span>
          <div className="top-actions">
            <select
              aria-label="Workspace"
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
            >
              {session.tenants.map((t) => (
                <option key={t.tenant_id} value={t.tenant_id}>
                  {t.name}
                </option>
              ))}
            </select>
            <button className="text" onClick={logout}>
              Sign out
            </button>
          </div>
        </header>
        <main className="content">
          {development && (
            <div className="demo-note">
              <span /> Development workspace · synthetic sample data
            </div>
          )}
          <div className="page-heading">
            <div>
              <span className="eyebrow">YOUR IMPACT, IN FOCUS</span>
              <h1>{title}</h1>
              <p>{description}</p>
            </div>
            <div>
              {route === "programmes" && allowed("programmes.draft.create") && (
                <button
                  className="primary"
                  onClick={() => setDialog({ mode: "programme" })}
                >
                  ＋ New programme
                </button>
              )}
              {route === "observations" &&
                allowed("observations.draft.create") && (
                  <button
                    className="primary"
                    onClick={() => setDialog({ mode: "observation" })}
                  >
                    ＋ Add observation
                  </button>
                )}
              {route === "calculated-results" &&
                allowed("indicator.calculate") && (
                  <button
                    className="primary"
                    onClick={() => setDialog({ mode: "calculate" })}
                  >
                    ↗ Calculate result
                  </button>
                )}
              {route === "reports" && allowed("reports.draft.create") && (
                <button
                  className="primary"
                  onClick={() => setDialog({ mode: "report" })}
                >
                  ＋ Draft report
                </button>
              )}
            </div>
          </div>
          {toast && (
            <div className="success" role="status">
              ✓ {toast}
            </div>
          )}
          <ErrorBox error={error} />
          {route === "workspace-settings" ? (
            <WorkspaceSettings
              key={tenant}
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "account" ? (
            <AccountPanel request={api} explain={explain} />
          ) : route === "period-governance" ? (
            <PeriodGovernancePanel
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "work" ? (
            <WorkCenterPanel
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
            />
          ) : route === "changes" ? (
            <ChangesPanel
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "forms" ? (
            <FormsPanel
              key={tenant}
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "planning" ? (
            <PlanningPanel
              key={tenant}
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "configuration" ? (
            <ConfigurationPanel
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : route === "memberships" ? (
            <AdministrationPanel
              base={base}
              capabilities={access.capabilities}
              request={api}
              explain={explain}
              Dialog={Dialog}
            />
          ) : (
            <>
              <section className="metrics" aria-label="Loaded records">
                <div>
                  <span>Records loaded</span>
                  <strong>{page?.items.length ?? "—"}</strong>
                  <small>
                    {page?.next_cursor
                      ? "More records available"
                      : "Within your current access"}
                  </small>
                </div>
                <div>
                  <span>Awaiting a decision</span>
                  <strong>
                    {page?.items.filter((r) =>
                      ["Submitted", "InReview"].includes(r.lifecycle_state),
                    ).length ?? "—"}
                  </strong>
                  <small>In the records currently loaded</small>
                </div>
                <div className="metric-note">
                  <span className="eyebrow">BUILT ON EVIDENCE</span>
                  <h3>Every revision tells a story.</h3>
                  <p>
                    Decisions and results stay connected to their source
                    records.
                  </p>
                </div>
              </section>
              <section className="panel">
                <div className="panel-toolbar">
                  <div>
                    <h2>
                      {route === "memberships"
                        ? "Workspace members"
                        : nav.find((x) => x[0] === route)?.[1]}
                    </h2>
                    <small>
                      {page?.scope_label || "Your permitted records"}
                    </small>
                  </div>
                  <div className="toolbar-actions">
                    <input
                      aria-label="Search loaded records"
                      type="search"
                      placeholder="Search loaded records…"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                    />
                    <button
                      className="secondary"
                      aria-label="Refresh records"
                      onClick={() => setTick((t) => t + 1)}
                      disabled={busy}
                    >
                      ↻
                    </button>
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>{route === "memberships" ? "Member" : "Record"}</th>
                        <th>Status</th>
                        <th>Last updated</th>
                        <th>
                          <span className="sr-only">Open record</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r) => (
                        <tr key={r.object_id}>
                          <td>
                            <button
                              className="record-link"
                              onClick={() =>
                                setDialog({ mode: "inspect", row: r })
                              }
                            >
                              {label(r)}
                            </button>
                            <small className="record-id">
                              {r.object_id.slice(0, 8)} ·{" "}
                              {r.classification.toLowerCase()}
                            </small>
                          </td>
                          <td>
                            <Badge value={r.data.mode || r.lifecycle_state} />
                            {r.data.freshness?.stale && <Badge value="Stale" />}
                          </td>
                          <td>
                            {new Date(r.updated_at).toLocaleDateString(
                              undefined,
                              {
                                month: "short",
                                day: "numeric",
                                year: "numeric",
                              },
                            )}
                          </td>
                          <td>
                            <button
                              className="open"
                              aria-label={"Open " + label(r)}
                              onClick={() =>
                                setDialog({ mode: "inspect", row: r })
                              }
                            >
                              ↗
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {busy && !page ? (
                  <div className="empty" role="status">
                    Loading records…
                  </div>
                ) : !rows.length ? (
                  <div className="empty">
                    <h3>
                      {query
                        ? "No matching records"
                        : "Your next chapter starts here"}
                    </h3>
                    <p>
                      {query
                        ? "Try another search within the loaded records."
                        : "Records will appear here when they are available to you."}
                    </p>
                  </div>
                ) : null}
                <div className="panel-footer">
                  <span>
                    {rows.length} of {page?.items.length || 0} loaded records
                    shown
                  </span>
                  {page?.next_cursor && (
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={loadMore}
                    >
                      Load more
                    </button>
                  )}
                </div>
              </section>
            </>
          )}
          {route === "memberships" && (
            <section className="panel permissions">
              <h2>Your effective capabilities</h2>
              <p>Access is evaluated by the server for each request.</p>
              <div>
                {access.capabilities.map((cap) => (
                  <code key={cap}>{cap}</code>
                ))}
              </div>
            </section>
          )}
          <footer className="page-footer">
            Impact · A clearer view of change{" "}
            <span>Revision-aware workspace</span>
          </footer>
        </main>
      </div>
      {dialog && (
        <Dialog
          title={
            dialog.mode === "inspect"
              ? label(dialog.row!)
              : {
                  programme: "New programme",
                  observation: "Add observation",
                  calculate: "Calculate result",
                  report: "Draft internal report",
                  submit: "Submit for review",
                  review: "Review submission",
                  edit: "Edit programme",
                  "disclosure-request": "Request controlled publication",
                  "publish-report": "Publish approved disclosure",
                  "withdraw-report": "Withdraw controlled publications",
                }[dialog.mode] || "Record"
          }
          close={() => setDialog(null)}
        >
          <Editor
            key={dialog.mode + (dialog.row?.object_id || "")}
            mode={dialog.mode}
            row={dialog.row}
            route={route}
            base={base}
            allowed={allowed}
            completed={completed}
            navigate={(mode, row) => setDialog({ mode, row })}
          />
        </Dialog>
      )}
    </>
  );
}
function Dialog({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={(e) => {
        e.preventDefault();
        close();
      }}
      aria-labelledby="dialog-title"
    >
      <div className="dialog-heading">
        <div>
          <span className="eyebrow">IMPACT WORKSPACE</span>
          <h2 id="dialog-title">{title}</h2>
        </div>
        <button className="secondary" aria-label="Close dialog" onClick={close}>
          ×
        </button>
      </div>
      {children}
    </dialog>
  );
}
function Fields({ data }: { data: Record<string, any> }) {
  return (
    <dl className="fields">
      {Object.entries(data).map(([k, v]) => (
        <React.Fragment key={k}>
          <dt>{k.replaceAll("_", " ")}</dt>
          <dd
            className={
              ["coverage", "disaggregation"].includes(k)
                ? "wide-field"
                : undefined
            }
          >
            {v === null ? (
              "—"
            ) : k === "coverage" ? (
              <CoverageSummary data={v} />
            ) : k === "disaggregation" && Array.isArray(v) ? (
              <Breakdown entries={v} />
            ) : typeof v === "object" ? (
              <pre>{JSON.stringify(v, null, 2)}</pre>
            ) : (
              String(v)
            )}
          </dd>
        </React.Fragment>
      ))}
    </dl>
  );
}
function dimensionCodes(text: string) {
  const codes: Record<string, string> = {};
  for (const part of text.split(";")) {
    const [key, value] = part.split("=").map((x) => x.trim());
    if (key && value) codes[key] = value;
  }
  return codes;
}
function Breakdown({ entries }: { entries: any[] }) {
  return (
    <div className="table-scroll">
      <table aria-label="Category breakdown">
        <thead>
          <tr>
            <th>Dimension</th>
            <th>Category</th>
            <th>Result</th>
            <th>Contributors</th>
            <th>Additivity</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e) => (
            <tr key={e.dimension + "/" + e.category}>
              <td>
                {e.dimension} · v{e.dimension_version}
              </td>
              <td>{e.category}</td>
              <td>
                {e.value_state === "UNDEFINED"
                  ? "Undefined (" +
                    e.reason_code.replaceAll("_", " ").toLowerCase() +
                    ")"
                  : e.displayed_value}
              </td>
              <td>{e.contributor_count}</td>
              <td>
                {e.additivity === "ADDITIVE" ? "Adds to total" : "Not additive"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="footnote">
        The total is calculated from the approved source values, never from
        these rounded category values. Non-additive categories (multiselect,
        ratios, averages and positions) do not sum to the total.
      </p>
    </div>
  );
}
function Editor({
  mode,
  row,
  route,
  base,
  allowed,
  completed,
  navigate,
}: {
  mode: string;
  row?: RecordRow;
  route: string;
  base: string;
  allowed: (c: string) => boolean;
  completed: (m: string) => void;
  navigate: (m: string, r?: RecordRow) => void;
}) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [resources, setResources] = useState<Record<string, RecordRow[]>>({}),
    [candidate, setCandidate] = useState<RecordRow | null>(null),
    [currentTarget, setCurrentTarget] = useState<RecordRow | null>(null),
    [reportSnapshot, setReportSnapshot] = useState("");
  const operation = useRef(crypto.randomUUID()),
    captured = useRef(new Date().toISOString());
  useEffect(() => {
    const c = new AbortController();
    let routes: string[] = [];
    if (mode === "observation" || mode === "calculate")
      routes = ["indicator-instances"];
    if (mode === "calculate") routes.push("periods");
    if (mode === "submit") routes = ["workflow-templates"];
    if (mode === "report")
      routes = ["calculated-results", "snapshots", "report-templates"];
    if (mode === "disclosure-request")
      routes = ["publication-recipients", "workflow-templates"];
    if (mode === "publish-report") routes = ["disclosures"];
    if (mode === "programme" || mode === "edit")
      routes = ["reporting-calendars", "geographies"];
    Promise.all(
      routes.map(
        async (r) =>
          [
            r,
            (await api(base + r + "?limit=100", { signal: c.signal })).items,
          ] as const,
      ),
    )
      .then((x) => setResources(Object.fromEntries(x)))
      .catch((e) => {
        if (e.name !== "AbortError") setError(explain(e));
      });
    if (mode === "review" && row) {
      api(base + "workflows/" + row.object_id + "/candidate", {
        signal: c.signal,
      })
        .then(({ record: r, current_target }) => {
          if (r.revision_id !== row.data.candidate_revision)
            throw new Error("The candidate has changed. Refresh the queue.");
          setCandidate(r);
          setCurrentTarget(current_target || null);
        })
        .catch((e) => {
          if (e.name !== "AbortError") setError(explain(e));
        });
    }
    return () => c.abort();
  }, [mode]);
  async function send(
    target: string,
    data: Record<string, any>,
    method = "POST",
    expected?: string,
  ) {
    setBusy(true);
    setError("");
    try {
      await api(base + target, {
        method,
        body: JSON.stringify({
          operation_id: operation.current,
          ...(expected ? { expected_revision: expected } : {}),
          data,
        }),
      });
      completed("Saved successfully. The durable receipt has been recorded.");
    } catch (e) {
      setError(
        explain(e),
      ); /* Preserve operation ID: retries must remain exact. */
    } finally {
      setBusy(false);
    }
  }
  function form(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget),
      get = (k: string) => String(f.get(k) || "");
    if (mode === "programme" || mode === "edit")
      return send(
        "programmes" + (row ? "/" + row.object_id : ""),
        {
          title: get("title"),
          code: get("code"),
          ...Object.fromEntries(
            ["programme_type", "reporting_calendar_id", "geography_id"]
              .filter((k) => get(k))
              .map((k) => [k, get(k)]),
          ),
          ...(get("starts_at")
            ? {
                starts_at: new Date(
                  get("starts_at") + "T00:00:00Z",
                ).toISOString(),
              }
            : {}),
          ...(get("ends_at")
            ? { ends_at: new Date(get("ends_at") + "T23:59:59Z").toISOString() }
            : {}),
        },
        row ? "PATCH" : "POST",
        row?.revision_id,
      );
    if (mode === "observation") {
      const value = get("value"),
        numerator = get("numerator"),
        denominator = get("denominator");
      return send("observations", {
        source_namespace: get("source_namespace"),
        source_key: get("source_key"),
        indicator_id: get("indicator_id"),
        event_at: new Date(get("event_at") + "T12:00:00Z").toISOString(),
        captured_at: captured.current,
        capture_zone: "UTC",
        value_state: "PRESENT",
        value,
        ...(numerator !== "" ? { numerator } : {}),
        ...(denominator !== "" ? { denominator } : {}),
        source_version: "1",
        dimension_values: dimensionCodes(get("dimension_values")),
      });
    }
    if (mode === "submit")
      return send(
        route + "/" + row!.object_id + "/actions/submit",
        { workflow_version: get("workflow_version") },
        "POST",
        row!.revision_id,
      );
    if (mode === "calculate") {
      const indicator = resources["indicator-instances"]?.find(
        (r) => r.object_id === get("indicator_id"),
      );
      if (indicator)
        return send(
          "indicator-instances/" + indicator.object_id + "/actions/calculate",
          { period_id: get("period_id") },
          "POST",
          indicator.revision_id,
        );
    }
    if (mode === "report") {
      const r = resources["calculated-results"]?.find(
        (r) => r.revision_id === get("result_revision"),
      );
      const template = resources["report-templates"]?.find(
          (r) => r.revision_id === get("template_version"),
        ),
        templateSection = template?.data.sections?.[0],
        bindingCode = templateSection?.required_binding_codes?.[0] || "RESULT";
      return send("reports", {
        template_version: get("template_version"),
        snapshot_id: get("snapshot_id"),
        language: "en",
        audience_class: "INTERNAL",
        sections: [
          {
            section_code: templateSection?.section_code || "SUMMARY",
            heading: get("heading"),
            narrative: get("narrative"),
            bindings: r
              ? [
                  {
                    binding_code: bindingCode,
                    result_revision: r.revision_id,
                    display_decimals: r.data.display_decimals,
                    unit: r.data.unit,
                  },
                ]
              : [],
            evidence_revisions: [],
          },
        ],
      });
    }
    if (mode === "disclosure-request")
      return send("disclosure-requests", {
        artifact_version: row!.revision_id,
        recipients: [
          {
            membership_id: get("recipient_id"),
            allow_download: f.get("allow_download") === "on",
          },
        ],
        purpose: get("purpose"),
        expires_at: new Date(get("expires_at") + ":00Z").toISOString(),
        public: false,
        workflow_version: get("workflow_version"),
      });
    if (mode === "publish-report")
      return send(
        "reports/" + row!.object_id + "/actions/publish",
        {
          approved_candidate_revision: row!.revision_id,
          disclosure_id: get("disclosure_id"),
        },
        "POST",
        row!.revision_id,
      );
    if (mode === "withdraw-report")
      return send(
        "reports/" + row!.object_id + "/actions/withdraw",
        { reason: get("reason") },
        "POST",
        row!.revision_id,
      );
  }
  const selection = (
    key: string,
    name: string,
    records: RecordRow[],
    value = "object_id",
  ) => (
    <label>
      {name}
      <select name={key} aria-label={name} required defaultValue="">
        <option value="" disabled>
          Choose {name.toLowerCase()}
        </option>
        {records.map((r) => (
          <option key={r.object_id} value={(r as any)[value]}>
            {label(r)}
          </option>
        ))}
      </select>
    </label>
  );
  if (mode === "inspect" && row)
    return (
      <>
        <div className="detail-meta">
          <Badge value={row.lifecycle_state} />
          <span>Revision {row.revision_id.slice(0, 8)}</span>
        </div>
        <Fields data={row.data} />
        {route === "programmes" &&
          ["Draft", "Ready"].includes(row.lifecycle_state) && (
            <ProgrammeReadiness
              {...{ base, row, request: api, explain, allowed }}
              complete={() => completed("Programme state updated.")}
            />
          )}
        <div className="dialog-actions">
          {route === "programmes" &&
            ["Draft", "Returned"].includes(row.lifecycle_state) &&
            allowed("programmes.draft.edit") && (
              <button className="primary" onClick={() => navigate("edit", row)}>
                Edit programme
              </button>
            )}
          {route === "observations" &&
            ["Draft", "Returned"].includes(row.lifecycle_state) &&
            allowed("observation.submit") && (
              <button
                className="primary"
                onClick={() => navigate("submit", row)}
              >
                Submit for review
              </button>
            )}
          {route === "reports" &&
            ["Draft", "Returned"].includes(row.lifecycle_state) &&
            allowed("report.submit") && (
              <button
                className="primary"
                onClick={() => navigate("submit", row)}
              >
                Submit frozen package for review
              </button>
            )}
          {route === "reports" && row.lifecycle_state === "Approved" && (
            <a
              className="primary"
              href={base + "reports/" + row.object_id + "/export"}
              target="_blank"
              rel="noreferrer"
            >
              Open approved export
            </a>
          )}
          {route === "reports" && row.lifecycle_state === "Approved" && (
            <a
              className="secondary button"
              href={base + "reports/" + row.object_id + "/export.csv"}
            >
              Download bound values (CSV)
            </a>
          )}
          {route === "reports" &&
            row.lifecycle_state === "Approved" &&
            allowed("disclosure.request") && (
              <button
                className="secondary"
                onClick={() => navigate("disclosure-request", row)}
              >
                Request controlled publication
              </button>
            )}
          {route === "reports" &&
            row.lifecycle_state === "Approved" &&
            allowed("report.publish") && (
              <button
                className="primary"
                onClick={() => navigate("publish-report", row)}
              >
                Publish approved disclosure
              </button>
            )}
          {route === "reports" &&
            row.lifecycle_state === "Approved" &&
            allowed("report.withdraw") && (
              <button
                className="secondary danger"
                onClick={() => navigate("withdraw-report", row)}
              >
                Withdraw publications
              </button>
            )}
          {route === "workflows" &&
            row.lifecycle_state === "InReview" &&
            allowed("workflow.approve") && (
              <button
                className="primary"
                onClick={() => navigate("review", row)}
              >
                Review submission
              </button>
            )}
        </div>
      </>
    );
  if (mode === "review")
    return (
      <>
        <p className="muted">
          Decide on the exact submitted revision. Content authors cannot approve
          their own work.
        </p>
        <ErrorBox error={error} />
        {candidate ? (
          <>
            {currentTarget && (
              <section aria-label="Current approved record">
                <h3>Current approved record</h3>
                <Fields data={currentTarget.data} />
                {candidate.data.target_revision !==
                  currentTarget.revision_id && (
                  <p role="alert">
                    This request targets an older revision. Return it for an
                    update before approval.
                  </p>
                )}
              </section>
            )}
            <h3>Submitted request</h3>
            <Fields data={candidate.data} />
          </>
        ) : (
          <p>Loading the submitted record…</p>
        )}
        <form onSubmit={(e) => e.preventDefault()}>
          <label>
            Decision reason
            <textarea
              id="decision-reason"
              name="reason"
              maxLength={2000}
              placeholder="Explain your decision…"
            />
          </label>
          <div className="dialog-actions">
            {(["return", "reject", "approve"] as const)
              .filter((a) => allowed("workflow." + a))
              .map((a) => (
                <button
                  type="button"
                  className={a === "approve" ? "primary" : "secondary"}
                  key={a}
                  disabled={busy || !candidate}
                  onClick={() => {
                    const reason = (
                      document.getElementById(
                        "decision-reason",
                      ) as HTMLTextAreaElement
                    ).value;
                    if (a !== "approve" && !reason.trim()) {
                      setError("Add a reason for this decision.");
                      return;
                    }
                    send(
                      "workflows/" + row!.object_id + "/actions/" + a,
                      {
                        candidate_revision: row!.data.candidate_revision,
                        reason,
                      },
                      "POST",
                      row!.revision_id,
                    );
                  }}
                >
                  {a === "approve"
                    ? "Approve"
                    : a === "return"
                      ? "Return for changes"
                      : "Reject"}
                </button>
              ))}
          </div>
        </form>
      </>
    );
  return (
    <form onSubmit={form}>
      <ErrorBox error={error} />
      {["programme", "edit"].includes(mode) && (
        <>
          <label>
            Programme title
            <input
              name="title"
              required
              maxLength={200}
              defaultValue={row?.data.title || ""}
              autoFocus
            />
          </label>
          <label>
            Programme code
            <input
              name="code"
              required
              maxLength={64}
              defaultValue={row?.data.code || ""}
            />
          </label>
          <div className="form-grid">
            <label>
              Start date
              <input
                type="date"
                name="starts_at"
                defaultValue={row?.data.starts_at?.slice(0, 10)}
              />
            </label>
            <label>
              End date
              <input
                type="date"
                name="ends_at"
                defaultValue={row?.data.ends_at?.slice(0, 10)}
              />
            </label>
          </div>
          <label>
            Programme type
            <input
              name="programme_type"
              maxLength={64}
              defaultValue={row?.data.programme_type || ""}
              placeholder="e.g. Community health"
            />
          </label>
          {[
            [
              "reporting-calendars",
              "reporting_calendar_id",
              "Reporting calendar",
            ],
            ["geographies", "geography_id", "Geography"],
          ].map(([resource, key, title]) => (
            <label key={key}>
              {title}
              <select
                name={key}
                aria-label={title}
                defaultValue={row?.data[key] || ""}
              >
                <option value="">Choose before activation</option>
                {(resources[resource] || [])
                  .filter((r) => r.lifecycle_state === "Active")
                  .map((r) => (
                    <option key={r.object_id} value={r.object_id}>
                      {label(r)}
                    </option>
                  ))}
              </select>
            </label>
          ))}
        </>
      )}
      {mode === "observation" && (
        <>
          {selection(
            "indicator_id",
            "Indicator",
            (resources["indicator-instances"] || []).filter(
              (r) => r.lifecycle_state === "Active",
            ),
          )}
          <label>
            Source namespace
            <input
              name="source_namespace"
              required
              maxLength={64}
              defaultValue="MANUAL"
            />
          </label>
          <label>
            Source key
            <input
              name="source_key"
              required
              maxLength={200}
              placeholder="e.g. field-visit-2026-001"
            />
          </label>
          <label>
            Event date (UTC)
            <input
              type="date"
              name="event_at"
              required
              defaultValue={new Date().toISOString().slice(0, 10)}
            />
          </label>
          <label>
            Recorded value
            <input name="value" required inputMode="decimal" placeholder="80" />
          </label>
          <div className="form-grid">
            <label>
              Numerator
              <input name="numerator" inputMode="decimal" placeholder="8" />
            </label>
            <label>
              Denominator
              <input name="denominator" inputMode="decimal" placeholder="10" />
            </label>
          </div>
          <label>
            Dimension codes (optional)
            <input
              name="dimension_values"
              maxLength={500}
              placeholder="sex=F; service=A|B"
            />
          </label>
          <p className="footnote">
            For ratio and percentage indicators, enter both components. Results
            pool approved components before rounding. Dimension codes must
            belong to the indicator&apos;s approved disaggregation scheme.
          </p>
        </>
      )}
      {mode === "submit" && (
        <>
          <p>
            Submit this draft to one independent reviewer. The submitted
            revision will be locked for review.
          </p>
          {selection(
            "workflow_version",
            "Review template",
            resources["workflow-templates"] || [],
            "revision_id",
          )}
        </>
      )}
      {mode === "calculate" && (
        <>
          <p>
            Calculate a provisional result from approved observations within an
            open period.
          </p>
          {selection(
            "indicator_id",
            "Indicator",
            (resources["indicator-instances"] || []).filter(
              (r) => r.lifecycle_state === "Active",
            ),
          )}
          {selection(
            "period_id",
            "Reporting period",
            (resources["periods"] || []).filter(
              (r) => r.lifecycle_state === "Open",
            ),
          )}
          <p className="footnote">
            Coverage follows the approved collection plan when available. The
            result will be clearly marked provisional.
          </p>
        </>
      )}
      {mode === "report" && (
        <>
          {selection(
            "template_version",
            "Approved report template",
            (resources["report-templates"] || []).filter((r) =>
              ["Approved", "Active"].includes(r.lifecycle_state),
            ),
            "revision_id",
          )}
          <label>
            Locked snapshot
            <select
              name="snapshot_id"
              aria-label="Locked snapshot"
              required
              value={reportSnapshot}
              onChange={(event) => setReportSnapshot(event.target.value)}
            >
              <option value="" disabled>
                Choose locked snapshot
              </option>
              {(resources.snapshots || [])
                .filter((r) => r.lifecycle_state === "Locked")
                .map((r) => (
                  <option key={r.object_id} value={r.object_id}>
                    Snapshot {r.object_id.slice(0, 8)} · {r.data.locked_at}
                  </option>
                ))}
            </select>
          </label>
          <label>
            Section heading
            <input name="heading" maxLength={200} required />
          </label>
          <label>
            Narrative
            <textarea name="narrative" maxLength={20000} required />
          </label>
          <label>
            Result to reference
            <select
              name="result_revision"
              aria-label="Result to reference"
              required
            >
              <option value="">Choose an official snapshot result</option>
              {(resources["calculated-results"] || [])
                .filter(
                  (r) =>
                    r.data.mode === "OFFICIAL" &&
                    (resources.snapshots || [])
                      .find((s) => s.object_id === reportSnapshot)
                      ?.data.result_versions?.includes(r.revision_id),
                )
                .map((r) => (
                  <option key={r.object_id} value={r.revision_id}>
                    {label(r)} · {r.data.mode}
                  </option>
                ))}
            </select>
          </label>
          <p className="footnote">
            The draft binds only to the selected locked snapshot. Independent
            approval freezes its exact template, result and evidence revisions.
            Write numeric claims as binding placeholders such as {"{{RESULT}}"};
            unbound numbers block submission.
          </p>
        </>
      )}
      {mode === "disclosure-request" && (
        <>
          <p>
            Request independent review for this exact approved report revision.
            This release supports authenticated workspace recipients only—never
            anonymous public links.
          </p>
          <label>
            Publication recipient
            <select
              name="recipient_id"
              aria-label="Publication recipient"
              required
              defaultValue=""
            >
              <option value="" disabled>
                Choose an active member
              </option>
              {(resources["publication-recipients"] || []).map((item: any) => (
                <option key={item.membership_id} value={item.membership_id}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Purpose
            <select name="purpose" aria-label="Publication purpose" required>
              <option value="PARTNER_REPORTING">Partner reporting</option>
              <option value="FUNDER_REPORTING">Funder reporting</option>
              <option value="INTERNAL_OVERSIGHT">Internal oversight</option>
            </select>
          </label>
          <label>
            Publication expiry (UTC)
            <input
              type="datetime-local"
              name="expires_at"
              required
              defaultValue={new Date(Date.now() + 7 * 86400000)
                .toISOString()
                .slice(0, 16)}
            />
          </label>
          <label className="check-row">
            <input type="checkbox" name="allow_download" defaultChecked />
            Permit the selected recipient to download the bound-values CSV
          </label>
          {selection(
            "workflow_version",
            "Disclosure review template",
            resources["workflow-templates"] || [],
            "revision_id",
          )}
          <p className="footnote">
            The recipient, purpose, expiry and download right are frozen in the
            reviewed disclosure. Broader access requires a new decision.
          </p>
        </>
      )}
      {mode === "publish-report" && (
        <>
          <p>
            Publish only an independently approved disclosure that names this
            exact report revision. Recipient eligibility and expiry are checked
            again now.
          </p>
          <label>
            Approved disclosure
            <select
              name="disclosure_id"
              aria-label="Approved disclosure"
              required
              defaultValue=""
            >
              <option value="" disabled>
                Choose an approved disclosure
              </option>
              {(resources.disclosures || [])
                .filter(
                  (item) =>
                    item.lifecycle_state === "Approved" &&
                    item.data.artifact_version === row?.revision_id,
                )
                .map((item) => (
                  <option key={item.object_id} value={item.object_id}>
                    {item.data.purpose.replaceAll("_", " ").toLowerCase()} ·
                    expires{" "}
                    {new Date(item.data.expires_at).toLocaleDateString()}
                  </option>
                ))}
            </select>
          </label>
          <p className="footnote">
            Publishing creates immutable HTML and CSV artifacts. Only named,
            currently active recipients can open them; each access is recorded.
          </p>
        </>
      )}
      {mode === "withdraw-report" && (
        <>
          <p>
            Withdraw every active controlled publication of this exact report
            revision. Stored artifacts and prior access records remain for
            audit.
          </p>
          <label>
            Withdrawal reason
            <textarea name="reason" maxLength={2000} required />
          </label>
        </>
      )}
      <div className="dialog-actions">
        <button className="primary" disabled={busy}>
          {busy
            ? "Saving…"
            : mode === "calculate"
              ? "Calculate"
              : mode === "submit"
                ? "Submit for review"
                : mode === "disclosure-request"
                  ? "Request disclosure review"
                  : mode === "publish-report"
                    ? "Publish controlled artifact"
                    : mode === "withdraw-report"
                      ? "Withdraw controlled publications"
                      : "Save draft"}
        </button>
      </div>
    </form>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
