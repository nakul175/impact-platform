import React, { useState } from "react";

type Section = {
  section_code: string;
  heading: string;
  narrative: string;
  bindings: {
    binding_code: string;
    result_revision: string;
    display_decimals: number;
    unit: string;
  }[];
  evidence_revisions: string[];
  charts: never[];
};
type Draft = {
  draft_id: string;
  generation: number;
  proposed_sections: Section[];
  evidence_gaps: {
    section_code: string;
    reason: string;
    binding_codes?: string[];
  }[];
  mandatory_caveat_codes: string[];
};
type Props = {
  base: string;
  policyVersion: number | null;
  canDraft: boolean;
  canReview: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};

export function AIReportDrafting({
  base,
  policyVersion,
  canDraft,
  canReview,
  request,
  explain,
}: Props) {
  const [form, setForm] = useState({
    snapshot_id: "",
    snapshot_revision_id: "",
    template_revision_id: "",
    section_code: "",
    narrative: "",
    binding_code: "",
    result_revision: "",
    unit: "",
    evidence_revision: "",
  });
  const [draft, setDraft] = useState<Draft | null>(null);
  const [finalSections, setFinalSections] = useState<Section[]>([]);
  const [reviewed, setReviewed] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const update = (name: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [name]: value }));
  if (!canDraft) return null;
  return (
    <section aria-labelledby="ai-report-drafting">
      <h3 id="ai-report-drafting">Snapshot-bound report drafting</h3>
      <p className="muted">
        Proposals use one locked snapshot and approved template. Official
        numbers remain result bindings, missing evidence stays visible, and
        human wording is saved as a separate review.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setBusy(true);
          setError("");
          setReviewed(false);
          try {
            const section: Section = {
              section_code: form.section_code,
              heading: form.section_code.replaceAll("_", " "),
              narrative: form.narrative,
              bindings:
                form.binding_code && form.result_revision
                  ? [
                      {
                        binding_code: form.binding_code,
                        result_revision: form.result_revision,
                        display_decimals: 2,
                        unit: form.unit,
                      },
                    ]
                  : [],
              evidence_revisions: form.evidence_revision
                ? [form.evidence_revision]
                : [],
              charts: [],
            };
            const result = await request(base + "ai-enablement/report-drafts", {
              method: "POST",
              body: JSON.stringify({
                operation_id: crypto.randomUUID(),
                snapshot_id: form.snapshot_id,
                snapshot_revision_id: form.snapshot_revision_id,
                template_revision_id: form.template_revision_id,
                language: "en",
                policy_version: policyVersion,
                section_inputs: [section],
                prior_draft_id: null,
                regenerated_section_codes: [],
              }),
            });
            setDraft(result);
            setFinalSections(result.proposed_sections);
          } catch (caught) {
            setError(explain(caught));
          } finally {
            setBusy(false);
          }
        }}
      >
        <fieldset disabled={busy || policyVersion === null}>
          <div className="form-grid">
            {(
              [
                ["snapshot_id", "Locked snapshot ID"],
                ["snapshot_revision_id", "Snapshot revision"],
                ["template_revision_id", "Approved template revision"],
                ["section_code", "Template section code"],
                ["binding_code", "Metric binding code"],
                ["result_revision", "Official result revision"],
                ["unit", "Result unit"],
                ["evidence_revision", "Evidence revision (optional)"],
              ] as const
            ).map(([name, text]) => (
              <label key={name}>
                {text}
                <input
                  required={!name.endsWith("evidence_revision")}
                  value={form[name]}
                  onChange={(event) => update(name, event.target.value)}
                />
              </label>
            ))}
          </div>
          <label>
            Proposed narrative (use {"{{binding_code}}"} for official numbers)
            <textarea
              required
              maxLength={20000}
              value={form.narrative}
              onChange={(event) => update("narrative", event.target.value)}
            />
          </label>
          <button type="submit">Create bound proposal</button>
        </fieldset>
      </form>
      {error && <div className="error">{error}</div>}
      {draft && (
        <div aria-live="polite">
          <p className="badge">Draft generation {draft.generation}</p>
          {!!draft.evidence_gaps.length && (
            <div>
              <h4>Evidence gaps</h4>
              <ul>
                {draft.evidence_gaps.map((gap) => (
                  <li key={gap.section_code + gap.reason}>
                    {gap.section_code}: {gap.reason.replaceAll("_", " ")}
                    {gap.binding_codes?.length
                      ? ` (${gap.binding_codes.join(", ")})`
                      : ""}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {finalSections.map((section, index) => (
            <label key={section.section_code}>
              Final human wording for {section.heading}
              <textarea
                maxLength={20000}
                value={section.narrative}
                onChange={(event) =>
                  setFinalSections((current) =>
                    current.map((item, itemIndex) =>
                      itemIndex === index
                        ? { ...item, narrative: event.target.value }
                        : item,
                    ),
                  )
                }
              />
            </label>
          ))}
          {canReview && (
            <button
              type="button"
              disabled={busy || reviewed}
              onClick={async () => {
                setBusy(true);
                setError("");
                try {
                  await request(
                    base +
                      `ai-enablement/report-drafts/${draft.draft_id}/actions/review`,
                    {
                      method: "POST",
                      body: JSON.stringify({
                        operation_id: crypto.randomUUID(),
                        final_sections: finalSections,
                        mandatory_caveat_codes: draft.mandatory_caveat_codes,
                      }),
                    },
                  );
                  setReviewed(true);
                } catch (caught) {
                  setError(explain(caught));
                } finally {
                  setBusy(false);
                }
              }}
            >
              Record human review
            </button>
          )}
          {reviewed && (
            <p role="status">Human wording and corrections recorded.</p>
          )}
        </div>
      )}
    </section>
  );
}
