# Impact Management API and Event Contracts

This specification defines the transport contracts needed to implement the domain API, asynchronous events and resumable media transfer. The normative machine-readable files are contracts/openapi.json, event.schema.json, event-catalogue.json and access-policy.json. The API contract version is 1.1.0. The document resolves the nested DTO and media protocol gaps in LLD v1.0.

## 1 Contract surface and versioning

| Contract item | Count | Authoritative file |
| --- | --- | --- |
| API paths | 162 | contracts/openapi.json |
| API operations | 235 | contracts/openapi.json |
| Named schemas | 453 | contracts/openapi.json |
| Event types | 24 | contracts/event-catalogue.json |
| Exact capabilities | 183 | contracts/access-policy.json |

The API root is /v1. Tenant domain routes begin /v1/tenants/{tenant_id}. UUIDs are opaque. References must resolve within the current tenant and to the declared object type or immutable revision. A syntactically valid UUID is insufficient authority or referential validity. The operation inventory in the register maps every route and method to an exact capability.

Draft inputs may be incomplete while users compose them. Every supplied value must be valid. Activation, submission, publication and approval require the full FSD entity and lifecycle rules. Read-only calculations, decisions, snapshots, audit events and notifications cannot be manufactured through a generic create route. Workflow records are constructed by submission handlers rather than edited through a generic PATCH.

All defined object DTOs reject unknown properties. Dynamic answer and dimension maps allow only bounded keys and typed values. Lists have bounded lengths. No generic object or array of arbitrary values remains in the supplied schemas. Document-level validation, such as an acyclic framework or compatible units, supplements structural JSON validation.

## 2 Identity and HTTP behaviour

The same-origin web client uses a Secure HttpOnly host-only session cookie, SameSite protection, a session-bound CSRF token and validated Origin on mutations. The browser OIDC flow uses code with PKCE. Service and native clients use a qualified bearer flow. A request that carries conflicting identity credentials is rejected; the server does not select whichever identity grants more authority.

The server derives the principal, membership, tenant policy epoch and assurance context. Clients cannot set issuer, approver, original author, scan result, joined time, receipt time or commercial state through a draft input. User switching clears old request caches and subscriptions. Mutation responses use Cache-Control no-store; sensitive reads are private and no-store unless a qualified cache policy explicitly applies.

List limit is 1 to 100 and defaults to 50. An opaque cursor binds tenant, principal visibility, filter digest, stable ordering, schema version and expiry. The default order is creation time then object ID; a route that permits another sort advertises it explicitly. A policy change invalidates the cursor. Do not reveal the hidden count through total_rows. Cursors are authenticated and expire after 15 minutes as an implementation choice.

Transport rejects malformed JSON, duplicate object keys, invalid UTF-8, excess nesting and oversized bodies before domain processing. Normal JSON bodies are limited to 2 MiB; upload byte limits are separate. A correlation ID is generated or strictly parsed from the request and returned safely. Error messages never echo tokens, private queries or raw upstream responses.

## 3 Commands and concurrency

A create command contains operation_id and data. A mutation of an existing object also contains expected_revision. PATCH merges supplied top-level draft fields atomically. Omitted fields retain their values; a supplied nested object or array replaces that whole field. Null clears only a field whose schema permits null. An empty patch is invalid. No implicit merge of competing repeated form rows occurs.

The operation identity is tenant, actor, command type and operation ID. The canonical hash covers the route's logical target, method and validated payload, including the expected revision. Canonical JSON sorts keys, preserves array order and Unicode values, uses compact UTF-8, and permits decimal strings rather than binary floats. Search normalisation is separate. Equivalent transport whitespace does not create a new logical command; a different target or value does.

Within the transaction, acquire the policy and subject epoch locks, receipt lock and object head locks in the LLD order. A matching completed receipt is returned after present access is checked, even if the original expected revision is now old. The same operation ID with another payload returns CONFLICT_OPERATION. A different command with a stale expected revision returns CONFLICT_VERSION. The same receipt includes the original correlation ID and commit timestamp.

