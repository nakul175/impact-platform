import React, { useEffect, useMemo, useState } from "react";
import type { Diagnosis, DiagnosisProblem } from "./AIDiagnosis";

type Measure = {
  value: string;
  unit: string;
  basis: string;
  observed_from: string;
  observed_to: string;
};
type MetricName = "time" | "cost" | "quality" | "reach";
type Baseline = {
  object_id: string;
  revision_id: string;
  business_state: "Draft" | "Locked";
  data: {
    diagnosis_id: string;
    diagnosis_revision: string;
    problem_id: string;
    title: string;
    metrics: Partial<Record<MetricName, Measure>>;
    supporting_evidence: string;
    evidence_references: { object_id: string; revision_id: string }[];
    locked_at?: string;
  };
};
type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
  capabilities: string[];
};
const names: MetricName[] = ["time", "cost", "quality", "reach"];
const emptyMeasure = (): Measure => ({
  value: "",
  unit: "",
  basis: "",
  observed_from: "",
  observed_to: "",
});

export function AIProblemBaselinesPanel(props: Props) {
  const canRead = props.capabilities.includes("ai.problem-baseline.read");
  const canManage = props.capabilities.includes("ai.problem-baseline.manage");
  const [diagnoses, setDiagnoses] = useState<Diagnosis[]>([]);
  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [diagnosisId, setDiagnosisId] = useState("");
  const [problemId, setProblemId] = useState("");
  const [current, setCurrent] = useState<Baseline | null>(null);
  const [title, setTitle] = useState("Problem baseline");
  const [metrics, setMetrics] = useState<Record<MetricName, Measure>>({
    time: emptyMeasure(),
    cost: emptyMeasure(),
    quality: emptyMeasure(),
    reach: emptyMeasure(),
  });
  const [supportingEvidence, setSupportingEvidence] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const diagnosis = diagnoses.find((item) => item.object_id === diagnosisId);
  const problems = useMemo(() => {
    if (!diagnosis) return [] as DiagnosisProblem[];
    const byId = new Map(
      diagnosis.data.problems.map((item) => [item.problem_id, item]),
    );
    return diagnosis.data.priority_order
      .map((id) => byId.get(id))
      .filter((item): item is DiagnosisProblem => !!item);
  }, [diagnosis]);

  async function refresh() {
    if (!canRead) return;
    try {
      const [diagnosisPage, baselinePage] = await Promise.all([
        props.request(props.base + "ai-enablement/diagnoses?limit=100"),
        props.request(props.base + "ai-enablement/problem-baselines?limit=100"),
      ]);
      const completed = Array.isArray(diagnosisPage?.items)
        ? diagnosisPage.items.filter(
            (item: Diagnosis) => item.business_state === "Completed",
          )
        : [];
      setDiagnoses(completed);
      setBaselines(
        Array.isArray(baselinePage?.items) ? baselinePage.items : [],
      );
      if (!diagnosisId && completed.length)
        setDiagnosisId(completed[0].object_id);
    } catch (error) {
      setMessage(props.explain(error));
    }
  }

  useEffect(() => {
    void refresh();
  }, [props.base, canRead]);

  useEffect(() => {
    if (!diagnosis) {
      setProblemId("");
      return;
    }
    if (!problems.some((item) => item.problem_id === problemId)) {
      setProblemId(problems[0]?.problem_id || "");
    }
  }, [diagnosisId, diagnoses, problems, problemId]);

  useEffect(() => {
    const item =
      baselines.find(
        (baseline) =>
          baseline.data.diagnosis_id === diagnosisId &&
          baseline.data.problem_id === problemId,
      ) || null;
    setCurrent(item);
    if (item) {
      setTitle(item.data.title);
      setSupportingEvidence(item.data.supporting_evidence);
      setMetrics({
        time: item.data.metrics.time || emptyMeasure(),
        cost: item.data.metrics.cost || emptyMeasure(),
        quality: item.data.metrics.quality || emptyMeasure(),
        reach: item.data.metrics.reach || emptyMeasure(),
      });
    } else {
      setTitle("Problem baseline");
      setSupportingEvidence("");
      setMetrics({
        time: emptyMeasure(),
        cost: emptyMeasure(),
        quality: emptyMeasure(),
        reach: emptyMeasure(),
      });
    }
  }, [diagnosisId, problemId, baselines]);

  async function save() {
    if (!diagnosis || !problemId) return;
    setBusy(true);
    setMessage("");
    const body: Record<string, unknown> = {
      operation_id: crypto.randomUUID(),
      data: {
        diagnosis_id: diagnosis.object_id,
        diagnosis_revision: diagnosis.revision_id,
        problem_id: problemId,
        title,
        metrics: Object.fromEntries(
          names
            .filter((name) =>
              Object.values(metrics[name]).some((value) => value.trim()),
            )
            .map((name) => [name, metrics[name]]),
        ),
        supporting_evidence: supportingEvidence,
        evidence_references: [],
      },
    };
    if (current) body.expected_revision = current.revision_id;
    try {
      await props.request(
        current
          ? props.base + "ai-enablement/problem-baselines/" + current.object_id
          : props.base + "ai-enablement/problem-baselines",
        {
          method: current ? "PUT" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
      );
      setMessage("Baseline draft saved.");
      await refresh();
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  async function lock() {
    if (!current || current.business_state === "Locked") return;
    setBusy(true);
    setMessage("");
    try {
      await props.request(
        props.base +
          "ai-enablement/problem-baselines/" +
          current.object_id +
          "/actions/lock",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: current.revision_id,
          }),
        },
      );
      setMessage(
        "Baseline locked. The recorded observations can no longer be edited.",
      );
      await refresh();
    } catch (error) {
      setMessage(props.explain(error));
    } finally {
      setBusy(false);
    }
  }

  if (!canRead) return null;
  const locked = current?.business_state === "Locked";
  return (
    <section className="card" aria-labelledby="problem-baseline-heading">
      <h2 id="problem-baseline-heading">Problem baselines</h2>
      <p className="muted">
        Record self-reported starting observations for one completed diagnosis
        problem. Locking preserves these values and does not independently
        approve an impact result.
      </p>
      <label>
        Completed diagnosis
        <select
          value={diagnosisId}
          onChange={(event) => setDiagnosisId(event.target.value)}
        >
          <option value="">Choose a diagnosis</option>
          {diagnoses.map((item) => (
            <option key={item.object_id} value={item.object_id}>
              {item.data.title}
            </option>
          ))}
        </select>
      </label>
      <label>
        Priority problem
        <select
          value={problemId}
          onChange={(event) => setProblemId(event.target.value)}
        >
          <option value="">Choose a problem</option>
          {problems.map((problem) => (
            <option key={problem.problem_id} value={problem.problem_id}>
              {problem.description}
            </option>
          ))}
        </select>
      </label>
      {diagnosis && problemId && (
        <>
          <label>
            Baseline title
            <input
              value={title}
              maxLength={150}
              disabled={locked || !canManage}
              onChange={(event) => setTitle(event.target.value)}
            />
          </label>
          {names.map((name) => (
            <fieldset key={name} disabled={locked || !canManage}>
              <legend>{name[0].toUpperCase() + name.slice(1)}</legend>
              <label>
                Exact observed value
                <input
                  inputMode="decimal"
                  value={metrics[name].value}
                  onChange={(event) =>
                    setMetrics({
                      ...metrics,
                      [name]: { ...metrics[name], value: event.target.value },
                    })
                  }
                />
              </label>
              <label>
                Unit
                <input
                  value={metrics[name].unit}
                  maxLength={80}
                  onChange={(event) =>
                    setMetrics({
                      ...metrics,
                      [name]: { ...metrics[name], unit: event.target.value },
                    })
                  }
                />
              </label>
              <label>
                Basis or denominator
                <input
                  value={metrics[name].basis}
                  maxLength={500}
                  onChange={(event) =>
                    setMetrics({
                      ...metrics,
                      [name]: { ...metrics[name], basis: event.target.value },
                    })
                  }
                />
              </label>
              <label>
                Observation starts
                <input
                  type="date"
                  value={metrics[name].observed_from}
                  onChange={(event) =>
                    setMetrics({
                      ...metrics,
                      [name]: {
                        ...metrics[name],
                        observed_from: event.target.value,
                      },
                    })
                  }
                />
              </label>
              <label>
                Observation ends
                <input
                  type="date"
                  value={metrics[name].observed_to}
                  onChange={(event) =>
                    setMetrics({
                      ...metrics,
                      [name]: {
                        ...metrics[name],
                        observed_to: event.target.value,
                      },
                    })
                  }
                />
              </label>
            </fieldset>
          ))}
          <label>
            Supporting evidence note
            <textarea
              value={supportingEvidence}
              maxLength={4000}
              disabled={locked || !canManage}
              onChange={(event) => setSupportingEvidence(event.target.value)}
            />
          </label>
          {locked && current?.data.locked_at && (
            <p role="status">
              Locked on {new Date(current.data.locked_at).toLocaleString()}.
            </p>
          )}
          {!locked && canManage && (
            <div className="button-row">
              <button type="button" disabled={busy} onClick={() => void save()}>
                {busy ? "Saving…" : "Save baseline draft"}
              </button>
              <button
                type="button"
                disabled={busy || !current}
                onClick={() => void lock()}
              >
                Lock complete baseline
              </button>
            </div>
          )}
          {message && <p role="status">{message}</p>}
        </>
      )}
    </section>
  );
}
