# Development increment 0.32: access extension and saved guidance

5 October 2026 · Build 0.32.0 local review candidate · domain API 1.23.0 · platform API 1.10.0 · schema 37.

This implementation appendage extends the same Tola/Impact Platform and nonprofit AI workspace. The proposed edition 1.0 BRD, FSD, HLD, LLD, editable documents, requirement registry, wireframes, 362-field dictionary and 108 specified case statuses keep their original reference point. The [release record](../../RELEASE-0.32-tola-ai-sprint.md) owns the final source-bound qualification summary. No design signoff, requirement acceptance, purchasing commitment, merge or deployment is recorded.

## Resulting behaviour

An existing organisation can deliberately extend access from its last applied profile to a registered newer profile. The owner proposes the exact additional capabilities, the named second administrator accepts, and an independent current operator approves. Relevant authority changes invalidate the proposal. Approval retains expiry dates, revoked earlier capabilities and deliberate omissions from managed roles. Separate authority renewal remains separate.

Saving a new adoption-plan revision captures the exact available learning/adoption, tool-directory and manual-practice guidance. The read-only saved-guidance panel lists actual saved revisions and loads their retained wording. Selecting a historical revision leaves the editable plan and learning progress unchanged. A missing legacy archive is unavailable; an unavailable retained practice edition produces a partial bundle. Historical supplier statements are historical and require direct confirmation before purchasing.

The loopback [live tracker](../../development-tracker/README.md) shows current workstreams, actual evidence, ETA ranges, confidence and stale-source warnings. The eight-hour window is 08:27:26–16:27:26 UTC / 13:57:26–21:57:26 IST. Four active agents including integration are the available maximum; additional work proceeds in waves. Elapsed time and the count of partially supported requirements never produce an overall completion percentage.

## Supporting requirement and case map

This is a support map. It does not mark a specified case executed or accepted.

| Requirements | Bounded added support | Named automated sources | Remaining scope |
| --- | --- | --- | --- |
| FR-NPA-006, FR-NPA-027, FR-NPA-039 | Atomic plan revision plus actual guidance binding; exact retry; bounded revision history | `test_ai_content_archives.py`, `test_ai_content_archives_live.py`, `test_ai_adoption_plans.py`, `tola-ai-sprint-check.mjs` | Formal specified-case execution, export/delete and operated service lifecycle |
| FR-NPA-007, FR-NPA-038 | Retained exact guide editions, verified archive hashes, legacy unavailable/partial states | `test_ai_content_archives_live.py`, `AIGuidanceArchive.tsx`, `tola-ai-sprint-check.mjs` | Human learning assessment, competency certification, guide governance and full retention policy |
| FR-NPA-025, FR-NPA-037, FR-NPA-039 | Current plan scope on guidance/history; natural-person-reviewed access extension; immutable registered profile and SQL narrowing checks | `test_access_upgrade.py`, `test_access_upgrade_unit.py`, `test_ai_content_archives_live.py` | Hosted/provider/security acceptance and complete platform access certification |
| FR-NPA-028, FR-NPA-040 | Real local browser smoke, retry, decision context/reset, read-only and mobile journeys | `tola-ai-sprint-check.mjs`, `sprint-0.32-browser-tests.json` | Manual assistive-technology review, hosted gates and nonprofit UAT |
| Core FR-TEN-001, FR-IAM-009, FR-SEC-003 | Reviewed additive capability delta and actual native runtime-role/archive fences | `test_access_upgrade.py`, `test_native_roles.py`, `test_ai_content_archives_live.py` | All original core acceptance criteria remain open |

The original core ledger retains 113 PARTIAL, 194 PENDING and zero accepted. The nonprofit feature registry retains its proposed baseline. The 108 specified cases remain SPECIFIED_NOT_RUN. Full native/application counts overlap focused counts and must not be added together.

## Current data and API appendage

The authoritative exact SQL and checksum register are in the [current migration dictionary](../../current/CURRENT-DATA-DICTIONARY.md). These are new additive migrations; prior migration bytes remain unchanged.

