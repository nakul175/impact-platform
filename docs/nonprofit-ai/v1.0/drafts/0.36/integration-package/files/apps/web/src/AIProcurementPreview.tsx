import { useEffect, useId, useRef, useState } from "react";
import {
  applyProcurementPreview,
  currentProcurementPreview,
  previewProcurement,
  procurementSourceFingerprint,
  type ProcurementDraft,
  type ProcurementPreview,
  type ProcurementPreviewSource,
} from "./AIProcurementPreviewModel";
type Props = Omit<ProcurementPreviewSource, "interactionGeneration"> & {
  onChange(value: ProcurementDraft): void;
};
const fields = [
  ["requirements", "Pilot requirements"],
  ["data_boundary", "Data boundary"],
  ["budget_notes", "Budget and nonprofit offer checks"],
  ["vendor_questions", "Questions for suppliers"],
] as const;

export function AIProcurementPreview({ onChange, ...inputs }: Props) {
  const id = useId();
  const signature = procurementSourceFingerprint({
    ...inputs,
    interactionGeneration: 0,
  });
  const generation = useRef({ signature, value: 0 });
  if (generation.current.signature !== signature) {
    generation.current = { signature, value: generation.current.value + 1 };
  }
  const source: ProcurementPreviewSource = {
    ...inputs,
    interactionGeneration: generation.current.value,
  };
  const latest = useRef(source);
  latest.current = source;
  const [preview, setPreview] = useState<ProcurementPreview | null>(null);
  const visible = currentProcurementPreview(source, preview) ? preview : null;
  const candidate = previewProcurement(source);
  useEffect(() => {
    setPreview(null);
  }, [signature, source.interactionGeneration]);
  function apply() {
    if (!visible) return;
    const value = applyProcurementPreview(latest.current, visible);
    if (!value) return;
    onChange(value);
    setPreview(null);
  }
  if (!source.canManage) return null;
  return (
    <section aria-labelledby={id + "-heading"} className="ai-notice">
      <h5 id={id + "-heading"}>Prepare a procurement draft</h5>
      <p>
        Preview the existing planning text from your current brief, shortlist
        and supplier questions. Review it before changing your four procurement
        fields.
      </p>
      <button
        type="button"
        className="secondary"
        disabled={!candidate}
        onClick={() => setPreview(candidate)}
      >
        Preview draft from brief and shortlist
      </button>
      {source.mutationBlocked && (
        <p>
          Wait for the pending saved-plan action before preparing or replacing
          draft text.
        </p>
      )}
      {visible && (
        <div role="group" aria-label="Procurement draft preview">
          <p>This preview has changed no field and saved nothing.</p>
          {visible.hasExistingWork && (
            <p>
              Your procurement fields already contain work. Applying this
              preview replaces all four fields below. Other plan fields are
              kept.
            </p>
          )}
          {fields.map(([key, title]) => (
            <section key={key} aria-labelledby={id + "-" + key}>
              <h6 id={id + "-" + key}>{title}</h6>
              <p className="ai-draft">{visible.proposed[key]}</p>
            </section>
          ))}
          <p className="muted">
            Current catalog edition {source.catalog.content_version}; tool
            directory edition {source.solutionsVersion ?? "unavailable"}. This
            prepares a local draft, without contacting suppliers or approving a
            purchase.
          </p>
          <button type="button" className="secondary" onClick={apply}>
            Replace these four draft fields
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => setPreview(null)}
          >
            Keep my procurement fields unchanged
          </button>
        </div>
      )}
    </section>
  );
}
