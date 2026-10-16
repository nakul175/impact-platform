import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  advanceDemo,
  freshDemo,
  saveDemo,
  sections,
  type SectionId,
} from "./PublicSandboxModel";
import "./styles.css";
import "./public-sandbox.css";

function PublicSandbox() {
  const [section, setSection] = useState<SectionId>("programmes");
  const [state, setState] = useState(freshDemo);
  const [editing, setEditing] = useState<string | null | undefined>(undefined);
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [filter, setFilter] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [resetting, setResetting] = useState(false);
  const current = sections.find(([id]) => id === section)!;
  const rows = state[section].filter((row) =>
    `${row.title} ${row.notes}`.toLowerCase().includes(filter.toLowerCase()),
  );
  const count = Object.values(state).reduce(
    (n, records) => n + records.length,
    0,
  );
  function navigate(id: SectionId) {
    setSection(id);
    setEditing(undefined);
    setFilter("");
    setError("");
    setNotice("");
    setResetting(false);
  }
  function open(id: string | null) {
    const row = state[section].find((r) => r.id === id);
    setEditing(id);
    setTitle(row?.title ?? "");
    setNotes(row?.notes ?? "");
    setError("");
    setNotice("");
  }
  function save(event: React.FormEvent) {
    event.preventDefault();
    try {
      setState(saveDemo(state, section, title, notes, editing ?? undefined));
      setEditing(undefined);
      setNotice("Draft saved in this tab only.");
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save this draft.");
    }
  }
  return (
    <div className="public-sandbox">
      <a className="skip-link" href="#demo-content">
        Skip to demo workspace
      </a>
      <header className="sandbox-top">
        <a className="sandbox-brand" href="/sandbox.html">
          imprana<span>.</span>
        </a>
        <span>Disposable demo workspace</span>
        <a href="/">Open shared workspace sign-in →</a>
      </header>
      <aside className="sandbox-boundary" aria-label="Demo limits">
        <strong>No login · invented data · this tab only</strong>
        <p>
          Explore sample screens with invented data. Create and edit local
          drafts, and try simulated reviews. No real workspace is connected;
          nothing is sent or published. Use invented text only. Refresh or reset
          to start over.
        </p>
      </aside>
      <div className="sandbox-shell">
        <nav className="sandbox-nav" aria-label="Demo sections">
          {sections.map(([id, label]) => (
            <button
              key={id}
              aria-current={section === id ? "page" : undefined}
              onClick={() => navigate(id)}
            >
              {label}
            </button>
          ))}
        </nav>
        <main id="demo-content" className="sandbox-main" tabIndex={-1}>
          <div className="sandbox-heading">
            <div>
              <span className="eyebrow">FICTIONAL COMMUNITY ORGANISATION</span>
              <h1>{current[1]}</h1>
              <p>
                Explore a {current[2].toLowerCase()} using disposable sample
                data.
              </p>
            </div>
            <button
              onClick={() => {
                setResetting(true);
                setEditing(undefined);
              }}
            >
              Reset demo
            </button>
          </div>
          {resetting && (
            <section className="sandbox-reset" aria-label="Confirm demo reset">
              <p>
                Discard every demo change in this tab and restore the invented
                examples?
              </p>
              <button
                className="primary"
                onClick={() => {
                  setState(freshDemo());
                  setResetting(false);
                  setError("");
                  setFilter("");
                  setNotice("Demo reset. All local changes were discarded.");
                }}
              >
                Discard changes and reset
              </button>
              <button onClick={() => setResetting(false)}>
                Keep my changes
              </button>
            </section>
          )}
          <div className="sandbox-stats">
            <article>
              <span>Sections to explore</span>
              <strong>{sections.length}</strong>
            </article>
            <article>
              <span>Records in this tab</span>
              <strong>{count}</strong>
            </article>
            <article>
              <span>Connected organisations</span>
              <strong>0</strong>
            </article>
          </div>
          <p className="sandbox-notice" role="status">
            {notice}
          </p>
          {error && (
            <p role="alert" className="sandbox-error">
              {error}
            </p>
          )}
          {editing !== undefined ? (
            <form className="sandbox-editor" onSubmit={save}>
              <h2>
                {editing ? "Edit" : "New"} {current[2].toLowerCase()}
              </h2>
              <label htmlFor="demo-title">Title</label>
              <input
                id="demo-title"
                autoFocus
                maxLength={120}
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
              <label htmlFor="demo-notes">Notes</label>
              <textarea
                id="demo-notes"
                maxLength={2000}
                rows={5}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
              <p>
                Saving after a simulated review returns this sample to draft.
                Nothing is sent to a server.
              </p>
              <div>
                <button type="submit" className="primary">
                  Save local draft
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditing(undefined);
                    setError("");
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="sandbox-toolbar">
                <label>
                  Search this section
                  <input
                    type="search"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                  />
                </label>
                <button className="primary" onClick={() => open(null)}>
                  New {current[2].toLowerCase()}
                </button>
              </div>
              <section
                aria-label={`${current[1]} demo records`}
                className="sandbox-records"
              >
                {rows.length === 0 && (
                  <p>
                    No matching samples. Clear the search or create a local
                    draft.
                  </p>
                )}
                {rows.map((row) => (
                  <article key={row.id}>
                    <div className="sandbox-record-top">
                      <h2>{row.title}</h2>
                      <span className="sandbox-badge">{row.status}</span>
                    </div>
                    <p className="sandbox-notes">{row.notes}</p>
                    <div className="sandbox-actions">
                      <button onClick={() => open(row.id)}>Edit draft</button>
                      {row.status !== "Reviewed (simulation)" && (
                        <button
                          onClick={() => {
                            try {
                              setState(advanceDemo(state, section, row.id));
                              setNotice(
                                "Simulation only. No real submission, approval, grant or publication occurred.",
                              );
                            } catch (e) {
                              setError(
                                e instanceof Error
                                  ? e.message
                                  : "Could not advance this example.",
                              );
                            }
                          }}
                        >
                          {row.status === "Draft"
                            ? "Simulate submission"
                            : "Simulate review"}
                        </button>
                      )}
                    </div>
                    <details>
                      <summary>
                        Local demo history ({row.history.length})
                      </summary>
                      <ul>
                        {row.history.map((text, i) => (
                          <li key={i}>{text}</li>
                        ))}
                      </ul>
                    </details>
                  </article>
                ))}
              </section>
            </>
          )}
          <footer className="sandbox-footer">
            These samples demonstrate navigation and local editing only. Use the
            authenticated workspace for real API journeys and governed
            approvals.
          </footer>
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(<PublicSandbox />);
