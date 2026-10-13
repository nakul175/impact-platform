import React, { useEffect, useRef, useState } from "react";

type Training = {
  plan_id: string;
  plan_revision: string;
  solution_id: string;
  deployment_attestation_id: string;
  role: "AUTHOR";
  content_version: "role-training-2026-10-12.1";
  modules: {
    key: string;
    version: "role-training-2026-10-12.1";
    title: string;
    lesson: string;
    exercise: string;
    completed: boolean;
    completed_at: string | null;
  }[];
};

export function AIRoleTrainingPanel({
  base,
  contextKey,
  canRead,
  planId,
  solutionId,
  request,
  explain,
}: {
  base: string;
  contextKey: string;
  canRead: boolean;
  planId: string;
  solutionId: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
}) {
  const [training, setTraining] = useState<Training | null>(null);
  const [unavailable, setUnavailable] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const pending = useRef<{ key: string; body: string } | null>(null);
  const epoch = useRef(0);
  const completionController = useRef<AbortController | null>(null);
  useEffect(() => {
    const currentEpoch = ++epoch.current;
    const controller = new AbortController();
    completionController.current?.abort();
    pending.current = null;
    setTraining(null);
    setUnavailable(false);
    setError("");
    if (!canRead) {
      setUnavailable(true);
      return () => controller.abort();
    }
    request(
      `${base}ai-enablement/plans/${planId}/role-training?solution_id=${encodeURIComponent(solutionId)}`,
      { signal: controller.signal },
    )
      .then((value: Training) => {
        if (!controller.signal.aborted && epoch.current === currentEpoch)
          setTraining(value);
      })
      .catch((cause: { code?: string }) => {
        if (controller.signal.aborted || epoch.current !== currentEpoch) return;
        if (
          ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"].includes(
            cause?.code ?? "",
          )
        )
          setUnavailable(true);
        else setError(explain(cause));
      });
    return () => {
      controller.abort();
      completionController.current?.abort();
    };
  }, [base, contextKey, canRead, planId, solutionId, request, explain]);

  async function complete(key: string, version: string) {
    if (!training || busy || (pending.current && pending.current.key !== key))
      return;
    if (!pending.current) {
      pending.current = {
        key,
        body: JSON.stringify({
          operation_id: crypto.randomUUID(),
          expected_plan_revision: training.plan_revision,
          solution_id: training.solution_id,
          module_version: version,
        }),
      };
    }
    const captured = pending.current;
    const currentEpoch = epoch.current;
    const controller = new AbortController();
    completionController.current?.abort();
    completionController.current = controller;
    setBusy(key);
    setError("");
    try {
      await request(
        `${base}ai-enablement/plans/${planId}/role-training/modules/${encodeURIComponent(captured.key)}/actions/complete`,
        { method: "POST", body: captured.body, signal: controller.signal },
      );
      if (controller.signal.aborted || epoch.current !== currentEpoch) return;
      const value: Training = await request(
        `${base}ai-enablement/plans/${planId}/role-training?solution_id=${encodeURIComponent(solutionId)}`,
        { signal: controller.signal },
      );
      if (controller.signal.aborted || epoch.current !== currentEpoch) return;
      pending.current = null;
      setTraining(value);
    } catch (cause) {
      if (controller.signal.aborted || epoch.current !== currentEpoch) return;
      const failure = cause as { code?: string };
      if (
        ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"].includes(
          failure.code ?? "",
        )
      ) {
        pending.current = null;
        setTraining(null);
        setUnavailable(true);
        return;
      }
      if (
        failure.code &&
        !["SERVICE_UNAVAILABLE", "INTERNAL_ERROR"].includes(failure.code)
      )
        pending.current = null;
      setError(explain(cause));
    } finally {
      if (epoch.current === currentEpoch) setBusy("");
    }
  }

  if (unavailable) return null;
  return (
    <section aria-labelledby={`role-training-${solutionId}`}>
      <h5 id={`role-training-${solutionId}`}>Data Author training</h5>
      <p className="muted">
        Required modules for your current Data Author role and this explicitly
        recorded deployed solution. Modules assigned only to other roles are
        excluded. Completion is personal progress, not certification.
      </p>
      {!training && !error && <p role="status">Loading role training…</p>}
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {pending.current && !busy && (
        <p role="status">
          Retry the pending completion before recording another module.
        </p>
      )}
      {training?.modules.map((module) => (
        <article className="ai-learning-step" key={module.key}>
          <h6>{module.title}</h6>
          <p>{module.lesson}</p>
          <p>
            <strong>Practice:</strong> {module.exercise}
          </p>
          {module.completed ? (
            <p role="status">
              Completed{" "}
              {module.completed_at
                ? new Date(module.completed_at).toLocaleString()
                : ""}
            </p>
          ) : (
            <button
              type="button"
              className="secondary"
              disabled={
                Boolean(busy) ||
                Boolean(pending.current && pending.current.key !== module.key)
              }
              onClick={() => void complete(module.key, module.version)}
            >
              {pending.current?.key === module.key
                ? "Retry pending completion"
                : "Record my completion"}
            </button>
          )}
        </article>
      ))}
    </section>
  );
}