Successful synchronous changes return 200 with a committed receipt. Asynchronous acceptance returns 202 with a durable job receipt. A 202 response does not mean an import, report, deletion or sync has completed. The client polls a scoped job route or subscribes through the qualified event channel. Request cancellation cannot erase a committed item.

## 4 Error and value contracts

| Semantic code | HTTP | Treatment |
| --- | --- | --- |
| AUTH_REQUIRED | 401 | Establish valid identity |
| ASSURANCE_REQUIRED | 403 | Repeat the required strong authentication |
| RESOURCE_UNAVAILABLE | 404 | Same response for missing and hidden objects |
| POLICY_DENIED | 403 | Current capability, purpose or independence failed |
| VALIDATION_FAILED | 422 | Field-linked safe validation messages |
| CONFLICT_VERSION | 409 | Read current permitted revision and reconcile |
| CONFLICT_OPERATION | 409 | Operation ID was reused for another logical request |
| STATE_TRANSITION_DENIED | 409 | Requested transition is invalid for current state |
| EVIDENCE_REQUIRED | 422 | Required qualified evidence is absent |
| INCOMPATIBLE_MEASURE | 422 | Units or combination semantics do not match |
| UNDEFINED_RESULT | 200 result | Typed undefined value, absent numeric result |
| LIMIT_EXCEEDED | 429 | Bounded retry guidance; no silent partial effect |
| DEPENDENCY_UNAVAILABLE | 503 | Safe retry under the same operation identity |
| QUARANTINED | 423 | Content remains unavailable pending qualified processing |
| EXPIRED_GRANT | 410 | Renew authority through the permitted workflow |

Missing and hidden resources use the same 404 code, message class and field shape. Self-approval returns POLICY_DENIED with reason_code INDEPENDENCE_REQUIRED. A displayed undefined calculation uses a successful typed result with ValueState UNDEFINED, absent numeric value and a reason; it is not silently converted to zero or a server error.

A number is a decimal string with up to 26 integral digits and 12 fractional digits. Exponents, NaN, infinity, binary floats, overflow and excess precision are rejected. Intermediate calculation precision is at least 50 digits; official storage and display follow the LLD rounding contract. Geographic coordinates also use decimal strings, with latitude from -90 to 90, longitude from -180 to 180 and nonnegative accuracy checked semantically.

Text limits count Unicode scalar values. Codes are at most 64 characters, titles 200, ordinary descriptions 2000, comments 5000 and designated narrative fields 20000. Stored source codes preserve leading zeros. A field's classification and purpose follow it into reports, extracts, exports and model context.

## 5 Resumable upload protocol

Create an upload with purpose, mode WHOLE or MULTIPART, content type, exact expected byte count and SHA256. Maximum evidence media size is 25,000,000 bytes; maximum import file size is 100,000,000 bytes. Return upload ID, revision, state OPEN, 1,048,576-byte part size, expiry and any received parts. The upload lease lasts 24 hours from creation and cannot be extended by a client clock. Uncommitted parts are cleaned within 24 hours of expiry or cancellation.

For multipart mode, PUT parts numbered from 1. Offset is part_number minus one, multiplied by the part size. Every nonfinal part has the full part size; the final part has the exact remainder. The maximum is 96 parts. Each PUT supplies Content-Length and X-Content-SHA256. The receiver streams within a fixed memory bound, calculates the digest, and commits the part receipt only after durable storage. A matching retry returns the original receipt; another digest at the same number returns a conflict.

The upload owner, tenant, current scope and purpose are checked for every part and status request. Status reveals only the owner's eligible upload. A client recovering after a lost response reads the server's part manifest and transmits only missing parts. Received bytes are calculated from committed receipts, not an optimistic local counter. Changing the source file requires a new upload session.

