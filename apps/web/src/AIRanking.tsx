import React, { useEffect, useRef, useState } from "react";
import type { Profile } from "./AIEnablement";

// US-MP-03: opportunities ranked by impact, effort, cost and readiness with the organisation's own
// weights. The server computes every score and total (exact decimal strings); this panel only shows
// them. Hidden controls are never security: changing weights needs ai.enablement.manage on the server.
type Criterion = "impact" | "effort" | "cost" | "readiness";
export type RankingWeights = Record<Criterion, number>;
type WeightsView = {
  source: "DEFAULT" | "SAVED";
  revision_id: string | null;
  weights: RankingWeights;
  saved_at: string | null;
  saved_by: string | null;
};
type RankedOpportunity = {
  rank: number;
  use_case_id: string;
  scores: RankingWeights;
  weighted_total: string;
  readiness_gaps: string[];
};
type Ranking = {
  content_version: string;
  score_version: string;
  score_status: string;
  weights: RankingWeights;
  weights_source: "DEFAULT" | "SAVED";
  weights_revision_id: string | null;
  items: RankedOpportunity[];
  unranked: { use_case_id: string; missing_scores: string[] }[];
};
type Requester = (path: string, options?: RequestInit) => Promise<any>;

const CRITERIA: { key: Criterion; label: string; direction: string }[] = [
  { key: "impact", label: "Impact", direction: "higher is better" },
  { key: "effort", label: "Effort", direction: "lower is better" },
  { key: "cost", label: "Cost", direction: "lower is better" },
  { key: "readiness", label: "Readiness", direction: "higher is better" },
];
const WHOLE = /^(0|[1-9][0-9]?|100)$/;

function when(value: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}
const weightsText = (weights: RankingWeights) =>
  CRITERIA.map((item) => item.label + " " + weights[item.key]).join(", ");

