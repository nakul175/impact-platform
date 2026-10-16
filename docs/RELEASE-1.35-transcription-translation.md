# Release 1.35 coding candidate — transcription and translation

FR-EVD-006 / APL-644 creates labelled transcript or translation artifacts only through an approved destination and permitted task. Source recording and destination revisions, offsets, source classification and a no-fallback rule are retained; uncertain speakers or timings remain unknown.

Corrections create a new artifact revision while retaining automated text. Quotations pin the corrected artifact and original recording and require explicit original-meaning review.

## Positive-journey qualification status

The synthetic live journey is implemented in
`qualification/test_transcription_translation_live.py`. It creates a synthetic recording, requests
an approved translation, corrects the segment at 03:12, creates a reviewed quotation and inspects
the durable revision chain for the recording pin and retained automated text.

The initial 16 October 2026 run exposed missing policy operations and registry kinds. Migration 0108
now registers approved destinations, transcript artifacts and quotation references behind restrictive
delivery-worker fences. The generated policy limits writes to existing evaluation-edit authority;
runtime checks current recording/destination read authority and refuses reversed segment offsets.

The repaired exact-candidate run passed the positive journey: **1 passed**. This is local synthetic
evidence only; CI, merge, staging deployment and owner acceptance remain separate gates.
