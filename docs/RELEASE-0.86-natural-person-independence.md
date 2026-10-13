# Release 0.86 coding candidate — shared natural-person independence

FR-ACC-004 / APL-351 centralises natural-person independence for the core immutable workflow review and versioned value-case approval paths. Approval now compares the current verified natural person with the complete immutable material-author set rather than login, role, group or principal identity. A missing/service natural identity and an empty author set fail closed. A second login or group membership cannot create independence because verified aliases resolve to the same natural person.

Core workflow submission already snapshots the candidate's material authors against the exact candidate revision; editing creates a new candidate revision/workflow decision context. Value-case revision writes retain every natural author and revising a locked case returns it to Draft with no carried approval. Emergency exceptions are not introduced.

Other specialised approval modules retain their existing natural-person checks pending combined review. Source checks only; tests, CI, merge, staging and acceptance are deferred.
