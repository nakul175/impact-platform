# Release 1.04 coding candidate — governed numerical analysis

FR-AI-006 / APL-538 adds a reserved numerical-analysis workspace for Analysts and MEL Administrators. A request supplies a closed typed plan: the pooled-percentage measure, two to twenty exact `CalculatedResult` revisions, an exact current period revision, an explicit empty filter and dimension set, an official or provisional source mode, and the sole permitted `POOL_RATIO` operation.

The service rechecks the caller's current authority and exact period head, then reads each pinned result through the existing revision service. Sources must contain stored numerator and denominator values for the selected period and use a ratio or percentage measurement type. The deterministic decimal tool pools numerator and denominator independently, calculates the percentage at precision 100 and rounds half-up to two places. For inputs 50/100 and 1/10 it returns `46.36 percent (51/110)`, the exact source references and a content-addressed calculation receipt. The returned value is never recomputed by a model.

The endpoint accepts no SQL, code or free-form operation. A supplied drafted claim must equal the tool result exactly or delivery is refused with `AI_NUMERIC_CLAIM_MISMATCH`. Zero denominators, negative or incompatible inputs and changed period authority are refused.

Migration 0088 adds `NUMERIC_ANALYSIS` to the closed policy vocabulary. Current policy validation, runtime gate and policy UI keep it reserved-disabled, so activation requires a later reviewed application change and owner decision. No policy row, governed result or official value is rewritten. Tests and CI remain deferred by owner request; this candidate is unmerged and undeployed.
