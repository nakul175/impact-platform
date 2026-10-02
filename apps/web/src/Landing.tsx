import { useEffect, useState } from "react";

type Props = {
  identity: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  logout: () => void;
  openConsole: () => void;
};

// The start page of a signed-in person who belongs to no workspace yet (v0.26a). It says in plain
// language what happens next, for an operator, a nominated operator, a nominated owner or anyone else.
export function NoWorkspace({
  identity,
  request,
  explain,
  logout,
  openConsole,
}: Props) {
  const [operators, setOperators] = useState<any>(null),
    [tenants, setTenants] = useState<any>(null),
    [error, setError] = useState(""),
    [copied, setCopied] = useState(false);
  useEffect(() => {
    const c = new AbortController();
    Promise.all([
      request("/v1/platform/operators", { signal: c.signal }).catch(() => null),
      request("/v1/platform/tenants", { signal: c.signal }).catch(() => null),
    ])
      .then(([o, t]) => {
        if (c.signal.aborted) return;
        setOperators(o);
        setTenants(t);
      })
      .catch((e) => {
        if (!c.signal.aborted) setError(explain(e));
      });
    return () => c.abort();
  }, []);
  const operator = Boolean(operators?.operator);
  const activeOperators = (operators?.operators || []).filter(
    (o: any) => o.active,
  ).length;
  const nominated = (operators?.nominations || []).filter(
    (n: any) => !operator && n.state === "Nominated",
  );
  const owned = (tenants?.items || []).filter(
    (t: any) => t.owner_identity_id === identity,
  );
  async function copy() {
    try {
      await navigator.clipboard.writeText(identity);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }
  return (
    <main className="join-page">
      <section className="panel" aria-labelledby="no-workspace">
        <h1 id="no-workspace">No active workspace</h1>
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        {!operators && !error && <p role="status">Checking what is next…</p>}
        {nominated.length > 0 && (
          <div className="success" role="status">
            You have been nominated as a platform operator by{" "}
            {nominated[0].nominator_name}. Open the console to accept or decline
            it.
          </div>
        )}
        {owned.some((t: any) => t.state === "Requested") && (
          <div className="success" role="status">
            You have been named owner of{" "}
            {owned.find((t: any) => t.state === "Requested").operating_name}.
            Open the console to review and accept it.
          </div>
        )}
        {operator ? (
          <>
            <p>
              You are a platform operator. No organisation workspace exists for
              you yet. Setting one up takes these steps; the platform asks for a
              different person at some of them on purpose, so that nobody can
              approve their own request.
            </p>
            <ol className="next-steps">
              <li>
                <strong>Add a second operator.</strong> In the console, under
                Platform operators, nominate a colleague by e-mail and create
                their sign-in. Give them the one-time password yourself. They
                sign in, set their own password and authenticator app, and
                accept.{" "}
                {activeOperators >= 2
                  ? "Done: there are " + activeOperators + " active operators."
                  : "Not yet: you are the only active operator."}
              </li>
              <li>
                <strong>Create sign-ins</strong> for the person who will own the
                organisation and for its second administrator (two different
                people). Each signs in once.
              </li>
              <li>
                <strong>Request the organisation</strong> and choose its owner.
                The operator who requests it cannot activate it, and neither can
                its owner.
              </li>
              <li>
                <strong>The owner accepts</strong> and names a recovery contact,
                who confirms; another operator approves the contact and{" "}
                <strong>activates</strong> the organisation.
              </li>
              <li>
                <strong>The owner proposes initial access</strong> with a second
                administrator, who accepts; an operator who is neither of them
                approves. The owner then sets up the standard reference data
                (calendar, review template, report template) under People &
                access.
              </li>
            </ol>
          </>
        ) : (
          <p>
            Your sign-in works, but no organisation has given you access yet. If
            you received an invitation link, open it now. Otherwise give the
            person who manages your organisation your identity reference.
          </p>
        )}
        <p>
          Your identity reference: <code>{identity}</code>{" "}
          <button className="text" onClick={copy}>
            {copied ? "Copied" : "Copy"}
          </button>
        </p>
        <p className="footnote">
          {operator
            ? "Every step above is in the Tenant lifecycle console."
            : "Nominations and ownership requests addressed to you are in the Tenant lifecycle console."}
        </p>
        <div className="toolbar">
          <button className="primary" onClick={openConsole}>
            Tenant lifecycle
          </button>
          <button className="secondary" onClick={logout}>
            Sign out
          </button>
        </div>
      </section>
    </main>
  );
}
