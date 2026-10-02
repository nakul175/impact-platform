import { useRef, useState, type FormEvent } from "react";

type Requester = (path: string, options?: RequestInit) => Promise<any>;

// The one place a one-time password is shown (v0.26a): the live response of the operation that
// created or reissued it. It is never stored by the platform and a retry never returns it.
export function OneTimeCredential({
  account,
  email,
  done,
}: {
  account: any;
  email: string;
  done: () => void;
}) {
  const [copied, setCopied] = useState("");
  async function copy(value: string, what: string) {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(what + " copied.");
    } catch {
      setCopied("Copy it by selecting the text.");
    }
  }
  if (!account.temporary_password)
    return (
      <section className="panel" aria-label="Sign-in account">
        <h2>Sign-in account for {account.email_mask}</h2>
        <p role="status">
          {account.provider_created
            ? "This sign-in was already created; its one-time password was shown once and cannot be shown again. Issue a new one from the list of sign-in accounts if it was lost."
            : "This person already had a sign-in. They keep using their own password; nothing was changed."}
        </p>
        <button className="secondary" onClick={done}>
          Close
        </button>
      </section>
    );
  return (
    <section
      className="panel one-time-credential"
      aria-label="One-time password"
    >
      <h2>Pass these on to {email}</h2>
      <p className="admin-warning">
        This one-time password is shown only now. The platform does not keep it.
        Give it to the person yourself, by a channel you trust (in person or by
        phone), not in the same message as their e-mail address.
      </p>
      <dl className="fields">
        <div className="admin-detail-row">
          <dt>Sign in at</dt>
          <dd>
            <code>{account.sign_in_url}</code>
          </dd>
        </div>
        <div className="admin-detail-row">
          <dt>User name</dt>
          <dd>
            <code>{email}</code>
          </dd>
        </div>
      </dl>
      <label>
        One-time password
        <input
          readOnly
          aria-label="One-time password"
          value={account.temporary_password}
          onFocus={(e) => e.target.select()}
        />
      </label>
      <div className="toolbar">
        <button
          className="secondary"
          onClick={() => copy(account.temporary_password, "Password")}
        >
          Copy password
        </button>
        <button
          className="secondary"
          onClick={() => copy(account.sign_in_url, "Address")}
        >
          Copy sign-in address
        </button>
      </div>
      {copied && <p role="status">{copied}</p>}
      <p>
        At their first sign-in they choose their own password and set up an
        authenticator app (for example Google or Microsoft Authenticator). Until
        then you can issue a new one-time password if this one is lost; after
        that, only they can sign in with it.
      </p>
      <button className="primary" onClick={done}>
        I have noted it — hide the password
      </button>
    </section>
  );
}

export function SignInForm({
  request,
  explain,
  tenantId = null,
  nominationId = null,
  email = "",
  intro,
  created,
  cancel,
}: {
  request: Requester;
  explain: (e: unknown) => string;
  tenantId?: string | null;
  nominationId?: string | null;
  email?: string;
  intro: string;
  created: (account: any, email: string) => void;
  cancel: () => void;
}) {
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const retry = useRef({ key: "", operation: "" });
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const data = {
      email: String(form.get("email") || "").trim(),
      first_name: String(form.get("first_name") || "").trim(),
      last_name: String(form.get("last_name") || "").trim(),
      nomination_id: nominationId,
      tenant_id: tenantId,
      reason: String(form.get("reason") || ""),
    };
    const key = JSON.stringify(data);
    if (retry.current.key !== key)
      retry.current = { key, operation: crypto.randomUUID() };
    try {
      const account = await request("/v1/platform/accounts", {
        method: "POST",
        body: JSON.stringify({ operation_id: retry.current.operation, data }),
      });
      created(account, data.email);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit} aria-label="Create a sign-in">
      <p>{intro}</p>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      <label>
        E-mail address
        <input
          name="email"
          type="email"
          required
          maxLength={254}
          defaultValue={email}
          autoComplete="off"
        />
      </label>
      <label>
        First name
        <input name="first_name" required maxLength={80} autoComplete="off" />
      </label>
      <label>
        Last name
        <input name="last_name" required maxLength={80} autoComplete="off" />
      </label>
      <label>
        Reason
        <textarea
          name="reason"
          required
          maxLength={1000}
          placeholder="Why this person needs a sign-in"
        />
      </label>
      <div className="toolbar">
        <button type="submit" className="primary" disabled={busy}>
          {busy ? "Creating…" : "Create sign-in"}
        </button>
        <button
          type="button"
          className="secondary"
          disabled={busy}
          onClick={cancel}
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
