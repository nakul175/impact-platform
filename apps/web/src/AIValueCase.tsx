import React, { useRef, useState } from "react";

type Result = {
  status: "COMPLETE_SELF_REPORTED_DRAFT";
  horizon_years: number;
  currency: string;
  costs: Record<"licences" | "setup" | "training" | "staff_time", string>;
  total_cost_of_ownership: string;
  gross_cost_benefit: string;
  net_benefit: string;
  roi_percent: string;
  cost_benefit_ratio: string;
  sector_benefits: {
    staff_hours_saved: string;
    baseline_cost_per_beneficiary: string;
    trial_cost_per_beneficiary: string;
    data_quality_change_points: string;
    reach_change: string;
  };
  disclaimer: string;
};
type ExportFormat = "PDF" | "DOCX";
type VersionReceipt = {
  object_id: string;
  revision_id: string;
  business_state: "Draft" | "Approved" | "Locked";
  baseline_revision: string | null;
  approved_at: string | null;
  approved_by: string | null;
};
type VersionRecord = VersionReceipt & { value_case: Result };
const blank = {
  baseline: "",
  trial: "",
  licences: "",
  setup: "",
  training: "",
  staff: "",
  baselineHours: "",
  trialHours: "",
  baselineBeneficiaries: "",
  trialBeneficiaries: "",
  baselineQuality: "",
  trialQuality: "",
  baselineReach: "",
  trialReach: "",
};

