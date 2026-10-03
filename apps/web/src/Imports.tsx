import React, { useEffect, useRef, useState } from "react";
import { usePendingOperations } from "./operations";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  data: Record<string, any>;
};
type Props = {
  base: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
};
type Binding = {
  column: string;
  indicator_id: string;
  value_role: string;
  unit: string;
};
// The contract bounds the content field below the 256 KiB request cap.
const MAX_CONTENT = 196608;

function command(
  request: Props["request"],
  path: string,
  method: string,
  id: string,
  data: unknown,
  revision?: string,
) {
  return request(path, {
    method,
    body: JSON.stringify({
      operation_id: id,
      ...(revision ? { expected_revision: revision } : {}),
      data,
    }),
  });
}

/** Read a chosen file: CSV as text, XLSX as base64 (first worksheet is imported). */
function readFile(file: File): Promise<{ format: string; content: string }> {
  const xlsx = file.name.toLowerCase().endsWith(".xlsx");
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onload = () => {
      const result = String(reader.result || "");
      resolve(
        xlsx
          ? { format: "XLSX", content: result.slice(result.indexOf(",") + 1) }
          : { format: "CSV", content: result },
      );
    };
    if (xlsx) reader.readAsDataURL(file);
    else reader.readAsText(file);
  });
}

