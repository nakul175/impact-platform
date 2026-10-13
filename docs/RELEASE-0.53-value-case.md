# Release 0.53 coding candidate: 1–3 year value case

US-VC-01 / APL-385 (frozen Gherkin SHA-256 `d67a78e3e480338c89c029cff0e44ad828bd78f35d1a0b66dab99bd15cbb2854`) adds deterministic cost-benefit, ROI, cost-benefit ratio and total-cost-of-ownership calculations for one, two or three years.

The closed request requires labelled baseline and trial annual operating-cost inputs plus every declared cost component: annual licences, one-off setup, one-off training and annual staff time. Missing source objects, missing components, coercion, negative inputs, horizons outside 1–3 years and zero TCO are refused rather than presented as a complete value case.

Arithmetic uses bounded decimal strings and a local high-precision decimal context. Baseline and trial operating costs are projected over the selected horizon. Gross cost benefit is baseline less trial operating cost; TCO is the four declared cost components over the horizon; net benefit is gross benefit less TCO; ROI is net benefit divided by TCO; cost-benefit ratio is gross benefit divided by TCO. Rounding occurs only at the six-decimal response boundary.

The completed opportunity-map view supplies a bounded input form and displays the full component breakdown. Results remain self-reported planning drafts, not official results, causal attribution, forecasts, funding decisions or procurement approval.

This is a coding-only candidate. Tests, CI, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
