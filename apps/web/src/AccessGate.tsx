// What the workspace shows before a person can use any area (v0.27): a quiet line while
// GET me/access is answered, and a plain-language waiting page when it answers with no
// capability at all. The commonest case is a workspace owner whose organisation is Active but
// whose initial access has not yet been applied: ownership never opens programme data, and the
// administrator access arrives only when the second administrator has accepted the proposal and
// an independent operator has approved it (docs/RELEASE-0.26a.md, DEPLOYMENT-GUIDE.md §4.1).
type Props = {
  state: "loading" | "waiting";
  custody: boolean;
  tenantName: string;
  openTenants: () => void;
  retry: () => void;
};
export function AccessGate({
  state,
  custody,
  tenantName,
  openTenants,
  retry,
}: Props) {
  if (state === "loading")
    return (
      <p className="empty" role="status">
        Checking your access…
      </p>
    );
  return (
    <section className="panel access-gate" aria-labelledby="access-gate">
      <span className="eyebrow">{tenantName.toUpperCase()}</span>
      <h1 id="access-gate">
        {custody
          ? "Your administrator access is being set up"
          : "Your access is being set up"}
      </h1>
      {custody ? (
        <>
          <p>
            You own this organisation&apos;s workspace. Ownership on its own
            does not open any programme data, so the areas of the workspace are
            not listed yet.
          </p>
          <p>Three steps give you administrator access:</p>
          <ol className="next-steps">
            <li>
              <strong>You propose initial access</strong> in the Tenant
              lifecycle console, under Initial access, and name a second
              administrator (a different person).
            </li>
            <li>
              <strong>The second administrator accepts</strong> the proposal
              with their own sign-in.
            </li>
            <li>
              <strong>A platform operator approves</strong> it. The operator
              must be neither of you.
            </li>
          </ol>
          <p>
            When the approval is recorded, choose <strong>Check again</strong>{" "}
            and the workspace areas appear here. Your first task after that is
            the standard reference data under People &amp; access.
          </p>
        </>
      ) : (
        <>
          <p>
            You are a member of this workspace, but no permission has been
            granted to you yet, so there is nothing to show.
          </p>
          <p>
            Ask the person who manages access for your organisation to grant you
            a role. When a grant is approved, choose{" "}
            <strong>Check again</strong>.
          </p>
        </>
      )}
      <div className="toolbar">
        <button className="primary" onClick={retry}>
          Check again
        </button>
        {custody && (
          <button className="secondary" onClick={openTenants}>
            Open the Tenant lifecycle console
          </button>
        )}
      </div>
    </section>
  );
}
