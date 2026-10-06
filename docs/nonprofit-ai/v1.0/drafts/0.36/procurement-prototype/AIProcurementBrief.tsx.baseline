import React from "react";

export type ProcurementBrief = {
  requirements: string;
  data_boundary: string;
  budget_notes: string;
  vendor_questions: string;
};

export function AIProcurementBriefFields({
  value,
  canEdit,
  onChange,
}: {
  value: ProcurementBrief;
  canEdit: boolean;
  onChange(value: ProcurementBrief): void;
}) {
  return (
    <fieldset disabled={!canEdit}>
      <legend>Your requirements</legend>
      {(
        [
          ["requirements", "Pilot requirements", 2000],
          ["data_boundary", "Data boundary", 2000],
          ["budget_notes", "Budget and nonprofit offer checks", 500],
          ["vendor_questions", "Questions for suppliers", 2000],
        ] as const
      ).map(([key, title, limit]) => (
        <label key={key}>
          {title}
          <textarea
            aria-label={title}
            maxLength={limit}
            rows={key === "vendor_questions" ? 6 : 4}
            value={value[key]}
            onChange={(event) =>
              onChange({ ...value, [key]: event.target.value })
            }
          />
        </label>
      ))}
    </fieldset>
  );
}
