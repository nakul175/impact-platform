# Release 0.67 candidate — progressive programme configuration

Coding-only candidate for **FR-UX-002 / APL-570**, preserving the frozen scenarios in `docs/backlog/backlog.csv`.

The simple programme template now writes every initial result and sharing choice into the programme draft: selected reporting calendar, result unit, `SUM` aggregation, reporting-calendar periods, explicit consent, internal or named-recipient audience, unique reach off, and sharing none. The create contract conditionally requires both the calendar and complete closed defaults whenever `template_code` is `SIMPLE`; invalid or omitted template defaults are rejected before any draft write.

The programme form reveals calculation/sharing choices in their relevant section and requires a final review before creation. That summary remains editable and names the selected calendar, exact first-result rule, unit, consent, audience, unique-reach and sharing choices. Saved template programmes show the same rules on inspection. Existing non-template drafts remain readable and editable without silently acquiring template semantics.

Tests, CI, merge, deployment, product acceptance, and human certification remain pending under the owner's coding-first instruction.
