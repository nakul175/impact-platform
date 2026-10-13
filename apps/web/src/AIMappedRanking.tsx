import React, { useState } from "react";
import type { Profile } from "./AIEnablement";

type Ranking = {
  weights: Record<"impact" | "effort" | "cost" | "readiness", number>;
  weights_source: "DEFAULT" | "SAVED";
  weights_revision_id: string | null;
  score_version: string;
  items: {
    rank: number;
    use_case_id: string;
    weighted_total: string;
    scores: Record<"impact" | "effort" | "cost" | "readiness", number>;
  }[];
  unranked: { use_case_id: string; missing_scores: string[] }[];
};

export function AIMappedRanking(props: {
  base: string;
  diagnosisId: string;
  revisionId: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
}) {
  const [profile, setProfile] = useState<Profile>({
    sector: "GENERAL",
    team_size: 1,
    goal: "",
    data_readiness: "NONE",
    ai_experience: "NONE",
    sensitive_data: false,
  });
  const [ranking, setRanking] = useState<Ranking | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function rank() {
    setBusy(true);
    setError("");
    setRanking(null);
    try {
      setRanking(
        (await props.request(
          `${props.base}ai-enablement/diagnoses/${props.diagnosisId}/opportunity-ranking`,
          {
            method: "POST",
            body: JSON.stringify({ revision_id: props.revisionId, profile }),
          },
        )) as Ranking,
      );
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-labelledby="mapped-ranking-title">
      <h4 id="mapped-ranking-title">Rank mapped opportunities</h4>
      <p className="muted">
        Readiness uses this bounded organisation profile. Saved organisation
        weights are applied exactly. Operations Head access remains read-only
        under the recorded owner decision.
      </p>
      <fieldset disabled={busy}>
        <legend>Organisation profile for readiness</legend>
        <label>
          Sector
          <select
            value={profile.sector}
            onChange={(event) =>
              setProfile({ ...profile, sector: event.target.value })
            }
          >
            {[
              "GENERAL",
              "EDUCATION",
              "HEALTH",
              "LIVELIHOODS",
              "ENVIRONMENT",
            ].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <label>
          Team size
          <input
            type="number"
            min={1}
            max={100000}
            value={profile.team_size}
            onChange={(event) =>
              setProfile({ ...profile, team_size: Number(event.target.value) })
            }
          />
        </label>
        <label>
          Goal
          <textarea
            maxLength={1000}
            value={profile.goal}
            onChange={(event) =>
              setProfile({ ...profile, goal: event.target.value })
            }
          />
        </label>
        <label>
          Data readiness
          <select
            value={profile.data_readiness}
            onChange={(event) =>
              setProfile({ ...profile, data_readiness: event.target.value })
            }
          >
            {["NONE", "BASIC", "STRUCTURED"].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <label>
          AI experience
          <select
            value={profile.ai_experience}
            onChange={(event) =>
              setProfile({ ...profile, ai_experience: event.target.value })
            }
          >
            {["NONE", "EXPERIMENTING", "REGULAR"].map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={profile.sensitive_data}
            onChange={(event) =>
              setProfile({ ...profile, sensitive_data: event.target.checked })
            }
          />{" "}
          Sensitive data is involved
        </label>
        <button
          type="button"
          disabled={!profile.goal.trim() || busy}
          onClick={rank}
        >
          {busy ? "Ranking…" : "Rank mapped opportunities"}
        </button>
      </fieldset>
      {error && <p role="alert">{error}</p>}
      {ranking && (
        <div
          className="table-scroll"
          role="region"
          aria-label="Mapped opportunity ranking"
          tabIndex={0}
        >
          <p>
            Weights:{" "}
            {Object.entries(ranking.weights)
              .map(([key, value]) => `${key} ${value}`)
              .join(", ")}{" "}
            ({ranking.weights_source.toLowerCase()}). Scores:{" "}
            {ranking.score_version}.
          </p>
          <table>
            <caption>
              Mapped opportunities, highest weighted total first
            </caption>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Opportunity</th>
                <th>Impact</th>
                <th>Effort</th>
                <th>Cost</th>
                <th>Readiness</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {ranking.items.map((item) => (
                <tr key={item.use_case_id}>
                  <td>{item.rank}</td>
                  <th scope="row">{item.use_case_id}</th>
                  <td>{item.scores.impact}</td>
                  <td>{item.scores.effort}</td>
                  <td>{item.scores.cost}</td>
                  <td>{item.scores.readiness}</td>
                  <td>{item.weighted_total}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!!ranking.unranked.length && (
            <p role="status">
              Not ranked because scores are incomplete:{" "}
              {ranking.unranked.map((item) => item.use_case_id).join(", ")}.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
