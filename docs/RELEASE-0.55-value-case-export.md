# Release 0.55 coding candidate: board/funder value-case export

US-VC-03 / APL-390 (frozen story Gherkin SHA-256 `5f31d595da2d71ef4cc96ec306a493d01d7451b93efe7c72b372b35a7c1f2df5`; containing feature-file SHA-256 `b72f197ce6422287c47a34c8e154d7dac7016fdc83a9247b7cdbc1b5eb414646`) adds PDF and DOCX exports for a complete self-reported value case.

The export endpoint accepts the same closed value-case inputs used by the calculation endpoint. It recalculates the business case on the server and renders its financial measures, cost components, sector benefits, baseline and trial source inputs, disclaimer, and every submitted assumption. It does not accept a client-composed result or a selectable assumption subset, so an omitted required input or empty assumption list is refused before any artifact is returned.

The response carries a format-bound filename, media type, byte length, SHA-256 digest, renderer version and assumption count alongside base64 artifact bytes. The browser verifies these bindings before download. The web interface offers PDF and DOCX downloads only after a successful complete calculation and sends the exact input snapshot that produced the displayed draft. Export requires the existing separate `ai.enablement.export` capability and fresh assurance; ordinary read authority does not imply export authority.

Exports remain self-reported planning drafts. They are not official impact results, board or funder approval, procurement authority, or proof that approval happened faster. This coding slice treats a successfully server-calculated input snapshot as the completed draft. It does not yet persist a pinned value-case revision or durable issuance/receipt, and it adds no approved baseline; those stateful boundaries remain for later stories/integration review.

This is a coding-only candidate. Tests, CI, independent review, merge, staging deployment and owner acceptance are intentionally deferred to the combined qualification phase.
