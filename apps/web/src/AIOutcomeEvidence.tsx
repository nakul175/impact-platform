import React, { useEffect, useRef, useState, type FormEvent } from "react";

type Request = (path: string, options?: RequestInit) => Promise<any>;

export function AIOutcomeSharingConsentPanel({
  base,
  request,
  explain,
  capabilities,
}: {
  base: string;
  request: Request;
  explain: (e: unknown) => string;
  capabilities: string[];
}) {
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const retry = useRef("");
  if (!capabilities.includes("ai.enablement.manage")) return null;
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    if (!retry.current) retry.current = crypto.randomUUID();
    try {
      const result = await request(
        base + "/ai-enablement/outcome-sharing-consents",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: retry.current,
            outcome_observation_id: form.get("outcome_id"),
            outcome_observation_revision: form.get("revision_id"),
            decision: form.get("decision"),
            allowed_metrics: form.getAll("metrics"),
            notice_version: form.get("notice_version"),
            reason: form.get("reason"),
          }),
        },
      );
      retry.current = "";
      setNotice(`${result.decision}: consent decision recorded.`);
    } catch (e) {
      setError(explain(e));
    }
  }
  return (
    <section className="panel" aria-labelledby="outcome-sharing-title">
      <h2 id="outcome-sharing-title">Share anonymised outcome evidence</h2>
      <p>
        Choose an exact outcome revision. Only selected measures enter fixed
        cross-organisation cells; cells from fewer than five organisations stay
        hidden.
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
      <form onSubmit={submit}>
        <label>
          Outcome observation ID
          <input name="outcome_id" required />
        </label>
        <label>
          Exact revision ID
          <input name="revision_id" required />
        </label>
        <fieldset>
          <legend>Measures</legend>
          {["time", "cost", "quality", "reach", "usage"].map((m) => (
            <label key={m}>
              <input type="checkbox" name="metrics" value={m} /> {m}
            </label>
          ))}
        </fieldset>
        <label>
          Decision
          <select name="decision">
            <option value="GRANTED">Grant</option>
            <option value="WITHDRAWN">Withdraw</option>
          </select>
        </label>
        <label>
          Notice version
          <input name="notice_version" required />
        </label>
        <label>
          Reason
          <textarea name="reason" required />
        </label>
        <button className="primary" type="submit">
          Record decision
        </button>
      </form>
    </section>
  );
}

export function AIOutcomeEvidencePanel({
  request,
  explain,
}: {
  request: Request;
  explain: (e: unknown) => string;
}) {
  const root = "/v1/platform/outcome-evidence-publications";
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function refresh() {
    try {
      setItems((await request(root)).items || []);
    } catch (e) {
      setError(explain(e));
    }
  }
  useEffect(() => {
    refresh();
  }, []);
  async function command(path: string, body: any) {
    setBusy(true);
    setError("");
    try {
      await request(path, { method: "POST", body: JSON.stringify(body) });
      await refresh();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel" aria-labelledby="outcome-evidence-title">
      <h2 id="outcome-evidence-title">Anonymised outcome evidence</h2>
      <p>
        Prepare a fixed snapshot, obtain independent approval, then publish.
        Consent and source revisions are rechecked at each step.
      </p>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      <button
        disabled={busy}
        className="primary"
        onClick={() => command(root, { operation_id: crypto.randomUUID() })}
      >
        Prepare snapshot
      </button>
      {!items.length && <p>No snapshots prepared.</p>}
      {items.map((p) => (
        <article key={p.publication_id}>
          <h3>{p.state}</h3>
          <p>
            <code>{p.publication_id}</code>
          </p>
          <ul>
            {p.artifact.items.map((c: any) => (
              <li key={`${c.metric}-${c.unit}-${c.period_bucket}`}>
                {c.metric} · {c.period_bucket}:{" "}
                {c.status === "WITHHELD"
                  ? `Withheld (${c.reason})`
                  : `${c.mean_value} ${c.unit} across ${c.organisation_count} organisations`}
              </li>
            ))}
          </ul>
          {p.state !== "PUBLISHED" && (
            <button
              disabled={busy}
              className="secondary"
              onClick={() =>
                command(
                  `${root}/${p.publication_id}/actions/${p.state === "PREPARED" ? "approve" : "publish"}`,
                  {
                    operation_id: crypto.randomUUID(),
                    expected_revision: p.revision_id,
                  },
                )
              }
            >
              {p.state === "PREPARED" ? "Approve independently" : "Publish"}
            </button>
          )}
        </article>
      ))}
    </section>
  );
}
