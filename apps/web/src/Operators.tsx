import { useEffect, useRef, useState, type FormEvent } from "react";
import { OneTimeCredential, SignInForm } from "./Accounts";

type Props = {
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  changed?: () => void;
};
const inDays = (days: number) =>
  new Date(Date.now() + days * 86400000).toISOString().slice(0, 10);

// Operators panel of the tenant-lifecycle console (v0.26a): a platform operator nominates a person
// by e-mail for the operator role and can create that person's sign-in; the person accepts with
// their own sign-in. Nobody accepts for someone else and nobody nominates themselves.
export function Operators({ request, explain, changed }: Props) {
  const [directory, setDirectory] = useState<any>(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [mode, setMode] = useState<any>(null),
    [credential, setCredential] = useState<any>(null);
  const retry = useRef({ key: "", operation: "" });
  async function load(signal?: AbortSignal) {
    try {
      const result = await request("/v1/platform/operators", { signal });
      if (!signal?.aborted) {
        setDirectory(result);
        setError("");
      }
    } catch (e) {
      if (!signal?.aborted) setError(explain(e));
    }
  }
  useEffect(() => {
    const c = new AbortController();
    load(c.signal);
    return () => c.abort();
  }, []);
  function operation(key: string) {
    if (retry.current.key !== key)
      retry.current = { key, operation: crypto.randomUUID() };
    return retry.current.operation;
  }
  async function post(path: string, body: any, success: string) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const result = await request(path, {
        method: "POST",
        body: JSON.stringify({
          ...body,
          operation_id: operation(JSON.stringify([path, body])),
        }),
      });
      retry.current = { key: "", operation: "" };
      setMode(null);
      setNotice(success);
      await load();
      changed?.();
      return result;
    } catch (e) {
      setError(explain(e));
      return null;
    } finally {
      setBusy(false);
    }
  }
  async function nominate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") || "").trim();
    const result = await post(
      "/v1/platform/operator-nominations",
      {
        data: {
          email,
          operator_expires_at: new Date(
            String(form.get("expires")) + "T23:59:59Z",
          ).toISOString(),
          reason: String(form.get("reason") || ""),
        },
      },
      "Nomination recorded. The person must sign in with this address and accept it themselves.",
    );
    if (result && directory?.accounts_enabled)
      setMode({ kind: "signin", nomination: result, email });
  }
  async function decide(nomination: any, action: string, reason: string) {
    await post(
      "/v1/platform/operator-nominations/" +
        nomination.nomination_id +
        "/actions/" +
        action,
      { expected_revision: nomination.revision_id, data: { reason } },
      {
        accept: "You are now a platform operator.",
        decline: "Nomination declined.",
        cancel: "Nomination cancelled.",
      }[action] || "Saved.",
    );
  }
  // Operator lifecycle (v0.27): another active operator renews before expiry or deactivates, with a
  // reason and a sign-in from the last five minutes; never oneself.
  async function renew(event: FormEvent<HTMLFormElement>, operator: any) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await post(
      "/v1/platform/operators/" + operator.identity_id + "/actions/renew",
      {
        expected_revision: operator.revision_id,
        data: {
          expires_at: new Date(
            String(form.get("expires")) + "T23:59:59Z",
          ).toISOString(),
          reason: String(form.get("reason") || ""),
        },
      },
      "Operator role renewed.",
    );
  }
  async function deactivate(event: FormEvent<HTMLFormElement>, operator: any) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await post(
      "/v1/platform/operators/" + operator.identity_id + "/actions/deactivate",
      {
        expected_revision: operator.revision_id,
        data: { reason: String(form.get("reason") || "") },
      },
      "Operator deactivated. Their control-plane authority ended at once.",
    );
  }
  async function reissue(event: FormEvent<HTMLFormElement>, account: any) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") || "").trim();
    const result = await post(
      "/v1/platform/accounts/" + account.account_id + "/actions/reissue",
      {
        expected_revision: account.revision_id,
        data: { email, reason: String(form.get("reason") || "") },
      },
      "A new one-time password was issued.",
    );
    if (result) setCredential({ account: result, email });
  }
  if (credential)
    return (
      <OneTimeCredential
        account={credential.account}
        email={credential.email}
        done={() => setCredential(null)}
      />
    );
  if (!directory)
    return error ? (
      <div className="error" role="alert">
        {error}
      </div>
    ) : (
      <p role="status">Loading operators…</p>
    );
  const mine = directory.nominations.filter(
    (n: any) => !directory.operator || n.nominee_identity_id === null,
  );
  return (
    <section className="panel" aria-label="Operators">
      <h2>Platform operators</h2>
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
      {!directory.operator && (
        <>
          {!mine.filter((n: any) => n.state === "Nominated").length && (
            <p>No operator nomination is waiting for you.</p>
          )}
          {mine
            .filter((n: any) => n.state === "Nominated")
            .map((n: any) => (
              <article className="panel" key={n.nomination_id}>
                <h3>You are nominated as a platform operator</h3>
                <p>
                  {n.nominator_name} nominated you until{" "}
                  {new Date(n.operator_expires_at).toLocaleDateString()}.
                  Reason: {n.reason}
                </p>
                <p>
                  Operators review and activate organisations; they never see
                  programme data. Accepting needs a sign-in from the last five
                  minutes with your authenticator app.
                </p>
                <div className="toolbar">
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() =>
                      decide(n, "accept", "I accept the operator role")
                    }
                  >
                    Accept operator role
                  </button>
                  <button
                    className="secondary"
                    disabled={busy}
                    onClick={() => decide(n, "decline", "Declined")}
                  >
                    Decline
                  </button>
                </div>
              </article>
            ))}
        </>
      )}
      {directory.operator && (
        <>
          <p>
            Tenant activation needs an operator who is a different person from
            the operator who requested the organisation and from its owner. Add
            a second operator here: nominate them, create their sign-in, and
            they accept it themselves.
          </p>
          <div className="toolbar">
            <button
              className="primary"
              onClick={() => setMode({ kind: "nominate" })}
            >
              Nominate an operator
            </button>
            {directory.accounts_enabled && (
              <button
                className="secondary"
                onClick={() => setMode({ kind: "signin" })}
              >
                Create a sign-in for someone
              </button>
            )}
            <button
              className="secondary"
              disabled={busy}
              onClick={() => load()}
            >
              Refresh operators
            </button>
          </div>
          {mode?.kind === "nominate" && (
            <form
              onSubmit={nominate}
              aria-label="Nominate an operator"
              className="panel"
            >
              <label>
                Their e-mail address
                <input
                  name="email"
                  type="email"
                  required
                  maxLength={254}
                  autoComplete="off"
                />
              </label>
              <label>
                Operator role until
                <input
                  name="expires"
                  type="date"
                  required
                  min={inDays(1)}
                  max={inDays(365)}
                  defaultValue={inDays(180)}
                />
              </label>
              <label>
                Reason
                <textarea
                  name="reason"
                  required
                  maxLength={1000}
                  defaultValue="Second platform operator for independent reviews and activation"
                />
              </label>
              <div className="toolbar">
                <button type="submit" className="primary" disabled={busy}>
                  {busy ? "Saving…" : "Nominate"}
                </button>
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setMode(null)}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
          {mode?.kind === "signin" && (
            <section className="panel">
              <SignInForm
                request={request}
                explain={explain}
                nominationId={mode.nomination?.nomination_id || null}
                email={mode.email || ""}
                intro={
                  mode.nomination
                    ? "Create their sign-in now. You will see a one-time password once; hand it over yourself. They choose their own password and set up an authenticator app at first sign-in."
                    : "Create a sign-in for a person who will own an organisation, be its second administrator or join as a member. It carries no authority by itself."
                }
                created={(account, email) => {
                  setMode(null);
                  setCredential({ account, email });
                  load();
                }}
                cancel={() => setMode(null)}
              />
            </section>
          )}
          <h3>Operators</h3>
          <p>
            An operator role expires. Another operator renews it before then or
            deactivates it; nobody renews or deactivates themselves, and the
            last active operator cannot be deactivated.
          </p>
          <ul>
            {directory.operators.map((o: any) => (
              <li key={o.identity_id}>
                <strong>{o.display_name}</strong> {o.email_mask || ""} ·{" "}
                {o.state.toLowerCase()}
                {o.identity_id === directory.identity_id ? " (you)" : ""}{" "}
                {o.state === "Deactivated" ? "since" : "until"}{" "}
                {new Date(
                  o.state === "Deactivated" ? o.updated_at : o.expires_at,
                ).toLocaleDateString()}
                {o.active && o.identity_id !== directory.identity_id && (
                  <span className="toolbar">
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() => setMode({ kind: "renew", operator: o })}
                    >
                      Renew operator role
                    </button>
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() =>
                        setMode({ kind: "deactivate", operator: o })
                      }
                    >
                      Deactivate
                    </button>
                  </span>
                )}
                {mode?.kind === "renew" &&
                  mode.operator.identity_id === o.identity_id && (
                    <form
                      onSubmit={(e) => renew(e, o)}
                      aria-label="Renew operator role"
                      className="panel"
                    >
                      <label>
                        Operator role until
                        <input
                          name="expires"
                          type="date"
                          required
                          min={inDays(1)}
                          max={inDays(365)}
                          defaultValue={inDays(180)}
                        />
                      </label>
                      <label>
                        Reason
                        <textarea name="reason" required maxLength={1000} />
                      </label>
                      <div className="toolbar">
                        <button
                          type="submit"
                          className="primary"
                          disabled={busy}
                        >
                          {busy ? "Saving…" : "Renew"}
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => setMode(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}
                {mode?.kind === "deactivate" &&
                  mode.operator.identity_id === o.identity_id && (
                    <form
                      onSubmit={(e) => deactivate(e, o)}
                      aria-label="Deactivate operator"
                      className="panel"
                    >
                      <p>
                        Their authority to review, activate and administer
                        organisations ends at once. Pending nominations they
                        made can no longer be accepted.
                      </p>
                      <label>
                        Reason
                        <textarea name="reason" required maxLength={1000} />
                      </label>
                      <div className="toolbar">
                        <button
                          type="submit"
                          className="primary"
                          disabled={busy}
                        >
                          {busy ? "Saving…" : "Deactivate operator"}
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => setMode(null)}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}
              </li>
            ))}
          </ul>
          {directory.changes.length > 0 && (
            <>
              <h3>Operator changes</h3>
              <ul>
                {directory.changes.map((g: any) => (
                  <li key={g.change_id}>
                    {new Date(g.created_at).toLocaleDateString()} ·{" "}
                    {g.action === "renew" ? "renewed" : "deactivated"}{" "}
                    <strong>
                      {directory.operators.find(
                        (o: any) => o.identity_id === g.operator_identity_id,
                      )?.display_name || "an operator"}
                    </strong>{" "}
                    by {g.actor_name}
                    {g.action === "renew" &&
                      " until " + new Date(g.expires_at).toLocaleDateString()}
                    . Reason: {g.reason}
                  </li>
                ))}
              </ul>
            </>
          )}
          <h3>Nominations</h3>
          {!directory.nominations.length && <p>No nominations yet.</p>}
          <ul>
            {directory.nominations.map((n: any) => (
              <li key={n.nomination_id}>
                <strong>{n.email_mask}</strong> · {n.state} · by{" "}
                {n.nominator_name}
                {n.account_created_by_nominator &&
                  " · sign-in created by the nominating operator"}
                {n.state === "Nominated" && (
                  <span className="toolbar">
                    {directory.accounts_enabled && (
                      <button
                        className="secondary"
                        onClick={() =>
                          setMode({ kind: "signin", nomination: n, email: "" })
                        }
                      >
                        Create their sign-in
                      </button>
                    )}
                    <button
                      className="secondary"
                      disabled={busy}
                      onClick={() =>
                        decide(n, "cancel", "Cancelled by an operator")
                      }
                    >
                      Cancel nomination
                    </button>
                  </span>
                )}
              </li>
            ))}
          </ul>
          <h3>People with a sign-in</h3>
          <p>
            The identity reference identifies a person when you request an
            organisation for them or name them as recovery contact or second
            administrator.
          </p>
          <ul>
            {directory.identities.map((p: any) => (
              <li key={p.identity_id}>
                <strong>{p.display_name}</strong> {p.email_mask || ""}
                {p.operator ? " · operator" : ""}
                {!p.signed_in ? " · has not signed in yet" : ""}
                <br />
                <code>{p.identity_id}</code>
              </li>
            ))}
          </ul>
          <h3>Sign-in accounts created here</h3>
          {!directory.accounts.length && <p>None yet.</p>}
          <ul>
            {directory.accounts.map((a: any) => (
              <li key={a.account_id}>
                <strong>{a.email_mask}</strong> · one-time passwords issued:{" "}
                {a.credentials_issued}
                {a.provider_created && (
                  <button
                    className="text"
                    onClick={() => setMode({ kind: "reissue", account: a })}
                  >
                    Issue a new one-time password
                  </button>
                )}
                {mode?.kind === "reissue" &&
                  mode.account.account_id === a.account_id && (
                    <form
                      onSubmit={(e) => reissue(e, a)}
                      aria-label="Issue a new one-time password"
                    >
                      <p>
                        Only possible while the person has not yet chosen their
                        own password. Type their e-mail address again.
                      </p>
                      <label>
                        Their e-mail address
                        <input name="email" type="email" required />
                      </label>
                      <label>
                        Reason
                        <textarea name="reason" required maxLength={1000} />
                      </label>
                      <button className="primary" disabled={busy}>
                        Issue
                      </button>
                    </form>
                  )}
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
