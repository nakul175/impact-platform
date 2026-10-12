# Release 1.00 coding candidate — traceable proposal extraction

FR-AI-002 / APL-531 adds a review-only extraction path for clean UTF-8 text Evidence. It returns field proposals with the exact source object/revision, line or section, evidence span and classification. Duplicate source commitments remain separate conflicts and absent dates, targets or populations remain explicitly missing.

Review records selective acceptance and explicit human additions with rationale. Apply rechecks current source authority, the exact source head and the policy version; any change refuses the action. The result can become `READY_FOR_DOMAIN_DRAFT`, but this increment writes no framework, target or other domain object and does not activate the tenant's reserved extraction policy.

The qualified input profile is deliberately limited to previously scanned `text/plain` Evidence. PDF parsing, OCR and an external model/provider remain outside this candidate because no parser/provider or new spend was approved. Tests, CI, merge, staging deployment and owner acceptance are deferred by the owner for combined qualification.