Complete supplies operation ID, expected upload revision, ordered part list and whole-file digest. Under an upload lock the handler checks contiguity, exact sizes, receipt hashes and total bytes, seals the manifest, and changes the state to ASSEMBLING. No further part changes are accepted. The worker verifies the concatenated byte digest, moves through QUARANTINED and SCANNING, and marks CLEAN only after the qualified scanner accepts the actual file type and content.

Upload completion queues a job and is replayable. A lost acknowledgement is recovered by receipt or job lookup. A stale worker cannot publish because every state change checks the lease generation and sealed manifest digest. A digest mismatch or malware result produces REJECTED; scanner unavailability remains unusable and visible. A usable evidence attachment is created only from CLEAN content. Approved report bytes and downloads remain mediated by present disclosure policy.

Cancel requires current authority and expected revision. If assembly is running, record cancellation and stop at the bounded worker boundary. A completed approved artifact is governed by withdrawal and retention rules, not upload cancellation. Cleanup removes abandoned temporary bytes only after proving no completed blob or legal hold depends on them.

## 6 Submission and form validation

Answer values are tagged: text, decimal, integer, boolean, date, datetime, single choice, multiple choice, media, geopoint, repeat or explicit missingness. A repeat contains stable row IDs and another bounded answer map. The instrument limits remain 200 questions and 100 repeat rows; nested expression and execution bounds follow the LLD. Media references identify upload sessions and requiredness rather than pretending an untransferred attachment exists.

Validation checks the published form revision, field code, answer type, permitted choices, requiredness, relevance, repeat context and purpose. Hidden-value CLEAR or RETAIN_RESTRICTED behaviour comes from the published field definition. A received submission is distinct from an approved observation. An offline grant proves only its signed scope and lease; current server authority and compatibility are rechecked at sync. Expired grants return EXPIRED_GRANT with no partial domain write.

## 7 Events and webhooks

Events carry event ID, tenant, event type, schema version, aggregate ID, aggregate revision, monotonic aggregate sequence, occurrence time, actor, correlation, optional causation and a reference-only payload. No participant identifiers, credentials, file bytes or generated narratives are placed on the bus. The consumer retrieves current permitted content using the references when needed.

Write the event and outbox intent in the same transaction as the domain revision. Transport provides at-least-once delivery. Consumer deduplication uses tenant, consumer and event ID, and business source identities provide an additional guard. An event's sequence is taken from the locked aggregate revision counter. An older duplicate is ignored after receipt reconciliation; a gap pauses ordered projection application and reloads the authoritative state. UUID ordering is never used as sequence ordering.

The catalogue contains 24 event types with producers and consumer classes. Queue retention is seven days in this baseline; archive retention follows the governed audit and source policies. Replay uses a dedicated audited command, current authority and the original business identity. It cannot recreate deleted personal content or rerun an uncontrolled external side effect.

External webhooks use a separate delivery ID for each attempt and a stable event ID. Sign HMAC SHA256 over timestamp, a period character and the exact body bytes using a rotated destination secret identified by key ID. The receiver allows a five-minute timestamp window, constant-time comparison and deduplication. Attempts use bounded exponential backoff with jitter and enter a failure queue after eight attempts or 24 hours. Credential overlap is at most 24 hours. Destination changes require requalification, and each retry rechecks current scope.

## 8 Compatibility and validation

Pin the schema version in generated clients and event consumers. Additive optional properties require compatible closed DTO regeneration before a client sends them. Removing or reinterpreting a field requires a new supported contract version. A stored form or indicator revision keeps its original schema and meaning. Version changes include fixtures, migrations and tests in the same change set.

The preparation suite validates schema structure, reference resolution, malformed values, protected fields, multipart boundaries and route-to-policy coverage. Actual HTTP, cookie, streaming, concurrent commit and provider behaviour must pass against the implementation. See the execution report for the distinction between preparation checks and deployed tests.

## 9 Technical references

OpenAPI 3.1.1 defines the contract format: https://spec.openapis.org/oas/v3.1.1.html. The event and queue design follows the AWS transactional outbox and at-least-once delivery guidance at https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html and https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html. Protocol bounds and workflow decisions in this document are project design choices.
