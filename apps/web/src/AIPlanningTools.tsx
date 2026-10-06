import React, { useEffect, useId, useRef, useState } from "react";
import "./ai-planning-tools.css";

type CostCategory =
  | "SETUP"
  | "SUBSCRIPTION"
  | "USAGE"
  | "INTEGRATION"
  | "TRAINING"
  | "REVIEW"
  | "SUPPORT"
  | "EXIT"
  | "OTHER";
export type CostLine = {
  id: string;
  category: CostCategory;
  label: string;
  quantity: string;
  unit_amount: string | null;
  cadence: "ONE_OFF" | "MONTHLY";
};
export type CostOffer = { id: string; name: string; lines: CostLine[] };
export type CostInput = {
  currency: string;
  period_months: number;
  offers: CostOffer[];
};
export type PilotSample = {
  sample_size: number;
  total_drafting_minutes: string;
  total_review_minutes: string;
  factual_corrections: number;
};
export type PilotInput = {
  task_label: string;
  baseline: PilotSample;
  pilot: PilotSample;
  comparable: boolean;
  notes: string;
};
export type PlanningInputs = {
  cost_comparison: CostInput | null;
  pilot_evaluation: PilotInput | null;
};
type ToolProps<T> = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  value: T | null;
  onChange: (value: T | null) => void;
  canManage: boolean;
};
type CostResult = {
  currency: string;
  period_months: number;
  status: "COMPLETE" | "INCOMPLETE";
  offers: {
    id: string;
    name: string;
    known_subtotal: string;
    complete_total: string | null;
    missing_line_ids: string[];
  }[];
  cheapest_offer_ids: string[];
  disclaimer: string;
};
type PilotMeasures = {
  total_minutes: string;
  minutes_per_item: string;
  factual_corrections_per_item: string;
};
type PilotResult = {
  status: "SELF_REPORTED_DRAFT";
  task_label: string;
  comparable: boolean;
  notes: string;
  source: { baseline: PilotSample; pilot: PilotSample };
  baseline: PilotMeasures;
  pilot: PilotMeasures;
  improvement: {
    status: "DEFINED" | "UNDEFINED";
    percent: string | null;
    reason: "COMPARABLE_SAMPLES" | "ZERO_BASELINE" | "SAMPLES_NOT_COMPARABLE";
  };
  disclaimer: string;
};

const categories: CostCategory[] = [
  "SETUP",
  "SUBSCRIPTION",
  "USAGE",
  "INTEGRATION",
  "TRAINING",
  "REVIEW",
  "SUPPORT",
  "EXIT",
  "OTHER",
];
export type CostCoverageStatus =
  | "AMOUNTS_RECORDED"
  | "UNKNOWN_AMOUNT"
  | "NOT_RECORDED";
export type CostCoverageRow = {
  category: CostCategory;
  offers: { id: string; name: string; status: CostCoverageStatus }[];
};
// Describe entered coverage only. No amount, currency or total is calculated.
export function costCategoryCoverage(value: CostInput): CostCoverageRow[] {
  return categories.map((category) => ({
    category,
    offers: value.offers.map((offer) => {
      const lines = offer.lines.filter((line) => line.category === category);
      return {
        id: offer.id,
        name: offer.name,
        status: !lines.length
          ? "NOT_RECORDED"
          : lines.some((line) => line.unit_amount === null)
            ? "UNKNOWN_AMOUNT"
            : "AMOUNTS_RECORDED",
      };
    }),
  }));
}
const coverageLabel: Record<CostCoverageStatus, string> = {
  AMOUNTS_RECORDED: "Amounts recorded",
  UNKNOWN_AMOUNT: "Contains an unknown amount",
  NOT_RECORDED: "Not recorded",
};

const decimalPattern = /^(?:0|[1-9][0-9]{0,25})(?:\.[0-9]{1,12})?$/;
const idPattern = /^[a-z][a-z0-9_-]{0,63}$/;
const categoryLabel = (value: string) =>
  value[0] + value.slice(1).replaceAll("_", " ").toLowerCase();
