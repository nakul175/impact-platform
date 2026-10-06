# Nonprofit AI Enablement Acceptance and Change Control

Edition 1.0 · 5 October 2026 · Proposed review procedure

## Review order

Review the BRD first for the business problem, people, outcomes, exclusions and R1/R2/R3 dependency scope. Resolve the decisions needed for the selected phase and record approval of that scope. Review the FSD against the approved BRD, then the HLD against the FSD, then the LLD against the HLD. Tests, wireframes and dictionary may be drafted in parallel but must be reconciled before that baseline is approved.

Use requirements.json and traceability.csv to follow a requirement through behavior, components, implementation design, fields, screens and test cases. Review proposed records with the intended role owners and representative nonprofit users. A screen can illustrate a target workflow without granting authority or proving it exists.

## Evidence and status rules

SPECIFIED_NOT_RUN means a test case is ready for execution. Related previous local assertions are supporting evidence recorded separately. A test execution needs candidate commit, build/schema/API versions, environment, fixture/harness, actual observations, evidence and a named executor. TARGET or CONDITIONAL_TARGET means behavior is still proposed. LOCAL_IMPLEMENTATION does not mean formal acceptance or production readiness.

A requirement becomes accepted only when its approved scope has passing relevant positive/negative and recovery evidence in the specified environment, unresolved defects are addressed through an accountable decision, and the appointed human records acceptance. Required hosted gates and owner merge confirmation remain separate release obligations. The original 307 impact requirement statuses are unchanged.

## Test execution record

Copy test-run-template.csv to a new dated evidence location; never overwrite the design case catalogue with mutable run results. Populate one row for each executed or blocked case. Record actual results rather than copying expected results. Attach or link only synthetic, minimised evidence and exclude credentials, raw prompts and personal data.

Use NOT_STARTED, PASS, FAIL, BLOCKED or NOT_APPLICABLE as run result values. BLOCKED needs an exact implementation, policy, funding or environment reason. NOT_APPLICABLE requires an explicit approved scope decision; it cannot hide a requirement to make completion look higher. An interrupted or unknown external action needs investigation, not an invented PASS. Defects identify severity, affected requirement, reproducer, owner, disposition and retest evidence.

## UAT sign off record

For each proposed acceptance, record the approved phase and exact requirement IDs; candidate commit and versions; user roles and organisation scope; executed case and evidence references; known limitations and outstanding defects; the approving natural person's name, role and date; and the explicit decision ACCEPT, REJECT or DEFER. A prefilled document, generic yes or code author's test result is not an independent procurement/delivery decision.

No acceptance signature is present in edition 1.0. Review scope approval, business UAT acceptance and release merge approval separately so each authorisation has a clear object and consequence. Financial operator responsibilities, live provider spending and supplier disclosures require their own approved scope.

## Change request record

A change request records its identifier, requester, problem, proposed behavior, affected BR/FR IDs, decision dependencies, impacted screens/fields/contracts/components/tests, data migration and compatibility needs, operational consequences, estimate and approving human. Retain the prior edition and update all dependent artefacts together. Link the eventual implementation commit and executed regression evidence before closing the change.

Material changes to approved source evidence, quotes, disclosures or rules create new revisions and a new decision where required. Do not repoint approved snapshots or reinterpret earlier lesson progress. Defer scope through an explicit owner decision; never delete requirements solely because the existing product does not implement them.

## Documentation quality checks

The offline validation helper checks requirement IDs, document links, test references, fields and coverage and regenerates the traceability view. This checks package consistency, not whether the product satisfies the requirements. Editable Word copies are generated from canonical Markdown and rendered for visual inspection before delivery. Record the inspected page counts, file hashes and any remaining limitation in visual-review.json. Rebuilding a Word file invalidates its earlier visual review until every newly rendered page is inspected again.
