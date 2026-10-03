import React, { useEffect, useState } from "react";
import { Fill } from "./Forms";
import { usePendingOperations } from "./operations";

type Row = {
  object_id: string;
  revision_id: string;
  lifecycle_state: string;
  data: Record<string, any>;
};
type Props = {
  base: string;
  principalId: string;
  capabilities: string[];
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (e: unknown) => string;
  Dialog: React.ComponentType<{
    title: string;
    close: () => void;
    children: React.ReactNode;
  }>;
};
type Coverage = {
  coverage_state: string;
  coverage_percent: string | null;
  expected_count: number;
  assigned_count: number;
  received_count: number;
  unassigned_count: number;
  units: {
    unit_key: string;
    assignment_id: string | null;
    assignee_id: string | null;
    assignment_state: string | null;
    received: boolean;
  }[];
};
const dateInput = (value?: string) => {
  if (!value) return "";
  const date = new Date(value);
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
};
const utcDate = (value: string) => new Date(value).toISOString();
const unitsOf = (value: string) => [
  ...new Set(
    value
      .split(/[\s,]+/)
      .map((unit) => unit.trim())
      .filter(Boolean),
  ),
];

export function RoundsPanel({
  base,
  principalId,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const allowed = (cap: string) => capabilities.includes(cap);
  const [rounds, setRounds] = useState<Row[]>([]);
  const [assignments, setAssignments] = useState<Row[]>([]);
  const [forms, setForms] = useState<Row[]>([]);
  const [periods, setPeriods] = useState<Row[]>([]);
  const [members, setMembers] = useState<
    { principal_id: string; display_name: string }[]
  >([]);
  const [published, setPublished] = useState<Record<string, string>>({});
  const [coverage, setCoverage] = useState<Record<string, Coverage>>({});
  const [dialog, setDialog] = useState<
    | { mode: "round"; row?: Row }
    | { mode: "assign"; round: Row; unit_key: string }
    | { mode: "reassign"; row: Row }
    | { mode: "collect"; row: Row; form: Row }
    | null
  >(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [tick, setTick] = useState(0);
  const [template, setTemplate] = useState("");
  const operations = usePendingOperations();

  useEffect(() => {
    let active = true;
    const list = (route: string) =>
      request(base + route + "?limit=100").then((page) => page.items);
    // One unavailable optional list must not hide forms and periods needed to create a round.
    const guarded = (cap: string, route: string) =>
      allowed(cap)
        ? list(route).catch((e) => {
            if (active) setError(`${route}: ${explain(e)}`);
            return [];
          })
        : Promise.resolve([]);
    Promise.all([
      guarded("collection-rounds.read", "collection-rounds"),
      guarded("assignments.read", "assignments"),
      guarded("forms.read", "forms"),
      guarded("periods.read", "periods"),
      guarded("memberships.read", "membership-directory"),
      request(base + "workflow-templates?limit=10").catch(() => ({
        items: [],
      })),
    ])
      .then(([r, a, f, p, m, t]) => {
        if (!active) return;
        setRounds(r);
        setAssignments(a);
        setForms(f);
        setPeriods(p);
        setMembers(m.filter((member: any) => member.state === "Active"));
        setTemplate(t.items[0]?.revision_id || "");
      })
      .catch((e) => active && setError(explain(e)));
    return () => {
      active = false;
    };
  }, [base, tick]);

  useEffect(() => {
    let active = true;
    Promise.all(
      forms.map((form) =>
        request(base + "forms/" + form.object_id + "/published")
          .then((version) => [form.object_id, version.form_version] as const)
          .catch(() => null),
      ),
    ).then((rows) => {
      if (active)
        setPublished(Object.fromEntries(rows.filter((row) => row !== null)));
    });
    return () => {
      active = false;
    };
  }, [base, forms]);

  async function showCoverage(row: Row) {
    try {
      const result = await request(
        base + "collection-rounds/" + row.object_id + "/coverage",
      );
      setCoverage((current) => ({ ...current, [row.object_id]: result }));
      setError("");
    } catch (e) {
      setError(explain(e));
    }
  }

  async function save(route: string, method: string, data: unknown, row?: Row) {
    const key = method + ":" + route + ":" + (row?.object_id || "new");
    setBusy(true);
    setError("");
    try {
      await request(base + route + (row ? "/" + row.object_id : ""), {
        method,
        body: JSON.stringify({
          operation_id: operations.id(key, [row?.revision_id, data]),
          ...(row ? { expected_revision: row.revision_id } : {}),
          data,
        }),
      });
      operations.done(key);
      setMessage(
        "Saved. Current grants and eligibility were checked by the server.",
      );
      setDialog(null);
      setCoverage({});
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }

  async function reassign(row: Row, assignee_id: string, reason: string) {
    const key = "reassign:" + row.object_id;
    setBusy(true);
    setError("");
    try {
      await request(
        base + "assignments/" + row.object_id + "/actions/reassign",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: operations.id(key, [
              row.revision_id,
              assignee_id,
              reason,
            ]),
            expected_revision: row.revision_id,
            data: { assignee_id, reason },
          }),
        },
      );
      operations.done(key);
      setDialog(null);
      setMessage(
        "Assignment moved. The previous holder can no longer submit it.",
      );
      setCoverage({});
      setTick((value) => value + 1);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }

  const names = (id?: string) =>
    members.find((member) => member.principal_id === id)?.display_name ||
    (id ? "Member " + id.slice(0, 8) : "Unassigned");
  const openAssignments = assignments.filter(
    (row) => row.lifecycle_state === "Draft",
  );

  return (
    <>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {message && (
        <p className="success" role="status">
          {message}
        </p>
      )}
      <section className="panel">
        <div className="setup-heading">
          <div>
            <h2>Collection rounds</h2>
            <p className="muted">
              Set expected units against a published form and a reporting
              period. Coverage counts submitted responses; it does not approve
              their observations.
            </p>
          </div>
          {allowed("collection-rounds.draft.create") && (
            <button
              className="primary"
              onClick={() => setDialog({ mode: "round" })}
            >
              New round
            </button>
          )}
        </div>
        {!allowed("collection-rounds.read") ? (
          <p>Round details require collection-rounds.read access.</p>
        ) : !rounds.length ? (
          <p>No collection rounds are visible.</p>
        ) : (
          <div
            className="table-wrap"
            role="region"
            aria-label="Collection rounds"
            tabIndex={0}
          >
            <table>
              <thead>
                <tr>
                  <th>Round</th>
                  <th>Due</th>
                  <th>Expected</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rounds.map((row) => (
                  <React.Fragment key={row.object_id}>
                    <tr>
                      <td>{row.data.title}</td>
                      <td>{row.data.due_at?.slice(0, 10)}</td>
                      <td>{row.data.expected_units?.length || 0}</td>
                      <td>
                        <button
                          className="secondary"
                          onClick={() => void showCoverage(row)}
                        >
                          Coverage
                        </button>{" "}
                        {allowed("collection-rounds.draft.edit") && (
                          <button
                            className="secondary"
                            onClick={() => setDialog({ mode: "round", row })}
                          >
                            Edit
                          </button>
                        )}
                      </td>
                    </tr>
                    {coverage[row.object_id] && (
                      <tr>
                        <td colSpan={4}>
                          <p role="status">
                            {coverage[row.object_id].coverage_state ===
                            "NOT_APPLICABLE"
                              ? "No units expected · coverage not applicable"
                              : `${coverage[row.object_id].received_count} of ${coverage[row.object_id].expected_count} received (${coverage[row.object_id].coverage_percent}%)`}
                            {" · "}
                            {coverage[row.object_id].unassigned_count}{" "}
                            unassigned
                          </p>
                          <div
                            className="table-wrap"
                            role="region"
                            aria-label={row.data.title + " units"}
                            tabIndex={0}
                          >
                            <table>
                              <thead>
                                <tr>
                                  <th>Unit</th>
                                  <th>Holder</th>
                                  <th>State</th>
                                  <th>Response</th>
                                  <th>Action</th>
                                </tr>
                              </thead>
                              <tbody>
                                {coverage[row.object_id].units.map((unit) => (
                                  <tr key={unit.unit_key}>
                                    <td>{unit.unit_key}</td>
                                    <td>
                                      {names(unit.assignee_id || undefined)}
                                    </td>
                                    <td>
                                      {unit.assignment_state || "Unassigned"}
                                    </td>
                                    <td>
                                      {unit.received ? "Submitted" : "Missing"}
                                    </td>
                                    <td>
                                      {!unit.assignment_id &&
                                        allowed("assignments.draft.create") && (
                                          <button
                                            className="secondary"
                                            onClick={() =>
                                              setDialog({
                                                mode: "assign",
                                                round: row,
                                                unit_key: unit.unit_key,
                                              })
                                            }
                                          >
                                            Assign
                                          </button>
                                        )}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      {allowed("assignments.read") && (
        <section className="panel">
          <h2>Assignments</h2>
          <p className="muted">
            Collectors see only tasks they hold. Managers see assignments within
            their read access.
          </p>
          {!assignments.length ? (
            <p>No assignments are visible.</p>
          ) : (
            <div
              className="table-wrap"
              role="region"
              aria-label="Assignments"
              tabIndex={0}
            >
              <table>
                <thead>
                  <tr>
                    <th>Unit</th>
                    <th>Holder</th>
                    <th>Due</th>
                    <th>State</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {assignments.map((row) => {
                    const round = rounds.find(
                      (r) => r.object_id === row.data.round_id,
                    );
                    const form =
                      round &&
                      forms.find((f) => f.object_id === round.data.form_id);
                    return (
                      <tr key={row.object_id}>
                        <td>{row.data.unit_key || "Legacy task"}</td>
                        <td>{names(row.data.assignee_id)}</td>
                        <td>{row.data.due_at?.slice(0, 10)}</td>
                        <td>
                          {row.lifecycle_state === "Draft"
                            ? "Open"
                            : row.lifecycle_state}
                        </td>
                        <td>
                          {row.lifecycle_state === "Draft" &&
                            row.data.assignee_id === principalId &&
                            form &&
                            allowed("submissions.draft.create") && (
                              <button
                                className="primary"
                                onClick={() =>
                                  setDialog({ mode: "collect", row, form })
                                }
                              >
                                Collect
                              </button>
                            )}{" "}
                          {row.lifecycle_state === "Draft" &&
                            allowed("assignment.reassign") && (
                              <button
                                className="secondary"
                                onClick={() =>
                                  setDialog({ mode: "reassign", row })
                                }
                              >
                                Reassign
                              </button>
                            )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          {openAssignments.length === 100 && (
            <p className="muted">Showing the first 100 assignments.</p>
          )}
        </section>
      )}
      {dialog?.mode === "round" && (
        <Dialog
          title={dialog.row ? "Edit collection round" : "New collection round"}
          close={() => setDialog(null)}
        >
          <RoundEditor
            row={dialog.row}
            forms={forms}
            periods={periods}
            published={published}
            busy={busy}
            save={(data) =>
              save(
                "collection-rounds",
                dialog.row ? "PATCH" : "POST",
                data,
                dialog.row,
              )
            }
          />
        </Dialog>
      )}
      {dialog?.mode === "assign" && (
        <Dialog
          title={"Assign " + dialog.unit_key}
          close={() => setDialog(null)}
        >
          <AssignmentEditor
            members={members}
            due={dialog.round.data.due_at}
            busy={busy}
            save={(assignee_id, due_at) =>
              save("assignments", "POST", {
                round_id: dialog.round.object_id,
                form_version: dialog.round.data.form_version,
                unit_key: dialog.unit_key,
                assignee_id,
                due_at,
              })
            }
          />
        </Dialog>
      )}
      {dialog?.mode === "reassign" && (
        <Dialog
          title={"Reassign " + dialog.row.data.unit_key}
          close={() => setDialog(null)}
        >
          <ReassignmentEditor
            members={members}
            current={dialog.row.data.assignee_id}
            busy={busy}
            save={(assignee, reason) => reassign(dialog.row, assignee, reason)}
          />
        </Dialog>
      )}
      {dialog?.mode === "collect" && (
        <Dialog
          title={"Collect " + dialog.row.data.unit_key}
          close={() => setDialog(null)}
        >
          <Fill
            base={base}
            request={request}
            explain={explain}
            form={dialog.form}
            assignment={dialog.row}
            template={template}
            canSubmit={
              allowed("submission.submit") &&
              (!(dialog.form.data.fields || []).some(
                (field: any) => field.indicator_id,
              ) ||
                (allowed("observation.submit") &&
                  allowed("indicator-instances.read")))
            }
            done={(text) => {
              setDialog(null);
              setMessage(text);
              setTick((value) => value + 1);
            }}
          />
        </Dialog>
      )}
    </>
  );
}

function RoundEditor({
  row,
  forms,
  periods,
  published,
  busy,
  save,
}: {
  row?: Row;
  forms: Row[];
  periods: Row[];
  published: Record<string, string>;
  busy: boolean;
  save: (data: unknown) => Promise<void>;
}) {
  const [form, setForm] = useState(row?.data.form_id || "");
  const [period, setPeriod] = useState(row?.data.period_id || "");
  const [title, setTitle] = useState(row?.data.title || "");
  const [due, setDue] = useState(dateInput(row?.data.due_at));
  const [units, setUnits] = useState(
    (row?.data.expected_units || []).join("\n"),
  );
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void save(
          row
            ? { title, due_at: utcDate(due), expected_units: unitsOf(units) }
            : {
                form_id: form,
                form_version: published[form],
                period_id: period,
                title,
                due_at: utcDate(due),
                expected_units: unitsOf(units),
              },
        );
      }}
    >
      {!row && (
        <div className="form-grid">
          <label>
            Published form
            <select
              aria-label="Published form"
              required
              value={form}
              onChange={(e) => setForm(e.target.value)}
            >
              <option value="">Choose a form</option>
              {forms
                .filter((f) => published[f.object_id])
                .map((f) => (
                  <option key={f.object_id} value={f.object_id}>
                    {f.data.title}
                  </option>
                ))}
            </select>
          </label>
          <label>
            Period
            <select
              aria-label="Period"
              required
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            >
              <option value="">Choose a period</option>
              {periods.map((p) => (
                <option key={p.object_id} value={p.object_id}>
                  {p.data.title || p.data.code || p.object_id.slice(0, 8)}
                </option>
              ))}
            </select>
          </label>
        </div>
      )}
      <div className="form-grid">
        <label>
          Title
          <input
            required
            maxLength={200}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        <label>
          Due date and time
          <input
            required
            type="datetime-local"
            value={due}
            onChange={(e) => setDue(e.target.value)}
          />
        </label>
      </div>
      <label>
        Expected unit keys, one per line
        <textarea
          value={units}
          onChange={(e) => setUnits(e.target.value)}
          rows={6}
        />
      </label>
      <p className="muted">
        Existing assigned units cannot be removed. Dates use your local time
        zone.
      </p>
      <button
        className="primary"
        disabled={busy || (!row && (!published[form] || !period))}
      >
        Save round
      </button>
    </form>
  );
}

function AssignmentEditor({
  members,
  due,
  busy,
  save,
}: {
  members: { principal_id: string; display_name: string }[];
  due: string;
  busy: boolean;
  save: (assignee: string, due: string) => Promise<void>;
}) {
  const [assignee, setAssignee] = useState("");
  const [date, setDate] = useState(dateInput(due));
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save(assignee, utcDate(date));
      }}
    >
      <MemberField members={members} value={assignee} change={setAssignee} />
      <label>
        Due date and time
        <input
          required
          type="datetime-local"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </label>
      <p className="muted">
        The server checks that the member is active and can submit responses. An
        assignment grants no access.
      </p>
      <button className="primary" disabled={busy}>
        Assign unit
      </button>
    </form>
  );
}

function ReassignmentEditor({
  members,
  current,
  busy,
  save,
}: {
  members: { principal_id: string; display_name: string }[];
  current: string;
  busy: boolean;
  save: (assignee: string, reason: string) => Promise<void>;
}) {
  const [assignee, setAssignee] = useState("");
  const [reason, setReason] = useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save(assignee, reason);
      }}
    >
      <MemberField
        members={members.filter((m) => m.principal_id !== current)}
        value={assignee}
        change={setAssignee}
      />
      <label>
        Reason
        <textarea
          required
          maxLength={2000}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
        />
      </label>
      <button className="primary" disabled={busy || !reason.trim()}>
        Reassign
      </button>
    </form>
  );
}

function MemberField({
  members,
  value,
  change,
}: {
  members: { principal_id: string; display_name: string }[];
  value: string;
  change: (value: string) => void;
}) {
  return (
    <label>
      Member
      {members.length ? (
        <select required value={value} onChange={(e) => change(e.target.value)}>
          <option value="">Choose a member</option>
          {members.map((member) => (
            <option key={member.principal_id} value={member.principal_id}>
              {member.display_name}
            </option>
          ))}
        </select>
      ) : (
        <input
          required
          type="text"
          pattern="[a-fA-F0-9-]{36}"
          value={value}
          onChange={(e) => change(e.target.value)}
          placeholder="Member principal ID"
        />
      )}
    </label>
  );
}
