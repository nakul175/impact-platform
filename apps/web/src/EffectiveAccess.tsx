import { useEffect, useState, type FormEvent } from "react";

type Requester = (path: string, options?: RequestInit) => Promise<any>;
type Props = {
  base: string;
  request: Requester;
  explain: (error: unknown) => string;
  simulation?: boolean;
};

const operations = [
  ["list_programmes", "List programmes"],
  ["get_programmes", "Read a programme"],
  ["list_observations", "List observations"],
  ["get_observations", "Read an observation"],
  ["list_reports", "List reports"],
  ["get_reports", "Read a report"],
  ["list_dashboards", "List dashboards"],
  ["preview_dashboards", "Preview a dashboard"],
];

const words = (value: string) =>
  value
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/^./, (c) => c.toUpperCase());

export function EffectiveAccessPanel({
  base,
  request,
  explain,
  simulation = false,
}: Props) {
  const [operationId, setOperationId] = useState(operations[0][0]);
  const [objectId, setObjectId] = useState("");
  const [purpose, setPurpose] = useState("");
  const [fieldCategory, setFieldCategory] = useState("");
  const [fieldAccess, setFieldAccess] = useState<"READ" | "WRITE">("READ");
  const [members, setMembers] = useState<any[]>([]);
  const [subject, setSubject] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!simulation) return;
    const controller = new AbortController();
    request(base + "membership-directory?limit=100", {
      signal: controller.signal,
    })
      .then((page) => {
        if (controller.signal.aborted) return;
        setMembers(page.items || []);
        setSubject((current) => current || page.items?.[0]?.principal_id || "");
      })
      .catch((cause) => {
        if (!controller.signal.aborted) setError(explain(cause));
      });
    return () => controller.abort();
  }, [base, request, explain, simulation]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setResult(null);
    const body: Record<string, unknown> = {
      operation_id: operationId,
      object_id: objectId || null,
      purpose: purpose || null,
      field_category: fieldCategory || null,
      field_access: fieldCategory ? fieldAccess : null,
    };
    if (simulation) body.subject_principal_id = subject;
    try {
      setResult(
        await request(
          base +
            (simulation
              ? "access/effective/simulations"
              : "access/effective/self"),
          { method: "POST", body: JSON.stringify(body) },
        ),
      );
    } catch (cause) {
      setError(explain(cause));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      className="panel"
      aria-label={simulation ? "Simulate member access" : "Explain my access"}
    >
      <h2>{simulation ? "Simulate member access" : "Explain my access"}</h2>
      <p>
        This explanation uses current authority and shows only safe scope and
        restriction codes. It does not reveal protected record names or values.
      </p>
      <form onSubmit={submit}>
        <fieldset>
          <legend>Access context</legend>
          {simulation ? (
            <label>
              Member
              <select
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                required
              >
                {!members.length ? (
                  <option value="">No members available</option>
                ) : null}
                {members.map((member) => (
                  <option key={member.principal_id} value={member.principal_id}>
                    {member.display_name ||
                      member.email_mask ||
                      "Current member"}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label>
            Action
            <select
              value={operationId}
              onChange={(event) => setOperationId(event.target.value)}
            >
              {operations.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Record ID (optional)
            <input
              value={objectId}
              onChange={(event) => setObjectId(event.target.value)}
              placeholder="UUID"
            />
          </label>
          <label>
            Stated purpose (optional)
            <input
              value={purpose}
              onChange={(event) => setPurpose(event.target.value)}
              maxLength={100}
            />
          </label>
          <label>
            Field category (optional)
            <select
              value={fieldCategory}
              onChange={(event) => setFieldCategory(event.target.value)}
            >
              <option value="">No field check</option>
              <option>PUBLIC</option>
              <option>INTERNAL</option>
              <option>SENSITIVE</option>
              <option>DIRECT_IDENTIFIER</option>
            </select>
          </label>
          {fieldCategory ? (
            <label>
              Field access
              <select
                value={fieldAccess}
                onChange={(event) =>
                  setFieldAccess(event.target.value as "READ" | "WRITE")
                }
              >
                <option>READ</option>
                <option>WRITE</option>
              </select>
            </label>
          ) : null}
          <button type="submit" disabled={busy || (simulation && !subject)}>
            {busy
              ? "Checking…"
              : simulation
                ? "Simulate access"
                : "Explain my access"}
          </button>
        </fieldset>
      </form>
      {error ? (
        <div className="error" role="alert">
          {error}
        </div>
      ) : null}
      <div aria-live="polite">
        {result ? (
          <div>
            <p>
              <strong>{words(result.decision)}</strong> · {result.capability}
            </p>
            {result.restrictions.length ? (
              <p>Restrictions: {result.restrictions.map(words).join(", ")}</p>
            ) : null}
            {result.missing_assurance.length ? (
              <p>
                Still required: {result.missing_assurance.map(words).join(", ")}
              </p>
            ) : null}
            <table>
              <thead>
                <tr>
                  <th>Path</th>
                  <th>Source</th>
                  <th>Scope</th>
                  <th>Decision</th>
                  <th>Restrictions</th>
                </tr>
              </thead>
              <tbody>
                {result.grant_paths.map((path: any) => (
                  <tr key={path.path_id}>
                    <td>{path.path_id}</td>
                    <td>{words(path.source)}</td>
                    <td>{words(path.scope_type)}</td>
                    <td>{words(path.decision)}</td>
                    <td>
                      {path.restrictions.length
                        ? path.restrictions.map(words).join(", ")
                        : "None"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </section>
  );
}