let nextInputId = 0;
function inputId() {
  nextInputId += 1;
  return "input_" + crypto.randomUUID().replaceAll("-", "") + "_" + nextInputId;
}
function blankLine(): CostLine {
  return {
    id: inputId(),
    category: "OTHER",
    label: "",
    quantity: "",
    unit_amount: null,
    cadence: "ONE_OFF",
  };
}
function blankOffer(): CostOffer {
  return { id: inputId(), name: "", lines: [blankLine()] };
}
export function createBlankCostInput(): CostInput {
  return { currency: "", period_months: 0, offers: [blankOffer()] };
}
export function createBlankPilotInput(): PilotInput {
  const sample = (): PilotSample => ({
    sample_size: 0,
    total_drafting_minutes: "",
    total_review_minutes: "",
    factual_corrections: -1,
  });
  return {
    task_label: "",
    baseline: sample(),
    pilot: sample(),
    comparable: false,
    notes: "",
  };
}

// These checks prevent submitting unfinished drafts; the server remains authoritative.
export function validateCostInput(value: CostInput): string | null {
  if (!/^[A-Z]{3}$/.test(value.currency))
    return "Enter a three-letter currency code, such as INR, EUR or USD.";
  if (
    !Number.isInteger(value.period_months) ||
    value.period_months < 1 ||
    value.period_months > 60
  )
    return "Enter a comparison period between 1 and 60 whole months.";
  if (!value.offers.length || value.offers.length > 4)
    return "Include between one and four offers.";
  const offerIds = new Set<string>();
  for (const [offerIndex, offer] of value.offers.entries()) {
    if (!idPattern.test(offer.id) || offerIds.has(offer.id))
      return "Each offer needs a unique valid identifier.";
    offerIds.add(offer.id);
    if (!offer.name.trim() || offer.name.length > 150)
      return `Enter a name for offer ${offerIndex + 1}, up to 150 characters.`;
    if (!offer.lines.length || offer.lines.length > 20)
      return `Offer ${offerIndex + 1} needs between one and twenty cost lines.`;
    const lineIds = new Set<string>();
    for (const [lineIndex, line] of offer.lines.entries()) {
      const place = `Offer ${offerIndex + 1}, line ${lineIndex + 1}`;
      if (!idPattern.test(line.id) || lineIds.has(line.id))
        return `${place} needs a unique valid identifier.`;
      lineIds.add(line.id);
      if (!line.label.trim() || line.label.length > 150)
        return `${place} needs a description, up to 150 characters.`;
      if (!categories.includes(line.category))
        return `${place} needs a recognised cost category.`;
      if (!decimalPattern.test(line.quantity))
        return `${place} needs a non-negative plain decimal quantity (up to 26 whole and 12 decimal digits).`;
      if (line.unit_amount !== null && !decimalPattern.test(line.unit_amount))
        return `${place} needs a non-negative plain decimal unit amount, or a blank amount for unknown cost.`;
      if (!["ONE_OFF", "MONTHLY"].includes(line.cadence))
        return `${place} needs a one-off or monthly cadence.`;
    }
  }
  return null;
}
export function validatePilotInput(value: PilotInput): string | null {
  if (!value.task_label.trim() || value.task_label.length > 150)
    return "Describe the task being compared, up to 150 characters.";
  if (typeof value.comparable !== "boolean" || value.notes.length > 1000)
    return "Confirm comparability and keep notes within 1,000 characters.";
  for (const [key, name] of [
    ["baseline", "Baseline"],
    ["pilot", "Pilot"],
  ] as const) {
    const sample = value[key];
    if (
      !Number.isInteger(sample.sample_size) ||
      sample.sample_size < 1 ||
      sample.sample_size > 10000
    )
      return `${name} sample size must be between 1 and 10,000 whole items.`;
    if (
      !decimalPattern.test(sample.total_drafting_minutes) ||
      !decimalPattern.test(sample.total_review_minutes)
    )
      return `${name} drafting and review minutes must be non-negative plain decimals. Enter 0 when no time was recorded.`;
    if (
      !Number.isInteger(sample.factual_corrections) ||
      sample.factual_corrections < 0 ||
      sample.factual_corrections > 1000000
    )
      return `${name} factual corrections must be between 0 and 1,000,000 whole corrections.`;
  }
  return null;
}

