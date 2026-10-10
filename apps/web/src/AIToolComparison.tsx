import React from "react";

// US-DC-04: whether Imprana has a known commercial relationship with a listing's provider.
export type RelationshipType =
  | "referral_fee"
  | "revenue_share"
  | "reseller"
  | "sponsorship"
  | "ownership";
export type CommercialDisclosure = {
  status: "NONE_KNOWN" | "DISCLOSED";
  relationship_types: RelationshipType[];
  statement: string;
  declared_on: string;
  // PENDING: a draft prepared for Imprana editorial review, not yet confirmed. Absent only on the
  // invented tools of the public walkthrough, which make no editorial claim.
  editorial_confirmation?: "PENDING" | "CONFIRMED";
};

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
  // Always present in the current directory (the server refuses to serve a listing without one);
  // absent only in guidance archived before disclosures existed (edition v1).
  commercial_disclosure?: CommercialDisclosure;
};

const relationshipLabels: Record<RelationshipType, string> = {
  referral_fee: "Referral fee",
  revenue_share: "Revenue share",
  reseller: "Reseller",
  sponsorship: "Sponsorship",
  ownership: "Ownership",
};

export function disclosureHeadline(disclosure?: CommercialDisclosure | null) {
  if (!disclosure) return "Commercial disclosure not recorded";
  if (disclosure.status === "NONE_KNOWN")
    return "No commercial relationship known";
  const types = disclosure.relationship_types
    .map((type) => relationshipLabels[type] ?? type)
    .join(", ");
  return "Commercial relationship disclosed: " + (types || "type not stated");
}

// A labelled note, so a screen reader announces "Commercial disclosure for <tool>" with its text.
export function AIDisclosureLabel({
  name,
  disclosure,
  missing = "No disclosure was recorded for this listing.",
}: {
  name: string;
  disclosure?: CommercialDisclosure | null;
  missing?: string;
}) {
  const status = disclosure?.status ?? "NOT_RECORDED";
  return (
    <div
      className={
        "ai-disclosure" + (status === "DISCLOSED" ? " ai-disclosed" : "")
      }
      role="note"
      aria-label={"Commercial disclosure for " + name}
      data-disclosure-status={status}
    >
      <p className="ai-disclosure-headline">
        <strong>{disclosureHeadline(disclosure)}</strong>
        {disclosure?.editorial_confirmation === "PENDING" && (
          <span className="ai-disclosure-pending">
            {" "}
            · pending editorial confirmation
          </span>
        )}
      </p>
      {disclosure ? (
        <p className="ai-disclosure-statement">
          {disclosure.statement}{" "}
          <span className="ai-disclosure-date">
            Declared {disclosure.declared_on}.
          </span>
        </p>
      ) : (
        <p className="ai-disclosure-statement">{missing}</p>
      )}
    </div>
  );
}

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
            <th scope="row">Commercial disclosure</th>
            {selected.map((solution) => (
              <td key={solution.id}>
                <AIDisclosureLabel
                  name={solution.name}
                  disclosure={solution.commercial_disclosure}
                />
              </td>
            ))}
          </tr>
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
