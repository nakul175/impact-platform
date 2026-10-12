import React, { useEffect, useState } from "react";
import { AIMappedRanking } from "./AIMappedRanking";
import { AIValueCase } from "./AIValueCase";

type Example = {
  example_id: string;
  organisation: string;
  title: string;
  source_url: string;
  checked_on: string;
  summary: string;
};
type Opportunity = {
  pattern_id: string;
  kind: "AI_ASSISTED" | "TECHNOLOGY" | "PROCESS_FIX";
  title: string;
  description: string;
  match_basis: string[];
  real_world_examples: Example[];
  rationale: {
    plain_language: string;
    diagnosis_input_links: {
      problem_id: string;
      field: "description" | "affected_area";
    }[];
  };
};
type Mapping = {
  diagnosis_id: string;
  diagnosis_revision: string;
  pattern_edition: string;
  mapping_rule_version: string;
  mapping_state: "COMPLETE" | "INCOMPLETE";
  problems: { problem_id: string; opportunities: Opportunity[] }[];
  unmapped_problem_ids: string[];
  disclaimer: string;
};
type Problem = { problem_id: string; description: string };

export function AIOpportunityMap(props: {
  base: string;
  diagnosisId: string;
  revisionId: string;
  problems: Problem[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
}) {
  const [mapping, setMapping] = useState<Mapping | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    setMapping(null);
    setError("");
  }, [props.diagnosisId, props.revisionId]);
  const names = new Map(
    props.problems.map((problem) => [problem.problem_id, problem.description]),
  );
  async function load() {
    setBusy(true);
    setError("");
    try {
      const result = await props.request(
        `${props.base}/ai-enablement/diagnoses/${props.diagnosisId}/opportunity-map?revision_id=${props.revisionId}`,
      );
      setMapping(result as Mapping);
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section
      aria-labelledby="opportunity-map-title"
      className="ai-opportunity-map"
    >
      <h3 id="opportunity-map-title">Problem-to-opportunity map</h3>
      <p>Map priority problems to the current source-backed pattern library.</p>
      <button type="button" disabled={busy} onClick={load}>
        {busy ? "Mapping…" : "Map opportunities"}
      </button>
      {error && <p role="alert">{error}</p>}
      {mapping && (
        <>
          <p>
            <strong>
              {mapping.mapping_state === "COMPLETE"
                ? "Complete mapping"
                : "Incomplete mapping"}
            </strong>{" "}
            · Pattern edition {mapping.pattern_edition}
          </p>
          {mapping.mapping_state === "INCOMPLETE" && (
            <p role="status">
              {mapping.unmapped_problem_ids.length} priority problem(s) have no
              verified library match. This mapping is not accepted as complete.
            </p>
          )}
          <ol>
            {mapping.problems.map((item) => (
              <li key={item.problem_id}>
                <h4 id={`diagnosis-problem-${item.problem_id}`}>
                  {names.get(item.problem_id) || "Priority problem"}
                </h4>
                {!item.opportunities.length ? (
                  <p>No verified pattern-library opportunity.</p>
                ) : (
                  <ul>
                    {item.opportunities.map((opportunity) => (
                      <li key={opportunity.pattern_id}>
                        <strong>{opportunity.title}</strong>{" "}
                        <span>
                          (
                          {opportunity.kind === "PROCESS_FIX"
                            ? "Process fix — no technology purchase required"
                            : opportunity.kind === "AI_ASSISTED"
                              ? "AI assisted"
                              : "Technology"}
                          )
                        </span>
                        <p>{opportunity.description}</p>
                        <p>Matched on: {opportunity.match_basis.join(", ")}</p>
                        <p>
                          <strong>Why recommended:</strong>{" "}
                          {opportunity.rationale.plain_language}{" "}
                          {opportunity.rationale.diagnosis_input_links.map(
                            (link, index) => (
                              <React.Fragment
                                key={`${link.problem_id}-${link.field}`}
                              >
                                {index > 0 ? ", " : ""}
                                <a
                                  href={`#diagnosis-problem-${link.problem_id}`}
                                >
                                  diagnosis {link.field.replace("_", " ")}
                                </a>
                              </React.Fragment>
                            ),
                          )}
                        </p>
                        <ul>
                          {opportunity.real_world_examples.map((example) => (
                            <li key={example.example_id}>
                              <a
                                href={example.source_url}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {example.title}
                              </a>{" "}
                              — {example.organisation}. {example.summary} Source
                              checked {example.checked_on}.
                            </li>
                          ))}
                        </ul>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ol>
          <p className="muted">{mapping.disclaimer}</p>
          {mapping.mapping_state === "COMPLETE" && (
            <>
              <AIMappedRanking
                key={props.revisionId}
                base={props.base}
                diagnosisId={props.diagnosisId}
                revisionId={props.revisionId}
                request={props.request}
                explain={props.explain}
              />
              <AIValueCase
                base={props.base}
                opportunityIds={[
                  ...new Set(
                    mapping.problems.flatMap((problem) =>
                      problem.opportunities.map((item) => item.pattern_id),
                    ),
                  ),
                ]}
                request={props.request}
                explain={props.explain}
              />
            </>
          )}
        </>
      )}
    </section>
  );
}
