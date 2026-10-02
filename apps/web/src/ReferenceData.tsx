import { useRef, useState, type FormEvent } from "react";

type Props = {
  base: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};
const slug = (text: string, index: number) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 60) || "section_" + (index + 1);

// Reference data of a workspace (v0.26a): the reporting calendar with its periods, the review
// (workflow) template, report templates and geographies that programmes, forms, imports, targets,
// period close and reports need. Governed tenant-administration commands: a stated reason, a recent
// sign-in, an audit record.
export function ReferenceDataPanel({ base, request, explain }: Props) {
  const [mode, setMode] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const retry = useRef({ key: "", operation: "" });
  async function send(route: string, data: any, success: string) {
    setBusy(true);
    setError("");
    setNotice("");
    const key = JSON.stringify([route, data]);
    if (retry.current.key !== key)
      retry.current = { key, operation: crypto.randomUUID() };
    try {
      await request(base + route, {
        method: "POST",
        body: JSON.stringify({ operation_id: retry.current.operation, data }),
      });
      retry.current = { key: "", operation: "" };
      setMode("");
      setNotice(success);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const get = (k: string) => String(form.get(k) || "").trim();
    const reason = get("reason");
    if (mode === "calendar")
      send(
        "reporting-calendars",
        {
          title: get("title"),
          frequency: get("frequency"),
          zone: get("zone"),
          first_year: Number(get("first_year")),
          years: Number(get("years")),
          reason,
        },
        "Calendar and its periods created.",
      );
    else if (mode === "workflow")
      send(
        "workflow-templates",
        { title: get("title"), reason },
        "Review template created: one independent approval by a different person.",
      );
    else if (mode === "report")
      send(
        "report-templates",
        {
          title: get("title"),
          language: get("language"),
          sections: get("sections")
            .split("\n")
            .map((line) => line.trim())
            .filter(Boolean)
            .map((heading, index) => ({
              section_code: slug(heading, index),
              heading,
              required: true,
              narrative_limit: 4000,
            })),
          reason,
        },
        "Report template created.",
      );
    else if (mode === "geography")
      send(
        "geographies",
        { title: get("title"), code: get("code"), reason },
        "Geography created.",
      );
  }
  const year = new Date().getFullYear();
  return (
    <section className="panel" aria-label="Reference data">
      <h2>Reference data</h2>
      <p>
        Programmes need a reporting calendar and a geography; submissions, forms
        and imports need a review template; reports need a report template. The
        standard set adds a quarterly calendar for this year and next in the
        workspace's reporting time zone, a review template with one independent
        approval, a standard results report template and an organisation-wide
        geography.
      </p>
      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="success" role="status">
          {notice}
        </div>
      )}
      <div className="toolbar">
        <button
          className="primary"
          disabled={busy}
          onClick={() =>
            send(
              "reference-defaults",
              {
                reason:
                  "Standard reference data for this workspace (calendar, review and report templates, geography)",
              },
              "Standard reference data set up: 8 quarterly periods, a review template, a report template and a geography.",
            )
          }
        >
          {busy ? "Saving…" : "Set up the standard reference data"}
        </button>
        {[
          ["calendar", "Add a calendar"],
          ["workflow", "Add a review template"],
          ["report", "Add a report template"],
          ["geography", "Add a geography"],
        ].map(([key, label]) => (
          <button
            key={key}
            className="secondary"
            onClick={() => {
              setMode(key);
              setError("");
            }}
          >
            {label}
          </button>
        ))}
      </div>
      {mode && (
        <form onSubmit={submit} className="panel" aria-label="Reference data">
          <label>
            Title
            <input name="title" required maxLength={120} />
          </label>
          {mode === "calendar" && (
            <>
              <label>
                Frequency
                <select name="frequency" defaultValue="QUARTERLY">
                  <option value="MONTHLY">Monthly</option>
                  <option value="QUARTERLY">Quarterly</option>
                  <option value="ANNUAL">Annual</option>
                </select>
              </label>
              <label>
                Reporting time zone
                <input
                  name="zone"
                  required
                  maxLength={80}
                  defaultValue="Asia/Kolkata"
                />
              </label>
              <label>
                First year
                <input
                  name="first_year"
                  type="number"
                  min={2000}
                  max={2100}
                  defaultValue={year}
                  required
                />
              </label>
              <label>
                Number of years
                <input
                  name="years"
                  type="number"
                  min={1}
                  max={5}
                  defaultValue={2}
                  required
                />
              </label>
            </>
          )}
          {mode === "report" && (
            <>
              <label>
                Language code
                <input
                  name="language"
                  required
                  defaultValue="en"
                  pattern="[a-z]{2,3}(-[A-Z]{2})?"
                />
              </label>
              <label>
                Section headings, one per line
                <textarea
                  name="sections"
                  required
                  defaultValue={"Summary\nResults\nData quality and caveats"}
                />
              </label>
            </>
          )}
          {mode === "geography" && (
            <label>
              Code
              <input
                name="code"
                required
                maxLength={32}
                pattern="[A-Za-z0-9][A-Za-z0-9._\-]*"
              />
            </label>
          )}
          <label>
            Reason
            <textarea name="reason" required maxLength={2000} />
          </label>
          <div className="toolbar">
            <button type="submit" className="primary" disabled={busy}>
              {busy ? "Saving…" : "Save"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => setMode("")}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
