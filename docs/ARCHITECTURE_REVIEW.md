# Architecture review and implementation plan

Review date: 2026-11-20  
Scope: official Web SRS, live-schema mapping/gaps documents, API/operations/security docs, and all checked-in workspace source. No source feature code or database schema was changed during this review. No repository metadata exists (`git status` reports this directory is not a Git repository), so there is no trustworthy baseline diff.

## System shape observed

```text
Browser (React, one App component)
  ?? fetch() with bearer token in localStorage
       ?? FastAPI app/main.py (routes + auth + queries + business logic)
            ?? SQLAlchemy Core MetaData.reflect() against TiDB

Visible Agent process (agent/app/main.py)
  ?? SQLite queue scaffold
  ?? HTTPX client for an event batch route that the backend does not expose
```

- Backend configuration is in `backend/app/core/config.py`; database reflection is in `backend/app/database/schema.py`. `main.py` defines authentication, authorization helpers, SQL statements, route handlers, quiz scoring, and AI note orchestration in one module.
- Persistence uses reflected SQLAlchemy Core tables rather than explicit mapped models/repositories. This avoids guessed columns and startup DDL, but arbitrary `dict` request bodies and route-level table access make validation, ownership checks, and test isolation difficult.
- The web app has one role-agnostic navigation and one `App.tsx`; role differences are mostly labels and conditional buttons. Its API base URL is a source constant (`http://127.0.0.1:8765/api/v1`).
- The Agent currently prints diagnostics and sleeps. It has no collectors, configuration/pairing flow, credential store, heartbeat, policy sync, or event upload loop. Its client expects `/api/v1/agent/events/batch`, which does not exist.
- Runtime data store remains the existing TiDB schema. `DATABASE_MAPPING.md` documents 38 tables / 364 columns / 143 indexes / 70 foreign-key columns. All 38 table sections were inventoried against the listed columns. The mapping uses `?` as its generated placeholder for NULL defaults/empty key metadata (clarified in that document). `DATABASE_GAPS.md` calls out device pairing credentials, AI job lifecycle, object storage, policy/event workflows, and analytics workflow gaps. Its quiz status was stale and is now aligned with current code. This review proposes no DDL.

## Implemented API surface found in code

`GET /health`; `POST /api/v1/auth/login`; `GET /api/v1/auth/me`; `GET /api/v1/relationships`; generic `GET /api/v1/{resource}`; Guardian `POST /subjects`, `/schedules`, `/assignments`; Student `POST /notes`; Student study-session start/finish; `GET /dashboard/{role}`; quiz read/start/submit; `GET /monitoring/status`; and `POST /ai/analyze-note/{note_id}`.

The generic collection route maps only selected resource names, returns up to 100 rows without pagination/filter contract, and does not provide per-record read/update/delete APIs. Full endpoint details must be maintained in `API.md` as routes are modularized.

## Findings to address before feature expansion

### P0 ? access control and configuration

1. `GET /quizzes/{quiz_id}` authorizes Student assignment/Guardian relationship but does not scope Guardian reads to their linked Student or quiz ownership. Any authenticated Guardian can read an active quiz ID.
2. `POST /quizzes/{qid}/attempts` checks only Student role and active quiz; it does not verify that the quiz is assigned to that Student. This allows attempts on another family's quiz if its ID is known.
3. Guardian create-schedule/create-assignment accepts relation IDs (`subject_id`, `schedule_id`) from arbitrary request dicts without verifying those referenced records belong to the selected linked Student. Student note creation similarly accepts subject/topic/schedule IDs without ownership validation. Foreign keys protect existence, not family authorization.
4. JWT signing has a built-in `change-me-before-deploy` fallback and no startup refusal for production/default secrets. The `.env.example` does not define `JWT_SECRET`.
5. Browser access tokens are persisted in `localStorage` for a 10-hour JWT; there is no refresh/revocation route. XSS would expose the bearer token.

### P1 ? reliability and maintainability

- `current_user` catches all exceptions, including database connectivity errors, and converts them to 401; database failures can be misreported as invalid authentication.
- Startup reflection errors are logged then swallowed. The service can start with no reflected schema and fail later on requests.
- API error responses use FastAPI defaults; there is no documented shared `{code, detail, errors}` contract or application exception handler.
- Generic `Item.data: dict` drops unknown columns at insert time and does not enforce required domain fields, enum values, timezone rules, or schedule conflict/relationship rules before attempting a write.
- Quiz submission is atomic for its transaction, but attempt creation does not enforce assignment scope. Multiple-select scoring, immutable quiz versioning, explanation timing, retry policy beyond raw max attempts, and task completion criteria are absent.
- AI output validation checks top-level keys/types only. There is no persisted job lifecycle, request/provider failure record, prompt version, Guardian approval flow, or reference-material comparison. Frontend has no learning-notes UI despite the analysis endpoint.
- Agent queue initialization does not create the parent directory for its default SQLite path. Agent sync is not invoked by `run()`, and the target batch API is absent. No event contract/device credential is operational.
- There are no backend/Agent test files or test commands in package manifests/dependencies. No isolated DB fixture is configured.

