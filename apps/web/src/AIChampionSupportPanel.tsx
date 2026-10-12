import React, { useEffect, useRef, useState } from "react";

type Appointment = {
  object_id: string;
  revision_id: string;
  business_state: "Completed";
  appointment: {
    role: "CHAMPION";
    solution_id: string;
    champion_membership_id: string;
    support_owner_membership_id: string;
    guide_version: string;
    check_ins: { check_in_id: string; scheduled_at: string; title: string }[];
  };
};

type Guide = {
  title: string;
  version: string;
  sections: { key: string; title: string; body: string }[];
};

const terminal = ["AUTH_REQUIRED", "POLICY_DENIED", "RESOURCE_UNAVAILABLE"];

export function AIChampionSupportPanel({
  base,
  contextKey,
  canRead,
  canManage,
  planId,
  planRevision,
  solutionId,
  request,
  explain,
}: {
  base: string;
  contextKey: string;
  canRead: boolean;
  canManage: boolean;
  planId: string;
  planRevision: string;
  solutionId: string;
  request: (path: string, options?: RequestInit) => Promise<any>;
  explain: (error: unknown) => string;
}) {
  const [items, setItems] = useState<Appointment[]>([]);
  const [guide, setGuide] = useState<Guide | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const epoch = useRef(0);
  const pending = useRef<string | null>(null);
  const pendingScope = useRef("");
  const mutationController = useRef<AbortController | null>(null);

  async function load(signal: AbortSignal, currentEpoch: number) {
    const listed = await request(
      `${base}ai-enablement/plans/${planId}/champion-appointments`,
      { signal },
    );
    if (signal.aborted || epoch.current !== currentEpoch) return;
    setItems(listed.items);
    try {
      const opened = await request(
        `${base}ai-enablement/plans/${planId}/champion-guide?solution_id=${encodeURIComponent(solutionId)}`,
        { signal },
      );
      if (!signal.aborted && epoch.current === currentEpoch) setGuide(opened);
    } catch (cause) {
      if (signal.aborted || epoch.current !== currentEpoch) return;
      const code = (cause as { code?: string })?.code ?? "";
      if (["AUTH_REQUIRED", "POLICY_DENIED"].includes(code)) {
        setItems([]);
        setGuide(null);
        return;
      }
      if (code === "RESOURCE_UNAVAILABLE") {
        setGuide(null);
        return;
      }
      setError(explain(cause));
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    const currentEpoch = ++epoch.current;
    mutationController.current?.abort();
    const scope = `${contextKey}:${planId}:${solutionId}`;
    if (pendingScope.current !== scope) {
      pending.current = null;
      pendingScope.current = scope;
    }
    setItems([]);
    setGuide(null);
    setError("");
    setBusy(false);
    if (canRead)
      void load(controller.signal, currentEpoch).catch((cause) => {
        if (controller.signal.aborted || epoch.current !== currentEpoch) return;
        const code = (cause as { code?: string })?.code ?? "";
        if (terminal.includes(code)) {
          setItems([]);
          setGuide(null);
        } else setError(explain(cause));
      });
    return () => {
      controller.abort();
      mutationController.current?.abort();
    };
  }, [
    base,
    contextKey,
    canRead,
    planId,
    planRevision,
    solutionId,
    request,
    explain,
  ]);

  async function appoint(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !canManage) return;
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    if (!pending.current) {
      pending.current = JSON.stringify({
        operation_id: crypto.randomUUID(),
        expected_plan_revision: planRevision,
        champion_membership_id: String(
          form.get("champion_membership_id") || "",
        ),
        support_owner_membership_id: String(
          form.get("support_owner_membership_id") || "",
        ),
        check_ins: [
          {
            scheduled_at: new Date(
              String(form.get("scheduled_at")),
            ).toISOString(),
            title: String(form.get("title") || ""),
          },
        ],
      });
    }
    const body = pending.current;
    const currentEpoch = epoch.current;
    const controller = new AbortController();
    mutationController.current?.abort();
    mutationController.current = controller;
    setBusy(true);
    setError("");
    try {
      await request(
        `${base}ai-enablement/plans/${planId}/champion-appointments`,
        {
          method: "POST",
          body,
          signal: controller.signal,
        },
      );
      if (epoch.current !== currentEpoch) return;
      pending.current = null;
      await load(controller.signal, currentEpoch);
      formElement.reset();
    } catch (cause) {
      if (epoch.current !== currentEpoch) return;
      const code = (cause as { code?: string })?.code ?? "";
      if (code && !["SERVICE_UNAVAILABLE", "INTERNAL_ERROR"].includes(code))
        pending.current = null;
      if (terminal.includes(code)) {
        setItems([]);
        setGuide(null);
      }
      setError(explain(cause));
    } finally {
      if (epoch.current === currentEpoch) setBusy(false);
    }
  }

  if (!canRead) return null;
  return (
    <section aria-labelledby={`champion-support-${planId}`}>
      <h5 id={`champion-support-${planId}`}>Internal champion support</h5>
      <p className="muted">
        Champion is a designation for this deployed solution. It does not grant
        workspace permissions. Recorded check-ins are an internal schedule, not
        proof of calendar delivery or attendance.
      </p>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
      {canManage && (
        <form onSubmit={(event) => void appoint(event)}>
          <label>
            Champion membership ID
            <input
              name="champion_membership_id"
              required
              pattern="[0-9a-fA-F-]{36}"
            />
          </label>
          <label>
            Support owner membership ID
            <input
              name="support_owner_membership_id"
              required
              pattern="[0-9a-fA-F-]{36}"
            />
          </label>
          <label>
            First check-in
            <input name="scheduled_at" type="datetime-local" required />
          </label>
          <label>
            Check-in purpose
            <input name="title" maxLength={150} required />
          </label>
          <button type="submit" className="primary" disabled={busy}>
            {pending.current
              ? "Retry pending appointment"
              : "Appoint supported champion"}
          </button>
        </form>
      )}
      {items.map((item) => (
        <article className="ai-learning-step" key={item.object_id}>
          <h6>Confirmed champion appointment</h6>
          <p>Solution: {item.appointment.solution_id}</p>
          <p>Guide edition: {item.appointment.guide_version}</p>
          <ul>
            {item.appointment.check_ins.map((checkIn) => (
              <li key={checkIn.check_in_id}>
                {checkIn.title} —{" "}
                {new Date(checkIn.scheduled_at).toLocaleString()}
              </li>
            ))}
          </ul>
        </article>
      ))}
      {guide && (
        <article className="ai-learning-step">
          <h6>{guide.title}</h6>
          {guide.sections.map((section) => (
            <section key={section.key}>
              <h6>{section.title}</h6>
              <p>{section.body}</p>
            </section>
          ))}
        </article>
      )}
    </section>
  );
}
