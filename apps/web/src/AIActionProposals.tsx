import React, { useState } from "react";

type Props = {
  base: string;
  policyVersion: number | null;
  canCreate: boolean;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
};
type Proposal = {
  proposal_id: string;
  command_type: "CREATE_WORK_ITEM_DRAFT";
  before_values: null;
  after_values: Record<string, unknown>;
  affected_versions: {
    object_type: string;
    object_id: string;
    revision_id: string;
  }[];
  policy_version: number;
  consequences: string[];
  domain_side_effects_created: false;
};

export function AIActionProposals({
  base,
  policyVersion,
  canCreate,
  request,
  explain,
}: Props) {
  const [form, setForm] = useState({
    programme_id: "",
    programme_revision_id: "",
    title: "",
    assignee_id: "",
    due_at: "",
    severity: "MATERIAL",
    affected_versions: "",
    consequences: "",
  });
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [outcome, setOutcome] = useState("");
  const [error, setError] = useState("");
  if (!canCreate) return null;
  return (
    <section aria-labelledby="ai-action-proposals">
      <h3 id="ai-action-proposals">Draft action proposals</h3>
      <p className="muted">
        Generation creates no domain change. Review the exact before/after
        values, sources, policy and consequences, then confirm separately
        through the ordinary work-item command.
      </p>
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          setError("");
          setOutcome("");
          try {
            const affected = form.affected_versions
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
              .map((item) => {
                const [object_type, object_id, revision_id] = item.split(":");
                return { object_type, object_id, revision_id };
              });
            const result = await request(
              base + "ai-enablement/action-proposals",
              {
                method: "POST",
                body: JSON.stringify({
                  operation_id: crypto.randomUUID(),
                  command_type: "CREATE_WORK_ITEM_DRAFT",
                  scope_object_id: form.programme_id,
                  scope_revision_id: form.programme_revision_id,
                  after_values: {
                    programme_id: form.programme_id,
                    work_type: "ACTION",
                    title: form.title,
                    dependency_ids: [],
                    due_at: new Date(form.due_at).toISOString(),
                    assignee_id: form.assignee_id,
                    severity: form.severity,
                  },
                  affected_versions: affected,
                  policy_version: policyVersion,
                  consequences: form.consequences
                    .split("\n")
                    .map((item) => item.trim())
                    .filter(Boolean),
                  language: "en",
                }),
              },
            );
            setProposal(result);
          } catch (caught) {
            setError(explain(caught));
          }
        }}
      >
        {[
          ["programme_id", "Programme ID"],
          ["programme_revision_id", "Programme revision ID"],
          ["title", "Proposed action title"],
          ["assignee_id", "Assignee principal ID"],
          ["due_at", "Due date and time"],
          ["severity", "Severity"],
          [
            "affected_versions",
            "Affected versions (type:object:revision, comma separated)",
          ],
        ].map(([name, label]) => (
          <label key={name}>
            {label}
            <input
              required
              type={name === "due_at" ? "datetime-local" : "text"}
              value={form[name as keyof typeof form]}
              onChange={(event) =>
                setForm({ ...form, [name]: event.target.value })
              }
            />
          </label>
        ))}
        <label>
          Consequences, one per line
          <textarea
            required
            value={form.consequences}
            onChange={(event) =>
              setForm({ ...form, consequences: event.target.value })
            }
          />
        </label>
        <button disabled={policyVersion === null}>
          Generate proposal for review
        </button>
      </form>
      {proposal && (
        <article className="ai-result-card">
          <h4>Exact proposed change</h4>
          <p>
            <strong>Command:</strong> Create work-item draft only
          </p>
          <pre>
            {JSON.stringify(
              { before: proposal.before_values, after: proposal.after_values },
              null,
              2,
            )}
          </pre>
          <p>
            <strong>Affected versions:</strong>{" "}
            {proposal.affected_versions
              .map((item) => `${item.object_type} ${item.revision_id}`)
              .join(", ")}
          </p>
          <p>
            <strong>Policy version:</strong> {proposal.policy_version}
          </p>
          <ul>
            {proposal.consequences.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p>
            No domain side effects created. Protected results, grants,
            publication, deletion and independent decisions have no apply route.
          </p>
          <button
            type="button"
            disabled={Boolean(outcome)}
            onClick={async () => {
              setError("");
              try {
                const result = await request(
                  base +
                    `ai-enablement/action-proposals/${proposal.proposal_id}/actions/confirm`,
                  {
                    method: "POST",
                    body: JSON.stringify({
                      operation_id: crypto.randomUUID(),
                      language: "en",
                    }),
                  },
                );
                setOutcome(result.outcome_object_id);
              } catch (caught) {
                setError(explain(caught));
              }
            }}
          >
            Confirm through ordinary command
          </button>
          {outcome && <p role="status">Draft work item created: {outcome}</p>}
        </article>
      )}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
