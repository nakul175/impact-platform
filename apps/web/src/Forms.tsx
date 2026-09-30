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
  Dialog: React.ComponentType<{
    title: string;
    close: () => void;
    children: React.ReactNode;
  }>;
};
type Field = {
  field_id: string;
  stable_code: string;
  position: number;
  field_type: string;
  label: string;
  required: boolean;
  minimum?: string | null;
  maximum?: string | null;
  choices?: { code: string; label: string; active: boolean }[];
  indicator_id?: string | null;
  value_role?: string | null;
  dimension_code?: string | null;
  relevant_when?: { field_code: string; equals: string } | null;
};
const TYPES = ["DECIMAL", "INTEGER", "SINGLE_CHOICE", "BOOLEAN", "TEXT"];
const MISSING = [
  ["", "Answer"],
  ["NOT_COLLECTED", "Not collected"],
  ["NOT_APPLICABLE", "Not applicable"],
  ["DECLINED", "Declined"],
  ["UNKNOWN", "Unknown"],
];

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

const blankField = (position: number): Field => ({
  field_id: crypto.randomUUID(),
  stable_code: "q" + (position + 1),
  position,
  field_type: "DECIMAL",
  label: "",
  required: false,
});

/** Clean one edited field into the closed contract: empty optional values are omitted. */
function clean(f: Field, position: number) {
  const out: Record<string, unknown> = {
    field_id: f.field_id,
    stable_code: f.stable_code,
    position,
    field_type: f.field_type,
    label: f.label,
    required: f.required,
  };
  if (f.minimum) out.minimum = f.minimum;
  if (f.maximum) out.maximum = f.maximum;
  if (f.field_type === "SINGLE_CHOICE") out.choices = f.choices || [];
  if (f.indicator_id) {
    out.indicator_id = f.indicator_id;
    out.value_role = f.value_role || "VALUE";
  }
  if (f.dimension_code) out.dimension_code = f.dimension_code;
  if (f.relevant_when?.field_code)
    out.relevant_when = {
      field_code: f.relevant_when.field_code,
      equals: f.relevant_when.equals,
    };
  return out;
}

