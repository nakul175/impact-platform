# 0.97 bounded AI job execution

FR-AI-016b / APL-346 completes the coding half of durable advisory-job execution. The restricted worker claims queued jobs with a generation fence, records a server-owned 20-minute deadline, decrypts only the accepted request, minimizes the organization profile again and performs the provider call outside every database transaction. Jobs with source dependencies fail closed because the worker cannot impersonate the requester's current authority.

Terminal recording is fenced to the exact worker generation. A completed response is labelled `Advisory draft`; cancellation or expiry is labelled `Incomplete draft`, sets `complete=false` and `can_publish_final=false`, and preserves returned text when one exists. The database constraint makes an incomplete output structurally incapable of becoming a successful final draft. Each terminal outcome settles the exact reservation with non-negative actual units; a queued cancellation continues to release it without a provider call.

The worker AI switch and credentials are separate from API configuration and default off. This is a coding candidate only. Tests, CI, independent review, merge, staging deployment and owner acceptance remain pending for combined qualification.
