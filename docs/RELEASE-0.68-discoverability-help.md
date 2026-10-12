# Release 0.68 candidate — permission-aware discoverability and help

Coding-only candidate for **FR-UX-008 / APL-573**, preserving the frozen scenarios in `docs/backlog/backlog.csv`.

My Work now searches only server-returned assigned tasks, safe notifications and currently permitted indicator definitions. Recent work remains personal and current-authority filtered. A safe notification can focus its exact task only when that task is present in the caller's current permitted list; otherwise the UI reports unavailability without revealing the target. Context help explains a pending approval and the evidence recovery step in product language using a synthetic example.

Personal saved views are immutable `SavedView` registry revisions behind existing forced tenant RLS and an additional worker fence. Every view pins one exact approved definition revision and its search text. Reads are restricted to the current owner. Opening a view re-reads the definition with current authority: a retired, changed or newly forbidden definition never silently changes meaning and instead opens an explicit reviewed-rebind choice. Rebinding accepts only a currently permitted approved definition at its exact head revision and writes a new saved-view revision.

Domain API 1.59 adds personal saved-view list/create/read/patch contracts using the existing `work-items.read` authority. Tests, CI, merge, deployment, product acceptance, and human certification remain pending under the owner's coding-first instruction.
