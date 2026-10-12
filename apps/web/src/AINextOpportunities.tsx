import { useCallback, useEffect, useRef, useState } from "react";

type Request = <T>(path: string, options?: RequestInit) => Promise<T>;
type Suggestion = {
  suggestion_id: string;
  title: string;
  affected_area: string;
  explanation: string;
};
type Receipt = {
  cycle_state: "Diagnose";
  diagnosis_state: "Draft";
  diagnosis_id: string;
};

export function AINextOpportunitiesPanel(props: {
  base: string;
  capabilities: string[];
  request: Request;
  explain: (error: unknown) => string;
}) {
  const [items, setItems] = useState<Suggestion[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const statusRef = useRef<HTMLParagraphElement>(null);
  const canRead = props.capabilities.includes("ai.diagnosis.read");
  const canManage = props.capabilities.includes("ai.diagnosis.manage");
  const load = useCallback(async () => {
    if (!canRead) return;
    setBusy(true);
    try {
      const result = await props.request<{ items: Suggestion[] }>(
        `${props.base}/ai-enablement/next-opportunities`,
      );
      setItems(result.items);
      setError("");
    } catch (reason) {
      setError(props.explain(reason));
    } finally {
      setBusy(false);
    }
  }, [canRead, props]);
  useEffect(() => void load(), [load]);
  if (!canRead) return null;
  async function takeUp(item: Suggestion) {
    const operationId = crypto.randomUUID();
    setBusy(true);
    try {
      const receipt = await props.request<Receipt>(
        `${props.base}/ai-enablement/next-opportunities/${item.suggestion_id}/actions/take-up`,
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ operation_id: operationId }),
        },
      );
      if (
        receipt.cycle_state !== "Diagnose" ||
        receipt.diagnosis_state !== "Draft"
      )
        throw new Error("Unexpected cycle state");
      setStatus(
        `New Diagnose cycle started. Draft diagnosis ${receipt.diagnosis_id} is ready for review.`,
      );
      setError("");
      await load();
      requestAnimationFrame(() => statusRef.current?.focus());
    } catch (reason) {
      setError(props.explain(reason));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      className="ai-diagnosis"
      aria-labelledby="next-opportunities-title"
      aria-busy={busy}
    >
      <h2 id="next-opportunities-title">Suggested next opportunities</h2>
      <p>
        <strong>Improve</strong>
      </p>
      <p>
        Starting one creates a new Diagnose cycle and a blank draft diagnosis
        for review. It does not assess, approve, procure, pilot, or deploy
        anything.
      </p>
      {busy && <p role="status">Loading next opportunities…</p>}
      {error && <p role="alert">{error}</p>}
      {status && (
        <p ref={statusRef} tabIndex={-1} role="status" aria-live="polite">
          {status}
        </p>
      )}
      {!busy && items.length === 0 && (
        <p>
          No next opportunities are available from a completed quarterly value
          review.
        </p>
      )}
      <ul>
        {items.map((item) => (
          <li key={item.suggestion_id}>
            <article>
              <h3>{item.title}</h3>
              <p>Affected area: {item.affected_area}</p>
              <p>{item.explanation}</p>
              <button
                type="button"
                disabled={busy || !canManage}
                aria-label={`Start Diagnose cycle for ${item.title}`}
                onClick={() => void takeUp(item)}
              >
                Start Diagnose cycle
              </button>
            </article>
          </li>
        ))}
      </ul>
    </section>
  );
}