export function FormsPanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const allowed = (c: string) => capabilities.includes(c);
  const [programmes, setProgrammes] = useState<Row[]>([]);
  const [programme, setProgramme] = useState("");
  const [forms, setForms] = useState<Row[]>([]);
  const [indicators, setIndicators] = useState<Row[]>([]);
  const [template, setTemplate] = useState("");
  const [dialog, setDialog] = useState<null | {
    mode: "design" | "fill";
    row?: Row;
  }>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [tick, setTick] = useState(0);
  const pending = usePendingOperations();

  useEffect(() => {
    request(base + "programmes?limit=100")
      .then((p) => {
        setProgrammes(p.items);
        setProgramme((current) => current || p.items[0]?.object_id || "");
      })
      .catch((e) => setError(explain(e)));
    request(base + "workflow-templates?limit=10")
      .then((t) => setTemplate(t.items[0]?.revision_id || ""))
      .catch(() => setTemplate(""));
  }, [base]);
  useEffect(() => {
    if (!programme) return;
    Promise.all([
      request(base + "forms?limit=100"),
      allowed("indicator-instances.read")
        ? request(base + "indicator-instances?limit=100")
        : Promise.resolve({ items: [] }),
    ])
      .then(([f, i]) => {
        setForms(f.items.filter((r: Row) => r.data.programme_id === programme));
        setIndicators(
          i.items.filter((r: Row) => r.data.programme_id === programme),
        );
      })
      .catch((e) => setError(explain(e)));
  }, [base, programme, tick]);

  const done = (text: string) => {
    setDialog(null);
    setMessage(text);
    setError("");
    setTick((t) => t + 1);
  };
  async function act(row: Row, verb: string, data: unknown, text: string) {
    const key = verb + ":" + row.object_id;
    try {
      await command(
        request,
        base + "forms/" + row.object_id + "/actions/" + verb,
        "POST",
        pending.id(key, [row.revision_id, data]),
        data,
        row.revision_id,
      );
      pending.done(key);
      done(text);
    } catch (e) {
      setError(explain(e));
    }
  }

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
            <h2>Forms</h2>
            <p className="muted">
              Design a form bound to this programme's indicators, send it for
              independent review, publish the approved version and collect
              responses. Each response becomes observations that are reviewed
              like any other source; a blank answer is never recorded as zero.
            </p>
          </div>
          {allowed("forms.draft.create") && programme && (
            <button
              className="primary"
              onClick={() => setDialog({ mode: "design" })}
            >
              New form
            </button>
          )}
        </div>
        {!forms.length ? (
          <p className="muted">No forms for this programme yet.</p>
        ) : (
          <div className="table-scroll">
            <table aria-label="Forms">
              <thead>
                <tr>
                  <th>Form</th>
                  <th>State</th>
                  <th>Fields</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {forms.map((f) => (
                  <tr key={f.object_id}>
                    <td>
                      <strong>{f.data.title}</strong>{" "}
                      <small className="muted">{f.data.code}</small>
                    </td>
                    <td>{f.lifecycle_state}</td>
                    <td>{(f.data.fields || []).length}</td>
                    <td>
                      {["Draft", "Returned", "Published"].includes(
                        f.lifecycle_state,
                      ) &&
                        allowed("forms.draft.edit") && (
                          <button
                            className="secondary"
                            onClick={() =>
                              setDialog({ mode: "design", row: f })
                            }
                          >
                            {f.lifecycle_state === "Published"
                              ? "New version"
                              : "Edit"}
                          </button>
                        )}{" "}
                      {["Draft", "Returned"].includes(f.lifecycle_state) &&
                        allowed("form.submit") &&
                        template && (
                          <button
                            className="secondary"
                            onClick={() =>
                              act(
                                f,
                                "submit",
                                { workflow_version: template },
                                "Form version sent for independent review. Its schema is now locked.",
                              )
                            }
                          >
                            Send for review
                          </button>
                        )}{" "}
                      {f.lifecycle_state === "Approved" &&
                        allowed("form.publish") && (
                          <button
                            className="primary"
                            onClick={() =>
                              act(
                                f,
                                "publish",
                                { approved_candidate_revision: f.revision_id },
                                "Form version published. New responses use this version.",
                              )
                            }
                          >
                            Publish
                          </button>
                        )}{" "}
                      {allowed("submissions.draft.create") && (
                        <button
                          className="secondary"
                          onClick={() => setDialog({ mode: "fill", row: f })}
                        >
                          Fill in
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {dialog?.mode === "design" && (
        <Dialog
          title={dialog.row ? "Edit form " + dialog.row.data.code : "New form"}
          close={() => setDialog(null)}
        >
          <Designer
            base={base}
            request={request}
            explain={explain}
            row={dialog.row}
            programme={programme}
            indicators={indicators}
            done={done}
          />
        </Dialog>
      )}
      {dialog?.mode === "fill" && dialog.row && (
        <Dialog
          title={"Fill in " + dialog.row.data.title}
          close={() => setDialog(null)}
        >
          <Fill
            base={base}
            request={request}
            explain={explain}
            form={dialog.row}
            template={template}
            canSubmit={
              // Submitting reads the bound indicators with the submitter's own access.
              allowed("submission.submit") &&
              allowed("indicator-instances.read")
            }
            done={done}
          />
        </Dialog>
      )}
    </>
  );
}

function Designer({
  base,
  request,
  explain,
  row,
  programme,
  indicators,
  done,
}: {
  base: string;
  request: Props["request"];
  explain: Props["explain"];
  row?: Row;
  programme: string;
  indicators: Row[];
  done: (text: string) => void;
}) {
  const [code, setCode] = useState(row?.data.code || "");
  const [title, setTitle] = useState(row?.data.title || "");
  const [fields, setFields] = useState<Field[]>(
    row?.data.fields?.length ? row.data.fields : [blankField(0)],
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  // One identifier for the life of this dialog: a retry after a lost response is exact.
  const operation = useRef(crypto.randomUUID());
  const payload = useRef("");
  const update = (i: number, change: Partial<Field>) =>
    setFields((all) => all.map((f, j) => (j === i ? { ...f, ...change } : f)));

  async function save(e: React.FormEvent) {
    e.preventDefault();
    const data: Record<string, unknown> = {
      code,
      title,
      fields: fields.map(clean),
    };
    if (!row) {
      data.programme_id = programme;
      data.logic = [];
      data.translation_versions = [];
      data.compatibility_policy = "LOCK_PUBLISHED";
    }
    const fingerprint = JSON.stringify(data);
    if (payload.current && payload.current !== fingerprint)
      operation.current = crypto.randomUUID();
    payload.current = fingerprint;
    setBusy(true);
    try {
      await command(
        request,
        base + "forms" + (row ? "/" + row.object_id : ""),
        row ? "PATCH" : "POST",
        operation.current,
        data,
        row?.revision_id,
      );
      done(
        row?.lifecycle_state === "Published"
          ? "New form version drafted. The published version keeps collecting until the new one is approved and published."
          : "Form draft saved.",
      );
    } catch (err) {
      setError(explain(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={save}>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      <div className="form-grid">
        <label>
          Form code
          <input
            required
            maxLength={64}
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </label>
        <label>
          Form title
          <input
            required
            maxLength={200}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
      </div>
      <h3>Questions</h3>
      {fields.map((f, i) => (
        <fieldset key={f.field_id} className="planning-node-editor">
          <legend>Question {i + 1}</legend>
          <div className="form-grid">
            <label>
              Code {i + 1}
              <input
                required
                pattern="[A-Za-z][A-Za-z0-9_]{0,63}"
                value={f.stable_code}
                onChange={(e) => update(i, { stable_code: e.target.value })}
              />
            </label>
            <label>
              Question {i + 1} label
              <input
                required
                maxLength={200}
                value={f.label}
                onChange={(e) => update(i, { label: e.target.value })}
              />
            </label>
            <label>
              Type {i + 1}
              <select
                aria-label={"Type " + (i + 1)}
                value={f.field_type}
                onChange={(e) => update(i, { field_type: e.target.value })}
              >
                {TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t.toLowerCase().replace("_", " ")}
                  </option>
                ))}
              </select>
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={f.required}
                onChange={(e) => update(i, { required: e.target.checked })}
              />
              Required {i + 1}
            </label>
            {(f.field_type === "DECIMAL" || f.field_type === "INTEGER") && (
              <>
                <label>
                  Minimum {i + 1}
                  <input
                    inputMode="decimal"
                    value={f.minimum || ""}
                    onChange={(e) => update(i, { minimum: e.target.value })}
                  />
                </label>
                <label>
                  Maximum {i + 1}
                  <input
                    inputMode="decimal"
                    value={f.maximum || ""}
                    onChange={(e) => update(i, { maximum: e.target.value })}
                  />
                </label>
                <label>
                  Feeds indicator {i + 1}
                  <select
                    aria-label={"Feeds indicator " + (i + 1)}
                    value={f.indicator_id || ""}
                    onChange={(e) =>
                      update(i, { indicator_id: e.target.value || null })
                    }
                  >
                    <option value="">None</option>
                    {indicators.map((x) => (
                      <option key={x.object_id} value={x.object_id}>
                        {x.data.local_applicability || x.object_id.slice(0, 8)}
                      </option>
                    ))}
                  </select>
                </label>
                {f.indicator_id && (
                  <label>
                    Role {i + 1}
                    <select
                      aria-label={"Role " + (i + 1)}
                      value={f.value_role || "VALUE"}
                      onChange={(e) =>
                        update(i, { value_role: e.target.value })
                      }
                    >
                      <option value="VALUE">value</option>
                      <option value="NUMERATOR">numerator</option>
                      <option value="DENOMINATOR">denominator</option>
                    </select>
                  </label>
                )}
              </>
            )}
            {f.field_type === "SINGLE_CHOICE" && (
              <>
                <label>
                  Choices {i + 1} (code=label, comma separated)
                  <input
                    required
                    value={(f.choices || [])
                      .map((c) => c.code + "=" + c.label)
                      .join(", ")}
                    onChange={(e) =>
                      update(i, {
                        choices: e.target.value
                          .split(",")
                          .map((p) => p.trim())
                          .filter(Boolean)
                          .map((p) => {
                            const [c, ...l] = p.split("=");
                            return {
                              code: c.trim(),
                              label: (l.join("=") || c).trim(),
                              active: true,
                            };
                          }),
                      })
                    }
                  />
                </label>
                <label>
                  Disaggregation dimension {i + 1}
                  <input
                    value={f.dimension_code || ""}
                    onChange={(e) =>
                      update(i, { dimension_code: e.target.value || null })
                    }
                  />
                </label>
              </>
            )}
            {i > 0 && (
              <>
                <label>
                  Ask only when {i + 1}
                  <select
                    aria-label={"Ask only when " + (i + 1)}
                    value={f.relevant_when?.field_code || ""}
                    onChange={(e) =>
                      update(i, {
                        relevant_when: e.target.value
                          ? {
                              field_code: e.target.value,
                              equals: f.relevant_when?.equals || "",
                            }
                          : null,
                      })
                    }
                  >
                    <option value="">Always</option>
                    {fields
                      .slice(0, i)
                      .filter((u) =>
                        ["SINGLE_CHOICE", "BOOLEAN"].includes(u.field_type),
                      )
                      .map((u) => (
                        <option key={u.field_id} value={u.stable_code}>
                          {u.stable_code}
                        </option>
                      ))}
                  </select>
                </label>
                {f.relevant_when?.field_code && (
                  <label>
                    equals {i + 1}
                    <input
                      required
                      value={f.relevant_when.equals}
                      onChange={(e) =>
                        update(i, {
                          relevant_when: {
                            field_code: f.relevant_when!.field_code,
                            equals: e.target.value,
                          },
                        })
                      }
                    />
                  </label>
                )}
              </>
            )}
          </div>
          {fields.length > 1 && (
            <button
              type="button"
              className="secondary"
              onClick={() => setFields((all) => all.filter((_, j) => j !== i))}
            >
              Remove question {i + 1}
            </button>
          )}
        </fieldset>
      ))}
      <button
        type="button"
        className="secondary"
        onClick={() => setFields((all) => [...all, blankField(all.length)])}
      >
        Add question
      </button>{" "}
      <button className="primary" disabled={busy}>
        Save draft
      </button>
    </form>
  );
}

function relevant(fields: Field[], values: Record<string, string>) {
  const out: Record<string, boolean> = {};
  for (const f of [...fields].sort((a, b) => a.position - b.position)) {
    const rule = f.relevant_when;
    out[f.stable_code] = rule
      ? out[rule.field_code] && values[rule.field_code] === rule.equals
      : true;
  }
  return out;
}

function Fill({
  base,
  request,
  explain,
  form,
  template,
  canSubmit,
  done,
}: {
  base: string;
  request: Props["request"];
  explain: Props["explain"];
  form: Row;
  template: string;
  canSubmit: boolean;
  done: (text: string) => void;
}) {
  const [version, setVersion] = useState<any>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [unit, setUnit] = useState("");
  const [eventDate, setEventDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [draft, setDraft] = useState<Row | null>(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = usePendingOperations();
  const capturedAt = useRef(new Date().toISOString());
  const saved = useRef("");

  useEffect(() => {
    request(base + "forms/" + form.object_id + "/published")
      .then(setVersion)
      .catch((e) => setError(explain(e)));
  }, [form.object_id]);
  if (!version)
    return error ? (
      <div role="alert" className="error">
        {error}
      </div>
    ) : (
      <p role="status">Loading the published version…</p>
    );
  const fields: Field[] = [...version.data.fields].sort(
    (a: Field, b: Field) => a.position - b.position,
  );
  const shown = relevant(fields, values);

  function answers() {
    const out: Record<string, unknown> = {};
    for (const f of fields) {
      if (!shown[f.stable_code]) continue;
      const reason = reasons[f.stable_code];
      const value = values[f.stable_code];
      if (reason) out[f.stable_code] = { kind: "MISSING", reason };
      else if (value === undefined || value === "") continue;
      else if (f.field_type === "INTEGER")
        out[f.stable_code] = { kind: "INTEGER", value: Number(value) };
      else if (f.field_type === "BOOLEAN")
        out[f.stable_code] = { kind: "BOOLEAN", value: value === "true" };
      else out[f.stable_code] = { kind: f.field_type, value };
    }
    return out;
  }
  async function save(final: boolean) {
    setBusy(true);
    setError("");
    const when = new Date(eventDate + "T12:00:00Z").toISOString();
    const data: Record<string, unknown> = { answers: answers() };
    if (!draft) {
      Object.assign(data, {
        form_version: version.form_version,
        event_at: when,
        captured_at: capturedAt.current,
        capture_zone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
        ...(unit ? { unit_key: unit } : {}),
      });
    }
    try {
      let current = draft;
      const fingerprint = JSON.stringify(data.answers);
      // Unchanged answers since the last server save are not saved again, so a retried submit
      // after a lost response repeats the exact submit command and receives its receipt.
      if (!draft || saved.current !== fingerprint) {
        const saveKey = "save:" + (draft?.object_id || "new");
        const receipt = await command(
          request,
          base + "submissions" + (draft ? "/" + draft.object_id : ""),
          draft ? "PATCH" : "POST",
          pending.id(saveKey, [draft?.revision_id, data]),
          data,
          draft?.revision_id,
        );
        pending.done(saveKey);
        current = await request(base + "submissions/" + receipt.object_id);
        saved.current = fingerprint;
        setDraft(current);
      }
      if (!final) {
        setStatus("Server draft saved. You can resume it from this dialog.");
        return;
      }
      const submitKey = "submit:" + current!.object_id;
      const body = { workflow_version: template };
      const result = await command(
        request,
        base + "submissions/" + current!.object_id + "/actions/submit",
        "POST",
        pending.id(submitKey, [current!.revision_id, body]),
        body,
        current!.revision_id,
      );
      pending.done(submitKey);
      done(
        result.business_state === "Quarantined"
          ? "Response received on a superseded form version and quarantined; nothing was counted."
          : "Response submitted. Its observations are waiting for independent review.",
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save(true);
      }}
    >
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {status && (
        <p role="status" className="success">
          {status}
        </p>
      )}
      <p className="muted">
        Version {version.version_number} · published{" "}
        {version.published_at.slice(0, 10)}
      </p>
      <div className="form-grid">
        <label>
          Reporting unit
          <input
            value={unit}
            disabled={!!draft}
            pattern="[A-Za-z0-9][A-Za-z0-9_.:\-]{0,99}"
            onChange={(e) => setUnit(e.target.value)}
          />
        </label>
        <label>
          Event date
          <input
            type="date"
            required
            disabled={!!draft}
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
          />
        </label>
      </div>
      {fields
        .filter((f) => shown[f.stable_code])
        .map((f) => (
          <fieldset key={f.field_id} className="planning-node-editor">
            <legend>
              {f.label}
              {f.required ? " *" : ""}
            </legend>
            <div className="form-grid">
              {f.field_type === "SINGLE_CHOICE" ? (
                <label>
                  {f.label}
                  <select
                    aria-label={f.label}
                    disabled={!!reasons[f.stable_code]}
                    value={values[f.stable_code] || ""}
                    onChange={(e) =>
                      setValues({ ...values, [f.stable_code]: e.target.value })
                    }
                  >
                    <option value="">Choose</option>
                    {(f.choices || [])
                      .filter((c) => c.active)
                      .map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.label}
                        </option>
                      ))}
                  </select>
                </label>
              ) : f.field_type === "BOOLEAN" ? (
                <label>
                  {f.label}
                  <select
                    aria-label={f.label}
                    disabled={!!reasons[f.stable_code]}
                    value={values[f.stable_code] || ""}
                    onChange={(e) =>
                      setValues({ ...values, [f.stable_code]: e.target.value })
                    }
                  >
                    <option value="">Choose</option>
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                  </select>
                </label>
              ) : (
                <label>
                  {f.label}
                  <input
                    aria-label={f.label}
                    disabled={!!reasons[f.stable_code]}
                    inputMode={
                      f.field_type === "TEXT"
                        ? "text"
                        : f.field_type === "INTEGER"
                          ? "numeric"
                          : "decimal"
                    }
                    value={values[f.stable_code] || ""}
                    onChange={(e) =>
                      setValues({ ...values, [f.stable_code]: e.target.value })
                    }
                  />
                </label>
              )}
              <label>
                {f.label} status
                <select
                  aria-label={f.label + " status"}
                  value={reasons[f.stable_code] || ""}
                  onChange={(e) =>
                    setReasons({ ...reasons, [f.stable_code]: e.target.value })
                  }
                >
                  {MISSING.map(([v, l]) => (
                    <option key={v} value={v}>
                      {l}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </fieldset>
        ))}
      <p className="muted">
        Questions you leave blank are recorded as missing, never as zero.
      </p>
      <button
        type="button"
        className="secondary"
        disabled={busy}
        onClick={() => void save(false)}
      >
        Save draft
      </button>{" "}
      {canSubmit && template && (
        <button className="primary" disabled={busy}>
          Submit response
        </button>
      )}
    </form>
  );
}