export function AIOpportunityRanking({
  base,
  profile,
  titles,
  canManage,
  request,
  explain,
}: {
  base: string;
  profile: Profile;
  titles: Record<string, string>;
  canManage: boolean;
  request: Requester;
  explain: (e: unknown) => string;
}) {
  const [weights, setWeights] = useState<WeightsView | null>(null);
  const [loadError, setLoadError] = useState("");
  const [ranking, setRanking] = useState<Ranking | null>(null);
  const [rankError, setRankError] = useState("");
  const [rankingBusy, setRankingBusy] = useState(false);
  // The outcome of the last weights change: saved (status) or refused as stale (alert). Kept here
  // because the editor is re-created from the reloaded weights.
  const [savedNotice, setSavedNotice] = useState("");
  const [staleNotice, setStaleNotice] = useState("");
  const loads = useRef(0);
  const ranks = useRef(0);
  const briefKey = JSON.stringify(profile);
  const briefReady = profile.goal.trim().length > 0;

  function loadWeights() {
    const current = ++loads.current;
    setLoadError("");
    return request(base + "ai-enablement/ranking-weights")
      .then((result: WeightsView) => {
        if (current === loads.current) setWeights(result);
      })
      .catch((e) => {
        if (current === loads.current) setLoadError(explain(e));
      });
  }
  async function rank() {
    if (!briefReady) return;
    const current = ++ranks.current;
    setRankError("");
    setRankingBusy(true);
    try {
      const result = await request(base + "ai-enablement/ranking", {
        method: "POST",
        body: JSON.stringify({ profile }),
      });
      if (current !== ranks.current) return;
      setRanking(result);
      // The ranking used weights saved since this panel loaded them: show the weights in force.
      if (result.weights_revision_id !== (weights?.revision_id ?? null))
        void loadWeights();
    } catch (e) {
      if (current === ranks.current) setRankError(explain(e));
    } finally {
      if (current === ranks.current) setRankingBusy(false);
    }
  }
  useEffect(() => {
    setWeights(null);
    void loadWeights();
    return () => {
      loads.current += 1;
    };
  }, [base]);
  // A ranking belongs to the brief it was made for: any change to the brief clears it.
  useEffect(() => {
    ranks.current += 1;
    setRanking(null);
    setRankError("");
    setRankingBusy(false);
  }, [base, briefKey]);

  return (
    <section
      className="ai-ranking"
      aria-labelledby="ai-ranking-heading"
      data-weights-revision={weights?.revision_id ?? ""}
    >
      <h3 id="ai-ranking-heading">Rank opportunities</h3>
      <p className="muted">
        Each opportunity for your brief gets four scores from 1 to 5. Impact,
        effort and cost are editorial scores; readiness comes from the capacity
        gaps in your brief. Effort and cost count in reverse: less is better.
        Your organisation&apos;s weights decide how much each score counts.
      </p>
      {loadError && (
        <div className="error" role="alert">
          The ranking weights could not be loaded. {loadError}
        </div>
      )}
      {!weights && !loadError && <p role="status">Loading ranking weights…</p>}
      {weights && (
        <p className="ai-ranking-weights">
          {weights.source === "DEFAULT"
            ? "Weights in force: the defaults (" +
              weightsText(weights.weights) +
              "). Your organisation has not saved its own weights."
            : "Weights in force: " +
              weightsText(weights.weights) +
              (weights.saved_at ? ", saved " + when(weights.saved_at) : "") +
              "."}
        </p>
      )}
      {staleNotice && (
        <div className="error" role="alert">
          {staleNotice}
        </div>
      )}
      {savedNotice && <p role="status">{savedNotice}</p>}
      {weights && canManage && (
        <WeightsEditor
          key={weights.revision_id ?? "default"}
          base={base}
          current={weights}
          request={request}
          explain={explain}
          editing={() => {
            setSavedNotice("");
            setStaleNotice("");
          }}
          saved={() => {
            setStaleNotice("");
            setSavedNotice("Ranking weights saved.");
            void loadWeights();
            if (ranking) void rank();
          }}
          stale={(message) => {
            // Saved against weights that changed meanwhile: show the refusal and the weights now
            // in force; nothing was overwritten.
            setSavedNotice("");
            setStaleNotice(message);
            void loadWeights();
          }}
        />
      )}
      <div className="ai-actions">
        <button
          type="button"
          className="primary"
          disabled={!briefReady || rankingBusy}
          onClick={() => void rank()}
        >
          Rank opportunities
        </button>
      </div>
      {!briefReady && (
        <p className="muted">
          Describe what you would like AI to help with in your brief to rank
          opportunities.
        </p>
      )}
      {rankingBusy && <p role="status">Ranking opportunities…</p>}
      {rankError && (
        <div className="error" role="alert">
          {rankError}
        </div>
      )}
      {ranking && (
        <div
          className="ai-ranking-result"
          data-ranking-revision={ranking.weights_revision_id ?? "DEFAULT"}
        >
          <p className="muted">
            {ranking.weights_source === "DEFAULT"
              ? "Ranked with the default weights (" +
                weightsText(ranking.weights) +
                ")."
              : "Ranked with your organisation's weights (" +
                weightsText(ranking.weights) +
                "), revision " +
                ranking.weights_revision_id +
                "."}{" "}
            Editorial scores {ranking.score_version}
            {ranking.score_status.startsWith("EDITORIAL_DRAFT")
              ? " are an editorial draft pending advisor review."
              : "."}
          </p>
          {ranking.items.length > 0 ? (
            <div
              className="table-scroll"
              role="region"
              aria-label="Ranked opportunities table"
              tabIndex={0}
            >
              <table className="ai-ranking-table">
                <caption>
                  Ranked opportunities, highest weighted total first
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Rank</th>
                    <th scope="col">Opportunity</th>
                    {CRITERIA.map((item) => (
                      <th scope="col" key={item.key}>
                        {item.label} ({item.direction})
                      </th>
                    ))}
                    <th scope="col">Weighted total (of 100)</th>
                  </tr>
                </thead>
                <tbody>
                  {ranking.items.map((item) => (
                    <tr key={item.use_case_id} data-use-case={item.use_case_id}>
                      <td>{item.rank}</td>
                      <th scope="row">
                        {titles[item.use_case_id] || item.use_case_id}
                      </th>
                      {CRITERIA.map((criterion) => (
                        <td key={criterion.key}>
                          {item.scores[criterion.key]} of 5
                        </td>
                      ))}
                      <td>{item.weighted_total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No opportunity for this brief has all four scores yet.</p>
          )}
          <section
            className="ai-ranking-unranked"
            aria-labelledby="ai-ranking-unranked"
          >
            <h4 id="ai-ranking-unranked">Not ranked: scores incomplete</h4>
            {ranking.unranked.length ? (
              <ul>
                {ranking.unranked.map((item) => (
                  <li key={item.use_case_id} data-use-case={item.use_case_id}>
                    {titles[item.use_case_id] || item.use_case_id}: missing{" "}
                    {item.missing_scores.join(", ")}{" "}
                    {item.missing_scores.length === 1 ? "score" : "scores"}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">
                None: every opportunity for this brief has all four scores.
              </p>
            )}
          </section>
        </div>
      )}
    </section>
  );
}

function WeightsEditor({
  base,
  current,
  request,
  explain,
  editing,
  saved,
  stale,
}: {
  base: string;
  current: WeightsView;
  request: Requester;
  explain: (e: unknown) => string;
  editing: () => void;
  saved: () => void;
  stale: (message: string) => void;
}) {
  const [values, setValues] = useState<Record<Criterion, string>>({
    impact: String(current.weights.impact),
    effort: String(current.weights.effort),
    cost: String(current.weights.cost),
    readiness: String(current.weights.readiness),
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  // One operation identifier per payload for the life of this editor, so a retry after a lost
  // response repeats the exact command and the server returns its receipt.
  const attempt = useRef<{ payload: string; id: string } | null>(null);
  const whole = CRITERIA.every((item) => WHOLE.test(values[item.key]));
  const total = CRITERIA.reduce(
    (sum, item) =>
      sum + (WHOLE.test(values[item.key]) ? Number(values[item.key]) : 0),
    0,
  );
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    editing();
    if (!whole) {
      setError("Each weight is a whole number from 0 to 100.");
      return;
    }
    if (total !== 100) {
      setError(
        "The four weights must add up to 100; these add up to " + total + ".",
      );
      return;
    }
    const data = Object.fromEntries(
      CRITERIA.map((item) => [item.key, Number(values[item.key])]),
    );
    const payload = JSON.stringify({
      expected_revision: current.revision_id,
      data,
    });
    if (!attempt.current || attempt.current.payload !== payload)
      attempt.current = { payload, id: crypto.randomUUID() };
    setBusy(true);
    setError("");
    try {
      await request(base + "ai-enablement/ranking-weights", {
        method: "PUT",
        body: JSON.stringify({
          operation_id: attempt.current.id,
          expected_revision: current.revision_id,
          data,
        }),
      });
      saved();
    } catch (e) {
      if ((e as { reason?: string }).reason === "AI_RANKING_WEIGHTS_CHANGED")
        stale(explain(e));
      else setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="ai-weights-editor" onSubmit={submit} noValidate>
      <fieldset disabled={busy} aria-describedby="ai-weights-total">
        <legend>Your organisation&apos;s weights</legend>
        <p className="muted">
          Whole numbers from 0 to 100 that add up to 100. Saving is a preference
          for everyone in your organisation, recorded in the audit log; it needs
          no review.
        </p>
        <div className="ai-weights-grid">
          {CRITERIA.map((item) => (
            <label key={item.key}>
              {item.label} weight
              <input
                type="number"
                inputMode="numeric"
                min="0"
                max="100"
                step="1"
                required
                value={values[item.key]}
                aria-invalid={!WHOLE.test(values[item.key]) || total !== 100}
                onChange={(e) => {
                  setValues((previous) => ({
                    ...previous,
                    [item.key]: e.target.value,
                  }));
                  setError("");
                }}
              />
            </label>
          ))}
        </div>
        <p id="ai-weights-total" aria-live="polite">
          Total: {whole ? total : "—"} of 100
          {whole && total !== 100 ? " (must be exactly 100)" : ""}
        </p>
        {error && (
          <div className="error" role="alert">
            {error}
          </div>
        )}
        <button type="submit" className="secondary">
          {busy ? "Saving…" : "Save weights"}
        </button>
      </fieldset>
    </form>
  );
}
