# Release 0.46 coding candidate: advisor-scored option fit

This coding candidate implements US-DC-02 / APL-368 on the bounded shortlist from US-DC-01. An active same-tenant Imprana Advisor can record a fit assessment for one source-backed option and opportunity. The immutable record covers organisation size, budget, operating context, language, data sensitivity and existing systems, and pins the catalogue edition and rubric version.

The provisional pilot rubric uses integer values from 1 to 5 plus a required nonblank advisor explanation for every dimension. This scale and explanation requirement are implementation assumptions pending owner review. The source criteria do not define aggregate arithmetic, so the candidate does not invent a total score. It presents the six-dimensional assessment as complete only when the server accepted every required dimension; missing, extra, unsupported or non-advisor payloads are refused.

The scorer must hold the dedicated `ai.solution-fit.score` capability through an active same-tenant membership with a current natural-person binding and fresh assurance. Reads use `ai.enablement.read`. Records are tenant-fenced and insert-only; exact retries use the existing seven-day operation receipt. Stored natural identity is not returned by the API.

Automated scoring remains outside this candidate. A pilot fit is advisory and does not approve a product or purchase.

Status: coding complete as a candidate. Tests, CI, independent review, merge, deployment and owner acceptance have not been run or claimed, following the owner's request to batch those gates later.
