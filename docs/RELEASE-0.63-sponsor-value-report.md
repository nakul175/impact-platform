# Release 0.63 candidate — organisation-selected sponsor value report

## Delivered

US-IM-02 / APL-372 has a coding-only candidate for an Executive Director to select realised ROI and outcome items and explicitly generate one immutable report for one named active external sponsor membership. No report exists until that request. The sponsor can open only the exact report ID while the same identity and membership remain current and the report has not expired.

The organisation supplies actual realised benefit, cost, currency, period and a source-and-method note. The server calculates net benefit and ROI deterministically. The locked value case supplies planning context only, while the current outcome observation supplies usage, time, cost, quality and reach. The sponsor response and downloadable JSON contain only selected items plus mandatory period, currency, self-reported basis, expiry and disclaimer. Internal source selectors, recipient identifiers and the source note are not included in that artifact.

## Contract and persistence

Domain API 1.54 adds an explicit create route and recipient-bound single-report read. Schema57 registers `AISponsorValueReport` in the immutable generic object store and adds restrictive worker policies. The create operation retains exact uncertain-request identity. No historical value case, outcome observation, membership or report is rewritten.

## Limits

This candidate does not send email, create a public link or deliver externally. It does not convert planning estimates into actual results, independently verify the submitted actuals, prove causality or create official impact arithmetic. Report withdrawal and access-event reporting remain outside this story's frozen criteria.

## Reproduction

Only source formatting, Python compilation, generated-contract parsing and TypeScript compilation were run in this coding phase. Tests, CI, independent human review, merge and staging deployment remain later combined gates.

## Integration notes

Register migration0057 after0056. Rebuild contracts and API inventory. Keep release review `passed=false` until the later test and review phase supplies actual evidence.