| Object or response | Fields / storage / authority |
| --- | --- |
| `platform_access_profile` | Exact profile hash and manifest, registration/source migration; immutable deployment metadata. Runtime platform role SELECT only. |
| `tenant_access_upgrade` | Tenant-qualified request/revision, owner/second identities, exact authority/profile pins, bounded reason, consent/review/apply times, Requested/Accepted/Applied/Rejected/Cancelled state. Forced tenant row security and control-plane-only grants. |
| `tenant_access_upgrade_applied` | Insert-only tenant/request application marker and count of authorities added. Only the narrow reviewed applicator writes it. |
| `ai_content_snapshot` | Tenant/snapshot key, retained `nonprofit-ai-guidance-v1` schema, closed JSON payload, canonical 32-byte digest and first bundle capture time. Deduplicated by tenant/digest; insert-only, forced row security, application SELECT/INSERT only. |
| `ai_plan_content_binding` | Exact tenant/object/revision to guidance snapshot, typed composite foreign keys to `AIAdoptionPlan`. Insert-only and never re-pointed. |
| `AIAdoptionGuidance` | Exact object/revision, COMPLETE/PARTIAL/UNAVAILABLE, nullable archive schema/time/hash, and AVAILABLE/UNAVAILABLE catalog/solutions/practice components with versions and retained payloads. |
| Plan revision history | Newest-first actual available revision IDs/numbers, saved time, title and integrity-verified historical availability. Signed 15-minute cursor tied to tenant, principal, plan and current visibility. |
| `content_compatibility.historical_snapshots_available` | Derived from an actual verified archive, replacing the former constant false. Current edition comparisons do not rewrite history. |

The domain contract adds `get_ai_adoption_guidance` and `list_ai_adoption_revisions`, both under existing scoped `ai.enablement.read`. It has 245 implemented operations. The platform contract has 52 operations including the eight access-upgrade operations. No new tenant capability family or bootstrap profile hash is introduced.

A bundle's `captured_at` is its first capture; a later plan revision can reuse an unchanged bundle. Old-client omission of an existing worksheet preserves that worksheet and its edition. Only an actual matching prior practice archive can supply its old words. Unavailable words remain absent. The same edition cannot acquire different wording within a tenant; such a save rolls back with `AI_GUIDANCE_VERSION_CHANGED`.

## Integration, operations and qualification

The Mac operations fix preserves backup-set checksums, atomic replacement, disk guard, UTC schedule and weekly hard-link semantics with checked GNU/BSD alternatives. Its 61 focused checks use synthetic temporary sets and stub clients; they are distinct from the actual native database restore drill.

Native process restart qualification now reads the actual API process environment through the host kernel: Linux `/proc`, or macOS `KERN_PROCARGS2`. Missing/omitted environment inspection fails qualification. It never substitutes the runner environment or logs returned values. Parser and actual synthetic-child checks preserve the credential-isolation assertion; Darwin constants and layout were verified against the installed SDK and [Apple's kernel source](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_sysctl.c).

Focused actual PostgreSQL 17.11 qualification passed 193 checks with no skips; the first four missing-role-activation fixture failures remain recorded. Thirteen integrated Chrome browser groups passed against the final review screens, with seven clean automated scans across desktop, 320 px and 390 px. Final full PostgreSQL regression passes 1,689 checks (26 explicit skips and one deselection); actual API restart, backup/restored database and populated 33→37 upgrade all pass. Full PGlite regression passes 1,633 checks (82 skips and one deselection), including resolution of the seven historical Mac operations failures. Counts overlap focused runs. Exact reports and source fingerprints are in the release evidence; environment preparation alone is not qualification.

## Next bounded increment and retained targets

Isolated 0.33 work prepares deliberate links from an AI adoption plan to governed Tola programme/indicator/period evidence, preserving the distinction between frozen official and current provisional results. It also prepares consent-based internal peer advice between existing plan-authorised members. These drafts are excluded from the 0.32 checkpoint until integrated and qualified.

The operated marketplace, supplier onboarding and awards, external adviser engagement, generated task approval, competency assessment, live connectors, monetary/token budgets, AI-specific retention and conditional payments remain target work. Existing shared identity, authority, immutable revisions, audit, receipts, measurements and official arithmetic are reused throughout.
