import React, { useEffect, useRef, useState } from "react";
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
const targets: Record<string, string> = {
  Observation: "observations",
  CollectionPlan: "collection-plans",
  IndicatorInstance: "indicator-instances",
};
const name = (r: Row) =>
  r.data.title ||
  r.data.source_key ||
  r.data.local_applicability ||
  r.object_id.slice(0, 8);

export function ChangesPanel({
  base,
  capabilities,
  request,
  explain,
  Dialog,
}: Props) {
  const [rows, setRows] = useState<Row[]>([]),
    [error, setError] = useState("");
  const [resources, setResources] = useState<Record<string, Row[]>>({}),
    [members, setMembers] = useState<any[]>([]);
  const [kind, setKind] = useState("Observation"),
    [target, setTarget] = useState<Row | null>(null);
  const [editing, setEditing] = useState<Row | null | undefined>(undefined);
  const [values, setValues] = useState<Record<string, any>>({}),
    [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false),
    [epoch, setEpoch] = useState(0),
    [notice, setNotice] = useState("");
  const operation = useRef(crypto.randomUUID());
  const can = (cap: string) => capabilities.includes(cap);
  useEffect(() => {
    const controller = new AbortController();
    async function load(route: string) {
      let cursor = "",
        items: Row[] = [];
      do {
        const page = await request(
          base +
            route +
            "?limit=100" +
            (cursor ? "&cursor=" + encodeURIComponent(cursor) : ""),
          { signal: controller.signal },
        );
        items = [...items, ...page.items];
        cursor = page.next_cursor || "";
        if (items.length >= 1000 && cursor)
          throw new Error(
            "More than 1,000 records. Change requests cannot load this entire workspace yet.",
          );
      } while (cursor);
      return items;
    }
    const fail = (e: any) => {
      if (e.name !== "AbortError") setError(explain(e));
    };
    load("measurement-changes")
      .then((r) => {
        if (!controller.signal.aborted) setRows(r);
      })
      .catch(fail);
    Promise.all(
      [...Object.values(targets), "workflow-templates"]
        .filter((r) => can(r + ".read"))
        .map(async (r) => [r, await load(r)] as const),
    )
      .then((x) => {
        if (!controller.signal.aborted) setResources(Object.fromEntries(x));
      })
      .catch(fail);
    if (can("measurement-members.read"))
      request(base + "measurement-members", { signal: controller.signal })
        .then((x) => {
          if (!controller.signal.aborted) setMembers(x.items);
        })
        .catch(fail);
    return () => controller.abort();
  }, [base, epoch, capabilities]);
  function select(row: Row | null, selectedKind = kind) {
    setTarget(row);
    if (!row) {
      setValues({});
      return;
    }
    const fields =
      selectedKind === "Observation"
        ? ["value", "numerator", "denominator", "source_version"]
        : selectedKind === "CollectionPlan"
          ? ["title", "obligations"]
          : ["collector_id", "reviewer_id"];
    setValues(
      Object.fromEntries(
        fields
          .filter((f) => row.data[f] !== undefined)
          .map((f) => [f, row.data[f]]),
      ),
    );
  }
  async function save(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      const proposed = Object.fromEntries(
        Object.entries(values).filter(
          ([k, v]) => JSON.stringify(v) !== JSON.stringify(target.data[k]),
        ),
      );
      if (!Object.keys(proposed).length)
        throw new Error("Change at least one value before saving.");
      await request(
        base + "measurement-changes" + (editing ? "/" + editing.object_id : ""),
        {
          method: editing ? "PATCH" : "POST",
          body: JSON.stringify({
            operation_id: operation.current,
            ...(editing ? { expected_revision: editing.revision_id } : {}),
            data: {
              target_kind: kind,
              target_id: target.object_id,
              target_revision: target.revision_id,
              reason,
              proposed_data: proposed,
            },
          }),
        },
      );
      setEditing(undefined);
      setEpoch((x) => x + 1);
      setNotice("Change request saved. Submit it for independent review.");
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  async function submit(row: Row, template: string) {
    if (!template) return;
    setBusy(true);
    setError("");
    try {
      await request(
        base + "measurement-changes/" + row.object_id + "/actions/submit",
        {
          method: "POST",
          body: JSON.stringify({
            operation_id: crypto.randomUUID(),
            expected_revision: row.revision_id,
            data: { workflow_version: template },
          }),
        },
      );
      setEpoch((x) => x + 1);
      setNotice(
        "Submitted. An independent reviewer can decide in the Review queue.",
      );
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section aria-label="Governed measurement changes">
      <p>
        Approved values remain effective until an independent reviewer approves
        a change. Affected live results are marked stale and assigned for
        recalculation; locked snapshots stay unchanged.
      </p>
      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}
      {notice && (
        <div role="status" className="success">
          {notice}
        </div>
      )}
      {can("measurement-changes.draft.create") && (
        <button
          className="primary"
          onClick={() => {
            setEditing(null);
            setReason("");
            select(null);
            operation.current = crypto.randomUUID();
            setError("");
          }}
        >
          New change request
        </button>
      )}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Request</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Next step</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.object_id}>
                <td>
                  {row.data.target_kind} · {row.data.target_id.slice(0, 8)}
                  <details>
                    <summary>Proposed changes</summary>
                    <pre>{JSON.stringify(row.data.proposed_data, null, 2)}</pre>
                  </details>
                </td>
                <td>{row.data.reason}</td>
                <td>{row.lifecycle_state}</td>
                <td>
                  {["Draft", "Returned"].includes(row.lifecycle_state) && (
                    <>
                      {can("measurement-changes.draft.edit") && (
                        <button
                          onClick={() => {
                            const k = row.data.target_kind;
                            setKind(k);
                            const t = resources[targets[k]]?.find(
                              (x) => x.object_id === row.data.target_id,
                            );
                            if (!t) {
                              setError(
                                "Target unavailable. Refresh and check your access.",
                              );
                              return;
                            }
                            select(t, k);
                            setValues((v) => ({
                              ...v,
                              ...row.data.proposed_data,
                            }));
                            setReason(row.data.reason);
                            setEditing(row);
                            operation.current = crypto.randomUUID();
                          }}
                        >
                          Edit request
                        </button>
                      )}
                      {can("measurement-changes.submit") && (
                        <form
                          onSubmit={(e) => {
                            e.preventDefault();
                            void submit(
                              row,
                              String(
                                new FormData(e.currentTarget).get("template"),
                              ),
                            );
                          }}
                        >
                          <label>
                            Review policy
                            <select
                              aria-label="Review policy"
                              name="template"
                              required
                              defaultValue=""
                            >
                              <option value="">Choose policy</option>
                              {resources["workflow-templates"]
                                ?.filter((t) => t.lifecycle_state === "Active")
                                .map((t) => (
                                  <option
                                    key={t.object_id}
                                    value={t.revision_id}
                                  >
                                    {name(t)}
                                  </option>
                                ))}
                            </select>
                          </label>
                          <button disabled={busy}>Submit for review</button>
                        </form>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length && <p>No change requests yet.</p>}
      </div>
      {editing !== undefined && (
        <Dialog
          title={editing ? "Edit change request" : "New change request"}
          close={() => {
            if (!busy) setEditing(undefined);
          }}
        >
          <form onSubmit={save}>
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            <label>
              Change type
              <select
                aria-label="Change type"
                value={kind}
                onChange={(e) => {
                  setKind(e.target.value);
                  select(null);
                }}
              >
                <option value="Observation">
                  Correct approved measurement
                </option>
                <option value="CollectionPlan">Amend collection plan</option>
                <option value="IndicatorInstance">
                  Reassign responsibilities
                </option>
              </select>
            </label>
            <label>
              Approved record
              <select
                aria-label="Approved record"
                required
                value={target?.object_id || ""}
                onChange={(e) =>
                  select(
                    resources[targets[kind]]?.find(
                      (x) => x.object_id === e.target.value,
                    ) || null,
                  )
                }
              >
                <option value="">Choose record</option>
                {resources[targets[kind]]
                  ?.filter(
                    (r) =>
                      r.lifecycle_state ===
                      (kind === "IndicatorInstance" ? "Active" : "Approved"),
                  )
                  .map((r) => (
                    <option key={r.object_id} value={r.object_id}>
                      {name(r)}
                    </option>
                  ))}
              </select>
            </label>
            {target && (
              <>
                {kind === "Observation" && (
                  <>
                    {["value", "numerator", "denominator", "source_version"]
                      .filter((f) => f in values && values[f] !== null)
                      .map((f) => (
                        <label key={f}>
                          {
                            (
                              {
                                value: "Corrected value",
                                numerator: "Corrected numerator",
                                denominator: "Corrected denominator",
                                source_version: "Source version",
                              } as Record<string, string>
                            )[f]
                          }
                          <input
                            required
                            value={values[f]}
                            onChange={(e) =>
                              setValues({ ...values, [f]: e.target.value })
                            }
                          />
                        </label>
                      ))}
                  </>
                )}
                {kind === "CollectionPlan" && (
                  <>
                    <label>
                      Plan title
                      <input
                        required
                        value={values.title || ""}
                        onChange={(e) =>
                          setValues({ ...values, title: e.target.value })
                        }
                      />
                    </label>
                    <p>
                      Existing obligations remain in history. Add contributors,
                      correct details, or record a reviewed eligibility
                      exception with its reason and effective time.
                    </p>
                    {values.obligations?.map((o: any, i: number) => (
                      <fieldset key={i}>
                        <legend>Contributor {i + 1}</legend>
                        {[
                          "label",
                          "source_namespace",
                          "source_key",
                          "due_at",
                        ].map((f) => (
                          <label key={f}>
                            {f.replaceAll("_", " ")}
                            <input
                              required
                              readOnly={
                                i < target.data.obligations.length &&
                                ["source_namespace", "source_key"].includes(f)
                              }
                              value={o[f]}
                              onChange={(e) =>
                                setValues({
                                  ...values,
                                  obligations: values.obligations.map(
                                    (v: any, j: number) =>
                                      j === i
                                        ? { ...v, [f]: e.target.value }
                                        : v,
                                  ),
                                })
                              }
                            />
                          </label>
                        ))}
                        <label>
                          Eligibility
                          <select
                            aria-label={`Contributor ${i + 1} eligibility`}
                            value={o.eligibility || "REQUIRED"}
                            onChange={(e) =>
                              setValues({
                                ...values,
                                obligations: values.obligations.map(
                                  (v: any, j: number) => {
                                    if (j !== i) return v;
                                    if (e.target.value === "EXCEPTED")
                                      return {
                                        ...v,
                                        eligibility: "EXCEPTED",
                                        exclusion_reason:
                                          v.exclusion_reason || "",
                                        exclusion_effective_at:
                                          v.exclusion_effective_at ||
                                          new Date().toISOString(),
                                      };
                                    const next = {
                                      ...v,
                                      eligibility: "REQUIRED",
                                    };
                                    delete next.exclusion_reason;
                                    delete next.exclusion_effective_at;
                                    return next;
                                  },
                                ),
                              })
                            }
                          >
                            <option value="REQUIRED">Required</option>
                            <option value="EXCEPTED">
                              Excepted after review
                            </option>
                          </select>
                        </label>
                        {(o.eligibility || "REQUIRED") === "EXCEPTED" && (
                          <>
                            <label>
                              Exclusion reason
                              <textarea
                                required
                                maxLength={2000}
                                value={o.exclusion_reason || ""}
                                onChange={(e) =>
                                  setValues({
                                    ...values,
                                    obligations: values.obligations.map(
                                      (v: any, j: number) =>
                                        j === i
                                          ? {
                                              ...v,
                                              exclusion_reason: e.target.value,
                                            }
                                          : v,
                                    ),
                                  })
                                }
                              />
                            </label>
                            <label>
                              Exclusion effective time (UTC)
                              <input
                                required
                                value={o.exclusion_effective_at || ""}
                                onChange={(e) =>
                                  setValues({
                                    ...values,
                                    obligations: values.obligations.map(
                                      (v: any, j: number) =>
                                        j === i
                                          ? {
                                              ...v,
                                              exclusion_effective_at:
                                                e.target.value,
                                            }
                                          : v,
                                    ),
                                  })
                                }
                              />
                            </label>
                          </>
                        )}
                      </fieldset>
                    ))}
                    <button
                      type="button"
                      onClick={() =>
                        setValues({
                          ...values,
                          obligations: [
                            ...values.obligations,
                            {
                              label: "",
                              source_namespace: "MANUAL",
                              source_key: "",
                              due_at: target.data.obligations[0].due_at,
                              eligibility: "REQUIRED",
                            },
                          ],
                        })
                      }
                    >
                      Add contributor
                    </button>
                  </>
                )}
                {kind === "IndicatorInstance" && (
                  <>
                    <p>
                      Approval reassigns future collection and pending
                      observation reviews. Existing decisions keep their
                      original reviewer.
                    </p>
                    {["collector_id", "reviewer_id"].map((f) => (
                      <label key={f}>
                        {f === "collector_id" ? "Collector" : "Reviewer"}
                        <select
                          aria-label={
                            f === "collector_id" ? "Collector" : "Reviewer"
                          }
                          required
                          value={values[f] || ""}
                          onChange={(e) =>
                            setValues({ ...values, [f]: e.target.value })
                          }
                        >
                          <option value="">Choose eligible member</option>
                          {members
                            .filter(
                              (m) =>
                                m[
                                  f === "collector_id"
                                    ? "collector"
                                    : "reviewer"
                                ],
                            )
                            .map((m) => (
                              <option
                                key={m.principal_id}
                                value={m.principal_id}
                              >
                                {m.display_name}
                              </option>
                            ))}
                        </select>
                      </label>
                    ))}
                  </>
                )}
              </>
            )}
            <label>
              Reason for change
              <textarea
                required
                maxLength={2000}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </label>
            <button className="primary" disabled={busy || !target}>
              Save change request
            </button>
          </form>
        </Dialog>
      )}
    </section>
  );
}