export function ImportsPanel({ base, capabilities, request, explain }: Props) {
  const allowed = (c: string) => capabilities.includes(c);
  const [programmes, setProgrammes] = useState<Row[]>([]);
  const [programme, setProgramme] = useState("");
  const [periods, setPeriods] = useState<Row[]>([]);
  const [period, setPeriod] = useState("");
  const [indicators, setIndicators] = useState<Row[]>([]);
  const [batches, setBatches] = useState<Row[]>([]);
  const [selected, setSelected] = useState("");
  const [template, setTemplate] = useState("");
  const [file, setFile] = useState<{
    name: string;
    format: string;
    content: string;
  } | null>(null);
  const [unitColumn, setUnitColumn] = useState("unit");
  const [eventColumn, setEventColumn] = useState("");
  const [atomic, setAtomic] = useState(true);
  const [bindings, setBindings] = useState<Binding[]>([]);
  const [acceptWarnings, setAcceptWarnings] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [tick, setTick] = useState(0);
  const pending = usePendingOperations();
  const createId = useRef(crypto.randomUUID());

  useEffect(() => {
    request(base + "programmes?limit=100")
      .then((p) => {
        setProgrammes(p.items);
        setProgramme((current) => current || p.items[0]?.object_id || "");
      })
      .catch((e) => setError(explain(e)));
    request(base + "periods?limit=100")
      .then((p) => {
        setPeriods(p.items);
        setPeriod((current) => current || p.items[0]?.object_id || "");
      })
      .catch(() => setPeriods([]));
    request(base + "workflow-templates?limit=10")
      .then((t) => setTemplate(t.items[0]?.revision_id || ""))
      .catch(() => setTemplate(""));
  }, [base]);
  useEffect(() => {
    if (!programme) return;
    Promise.all([
      allowed("imports.read")
        ? request(base + "imports?limit=100")
        : Promise.resolve({ items: [] }),
      allowed("indicator-instances.read")
        ? request(base + "indicator-instances?limit=100")
        : Promise.resolve({ items: [] }),
    ])
      .then(([b, i]) => {
        setBatches(
          b.items.filter((r: Row) => r.data.programme_id === programme),
        );
        setIndicators(
          i.items.filter((r: Row) => r.data.programme_id === programme),
        );
      })
      .catch((e) => setError(explain(e)));
  }, [base, programme, tick]);

  const batch = batches.find((b) => b.object_id === selected);
  const refresh = (text: string) => {
    setMessage(text);
    setError("");
    setTick((t) => t + 1);
  };

  async function create() {
    if (!file) return;
    const data = {
      format: file.format,
      file_name: file.name,
      content: file.content,
      programme_id: programme,
      period_id: period,
      mode: "APPEND",
      atomic,
      mapping: {
        unit_column: unitColumn,
        ...(eventColumn ? { event_at_column: eventColumn } : {}),
        columns: bindings,
      },
    };
    try {
      const receipt = await command(
        request,
        base + "imports",
        "POST",
        createId.current,
        data,
      );
      createId.current = crypto.randomUUID();
      setSelected(receipt.object_id);
      refresh("Import batch saved as a draft. Preview it to check every row.");
    } catch (e) {
      setError(explain(e));
    }
  }

  async function act(row: Row, verb: string, data: unknown, text: string) {
    const key = verb + ":" + row.object_id;
    try {
      await command(
        request,
        base + "imports/" + row.object_id + "/actions/" + verb,
        "POST",
        pending.id(key, [row.revision_id, data]),
        data,
        row.revision_id,
      );
      pending.done(key);
      refresh(text);
    } catch (e) {
      setError(explain(e));
    }
  }

  const preview = batch?.data.preview;
  const counts = preview?.counts;
  return (
    <>
      <div className="planning-toolbar">
        <label>
          Programme
          <select
            aria-label="Programme"
            value={programme}
            onChange={(e) => setProgramme(e.target.value)}
          >
            {!programmes.length && <option value="">No programmes</option>}
            {programmes.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.title || p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
        <label>
          Period
          <select
            aria-label="Period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            {periods.map((p) => (
              <option key={p.object_id} value={p.object_id}>
                {p.data.code || p.object_id.slice(0, 8)}
              </option>
            ))}
          </select>
        </label>
      </div>
      <section className="panel setup-panel">
        {error && (
          <div role="alert" className="error">
            {error}
          </div>
        )}
        {message && (
          <p role="status" className="success">
            {message}
          </p>
        )}
        <div className="setup-heading">
          <div>
            <h2>Import batches</h2>
            <p className="muted">
              Load a CSV or XLSX file (up to {MAX_CONTENT / 1024} KiB and 500
              rows), map its columns by name to this programme's indicators,
              preview every row before anything is written, then commit. Each
              accepted row becomes observations that enter independent review; a
              blank cell is recorded as missing, never as zero.
            </p>
          </div>
        </div>
        {allowed("imports.draft.create") && programme && (
          <fieldset className="import-new">
            <legend>New batch</legend>
            <label>
              File
              <input
                type="file"
                aria-label="Source file"
                accept=".csv,.xlsx,text/csv"
                onChange={async (e) => {
                  const chosen = e.target.files?.[0];
                  if (!chosen) return;
                  try {
                    const read = await readFile(chosen);
                    if (read.content.length > MAX_CONTENT)
                      throw new Error(
                        "The file is larger than one import batch allows.",
                      );
                    setFile({ name: chosen.name, ...read });
                    setError("");
                  } catch (err) {
                    setFile(null);
                    setError(explain(err));
                  }
                }}
              />
            </label>
            <label>
              Unit column
              <input
                aria-label="Unit column"
                value={unitColumn}
                onChange={(e) => setUnitColumn(e.target.value)}
              />
            </label>
            <label>
              Event date column (optional)
              <input
                aria-label="Event date column"
                value={eventColumn}
                onChange={(e) => setEventColumn(e.target.value)}
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={atomic}
                onChange={(e) => setAtomic(e.target.checked)}
              />{" "}
              All rows or nothing (atomic)
            </label>
            {bindings.map((b, i) => (
              <div className="import-binding" key={i}>
                <input
                  aria-label={"Column " + (i + 1)}
                  placeholder="Column header"
                  value={b.column}
                  onChange={(e) =>
                    setBindings(
                      bindings.map((x, j) =>
                        j === i ? { ...x, column: e.target.value } : x,
                      ),
                    )
                  }
                />
                <select
                  aria-label={"Indicator " + (i + 1)}
                  value={b.indicator_id}
                  onChange={(e) =>
                    setBindings(
                      bindings.map((x, j) =>
                        j === i ? { ...x, indicator_id: e.target.value } : x,
                      ),
                    )
                  }
                >
                  {indicators.map((ind) => (
                    <option key={ind.object_id} value={ind.object_id}>
                      {ind.data.local_applicability ||
                        ind.object_id.slice(0, 8)}
                    </option>
                  ))}
                </select>
                <select
                  aria-label={"Role " + (i + 1)}
                  value={b.value_role}
                  onChange={(e) =>
                    setBindings(
                      bindings.map((x, j) =>
                        j === i ? { ...x, value_role: e.target.value } : x,
                      ),
                    )
                  }
                >
                  <option value="VALUE">Value</option>
                  <option value="NUMERATOR">Numerator</option>
                  <option value="DENOMINATOR">Denominator</option>
                </select>
                <input
                  aria-label={"Unit " + (i + 1)}
                  placeholder="Unit (as defined)"
                  value={b.unit}
                  onChange={(e) =>
                    setBindings(
                      bindings.map((x, j) =>
                        j === i ? { ...x, unit: e.target.value } : x,
                      ),
                    )
                  }
                />
              </div>
            ))}
            <button
              className="secondary"
              disabled={!indicators.length}
              onClick={() =>
                setBindings([
                  ...bindings,
                  {
                    column: "",
                    indicator_id: indicators[0]?.object_id || "",
                    value_role: "VALUE",
                    unit: "",
                  },
                ])
              }
            >
              Map a column
            </button>{" "}
            <button
              className="primary"
              disabled={!file || !bindings.length || !period}
              onClick={create}
            >
              Save draft
            </button>
          </fieldset>
        )}
        {!batches.length ? (
          <p className="muted">No import batches for this programme yet.</p>
        ) : (
          <div className="table-scroll">
            <table aria-label="Import batches">
              <thead>
                <tr>
                  <th>File</th>
                  <th>State</th>
                  <th>Rows</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {batches.map((b) => (
                  <tr key={b.object_id}>
                    <td>
                      <button
                        className="link"
                        onClick={() => setSelected(b.object_id)}
                      >
                        {b.data.file_name}
                      </button>
                    </td>
                    <td>{b.lifecycle_state}</td>
                    <td>
                      {b.data.preview
                        ? `${b.data.preview.counts.accepted} accepted · ${b.data.preview.counts.quarantined} quarantined · ${b.data.preview.counts.duplicate} duplicate`
                        : "Not previewed"}
                    </td>
                    <td>
                      {["Draft", "Previewed"].includes(b.lifecycle_state) &&
                        allowed("import.preview") && (
                          <button
                            className="secondary"
                            onClick={() => {
                              setSelected(b.object_id);
                              act(
                                b,
                                "preview",
                                {},
                                "Every row was checked. Nothing has been written yet.",
                              );
                            }}
                          >
                            Preview
                          </button>
                        )}{" "}
                      {["Draft", "Previewed"].includes(b.lifecycle_state) &&
                        allowed("import.cancel") && (
                          <button
                            className="secondary"
                            onClick={() =>
                              act(
                                b,
                                "cancel",
                                { reason: "Cancelled before commit" },
                                "Batch cancelled. Nothing was committed.",
                              )
                            }
                          >
                            Cancel
                          </button>
                        )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {batch && preview && (
          <div className="import-preview">
            <h3>Preview of {batch.data.file_name}</h3>
            <p>
              {counts.rows} rows: {counts.accepted} accepted,{" "}
              {counts.quarantined} quarantined, {counts.duplicate} duplicate;{" "}
              {counts.warnings} with warnings.
              {preview.dropped_columns?.length
                ? " Unmapped columns ignored: " +
                  preview.dropped_columns.join(", ") +
                  "."
                : ""}
            </p>
            {counts.unplanned > 0 && (
              <p role="note" className="import-unplanned">
                {counts.unplanned} accepted{" "}
                {counts.unplanned === 1 ? "value is" : "values are"} not named
                by the approved collection plan. They commit and are reviewed
                like any other value, but the period cannot close until a
                reviewed plan names each value's source key (namespace IMPORT,
                key unit/indicator id/period id; each value's key is in the
                interpretation cell's tooltip) or the value is resolved.
              </p>
            )}
            <div className="table-scroll">
              <table aria-label="Row outcomes">
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Unit</th>
                    <th>Outcome</th>
                    <th>Source cells</th>
                    <th>Interpretation</th>
                    <th>Reasons and warnings</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.rows.map((r: any) => (
                    <tr key={r.row_number}>
                      <td>{r.row_number}</td>
                      <td>{r.row_key || "—"}</td>
                      <td>{r.outcome}</td>
                      <td>
                        {Object.entries(r.raw || {})
                          .map(([k, v]) => k + ": " + JSON.stringify(v))
                          .join("; ")}
                      </td>
                      <td>
                        {(r.observations || []).map((o: any, i: number) => (
                          <span key={i} title={o.source_key || undefined}>
                            {i > 0 ? "; " : ""}
                            {o.value_state + (o.value ? " " + o.value : "")}
                            {o.planned === false
                              ? " (unplanned)"
                              : o.planned === true
                                ? " (planned)"
                                : ""}
                          </span>
                        ))}
                      </td>
                      <td>{[...r.reasons, ...r.warnings].join(", ")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {batch.lifecycle_state === "Previewed" &&
              allowed("import.commit") &&
              allowed("observation.submit") &&
              template && (
                <div className="import-commit">
                  {counts.warnings > 0 && (
                    <label className="checkbox">
                      <input
                        type="checkbox"
                        checked={acceptWarnings}
                        onChange={(e) => setAcceptWarnings(e.target.checked)}
                      />{" "}
                      I have reviewed the warnings; commit the flagged values
                      unchanged
                    </label>
                  )}
                  <button
                    className="primary"
                    disabled={
                      !counts.accepted ||
                      (counts.warnings > 0 && !acceptWarnings)
                    }
                    onClick={() =>
                      act(
                        batch,
                        "commit",
                        {
                          preview_hash: preview.preview_hash,
                          workflow_version: template,
                          ...(counts.warnings
                            ? { accept_warnings: acceptWarnings }
                            : {}),
                        },
                        "Accepted rows committed and sent for independent review.",
                      )
                    }
                  >
                    Commit {counts.accepted} accepted rows
                  </button>
                </div>
              )}
          </div>
        )}
      </section>
    </>
  );
}
