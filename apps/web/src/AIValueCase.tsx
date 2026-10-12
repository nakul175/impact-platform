import React, { useState } from "react";

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
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
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
  async function calculate() {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(
        (await props.request(`${props.base}/ai-enablement/value-case`, {
          method: "POST",
          body: JSON.stringify({
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
          }),
        })) as Result,
      );
    } catch (value) {
      setError(props.explain(value));
    } finally {
      setBusy(false);
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
        </div>
      )}
    </section>
  );
}
