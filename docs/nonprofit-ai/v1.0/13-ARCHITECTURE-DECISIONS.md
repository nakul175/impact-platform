# Nonprofit AI Enablement Architecture Decisions

Edition 1.0 · 5 October 2026 · Proposed extension choices

## Decision status

These records explain the design direction and its tradeoffs. Established platform controls remain mandatory; extension choices are proposed for review. This document is not an owner sign-off. Amend a record with rationale and affected requirements before replacing it.

### ADR NPA 001 Extend the governed platform

Reuse the FastAPI, PostgreSQL, React and worker architecture with existing identity, tenant authority, revisions, audit, outbox and receipts. Current adoption drafts already use the registry/revision mechanism. The alternative of a separate marketplace application would duplicate authority and create inconsistent cross-product decisions. The tradeoff is that every new workflow must respect the existing immutable and independent-review design. Scope: FR-NPA-006, 025, 027, 033 and 036.

### ADR NPA 002 Keep planning independent of generation

Readiness and catalogue matching remain deterministic, versioned and available without a provider. Generated advisory is an optional separately permitted draft. This gives reproducible reasoning and limits dependency failure. It requires maintained rules and may provide less personalised advice than unrestricted generation. Official impact arithmetic continues to use approved deterministic rules exclusively. Scope: FR-NPA-002, 003, 010, 024, 029 and 035.

### ADR NPA 003 Commit intent before external work

Create a bounded, authorised claim or outbox intent in a short transaction, call the external dependency outside the transaction, then record the outcome after current authority checks. Replay requires current access and the original payload binding. This avoids holding locks during network calls and supports accountability, but creates ambiguous crash windows requiring reconciliation rather than blind retry. An intent is never proof of delivery. Scope: FR-NPA-010, 014, 019, 020, 022, 023, 027 and 039.

### ADR NPA 004 Separate public claims from private evidence

Current editorial products remain source-backed content. Proposed suppliers submit evidence privately, then independent review publishes a deliberately public versioned snapshot. Do not grant operators global access to private organisation records to populate a marketplace. This separation adds review work but provides explicit disclosure boundaries and provenance. Scope: FR-NPA-004, 005, 017, 018, 025 and 031.

### ADR NPA 005 Preserve semantic versions of learning and plans

Pin catalogue versions in saves and preserve lesson meaning. Current completion keys are path plus position, so future content reordering needs an explicit migration or stable-ID model before it occurs. Recomputing old progress against reordered content is unacceptable. Maintaining old versions costs storage and curation but makes historical interpretation possible. Scope: FR-NPA-006, 007, 008, 031 and 038.

### ADR NPA 006 Stage financial services after operator decisions

The proposed product can support discovery, briefs and governed engagements before choosing a platform payment model. Integrated purchasing remains conditional R3. This avoids silently assuming a merchant, fee or financial-responsibility model. It delays full transaction convenience and requires explicit owner decisions and adapter qualification before activation. Scope: FR-NPA-015, 016, 018, 019, 020 and 023; decisions DEC-NPA-004, 007 and 015.

### ADR NPA 007 Keep private records tenant fenced

Every new tenant table must include tenant identity in primary and foreign keys, forced RLS and narrow runtime grants. Tenant write lock precedes authority; closed DTOs reject client-owned control metadata. Target entity names in the LLD and dictionary are proposals, not already migrated tables. This approach requires careful native-role and concurrency tests but prevents accidental organisation-wide or operator-wide leakage. Scope: FR-NPA-025, 026, 027, 037 and 039.

### ADR NPA 008 Reuse compatible patterns with provenance

Reuse the existing platform controls and compatible Mercy Corps export layouts/scenario vocabulary. Adapt MSME journey patterns around diagnosis, procurement, delivery and running services. Do not import Django permissions, incompatible arithmetic, manufacturing fixtures or commercial fees. Literal source adaptations retain licence/notice records and modification attribution. This accelerates well-understood components while preserving nonprofit decisions and platform invariants. Scope: FR-NPA-021, 024, 031, 035 and 036.

## Review criteria

For every proposed record, check that its affected functional requirements, data fields, wireframes and tests agree. Record the reviewing humans and unresolved assumptions. Native role/concurrency evidence, external adapter qualification and operational decisions are required where relevant; local code reading or an architecture diagram is not sufficient acceptance evidence.
