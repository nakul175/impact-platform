# Nonprofit AI Enablement Documentation

Edition 1.0 · 5 October 2026 · Proposed baseline for owner review

Start with the BRD. This package defines the nonprofit AI enablement extension around practical AI use, capacity building, discovery/comparison, procurement, human advice, governed delivery and outcomes. It preserves the existing impact-platform specifications. Current implementation facts use commit 36073f1, build 0.30.0 and schema 35; proposed marketplace and service work is explicitly labelled. This edition records no acceptance, deployment or financial commitment.

**Development appendage:** [DEVELOPMENT-0.31.md](DEVELOPMENT-0.31.md), the [0.31 release record](../../RELEASE-0.31-nonprofit-ai-planning.md) and [local evidence summary](../../evidence/nonprofit-ai-planning-local-summary.json) describe the first implementation increment: stable learning progress, supplied cost planning, self-reported pilot comparisons, manual task practice, saved source inputs and bounded advisory transfer. Local evidence is recorded with seven unchanged Mac operations failures; hosted/native gates remain outstanding. The core edition-1.0 documents and CSV/JSON baseline retain their original reference; related automated support does not mark the 108 specified cases executed or accepted.

**Development appendage 0.32:** [DEVELOPMENT-0.32.md](DEVELOPMENT-0.32.md) and the [release record](../../RELEASE-0.32-tola-ai-sprint.md) extend the actual product with reviewed access upgrades and exact saved guidance/history, alongside a live ETA tracker and Mac operations portability. Focused native 193 checks and13 real browser groups pass; full regression/recovery is being recorded. This appendage preserves the original proposed documentation and specified-case baseline.

## Core documents in review order

| Document | Purpose | Editable Word copy |
|---|---|---|
| [01 BRD](01-BRD.md) | Business problem, outcomes, people, scope and 36 business requirements | [BRD](editable/01-BRD.docx) |
| [02 FSD](02-FSD.md) | Detailed behavior, roles, states, exceptions and 40 functional requirements | [FSD](editable/02-FSD.docx) |
| [03 HLD](03-HLD.md) | Components, architecture, trust boundaries, data flows and deployment | [HLD](editable/03-HLD.docx) |
| [04 LLD](04-LLD.md) | Current contracts/algorithms and proposed implementation interfaces | [LLD](editable/04-LLD.docx) |

The BRD was authored first; FSD, HLD and LLD were derived sequentially. Testing and UX/data work proceeded in parallel against the same requirement identifiers. Markdown is the canonical source; regenerate Word copies after source changes and inspect all rendered pages.

## Testing and product design

| Artefact | Contents |
|---|---|
| [Test strategy](05-TEST-STRATEGY.md) | Smoke, unit, integration, regression, security, accessibility, performance, recovery and UAT layers with entry/exit rules |
| [Scenarios and detailed cases](06-TEST-SCENARIOS-AND-CASES.md) | 50 scenarios and 108 cases with steps, synthetic data and expected results |
| [Scenario inventory](test-scenarios.csv) and [case inventory](test-cases.csv) | Machine-readable references and evidence context; all new cases are SPECIFIED_NOT_RUN |
| [Execution template](test-run-template.csv) | Separate run outcomes, candidate/environment, actual results, defects and evidence |
| [Wireframes and journeys](07-WIREFRAMES-AND-JOURNEYS.md) | Screen mapping, user flows and state design |
| [Clickable wireframes](wireframes/index.html) | Offline synthetic prototype of current and proposed journeys; no real supplier/provider actions |
| [Data dictionary](08-DATA-DICTIONARY.md) and [field inventory](data-dictionary.csv) | 362 fields with types, constraints, ownership, privacy, retention and source/requirement links |
| [Architecture figure](architecture.svg) | Current implementation and proposed components with an explicit legend |

## Supporting documents

| Document | Purpose |
|---|---|
| [Security and privacy](09-SECURITY-AND-PRIVACY.md) | Assets, boundaries, threats, controls, data handling and required evidence |
| [Operations and release](10-OPERATIONS-AND-RELEASE.md) | Configuration, failures, recovery, onboarding, release gates and handover |
| [Decisions and risks](11-DECISIONS-AND-RISKS.md) | Sixteen open owner decisions and twelve delivery risks |
| [Delivery backlog](12-DELIVERY-BACKLOG.md) | Eleven work packages ordered by dependency rather than assumed dates |
| [Architecture decisions](13-ARCHITECTURE-DECISIONS.md) | Eight design choices and their tradeoffs |
| [Baseline and glossary](14-BASELINE-AND-GLOSSARY.md) | Verified sources, reuse provenance, terminology and current limits |
| [Acceptance and change control](15-ACCEPTANCE-AND-CHANGE-CONTROL.md) | Review sequence, test run/UAT records and change governance |
| [Requirement registry](requirements.json) and [traceability](traceability.csv) | Business to functional requirement, design, test, screen, data and decision mapping |
| [Documentation validation](documentation-validation.json) | Offline consistency checks; this is document QA, not product acceptance |
| [Visual review](visual-review.json) and [wireframe validation](wireframes/wireframe-validation.json) | Inspection of all 48 Word pages and separate checks of the synthetic prototype |

## Reading status and next review

LOCAL_IMPLEMENTATION and PARTIAL_LOCAL describe supporting code evidence. TARGET and CONDITIONAL_TARGET describe proposed work. All requirements remain proposed until scoped human approval and the required execution evidence. Recorded product tests predate this documentation task; cases written here are unrun. The original 307 impact requirements and their conservative acceptance ledger are unchanged.

Review the BRD first, focusing on the first cohort, initial tasks, data boundary and intended marketplace/service responsibilities. Then resolve dependent decisions and review the FSD, HLD and LLD with the appointed role owners. The backlog provides implementation slices once scope is approved. A wireframe, signed design or local test count does not itself authorise supplier disclosure, a payment, paid CI or a merge into auto-deploying main.

## Maintenance

From the repository root, run the offline helper with Python to validate identifiers, links and coverage and regenerate traceability:

```sh
python3 tools/documentation/validate_nonprofit_ai.py
```

Use a Python environment with python-docx to regenerate the four editable core documents:

```sh
python3 tools/documentation/build_nonprofit_ai.py
```

Render each Word file through the document renderer and visually inspect every page before distributing a changed edition. The ZIP package includes only delivery files; QA renders remain outside the repository. The interactive prototype has no external dependencies and keeps temporary changes in memory. Changes are not saved to the actual product.
