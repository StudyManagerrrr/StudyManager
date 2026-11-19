# Implementation Roadmap

This roadmap follows the technical audit and keeps schema/data safety as a hard gate. It orders work by authorization risk and dependency. Each unit must have isolated automated tests, a frontend build where applicable, contract documentation, and a compatibility review. Tests must not connect to or write the configured TiDB instance.

## Phase 0 — Audit and baseline (complete)

- Read SRS, DB mapping/gaps and all current source/docs.
- Record implementation status, request/response contracts, security findings, UI integration, schema compatibility and missing workflows in `TECHNICAL_AUDIT.md`.
- Confirm no duplicate method/path routes in the current FastAPI route declarations.
- No runtime or production mutation used in this static audit.

## Phase 1 — Isolated test harness and auth-critical fixes (next; P0/P1)

### Plan

1. Refactor engine/database creation behind an injectable dependency so `TestClient` can use an isolated SQLite fixture. Keep startup reflection opt-in/configurable for tests; assert no `create_all` path exists for TiDB.
2. Add `pytest` tests for token verification, inactive users, generic login errors, relationship scope, Guardian/Student route roles, record ownership, quiz assignment access, score calculation and duplicate submission behavior.
3. Remove the insecure JWT secret fallback for non-development environments; fail startup if the secret is absent, placeholder, or too weak. Add a test for each environment path.
4. Adjust auth exception handling so an invalid/missing token remains 401 while database/service failures remain server errors. Define the minimal stable error envelope.
5. Fix quiz detail and attempt creation authorization using assignment/Guardian relationships before any DB write.
6. Validate every provided `subject_id`, `topic_id`, and `schedule_id` against selected Student ownership before insert. Validate session schedule ownership and schedule time ordering.
7. Add tests proving rejected operations perform no persistence. Tests use injected SQLite fixtures only.

### Database impact

No DDL. `user_sessions` table exists according to mapping but this phase does not yet change auth lifecycle. No test connects to TiDB.

### Exit gate

- Isolated backend suite passes; unauthorized cross-family quiz and foreign-key cases are rejected.
- Frontend production build still passes.
- Startup security checks are documented; no source tests invoke production write routes.

## Phase 2 — Session lifecycle and stable API contracts (P1)

1. Decide token storage/session design (short access token, refresh rotation/revocation, logout) using mapped `user_sessions` fields. Confirm token hashing/expiry/revocation semantics before implementation.
2. Do not assume `user_sessions` supports refresh-token reuse detection; compare schema and document any gap. No new columns without explicit approval.
3. Add typed Pydantic request/response contracts and TypeScript API types. Remove arbitrary write dicts in favor of domain schemas.
4. Standardize errors, status codes, pagination, sorting, filters, and UTC/local timezone rules.
5. Add tests for password format compatibility without reading real user data. Do not silently rehash production accounts.

### Exit gate

- OpenAPI and `docs/API.md` agree with contracts.
- Auth session tests cover rotation/revocation or documented unsupported boundary.
- No secret in source, logs, or frontend bundle.

## Phase 3 — Role-aware frontend and core learning flows (P1/P2)

1. Configure API base from build/runtime environment and reject insecure production loopback/mixed-content configuration.
2. Split Guardian and Student navigation/routes; add route guards backed by `/auth/me` and backend authorization.
3. Extract shared API client and typed query hooks; either use installed TanStack Query/React Router or remove unused dependencies.
4. Implement schedule and task workflows incrementally: subject/topic ownership, recurrence and timezone, conflict detection, validated state transitions, Student completion/submission, Guardian feedback.
5. Implement notes UI and use the existing note/AI APIs only after access/consent and error states are clear.
6. Implement private materials upload/download only after file size/type checks, object storage contract, ownership checks, and retention plan.
7. Replace dead controls and hard-coded dates. Make every dashboard metric traceable to a real API calculation; label elapsed versus verified time distinctly.

### Exit gate

- Guardian and Student acceptance tests run against isolated backend fixtures.
- All visible buttons/forms have observable API-backed behavior or are removed.
- No mock data in production flows.

## Phase 4 — Quiz and AI review lifecycle (P1/P2)