function useCalculation<T, R>(
  props: ToolProps<T>,
  route: string,
  validation: string | null,
  sourceKey: string | null = null,
) {
  const { base, value, request, explain } = props;
  const signature = JSON.stringify([base, value, sourceKey]);
  const currentSignature = useRef(signature);
  currentSignature.current = signature;
  const epoch = useRef(0);
  const controller = useRef<AbortController | null>(null);
  const [state, setState] = useState<{
    signature: string;
    result: R | null;
    busy: boolean;
    error: string;
  }>({ signature, result: null, busy: false, error: "" });
  function invalidate() {
    epoch.current += 1;
    controller.current?.abort();
    controller.current = null;
    setState({
      signature: currentSignature.current,
      result: null,
      busy: false,
      error: "",
    });
  }
  useEffect(() => {
    invalidate();
    return () => {
      epoch.current += 1;
      controller.current?.abort();
    };
  }, [signature]);
  async function calculate() {
    if (!value || validation || state.busy) return;
    const operation = ++epoch.current;
    const capturedSignature = currentSignature.current;
    controller.current?.abort();
    const activeController = new AbortController();
    controller.current = activeController;
    setState({
      signature: capturedSignature,
      result: null,
      busy: true,
      error: "",
    });
    try {
      const result = await request(base + "ai-enablement/" + route, {
        method: "POST",
        body: JSON.stringify(value),
        signal: activeController.signal,
      });
      if (
        operation === epoch.current &&
        capturedSignature === currentSignature.current
      )
        setState({
          signature: capturedSignature,
          result,
          busy: false,
          error: "",
        });
    } catch (error) {
      if (
        operation === epoch.current &&
        capturedSignature === currentSignature.current &&
        !activeController.signal.aborted
      )
        setState({
          signature: capturedSignature,
          result: null,
          busy: false,
          error: explain(error),
        });
    } finally {
      if (operation === epoch.current) controller.current = null;
    }
  }
  const visible = state.signature === signature;
  return {
    result: visible ? state.result : null,
    busy: visible && state.busy,
    error: visible ? state.error : "",
    calculate,
    invalidate,
  };
}