export function AIValueCase(props: {
  base: string;
  opportunityIds: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
}) {
  const [opportunity, setOpportunity] = useState(props.opportunityIds[0] || "");
  const [years, setYears] = useState(1);
  const [currency, setCurrency] = useState("INR");
  const [values, setValues] = useState(blank);
  const [baselineLabel, setBaselineLabel] = useState("");
  const [trialLabel, setTrialLabel] = useState("");
  const [assumption, setAssumption] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [calculatedInput, setCalculatedInput] = useState<Record<
    string,
    unknown
  > | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);
  const [version, setVersion] = useState<VersionReceipt | null>(null);
  const [versionId, setVersionId] = useState("");
  const [loadingVersion, setLoadingVersion] = useState(false);
  const [savedInput, setSavedInput] = useState<string | null>(null);
  const [savingVersion, setSavingVersion] = useState(false);
  const [pendingVersionAction, setPendingVersionAction] = useState(false);
  const pendingVersion = useRef<{
    action: "create" | "approve" | "lock" | "revise";
    path: string;
    body: string;
    inputSnapshot: string | null;
  } | null>(null);
  const ready =
    opportunity &&
    baselineLabel.trim() &&
    trialLabel.trim() &&
    assumption.trim() &&
    Object.values(values).every((value) =>
      /^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$/.test(value),
    );
  const field = (key: keyof typeof values, label: string) => (
    <label>
      {label}
      <input
        inputMode="decimal"
        value={values[key]}
        onChange={(event) =>
          setValues({ ...values, [key]: event.target.value })
        }
      />
    </label>
  );
  function input() {
    return {
      opportunity_id: opportunity,
      horizon_years: years,
      currency,
      baseline: {
        source_label: baselineLabel,
        annual_operating_cost: values.baseline,
        annual_staff_hours: values.baselineHours,
        annual_beneficiaries: values.baselineBeneficiaries,
        data_quality_percent: values.baselineQuality,
        annual_reach: values.baselineReach,
      },
      trial: {
        source_label: trialLabel,
        annual_operating_cost: values.trial,
        annual_staff_hours: values.trialHours,
        annual_beneficiaries: values.trialBeneficiaries,
        data_quality_percent: values.trialQuality,
        annual_reach: values.trialReach,
      },
      costs: {
        licences_annual: values.licences,
        setup_one_off: values.setup,
        training_one_off: values.training,
        staff_time_annual: values.staff,
      },
      assumptions: [assumption],
    };
  }
  async function calculate() {
    setBusy(true);
    setError("");
    setResult(null);
    setCalculatedInput(null);
    try {
      const submitted = input();
      setResult(
        (await props.request(`${props.base}ai-enablement/value-case`, {
          method: "POST",
          body: JSON.stringify(submitted),
        })) as Result,
      );
      setCalculatedInput(submitted);
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setBusy(false);
    }
  }
  async function exportCase(format: ExportFormat) {
    if (!calculatedInput) return;
    setExporting(format);
    setError("");
    try {
      const artifact = (await props.request(
        `${props.base}ai-enablement/value-case/export`,
        {
          method: "POST",
          body: JSON.stringify({
            format,
            title: "Board or funder business case",
            value_case: calculatedInput,
          }),
        },
      )) as {
        manifest: {
          format: ExportFormat;
          filename: string;
          media_type: string;
          content_sha256: string;
          size_bytes: number;
          renderer_version: string;
          assumption_count: number;
        };
        content_base64: string;
      };
      const binary = atob(artifact.content_base64);
      const bytes = Uint8Array.from(binary, (character) =>
        character.charCodeAt(0),
      );
      const expectedMedia =
        format === "PDF"
          ? "application/pdf"
          : "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
      const expectedExtension = format === "PDF" ? ".pdf" : ".docx";
      const digest = Array.from(
        new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
      )
        .map((value) => value.toString(16).padStart(2, "0"))
        .join("");
      if (
        artifact.manifest.format !== format ||
        artifact.manifest.media_type !== expectedMedia ||
        !new RegExp(
          `^impact-value-case-[a-f0-9]{16}\\${expectedExtension}$`,
        ).test(artifact.manifest.filename) ||
        artifact.manifest.size_bytes !== bytes.byteLength ||
        artifact.manifest.content_sha256 !== digest ||
        artifact.manifest.renderer_version !== "ai-value-case-export-v1" ||
        artifact.manifest.assumption_count !== 1
      ) {
        throw new Error("Export artifact integrity check failed.");
      }
      const url = URL.createObjectURL(
        new Blob([bytes], { type: artifact.manifest.media_type }),
      );
      const link = document.createElement("a");
      link.href = url;
      link.download = artifact.manifest.filename;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setExporting(null);
    }
  }
  const displayedInput = calculatedInput
    ? JSON.stringify(calculatedInput)
    : null;
  const savedVersionDisplayed =
    displayedInput === null || displayedInput === savedInput;
  async function loadVersion() {
    if (!versionId.trim() || pendingVersion.current) return;
    setLoadingVersion(true);
    setError("");
    try {
      const loaded = (await props.request(
        `${props.base}ai-enablement/value-cases/${versionId.trim()}`,
      )) as VersionRecord;
      setVersion(loaded);
      setResult(loaded.value_case);
      setCalculatedInput(null);
      setSavedInput(null);
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setLoadingVersion(false);
    }
  }
  async function saveVersion(action: "create" | "approve" | "lock" | "revise") {
    if ((action === "create" || action === "revise") && !calculatedInput)
      return;
    if (action !== "create" && !version) return;
    setSavingVersion(true);
    setError("");
    try {
      if (pendingVersion.current?.action !== action) {
        if (pendingVersion.current) {
          throw new Error(
            "Retry the pending value-case action before starting another one.",
          );
        }
        const path =
          action === "create"
            ? `${props.base}ai-enablement/value-cases`
            : `${props.base}ai-enablement/value-cases/${version!.object_id}/actions/${action}`;
        const body: Record<string, unknown> = {
          operation_id: crypto.randomUUID(),
        };
        if (action !== "create") body.expected_revision = version!.revision_id;
        if (action === "create" || action === "revise")
          body.value_case = calculatedInput;
        pendingVersion.current = {
          action,
          path,
          body: JSON.stringify(body),
          inputSnapshot:
            action === "create" || action === "revise" ? displayedInput : null,
        };
        setPendingVersionAction(true);
      }
      const pending = pendingVersion.current!;
      const saved = (await props.request(pending.path, {
        method: "POST",
        body: pending.body,
      })) as VersionReceipt;
      setVersion(saved);
      if (action === "create" || action === "revise")
        setSavedInput(pending.inputSnapshot);
      pendingVersion.current = null;
      setPendingVersionAction(false);
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setSavingVersion(false);
    }
  }
  return (
    <section aria-labelledby="value-case-title">
      <h4 id="value-case-title">Build a 1–3 year value case</h4>
      <p>
        Use explicit baseline and trial costs. Every required cost component
        must be entered; zero is an explicit amount, not a missing value.
      </p>
      <fieldset disabled={busy}>
        <legend>Value-case inputs</legend>
        <label>
          Opportunity
          <select
            value={opportunity}
            onChange={(event) => setOpportunity(event.target.value)}
          >
            {props.opportunityIds.map((id) => (
              <option key={id}>{id}</option>
            ))}
          </select>
        </label>
        <label>
          Horizon
          <select
            value={years}
            onChange={(event) => setYears(Number(event.target.value))}
          >
            {[1, 2, 3].map((value) => (
              <option key={value} value={value}>
                {value} year{value > 1 ? "s" : ""}
              </option>
            ))}
          </select>
        </label>
        <label>
          Currency
          <input
            maxLength={3}
            value={currency}
            onChange={(event) => setCurrency(event.target.value.toUpperCase())}
          />
        </label>
        <label>
          Baseline source label
          <input
            maxLength={200}
            value={baselineLabel}
            onChange={(event) => setBaselineLabel(event.target.value)}
          />
        </label>
        {field("baseline", "Baseline annual operating cost")}
        {field("baselineHours", "Baseline annual staff hours")}
        {field("baselineBeneficiaries", "Baseline annual beneficiaries")}
        {field("baselineQuality", "Baseline data quality percent")}
        {field("baselineReach", "Baseline annual reach")}
        <label>
          Trial source label
          <input
            maxLength={200}
            value={trialLabel}
            onChange={(event) => setTrialLabel(event.target.value)}
          />
        </label>
        {field("trial", "Trial annual operating cost")}
        {field("trialHours", "Trial annual staff hours")}
        {field("trialBeneficiaries", "Trial annual beneficiaries")}
        {field("trialQuality", "Trial data quality percent")}
        {field("trialReach", "Trial annual reach")}
        {field("licences", "Annual licences")}
        {field("setup", "One-off setup")}
        {field("training", "One-off training")}
        {field("staff", "Annual staff time")}
        <label>
          Assumption
          <textarea
            maxLength={500}
            value={assumption}
            onChange={(event) => setAssumption(event.target.value)}
          />
        </label>
        <button type="button" disabled={!ready || busy} onClick={calculate}>
          {busy ? "Calculating…" : "Calculate value case"}
        </button>
      </fieldset>
      {error && <p role="alert">{error}</p>}
      <fieldset
        disabled={loadingVersion || savingVersion || pendingVersionAction}
      >
        <legend>Open a saved value case</legend>
        <label>
          Value-case ID
          <input
            value={versionId}
            onChange={(event) => setVersionId(event.target.value)}
          />
        </label>
        <button
          type="button"
          disabled={!versionId.trim()}
          onClick={loadVersion}
        >
          {loadingVersion ? "Opening…" : "Open saved value case"}
        </button>
      </fieldset>
      {result && (
        <div role="status">
          <h5>
            Complete self-reported draft · {result.horizon_years} year
            {result.horizon_years > 1 ? "s" : ""}
          </h5>
          <dl>
            <dt>Total cost of ownership</dt>
            <dd>
              {result.currency} {result.total_cost_of_ownership}
            </dd>
            <dt>Gross cost benefit</dt>
            <dd>
              {result.currency} {result.gross_cost_benefit}
            </dd>
            <dt>Net benefit</dt>
            <dd>
              {result.currency} {result.net_benefit}
            </dd>
            <dt>ROI</dt>
            <dd>{result.roi_percent}%</dd>
            <dt>Cost-benefit ratio</dt>
            <dd>{result.cost_benefit_ratio}</dd>
          </dl>
          <p>
            Cost components: licences {result.costs.licences}; setup{" "}
            {result.costs.setup}; training {result.costs.training}; staff time{" "}
            {result.costs.staff_time}.
          </p>
          <h6>Benefits in sector terms</h6>
          <dl>
            <dt>Staff hours saved</dt>
            <dd>{result.sector_benefits.staff_hours_saved}</dd>
            <dt>Baseline cost per beneficiary</dt>
            <dd>
              {result.currency}{" "}
              {result.sector_benefits.baseline_cost_per_beneficiary}
            </dd>
            <dt>Trial cost per beneficiary</dt>
            <dd>
              {result.currency}{" "}
              {result.sector_benefits.trial_cost_per_beneficiary}
            </dd>
            <dt>Data quality change</dt>
            <dd>
              {result.sector_benefits.data_quality_change_points} percentage
              points
            </dd>
            <dt>Reach change</dt>
            <dd>{result.sector_benefits.reach_change}</dd>
          </dl>
          <p className="muted">{result.disclaimer}</p>
          <h6>Approved baseline</h6>
          {!version && (
            <button
              type="button"
              disabled={!calculatedInput || savingVersion}
              onClick={() => saveVersion("create")}
            >
              {savingVersion ? "Saving…" : "Save value-case draft"}
            </button>
          )}
          {version?.business_state === "Draft" && (
            <>
              <p>
                A different authorised natural person must approve this saved
                draft.
              </p>
              <button
                type="button"
                disabled={savingVersion || !savedVersionDisplayed}
                onClick={() => saveVersion("approve")}
              >
                {savingVersion ? "Approving…" : "Approve saved draft"}
              </button>
            </>
          )}
          {version?.business_state === "Approved" && (
            <>
              <p>
                Approved {version.approved_at} by {version.approved_by}.
              </p>
              <button
                type="button"
                disabled={savingVersion || !savedVersionDisplayed}
                onClick={() => saveVersion("lock")}
              >
                {savingVersion ? "Locking…" : "Lock approved baseline"}
              </button>
            </>
          )}
          {version && !savedVersionDisplayed && (
            <p role="alert">
              The displayed calculation differs from the saved revision. Save a
              new revision before approval or locking.
            </p>
          )}
          {version?.business_state === "Locked" && (
            <>
              <p>
                Locked {version.approved_at} by {version.approved_by}. Baseline
                revision {version.baseline_revision}.
              </p>
              <button
                type="button"
                disabled={!calculatedInput || savingVersion}
                onClick={() => saveVersion("revise")}
              >
                {savingVersion
                  ? "Creating version…"
                  : "Create new version from these inputs"}
              </button>
            </>
          )}
          {version?.business_state === "Draft" && version.baseline_revision && (
            <p>
              New draft revision {version.revision_id}; locked baseline{" "}
              {version.baseline_revision} remains unchanged.
            </p>
          )}
          <h6>Board or funder export</h6>
          <p>
            The export recalculates this business case and lists every submitted
            assumption.
          </p>
          <button
            type="button"
            disabled={!calculatedInput || exporting !== null}
            onClick={() => exportCase("PDF")}
          >
            {exporting === "PDF" ? "Preparing PDF…" : "Download PDF"}
          </button>{" "}
          <button
            type="button"
            disabled={!calculatedInput || exporting !== null}
            onClick={() => exportCase("DOCX")}
          >
            {exporting === "DOCX" ? "Preparing document…" : "Download DOCX"}
          </button>
        </div>
      )}
    </section>
  );
}
