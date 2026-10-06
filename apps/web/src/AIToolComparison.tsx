import React from "react";

export type PublicToolSolution = {
  id: string;
  name: string;
  provider: string;
  category: string;
  use_case_ids: string[];
  description: string;
  deployment: string;
  commercial_model: string;
  nonprofit_offer: string;
  api_available: string;
  source_urls: { label: string; url: string }[];
  verification_notes: string[];
  data_review_questions: string[];
};

export function AIToolSources({ solution }: { solution: PublicToolSolution }) {
  return (
    <ul className="ai-sources">
      {solution.source_urls
        .filter((source) => source.url.startsWith("https://"))
        .map((source) => (
          <li key={source.url}>
            <a href={source.url} target="_blank" rel="noopener noreferrer">
              {source.label} ↗
            </a>
          </li>
        ))}
    </ul>
  );
}

const categoryLabel = (value: string) =>
  value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/^./, (character) => character.toUpperCase());

export function AIToolComparison({
  selected,
  onRemove,
}: {
  selected: PublicToolSolution[];
  onRemove?: (id: string) => void;
}) {
  if (!selected.length) return null;
  return (
    <section
      className="ai-comparison-scroll"
      tabIndex={0}
      aria-label="Tool comparison table"
    >
      <table
        className="ai-comparison"
        style={{ minWidth: 150 + 240 * selected.length }}
      >
        <thead>
          <tr>
            <th scope="col">Compare</th>
            {selected.map((solution) => (
              <th scope="col" key={solution.id}>
                {solution.name}
                {onRemove && (
                  <button
                    className="secondary"
                    type="button"
                    onClick={() => onRemove?.(solution.id)}
                    aria-label={"Remove " + solution.name + " from comparison"}
                  >
                    Remove
                  </button>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {(
            [
              ["Provider", "provider"],
              ["Category", "category"],
              ["Deployment", "deployment"],
              ["Commercial model", "commercial_model"],
              ["Nonprofit offer", "nonprofit_offer"],
              ["API availability", "api_available"],
            ] as const
          ).map(([title, key]) => (
            <tr key={key}>
              <th scope="row">{title}</th>
              {selected.map((solution) => (
                <td key={solution.id}>
                  {key === "category"
                    ? categoryLabel(solution.category)
                    : solution[key]}
                </td>
              ))}
            </tr>
          ))}
          <tr>
            <th scope="row">Published sources</th>
            {selected.map((solution) => (
              <td key={solution.id}>
                <AIToolSources solution={solution} />
              </td>
            ))}
          </tr>
          <tr>
            <th scope="row">Data questions</th>
            {selected.map((solution) => (
              <td key={solution.id}>
                <ul>
                  {solution.data_review_questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </section>
  );
}