export function AICostComparison(
  props: ToolProps<CostInput> & {
    inputContext?: "SAVED_PLAN" | "SAVED_NOT_REOPENED" | "UNSAVED_DRAFT";
    sourceRevision?: string;
  },
) {
  const { value, onChange, canManage } = props;
  const prefix = useId();
  const inputContext =
    props.inputContext === "SAVED_PLAN" && Boolean(props.sourceRevision)
      ? "SAVED_PLAN"
      : props.inputContext === "SAVED_NOT_REOPENED" ||
          props.inputContext === "SAVED_PLAN"
        ? "SAVED_NOT_REOPENED"
        : "UNSAVED_DRAFT";
  const sourceKey = JSON.stringify([
    inputContext,
    props.sourceRevision ?? null,
  ]);
  const validation = value ? validateCostInput(value) : null;
  const { result, busy, error, calculate, invalidate } = useCalculation<
    CostInput,
    CostResult
  >(props, "cost-comparison", validation, sourceKey);
  function update(next: CostInput | null) {
    if (!canManage) return;
    invalidate();
    onChange(next);
  }
  function updateOffer(index: number, next: CostOffer) {
    if (value)
      update({
        ...value,
        offers: value.offers.map((offer, position) =>
          position === index ? next : offer,
        ),
      });
  }
  function updateLine(offerIndex: number, lineIndex: number, next: CostLine) {
    if (!value) return;
    const offer = value.offers[offerIndex];
    updateOffer(offerIndex, {
      ...offer,
      lines: offer.lines.map((line, position) =>
        position === lineIndex ? next : line,
      ),
    });
  }
  return (
    <fieldset
      className="ai-planning-tool"
      aria-describedby={prefix + "-cost-help"}
    >
      <legend>Compare supplied costs</legend>
      <p id={prefix + "-cost-help"}>
        Record costs from your own quotes. One-off costs count once; monthly
        costs count for the whole comparison period. A blank amount means
        unknown, even for a zero quantity. Use one currency for every offer; no
        exchange rate or supplier price is supplied here.
      </p>
      <p className="ai-planning-note">
        Inputs are saved only when you save this adoption plan. Calculation
        results are temporary drafts, not procurement approval.
      </p>
      {!value ? (
        canManage ? (
          <button type="button" onClick={() => update(createBlankCostInput())}>
            Add cost comparison
          </button>
        ) : (
          <p>No cost comparison has been recorded in this plan.</p>
        )
      ) : (
        <>
          <p className="ai-planning-note" aria-live="polite">
            {inputContext === "SAVED_PLAN"
              ? "Calculation source: the opened saved plan inputs. Results remain temporary."
              : inputContext === "SAVED_NOT_REOPENED"
                ? "Calculation source: local plan inputs. Reopen the saved plan to check its saved revision."
                : "Calculation source: unsaved plan inputs. Save the plan to keep these entries."}
          </p>
          {!canManage && (
            <p className="ai-planning-note">
              You can calculate the inputs shown here. Editing and saving
              require plan management access.
            </p>
          )}
          <fieldset className="ai-planning-inputs" disabled={!canManage}>
            <legend>Comparison inputs</legend>
            <div className="ai-planning-grid">
              <label htmlFor={prefix + "-currency"}>
                Cost comparison currency
                <input
                  id={prefix + "-currency"}
                  value={value.currency}
                  maxLength={3}
                  placeholder="Three-letter code"
                  autoComplete="off"
                  onChange={(event) =>
                    update({
                      ...value,
                      currency: event.target.value.toUpperCase(),
                    })
                  }
                />
              </label>
              <label htmlFor={prefix + "-months"}>
                Comparison months
                <input
                  id={prefix + "-months"}
                  type="number"
                  min={1}
                  max={60}
                  step={1}
                  value={value.period_months === 0 ? "" : value.period_months}
                  onChange={(event) =>
                    update({
                      ...value,
                      period_months:
                        event.target.value === ""
                          ? 0
                          : Number(event.target.value),
                    })
                  }
                />
              </label>
            </div>
            {value.offers.map((offer, offerIndex) => (
              <fieldset className="ai-planning-offer" key={offer.id}>
                <legend>Offer {offerIndex + 1}</legend>
                <label htmlFor={prefix + "-" + offer.id + "-name"}>
                  Offer {offerIndex + 1} name
                  <input
                    id={prefix + "-" + offer.id + "-name"}
                    value={offer.name}
                    maxLength={150}
                    onChange={(event) =>
                      updateOffer(offerIndex, {
                        ...offer,
                        name: event.target.value,
                      })
                    }
                  />
                </label>
                {offer.lines.map((line, lineIndex) => {
                  const linePrefix = prefix + "-" + offer.id + "-" + line.id;
                  const lineName = `Offer ${offerIndex + 1}, line ${lineIndex + 1}`;
                  return (
                    <fieldset className="ai-planning-line" key={line.id}>
                      <legend>Cost line {lineIndex + 1}</legend>
                      <div className="ai-planning-grid">
                        <label htmlFor={linePrefix + "-label"}>
                          {lineName} description
                          <input
                            id={linePrefix + "-label"}
                            value={line.label}
                            maxLength={150}
                            onChange={(event) =>
                              updateLine(offerIndex, lineIndex, {
                                ...line,
                                label: event.target.value,
                              })
                            }
                          />
                        </label>
                        <label htmlFor={linePrefix + "-category"}>
                          {lineName} category
                          <select
                            id={linePrefix + "-category"}
                            value={line.category}
                            onChange={(event) =>
                              updateLine(offerIndex, lineIndex, {
                                ...line,
                                category: event.target.value as CostCategory,
                              })
                            }
                          >
                            {categories.map((category) => (
                              <option key={category} value={category}>
                                {categoryLabel(category)}
                              </option>
                            ))}
                          </select>
                        </label>
                        <label htmlFor={linePrefix + "-quantity"}>
                          {lineName} quantity
                          <input
                            id={linePrefix + "-quantity"}
                            type="text"
                            inputMode="decimal"
                            value={line.quantity}
                            maxLength={39}
                            onChange={(event) =>
                              updateLine(offerIndex, lineIndex, {
                                ...line,
                                quantity: event.target.value,
                              })
                            }
                          />
                        </label>
                        <label htmlFor={linePrefix + "-amount"}>
                          {lineName} unit amount ({value.currency || "currency"}
                          )
                          <input
                            id={linePrefix + "-amount"}
                            type="text"
                            inputMode="decimal"
                            value={line.unit_amount ?? ""}
                            maxLength={39}
                            placeholder="Blank means unknown"
                            aria-describedby={prefix + "-cost-help"}
                            onChange={(event) =>
                              updateLine(offerIndex, lineIndex, {
                                ...line,
                                unit_amount:
                                  event.target.value === ""
                                    ? null
                                    : event.target.value,
                              })
                            }
                          />
                        </label>
                        <label htmlFor={linePrefix + "-cadence"}>
                          {lineName} cadence
                          <select
                            id={linePrefix + "-cadence"}
                            value={line.cadence}
                            onChange={(event) =>
                              updateLine(offerIndex, lineIndex, {
                                ...line,
                                cadence: event.target
                                  .value as CostLine["cadence"],
                              })
                            }
                          >
                            <option value="ONE_OFF">One-off</option>
                            <option value="MONTHLY">Monthly</option>
                          </select>
                        </label>
                      </div>
                      <button
                        type="button"
                        disabled={offer.lines.length <= 1}
                        onClick={() =>
                          updateOffer(offerIndex, {
                            ...offer,
                            lines: offer.lines.filter(
                              (_, index) => index !== lineIndex,
                            ),
                          })
                        }
                      >
                        Remove {lineName.toLowerCase()}
                      </button>
                    </fieldset>
                  );
                })}
                <div className="ai-planning-actions">
                  <button
                    type="button"
                    disabled={offer.lines.length >= 20}
                    onClick={() =>
                      updateOffer(offerIndex, {
                        ...offer,
                        lines: [...offer.lines, blankLine()],
                      })
                    }
                  >
                    Add line to offer {offerIndex + 1}
                  </button>
                  <button
                    type="button"
                    disabled={value.offers.length <= 1}
                    onClick={() =>
                      update({
                        ...value,
                        offers: value.offers.filter(
                          (_, index) => index !== offerIndex,
                        ),
                      })
                    }
                  >
                    Remove offer {offerIndex + 1}
                  </button>
                </div>
              </fieldset>
            ))}
            <div className="ai-planning-actions">
              <button
                type="button"
                disabled={value.offers.length >= 4}
                onClick={() =>
                  update({ ...value, offers: [...value.offers, blankOffer()] })
                }
              >
                Add cost offer
              </button>
              <button type="button" onClick={() => update(null)}>
                Clear cost comparison
              </button>
            </div>
          </fieldset>
          {validation && <p className="ai-planning-note">{validation}</p>}
          <button
            type="button"
            disabled={busy || Boolean(validation)}
            onClick={calculate}
          >
            {busy ? "Calculating costs…" : "Calculate supplied costs"}
          </button>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          {result && (
            <section
              className="ai-planning-result"
              aria-label="Supplied cost results"
              aria-live="polite"
            >
              <h4>
                Draft entered-line comparison — {result.currency},{" "}
                {result.period_months} months
              </h4>
              <p>
                {result.status === "INCOMPLETE"
                  ? "Some entered amounts are unknown. No lowest entered-line total is selected while any offer has an unknown amount."
                  : "All entered amounts are known. This describes entered lines only; unrecorded cost categories remain unassessed. Totals are not verified quotes or a supplier recommendation."}
              </p>
              <p id={prefix + "-coverage-help"}>
                Compare what each offer records. Not recorded is neither zero
                nor not applicable. Unknown amounts also leave the entered-line
                total unknown; even a complete entered-line total does not show
                full supplier or ownership costs.
              </p>
              <p
                id={prefix + "-coverage-scroll"}
                className="ai-cost-coverage-hint"
              >
                Scroll across to compare offers that extend beyond this view.
              </p>
              <p
                id={prefix + "-coverage-title"}
                className="ai-cost-coverage-title"
              >
                Categories recorded in these entered lines
              </p>
              <div
                className="ai-cost-coverage"
                role="region"
                tabIndex={0}
                aria-label="Cost category coverage"
                aria-describedby={
                  prefix + "-coverage-help " + prefix + "-coverage-scroll"
                }
              >
                <table
                  aria-labelledby={prefix + "-coverage-title"}
                  style={{ minWidth: `${6 + value.offers.length * 7}rem` }}
                >
                  <thead>
                    <tr>
                      <th scope="col">Cost category</th>
                      {value.offers.map((offer) => (
                        <th scope="col" key={offer.id}>
                          {offer.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {costCategoryCoverage(value).map((row) => (
                      <tr key={row.category}>
                        <th scope="row">{categoryLabel(row.category)}</th>
                        {row.offers.map((offer) => (
                          <td key={offer.id}>{coverageLabel[offer.status]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="ai-planning-results-grid">
                {result.offers.map((offer) => {
                  const lowest =
                    result.status === "COMPLETE" &&
                    result.cheapest_offer_ids.includes(offer.id);
                  const labels =
                    value.offers.find((input) => input.id === offer.id)
                      ?.lines ?? [];
                  return (
                    <article className="ai-planning-result-card" key={offer.id}>
                      <h5>{offer.name}</h5>
                      <dl>
                        <dt>Exact known subtotal</dt>
                        <dd className="ai-planning-amount">
                          {offer.known_subtotal} {result.currency}
                        </dd>
                        <dt>Entered-line total</dt>
                        <dd className="ai-planning-amount">
                          {offer.complete_total === null
                            ? "Unknown"
                            : offer.complete_total + " " + result.currency}
                        </dd>
                      </dl>
                      {offer.missing_line_ids.length > 0 && (
                        <p>
                          Unknown amounts:{" "}
                          {offer.missing_line_ids
                            .map(
                              (id) =>
                                labels.find((line) => line.id === id)?.label ??
                                id,
                            )
                            .join(", ")}
                          .
                        </p>
                      )}
                      {lowest && (
                        <p className="ai-planning-note">
                          {result.cheapest_offer_ids.length > 1
                            ? "Equal lowest supplied entered-line total (tie)."
                            : "Lowest supplied entered-line total."}{" "}
                          This is not a supplier recommendation.
                        </p>
                      )}
                    </article>
                  );
                })}
              </div>
              <p className="ai-planning-note">
                Amounts above retain exact calculation precision; they are not
                rounded display values.
              </p>
              <p>{result.disclaimer}</p>
            </section>
          )}
        </>
      )}
    </fieldset>
  );
}

export function AIPilotEvaluation(props: ToolProps<PilotInput>) {
  const { value, onChange, canManage } = props;
  const prefix = useId();
  const validation = value ? validatePilotInput(value) : null;
  const { result, busy, error, calculate, invalidate } = useCalculation<
    PilotInput,
    PilotResult
  >(props, "pilot-evaluation", validation);
  function update(next: PilotInput | null) {
    if (!canManage) return;
    invalidate();
    onChange(next);
  }
  function updateSample(key: "baseline" | "pilot", next: PilotSample) {
    if (value) update({ ...value, [key]: next });
  }
  return (
    <fieldset
      className="ai-planning-tool"
      aria-describedby={prefix + "-pilot-help"}
    >
      <legend>Evaluate a pilot</legend>
      <p id={prefix + "-pilot-help"}>
        Compare staff time before and during a pilot, including human review.
        Report the number of items observed in each sample; different sample
        sizes are normalized per item. Use synthetic or approved non-sensitive
        material and leave personal information out of the task and notes.
      </p>
      <p className="ai-planning-note">
        SELF_REPORTED_DRAFT · Inputs are saved with this adoption plan. Results
        are temporary; they do not establish quality, causal benefit or official
        impact.
      </p>
      {!value ? (
        canManage ? (
          <button type="button" onClick={() => update(createBlankPilotInput())}>
            Add pilot evaluation
          </button>
        ) : (
          <p>No pilot evaluation has been recorded in this plan.</p>
        )
      ) : (
        <>
          {!canManage && (
            <p className="ai-planning-note">
              You can evaluate the saved inputs. Editing and saving require plan
              management access.
            </p>
          )}
          <fieldset className="ai-planning-inputs" disabled={!canManage}>
            <legend>Pilot observations</legend>
            <label htmlFor={prefix + "-task"}>
              Task being compared
              <input
                id={prefix + "-task"}
                value={value.task_label}
                maxLength={150}
                onChange={(event) =>
                  update({ ...value, task_label: event.target.value })
                }
              />
            </label>
            <div className="ai-planning-grid">
              {(
                [
                  ["baseline", "Baseline"],
                  ["pilot", "Pilot"],
                ] as const
              ).map(([key, name]) => {
                const sample = value[key];
                const fields = [
                  ["total_drafting_minutes", "Total drafting minutes"],
                  ["total_review_minutes", "Total human review minutes"],
                ] as const;
                return (
                  <fieldset className="ai-planning-sample" key={key}>
                    <legend>{name} sample</legend>
                    <label htmlFor={prefix + "-" + key + "-size"}>
                      {name} sample size (items)
                      <input
                        id={prefix + "-" + key + "-size"}
                        type="number"
                        min={1}
                        max={10000}
                        step={1}
                        value={
                          sample.sample_size === 0 ? "" : sample.sample_size
                        }
                        onChange={(event) =>
                          updateSample(key, {
                            ...sample,
                            sample_size:
                              event.target.value === ""
                                ? 0
                                : Number(event.target.value),
                          })
                        }
                      />
                    </label>
                    {fields.map(([field, label]) => (
                      <label
                        key={field}
                        htmlFor={prefix + "-" + key + "-" + field}
                      >
                        {name} {label.toLowerCase()}
                        <input
                          id={prefix + "-" + key + "-" + field}
                          type="text"
                          inputMode="decimal"
                          maxLength={39}
                          value={sample[field]}
                          onChange={(event) =>
                            updateSample(key, {
                              ...sample,
                              [field]: event.target.value,
                            })
                          }
                        />
                      </label>
                    ))}
                    <label htmlFor={prefix + "-" + key + "-corrections"}>
                      {name} factual corrections
                      <input
                        id={prefix + "-" + key + "-corrections"}
                        type="number"
                        min={0}
                        max={1000000}
                        step={1}
                        value={
                          sample.factual_corrections === -1
                            ? ""
                            : sample.factual_corrections
                        }
                        onChange={(event) =>
                          updateSample(key, {
                            ...sample,
                            factual_corrections:
                              event.target.value === ""
                                ? -1
                                : Number(event.target.value),
                          })
                        }
                      />
                    </label>
                  </fieldset>
                );
              })}
            </div>
            <label
              className="ai-planning-checkbox"
              htmlFor={prefix + "-comparable"}
            >
              <input
                id={prefix + "-comparable"}
                type="checkbox"
                checked={value.comparable}
                onChange={(event) =>
                  update({ ...value, comparable: event.target.checked })
                }
              />
              We judge these samples comparable in task type, difficulty and
              quality expectations.
            </label>
            <p className="ai-planning-note">
              This is your reported judgment. Normalizing sample sizes cannot
              verify comparable tasks.
            </p>
            <label htmlFor={prefix + "-notes"}>
              Pilot comparison notes
              <textarea
                id={prefix + "-notes"}
                maxLength={1000}
                rows={3}
                value={value.notes}
                onChange={(event) =>
                  update({ ...value, notes: event.target.value })
                }
              />
            </label>
            <button type="button" onClick={() => update(null)}>
              Clear pilot evaluation
            </button>
          </fieldset>
          {validation && <p className="ai-planning-note">{validation}</p>}
          <button
            type="button"
            disabled={busy || Boolean(validation)}
            onClick={calculate}
          >
            {busy
              ? "Calculating pilot comparison…"
              : "Calculate pilot comparison"}
          </button>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          {result && (
            <section
              className="ai-planning-result"
              aria-label="Pilot evaluation results"
              aria-live="polite"
            >
              <h4>Self-reported draft: {result.task_label}</h4>
              <p className="ai-planning-note">
                SELF_REPORTED_DRAFT · Calculated measures are rounded to up to
                six decimal places for display.
              </p>
              <div className="ai-planning-results-grid">
                {(
                  [
                    ["baseline", "Baseline"],
                    ["pilot", "Pilot"],
                  ] as const
                ).map(([key, name]) => (
                  <article className="ai-planning-result-card" key={key}>
                    <h5>{name}</h5>
                    <dl>
                      <dt>Reported sample size</dt>
                      <dd>{result.source[key].sample_size} items</dd>
                      <dt>Reported drafting minutes (exact input)</dt>
                      <dd className="ai-planning-amount">
                        {result.source[key].total_drafting_minutes}
                      </dd>
                      <dt>Reported review minutes (exact input)</dt>
                      <dd className="ai-planning-amount">
                        {result.source[key].total_review_minutes}
                      </dd>
                      <dt>Total drafting and review minutes (display)</dt>
                      <dd className="ai-planning-amount">
                        {result[key].total_minutes}
                      </dd>
                      <dt>Minutes per item (display)</dt>
                      <dd className="ai-planning-amount">
                        {result[key].minutes_per_item}
                      </dd>
                      <dt>Reported factual corrections</dt>
                      <dd>{result.source[key].factual_corrections}</dd>
                      <dt>Factual corrections per item (display)</dt>
                      <dd className="ai-planning-amount">
                        {result[key].factual_corrections_per_item}
                      </dd>
                    </dl>
                  </article>
                ))}
              </div>
              <p className="ai-planning-outcome">
                {result.improvement.status === "UNDEFINED"
                  ? result.improvement.reason === "ZERO_BASELINE"
                    ? "Time change is undefined because baseline time is zero."
                    : "Time change is undefined because the samples were reported as not comparable."
                  : result.improvement.percent?.startsWith("-")
                    ? `Pilot took more staff time per item. Relative time improvement: ${result.improvement.percent}%.`
                    : result.improvement.percent === "0"
                      ? "No measured time change per item (0% relative time improvement)."
                      : `Less staff time per item. Relative time improvement: ${result.improvement.percent}%.`}
              </p>
              <p>{result.disclaimer}</p>
            </section>
          )}
        </>
      )}
    </fieldset>
  );
}