### P2 ? frontend and developer experience

- One `App.tsx` owns authentication, navigation, fetches, forms, and rendering; React Router is included but unused. Guardian and Student navigation are not distinct, and many menu sections route to generic/empty records.
- API URL is hard-coded to loopback, making deployed or remote-hosted frontend use fail (and causing HTTPS mixed-content issues).
- Date/locale in the welcome panel is hard-coded. Visible buttons/notifications/search/settings include decorative or incomplete actions.
- `README.md`, `SECURITY_PRIVACY.md`, and `API.md` contain stale scope claims: security says Argon2-only while source accepts bcrypt; README says quiz scoring/submission are incomplete while routes exist; API docs omit quiz result, note analysis, and actual path names. Agent setup wording implies syncing readiness that code does not provide.
- No Git repository exists at this workspace root, so change history/review and rollback cannot currently be inspected.

## Database compatibility and protection

Current source reflects TiDB metadata only on startup and does not call `create_all`, Alembic, or migration commands. Route writes occur only on explicit user actions, but they target the configured shared database; therefore these endpoints were not invoked during this audit. No application rows were read and no production write was run in this review.

The live mapping remains the source for field names/types. Database relationships do not replace application authorization checks. No schema changes are proposed. If later work identifies a schema gap, document it in `DATABASE_GAPS.md` and obtain the separately required approval before any schema-changing action.

## Incremental implementation plan

### Module 1 ? test and security foundation (next)

- Add isolated SQLite test fixtures for the reflected/core tables needed by auth, Guardian/Student scopes, quiz access, and create operations; make engine/session dependencies overrideable without contacting TiDB.
- Add backend/Agent pytest setup and deterministic tests for 401, Guardian/Student relationship boundaries, unrelated-quiz access, referenced-record ownership, scoring, and queue path creation.
- Extract authorization and request/response schemas into small modules without changing endpoint contracts unnecessarily.
- Fix quiz read/start authorization and validate every foreign-key reference against the selected Student/Guardian relationship.
- Require a configured JWT secret outside development and reject the known fallback; correct database errors to remain server errors rather than 401.
- Run tests only against isolated fixtures; no TiDB CRUD smoke tests.

### Module 2 ? auth/session and route contracts

- Implement the approved session lifecycle using existing `user_sessions` table after verifying its current mapped shape; short-lived access token, revocation, logout, generic login failure, and rate limiting.
- Add centralized JSON error handling and strict request/response schemas; update API docs.
- Check legacy password verifier/hash parameters before any hash migration; do not rotate credentials silently.

### Module 3 ? Guardian/Student core learning

- Split subject/topic/schedule/assignment/note/session route/service modules.
- Define task criteria and schedule recurrence/conflict behavior from the SRS, then implement and test one workflow at a time.
- Build role-specific routes and usable note/material/schedule/task pages against the API; remove dead navigation before marking those views complete.

### Module 4 ? quiz/AI approval lifecycle

- Add quiz version and assignment-policy semantics using current columns where compatible; document any missing persistent fields in `DATABASE_GAPS.md`.
- Implement AI analysis/job/provider failure handling and Guardian review. Validate output with typed Pydantic schemas and tests with a mocked provider.
- Do not publish/auto-assign generated assessment unless an explicit Guardian approval rule permits it.

### Module 5 ? Agent, policies, analytics, production

- Specify and test pairing/credential design against existing schema first. Do not store long-lived secrets in generic settings absent a reviewed design.
- Implement visible collectors only after consent/policy UX, typed event validation, idempotency, acknowledgements, offline retry, and verified-duration calculation are testable.
- Add analytics from persisted evidence; distinguish unknown from zero and avoid overlap double-counting.
- Complete object storage, retention, localization, deployment, and acceptance flows after dedicated isolated tests.

## Approval items

- No approval is requested in this audit; no database change is proposed.
- Approval is required before any schema change, production migration, or change to monitoring/retention policy. Agent credential storage schema is a known decision point; next module can first evaluate existing tables without changing them.

## Audit verification

- Read-only workspace/source/document inspection only.
- No tests were run in this architecture-only phase.
- No database connection, application-data query, DDL, migration, or write was performed.