1. Define question-type contracts (multiple choice, multiple select, true/false, short answer), scoring/partial-answer rules, explanation timing, attempts and task pass criteria from SRS.
2. Add immutable quiz version semantics or document required schema gap before implementation. Preserve historical attempt interpretation.
3. Implement Guardian create/edit/review/publish and Student assigned-quiz flow. Do not reveal answer keys before submission.
4. Validate all AI output with Pydantic schemas; mock the provider only in tests. Persist job/error state using existing compatible fields where possible; document absent lifecycle fields in `DATABASE_GAPS.md`.
5. Add consent disclosure for sending notes to configured AI provider; store provider/model metadata and avoid logging note contents/secrets.
6. Test retries, max attempts, concurrent submits and ownership using isolated DB.

### Exit gate

- End-to-end note → AI proposal → Guardian review → quiz → score/retry flow is verified on isolated fixtures.
- AI unavailable/malformed cases return truthful failures and do not create fake outputs.

## Phase 5 — Agent pairing, event transport and transparent monitoring (P1/P2)

1. Design device pairing and secret lifecycle against the existing `devices`/`device_settings` schema. Do not use generic JSON settings as secret storage without a security design.
2. If existing schema is insufficient, update `DATABASE_GAPS.md` with options and request explicit approval before any schema action.
3. Define typed/versioned event and batch-acknowledgement contracts, stable IDs, idempotency, UTC timestamps, policy version, agent version, offline queue deletion semantics and revoked-device behavior.
4. Implement backend pairing/heartbeat/event ingest before enabling the Agent HTTP sync path.
5. Add explicit visible consent/policy UI before collecting app/idle data. Keep camera/screenshot features disabled until retention and access audit behavior is specified.
6. Implement verified study-time formula from available signals; distinguish unknown, idle, away, active and verified. Never equate presence with attention.
7. Build mocked Windows API tests for collectors and safe shutdown; no actual screenshot/camera collection in CI.

### Exit gate

- Agent can pair, visibly show state, queue and sync idempotently, and stop on revocation in mocked integration tests.
- UI shows acknowledged/enforced state only after server confirmation.

## Phase 6 — Analytics, notifications and production readiness (P2)

1. Derive daily/weekly/monthly analytics from stored evidence with timezone boundaries, overlap handling, completeness flags, and explicit metric definitions.
2. Add notification read/preferences/idempotency flows and tests.
3. Implement file/object storage and retention, audit access to sensitive data, export/delete workflows only after policy review.
4. Add WebSocket auth/scoping/reconnect tests or keep an explicit polling fallback.
5. Add deployment setup, secrets management, TLS/CORS guidance, backup/restore and Agent installation/revocation manuals.
6. Run isolated end-to-end flows, frontend responsive/accessibility checks, dependency/security review and performance checks.

### Exit gate

- Every SRS Definition-of-Done item claimed complete has UI/API/auth/persistence/loading/error tests.
- Security and privacy review passes; no production test writes or unapproved DDL.

## Approval gates

- This roadmap requests **no schema change now**.
- Any schema extension or migration requires a written gap/options/impact analysis, isolated test plan, backup/recovery plan, and the user's explicit approval before execution.
- Any production database write for verification, monitoring-consent change, retention change, or collection of new monitoring categories requires the relevant explicit authorization and documented behavior.

## Current implementation checkpoint (2026-11-20)

Phase 1 has started: JWT/session lifecycle, logout/revocation, login throttling, audit events, frontend in-memory access token use, and scoped quiz/foreign-key checks are implemented with 18 isolated SQLite tests. Frontend production build passes. These changes are partial remediation, not closure of the full authorization matrix.

Phase 2 has started: subject/topic/schedule read/detail/update and safe archive operations exist, plus Guardian create/list endpoints. Topic archival is omitted because the mapped schema has no archive column. Task lifecycle is deferred because the SRS status and completion model cannot be represented by mapped `learning_tasks`/`learning_notes`; see `DATABASE_GAPS.md`.

The current next action is to complete the task contract/schema analysis and add test-covered UI for already-supported subject/schedule/topic operations. Continue to use isolated DB fixtures. Do not execute DDL or test writes against TiDB. Any schema change requires a separate impact proposal and explicit approval.
