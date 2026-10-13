# Release 1.06 coding candidate — traceable qualitative assistance

FR-AI-008 / APL-597 adds an Analyst workspace for source-bound qualitative suggestions. Every run pins an exact current Evidence revision, its classification and language, an exact current approved Codebook revision, and the tenant AI policy version. A suggestion is accepted only when its quotation is the exact character span of the permitted UTF-8 source, its SHA-256 matches, its optional speaker reference already exists in the Evidence payload, and every proposed code exists in the pinned codebook.

Each viewpoint remains a separate immutable suggestion, including opposing multilingual views. The system does not infer consensus or merge speakers. Machine translation is labelled `MACHINE_UNREVIEWED`; a person must explicitly review it before it becomes `HUMAN_REVIEWED`, and translation cannot create a new source permission.

Review accepts or rejects one suggestion at a time. Accepted edits use the existing governed `QualitativeExtract` write path and inherit the exact source classification. Rejected suggestions create no domain object. The immutable review retains the original proposal, final codes and theme, translation status, reviewer, operation receipt, and resulting extract reference.

Migration 0090 creates tenant-fenced, insert-only run, suggestion and review records. The new use case remains reserved-disabled until combined qualification activates it. Tests and CI remain deferred by owner request; this coding candidate is unmerged and undeployed.
