import React, { useRef, useState } from "react";

type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  capabilities: string[];
};

const choices = [
  "ROI_PERCENT",
  "NET_BENEFIT",
  "REALISED_BENEFIT",
  "REALISED_COST",
  "USAGE",
  "TIME",
  "COST",
  "QUALITY",
  "REACH",
] as const;

export function AISponsorValueReportPanel(props: Props) {
  const canCreate = props.capabilities.includes("ai.enablement.manage");
  const canRead = props.capabilities.includes("publication.download");
  const [form, setForm] = useState<Record<string, string>>({
    title: "Realised value report",
    sponsor_membership_id: "",
    expires_at: "",
    value_case_object_id: "",
    value_case_revision: "",
    outcome_observation_id: "",
    outcome_observation_revision: "",
    currency: "",
    observed_from: "",
    observed_to: "",
    realised_benefit: "",
    realised_cost: "",
    source_note: "",
  });
  const [selected, setSelected] = useState<string[]>([]);
  const [reportId, setReportId] = useState("");
  const [report, setReport] = useState<any>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = useRef<string | null>(null);

  if (!canCreate && !canRead) return null;

  const update = (name: string, value: string) => {
    setForm({ ...form, [name]: value });
    pending.current = null;
  };

  async function generate() {
    setBusy(true);
    setMessage("");
    if (!pending.current) {
      pending.current = JSON.stringify({
        operation_id: crypto.randomUUID(),
        sponsor_membership_id: form.sponsor_membership_id,
        expires_at: form.expires_at,
        title: form.title,
        value_case_object_id: form.value_case_object_id,
        value_case_revision: form.value_case_revision,
        outcome_observation_id: form.outcome_observation_id,
        outcome_observation_revision: form.outcome_observation_revision,
        realised: {
          currency: form.currency,
          observed_from: form.observed_from,
          observed_to: form.observed_to,
          realised_benefit: form.realised_benefit,
          realised_cost: form.realised_cost,
          source_note: form.source_note,
        },
        selected_items: selected,
      });
    }
    try {
      const receipt = await props.request(
        `${props.base}ai-enablement/sponsor-value-reports`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: pending.current,
        },
      );
      pending.current = null;
      setReportId(receipt.object_id);
      setMessage(
        `Report generated on request: ${receipt.object_id}. No email or external delivery was sent.`,
      );
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  async function openReport() {
    setBusy(true);
    setMessage("");
    setReport(null);
    try {
      setReport(
        await props.request(
          `${props.base}ai-enablement/sponsor-value-reports/${reportId}`,
        ),
      );
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel" aria-labelledby="sponsor-report-heading">
      <h2 id="sponsor-report-heading">Sponsor report</h2>
      {canCreate && (
        <>
          <p>
            Choose exactly what the organisation shares. The period, currency,
            self-reported label and limitations are always included.
          </p>
          <div className="form-grid">
            {[
              ["title", "Report title"],
              ["sponsor_membership_id", "Named external sponsor membership ID"],
              ["expires_at", "Access expiry (ISO date/time with timezone)"],
              ["value_case_object_id", "Locked value case ID"],
              ["value_case_revision", "Locked value case revision"],
              ["outcome_observation_id", "Current outcome observation ID"],
              ["outcome_observation_revision", "Outcome observation revision"],
              ["currency", "Currency (ISO code)"],
              ["observed_from", "Actual period starts"],
              ["observed_to", "Actual period ends"],
              ["realised_benefit", "Realised benefit"],
              ["realised_cost", "Realised cost"],
            ].map(([name, label]) => (
              <label key={name}>
                {label}
                <input
                  type={name.startsWith("observed_") ? "date" : "text"}
                  value={form[name]}
                  onChange={(event) => update(name, event.target.value)}
                />
              </label>
            ))}
          </div>
          <label>
            Source and method note
            <textarea
              maxLength={2000}
              value={form.source_note}
              onChange={(event) => update("source_note", event.target.value)}
            />
          </label>
          <fieldset>
            <legend>Items selected by the organisation</legend>
            {choices.map((item) => (
              <label key={item}>
                <input
                  type="checkbox"
                  checked={selected.includes(item)}
                  onChange={(event) => {
                    setSelected(
                      event.target.checked
                        ? [...selected, item]
                        : selected.filter((value) => value !== item),
                    );
                    pending.current = null;
                  }}
                />
                {item.replaceAll("_", " ").toLowerCase()}
              </label>
            ))}
          </fieldset>
          <button
            type="button"
            disabled={busy || selected.length === 0}
            onClick={() => void generate()}
          >
            {busy ? "Generating…" : "Generate sponsor report"}
          </button>
        </>
      )}
      {canRead && (
        <>
          <h3>Open a report shared with you</h3>
          <label>
            Report ID
            <input
              value={reportId}
              onChange={(event) => setReportId(event.target.value)}
            />
          </label>
          <button
            type="button"
            disabled={busy || !reportId}
            onClick={() => void openReport()}
          >
            Open report
          </button>
          {report && (
            <article aria-label={report.title}>
              <h3>{report.title}</h3>
              <p>
                {report.reporting_basis.replaceAll("_", " ").toLowerCase()} ·{" "}
                {report.observed_from} to {report.observed_to}
              </p>
              <dl>
                {report.selected_items.map((item: string) => (
                  <React.Fragment key={item}>
                    <dt>{item.replaceAll("_", " ").toLowerCase()}</dt>
                    <dd>
                      {typeof report.items[item] === "string"
                        ? report.items[item]
                        : JSON.stringify(report.items[item])}
                    </dd>
                  </React.Fragment>
                ))}
              </dl>
              <p>{report.disclaimer}</p>
              <p>Access expires {report.expires_at}.</p>
            </article>
          )}
        </>
      )}
      {message && (
        <p role="status" aria-live="polite">
          {message}
        </p>
      )}
    </section>
  );
}
