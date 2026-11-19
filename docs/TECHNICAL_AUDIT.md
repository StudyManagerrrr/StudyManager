# Technical Audit — AI Learning Guardian

**Date:** 2026-11-20  
**Type:** Static technical audit  
**Scope:** `docs/AI_Learning_Guardian_Web_SRS_Codex.md`, `DATABASE_MAPPING.md`, `DATABASE_GAPS.md`, current API/architecture/operations/security documentation, and all source files under `backend/`, `frontend/`, `agent/`, and `scripts/`.

## Executive summary

The workspace contains a runnable **prototype foundation**, not an acceptance-ready Guardian/Student platform. The main stack is present (FastAPI, React/TypeScript, SQLAlchemy schema reflection, and a separate Python Agent directory), but product flows remain incomplete. No test files or test runner configuration were found. There is no `.git` directory in the workspace, so commit history and an authoritative change baseline are unavailable.

The main release blockers are security and correctness: a default JWT signing secret is accepted, quiz endpoints do not consistently enforce family/assignment scope, and create endpoints accept foreign-key IDs without verifying those records belong to the selected Student. Several UI labels overstate what the API measures. The Agent has no operational pairing or ingestion path.

**Data protection for this audit:** no application code was changed; no tests or API routes were run; no TiDB connection, application-row query, DDL, migration, or production write was performed. Database findings below use the checked-in mapping/gaps documents (38 tables, 364 columns, 143 indexes, 70 foreign-key columns), not a fresh live-schema inspection.

## Architecture and repository shape

| Component | Current implementation | Audit assessment |
|---|---|---|
| Backend | `backend/app/main.py`; FastAPI routes, auth, scope helpers, reflected table queries, quiz scoring, AI request/persistence | All responsibilities are compressed into one module. SQLAlchemy Core reflects the schema at runtime; explicit ORM entities, repositories, API schemas and service boundaries are largely absent. |
| Database | `backend/app/database/schema.py`; global SQLAlchemy engine and `MetaData.reflect()` | Startup does not call `create_all` or migrations. A global engine makes isolated test substitution harder. Reflected metadata protects against guessed columns, but not authorization errors. |
| Configuration | `backend/app/core/config.py` | Reads the root `.env`; contains an unsafe built-in JWT secret fallback and does not reject it for production. |
| Frontend | `frontend/src/App.tsx`, `main.tsx`, `style.css` | Single large component; React Router and TanStack Query are installed but not used for route/query ownership. API base is hard-coded to loopback. Guardian and Student navigation are not separated. |
| Windows Agent | `agent/app/main.py` | Visible diagnostic process plus queue and HTTP client classes. `run()` only prints and sleeps; it does not initialize, collect, or synchronize events. |
| Developer setup | `scripts/*.ps1`, README, pinned Python and npm manifests | Setup and run scripts exist. No backend/Agent tests, pytest dependency, frontend test runner, Docker Compose, or isolated test database configuration exists. |
| Repository control | Workspace has no `.git` directory | Cannot inspect commit history, user changes, or rollback baseline. |

## SRS functional coverage

Status means source evidence exists; it does not imply the feature is complete or passes tests.

| SRS area | Source evidence | Status / gap |
|---|---|---|
| FR-01 Authentication and accounts | `POST /auth/login`, `GET /auth/me`; Argon2 and bcrypt verification | **Partial.** No invitation/acceptance, refresh/logout/revocation, reset, Guardian PIN, rate limiting, session enforcement, or role redirect workflow. `user_sessions` exists in DB mapping but is unused. |
| FR-02 Computer monitoring | `GET /monitoring/status`; Agent diagnostics/queue/client classes | **Not operational.** No collectors, heartbeat route, event batch route, presence, consent flow, event idempotency, or verified-time calculation. |
| FR-03 Application/site policies | DB tables and generic list names | **Not implemented.** No CRUD, policy lifecycle/version/acknowledgement, enforcement, override, or audit workflow. |
| FR-04 Webcam presence | `presence_logs` and screenshot schema only | **Not implemented.** No camera access or opt-in status flow; no presence inference. |
| FR-05 Schedules | Guardian `POST /schedules`; generic list read | **Partial.** No update/delete, recurrence expansion, timezone model, conflict detection, agenda/calendar behavior, reminder, topic/objective, or status workflow. Input does not validate `end_at > start_at`. |
| FR-06 Tasks/assignments | Guardian `POST /assignments`; generic list read | **Partial.** Basic create/list only. No Student lifecycle, submission/revision/review, completion criteria, required quiz/note, minimum verified duration, or retry policy. |
| FR-07 Notes/materials | Student `POST /notes`; generic material/note reads | **Partial.** No note UI, edit/submit/revision, attachments/upload/download, private object storage, access policy, or file scanning. |
| FR-08 AI analysis | Provider adapter and `POST /ai/analyze-note/{note_id}` | **Partial.** External call and DB persistence exist, but no frontend note flow, typed output model (only top-level checks), job lifecycle, OCR/reference comparison, provider failure persistence, prompt version, or Guardian review/approval. Provider transmission privacy/consent is not surfaced. |
| FR-09 Quiz | Quiz read, attempt start, attempt submit, objective scoring | **Partial and authorization-risky.** No Guardian quiz author/review/publish or AI generation, multiple-select scoring, immutable versioning, full retry policy, explanation timing, or completion criteria. Cross-family scope gaps are detailed below. |
| FR-10 Analytics | `GET /analytics` returns daily report rows; dashboard counts tasks/sessions/schedules | **Partial and misleading.** No metric derivation, weekly/monthly aggregation, overlap handling, knowledge trends, monitoring completeness, or timezone/date range. Dashboard “Verified study time” displays session count, not duration; `valid_duration_seconds` is not calculated by the session API. |
| FR-11 Notifications | Generic `GET /notifications` | **Partial.** No mark-read/preferences/deduplication/reminder delivery. Header bell is decorative. |
| FR-12 Security/settings | JWT and role checks in part of API | **Partial.** Settings page has no backend workflow; no active session management, export/deletion, retention controls, Guardian PIN, full audit, or device revocation. |
| Guardian workflow / Student workflow | Shared page shell and limited APIs | **Not end-to-end.** Student has no distinct information architecture; required school/extra-class learning path and Guardian review/publish gates are absent. |
| Web-vs-Windows boundary | UI text says browser cannot monitor OS; Agent is separate | **Concept stated accurately**, but no operational Agent integration exists. |
| Privacy/reliability | No hidden service, keylogging, webcam, or fabricated event source found | **Partial.** No retention/consent workflow, offline sync, duplicate prevention, recovery, backup, or audit coverage. |

## API and contract audit

### Routes currently registered in `backend/app/main.py`

- `GET /health`
- `POST /api/v1/auth/login`; `GET /api/v1/auth/me`; `GET /api/v1/relationships`
- `GET /api/v1/{resource}` with an internal fixed allowlist (`subjects`, `topics`, `schedules`, `assignments`, `notes`, `sessions`, `materials`, `quizzes`, `devices`, `policies`, `website-policies`, `monitoring-events`, `analytics`, and notifications)
- `POST /api/v1/subjects`, `/schedules`, `/assignments` (Guardian checks)
- `POST /api/v1/notes` (Student check)
- `POST /api/v1/study-sessions/start`; `POST /api/v1/study-sessions/{sid}/finish`
- `GET /api/v1/dashboard/{role}`; `GET /api/v1/monitoring/status`
- `GET /api/v1/quizzes/{quiz_id}`; `POST /api/v1/quizzes/{qid}/attempts`; `POST /api/v1/quiz-attempts/{attempt_id}/submit`
- `POST /api/v1/ai/analyze-note/{note_id}`

**Duplicate routes:** no exact duplicate HTTP method/path was found. The generic one-segment `GET /api/v1/{resource}` does not duplicate the multi-segment quiz/AI/dashboard routes, but it is a broad dispatch endpoint whose behavior and response shape are hidden in a dictionary. The Agent targets `POST /api/v1/agent/events/batch`; that endpoint is absent. This is an integration mismatch, not a duplicate.

### Request/response contracts

| Route group | Request | Current response | Contract issue |
|---|---|---|---|
| Login | `{ "username": string, "password": string }` | `{access_token, token_type, user}` | No explicit response schema, token expiry field, rate limit, session ID, refresh/revoke contract. |
| Guardian create | `{ "data": { ...arbitrary keys... } }` | Inserted row dict | Arbitrary dict is filtered to reflected table columns; required fields/enums/time constraints are not validated at domain boundary. Invalid inserts can surface DB errors. |
| Student note | `{title, content?, subject_id?, topic_id?, schedule_id?}` | Inserted note row | Relation ownership and subject/topic consistency are not checked. |
| Session start/finish | `{schedule_id?, session_type?}` / `{notes?}` | Inserted row / elapsed seconds and `verified_study_seconds: 0` | Schedule ownership not checked; duration is wall-clock elapsed only. |
| Generic list | No body; no pagination/filter contract | Raw array of reflected row dicts | Response fields depend on live schema; one 100-row limit; no stable envelope, cursor, sort or filter contract. |
| Dashboard | No body | `{role, student_id, metrics, tasks, schedules, sessions}` | `role` path parameter is ignored; metrics omit SRS measures and are not timezone scoped. |
| Quiz detail | Path ID | `{id,title,description,passing_score,time_limit_seconds,questions[]}` | Hides `is_correct`/answer key as required, but does not scope Guardian reads. |
| Quiz submit | `{answers: [{question_id, ...answer fields}]}` | score/count/pass/review fields | `answers` items are untyped dicts; partial/unknown question semantics, supported types and answer schemas are not explicit. |
| AI analysis | Note ID path; note content read from DB | `{status, analysis}` | No job/resource ID or stable provider error schema; route sends note text to external provider when configured. |
| Errors | FastAPI defaults and `HTTPException` detail | Variable error bodies | No shared error envelope/code; SQL integrity errors are not mapped consistently. |

The frontend calls the backend via `fetch`, with JSON headers and a bearer token. It has no generated/shared TypeScript contract, runtime response validator, or typed API module. Details are in the frontend section below.

## Authentication, authorization and scoping

### Implemented

- Login looks up username or email, returns a generic 401, verifies Argon2 or bcrypt hashes.
- JWT identity is resolved by `sub`, then user is reloaded from `users` and active status checked. Role comes from the database record, not trusted from the JWT role claim.
- Student list scope is self; Guardian list scope uses active `guardian_student_links`.
- Guardian create checks `role == GUARDIAN` and selected `student_id` through relationship scope, with a single-linked-Student default.
- Student note and session creation check Student role. Session finish filters by both session ID and the authenticated Student ID.
- Quiz detail for a Student checks task assignment or a link to the quiz creator. Correct option flags and correct answer fields are not returned in quiz detail.

### High-risk authorization gaps

1. **Quiz detail, Guardian:** `get_quiz()` permits any authenticated Guardian to retrieve any active quiz ID; it does not verify the quiz creator/task belongs to the Guardian's linked Student.
2. **Quiz attempt creation, Student:** `attempt()` checks Student role and active quiz only; it does not call the assignment/Guardian-link authorization used by quiz detail. A Student can create an attempt for an unrelated active quiz if its ID is known.
3. **Related foreign keys:** Guardian schedules/tasks and Student notes scope the owning `student_id`, but accept `subject_id`, `schedule_id`, and `topic_id` without checking that each record belongs to the selected Student and that related subject/topic/schedule IDs are mutually consistent.
4. **Study session start:** accepts any `schedule_id` without checking schedule ownership. This creates a cross-family/inconsistent relation risk.
5. There is no authorization regression test suite to detect these cases.

### Authentication/security gaps

- `JWT_SECRET` falls back to the hard-coded literal `change-me-before-deploy`; settings do not refuse this value in production. `.env.example` has no JWT secret placeholder.
- Access JWT lifetime is 10 hours. Browser stores it in `localStorage`. There is no refresh, logout, revoke, or server-side token lookup; mapped `user_sessions` fields are unused.
- No login/pairing/sensitive-action rate limiting; no password reset, Guardian PIN, invitation or reauthentication flow.
- `current_user()` catches every exception, including database failures, and reports 401. This can misclassify availability incidents and masks operational error distinctions.
- Startup logs reflection failures and continues; health later may fail when it retries. Readiness/startup policy is not explicit.
- `CORS` defaults to configured frontend origin plus `http://127.0.0.1:5173`; deployment origin configuration must be checked and restricted.
- No evidence of logging passwords/tokens/API keys in current source; however logging/error behavior has not been covered by tests.

## Database mapping and gap analysis

Mapping inventory lists 38 base tables, 364 columns, 143 indexes and 70 foreign-key columns. Existing schema has substantial usable domains: `users`, `guardian_student_links`, `user_sessions`, subjects/topics/schedules/tasks, notes/materials/attachments, AI analyses, quizzes/questions/options/attempts/answers, study sessions, devices/settings, applications/policies, activity/monitoring/presence logs, reports, notifications, flashcards/reviews, achievements, and audit logs.

### Compatibility strengths

- `user_sessions` has `token_hash`, `expires_at`, and `revoked_at`; a session workflow may be possible without DDL, subject to a safe token design.
- Quiz questions/options/answers and attempts support basic objective scoring. `quiz_answers` has a unique `(attempt_id, question_id)` index.
- `ai_analyses` has summary, JSON concept/topic/recommendation fields, provider/model, status, and error text for simple note analysis.
- Daily and weekly reports, knowledge progress, and review-schedule tables exist.
- Existing schema reflection does not auto-create or alter tables.

### SRS concepts not directly represented or requiring compatibility review

These are gaps in checked-in mapping, not permission to change schema:

- `devices` has owner/identifier/status/heartbeat but no dedicated credential hash, pairing code, expiry, revocation timestamp, or paired-by field. `device_settings` is a 5-column generic key/value table and is not a reviewed secret store.
- No invitation or temporary access-request table is listed. `system_settings` is global key/value and does not obviously provide per-Guardian PIN or invitation lifecycle safely.
- `learning_tasks` has title, description, status, due/priority/estimate, subject/schedule/creator, but no explicit learning objectives, topic ID, required note/quiz, verified-minute threshold, passing/retry criteria, approval/revision state, or version.
- `study_schedules` has subject, title/type/times/recurrence JSON/reminder/location, but no direct topic/objective/timezone/status fields.
- `ai_analyses` is note-linked and lacks explicit requester, prompt version, input reference IDs, job lifecycle timestamps, approval state, and analysis version.
- `quizzes` lacks a quiz version/publication/approval field and snapshot semantics for historical attempts. Existing options encode correctness; quiz reads must keep those keys private.
- No table captures stable Agent `event_id`, `received_at`, `agent_version`, `policy_version`, or ingestion acknowledgement as explicit columns; `monitoring_events.id`/JSON could be considered only after an explicit compatibility review.
- File tables store paths/metadata but do not define an object-storage provider, safe signed download, access audit, scanning, or retention workflow. `screenshots` includes `retention_until` but no consent/access audit fields appear in that table.
- `guardian_student_links.student_id` is unique in the mapping, so each Student can have at most one active or historical Guardian link at a time unless index semantics/data lifecycle differ; this constrains SRS future multi-Guardian tenancy.
- `study_sessions` has elapsed/valid/break counters but no established policy formula; current route updates elapsed only and leaves valid duration zero.

No schema changes were made or are authorized by this report. Document any future mismatch in `DATABASE_GAPS.md` and get the approval required by project policy before a schema change.

## Frontend-to-backend connectivity and code authenticity

### Real API calls found

- Login → `POST /auth/login`; token restored through `GET /auth/me`.
- Dashboard → `GET /dashboard/{role}`.
- Resource pages → generic `GET /{resource}` for schedules, assignments, subjects, materials, quizzes; monitoring → `GET /monitoring/status`.
- Guardian form → `POST /subjects`, `/schedules`, or `/assignments`; then refreshes the collection.
- Student quiz panel → quiz detail, attempt start, and submit endpoints.
- All calls use the single hard-coded API base `http://127.0.0.1:8765/api/v1`.

### Not connected / dead or misleading UI

- There is no notes navigation/form, so `POST /notes` and the AI analysis endpoint cannot be reached through the UI.
- AI page remains an explanatory empty state; it does not expose the existing note-analysis endpoint.
- Settings, Notifications, Learning Materials upload, policies, audit history, and full analytics are not functional pages. Bell, search, streak, and several controls are decorative/nonfunctional.
- Student sees Guardian-oriented navigation. There is no distinct Student route map or protected route tree; internal page state selects views.
- “Verified study time” stat displays `sessions_today` (a session count) and not seconds/minutes. It is therefore mislabeled rather than a real verified-time metric.
- “Thursday, November 20” is hard-coded. It does not follow current date/user timezone.
- No fake monitoring events or fake AI results were found. Several fallback labels/placeholders (`—`, unknown/offline) are honest; the verified-time label is not.

## Endpoint duplication and incomplete logic

- **No duplicate method/path pairs** were found in the registered FastAPI routes.
- The generic GET dispatcher is broad but has a fixed resource-name allowlist. It is not a duplicate of multi-segment detail routes, though it hides per-resource response contracts and is unsuitable as a substitute for proper list/detail APIs.
- The Agent's configured target route is missing in the backend. This is a broken integration contract.
- Other incomplete logic: session overlap/duplicate-active-session concurrency; session schedule ownership; schedule time/conflict/recurrence validation; task state transitions/completion criteria; quiz assignment/version and concurrency rules; analytics timezone/overlap calculation; policy acknowledgement; event dedup; file authorization; AI job failure persistence.

## Severity-ranked issue list

### Critical

- **C1 — Insecure default JWT signing key accepted.** If deployed with default config or secret omitted, tokens can be forged; protect deployment and user data by rejecting startup until a secret is configured. Source: `backend/app/core/config.py` (`jwt_secret` default), `backend/app/main.py` (`token`, `current_user`).

### High

- **H1 — Cross-family quiz reads/attempts.** Guardian quiz read is unscoped; Student attempt creation bypasses assignment scope. Source: `backend/app/main.py`, `get_quiz()` and `attempt()`.
- **H2 — Related-record ownership not checked.** Create schedule/assignment/note/session can attach known foreign subject/topic/schedule IDs. Source: `create_schedule()`, `create_assignment()`, `create_note()`, `start_session()`.
- **H3 — Access token exposure and no revocation.** 10-hour JWT in `localStorage`, no logout/refresh/session validation; `user_sessions` is unused. Source: `frontend/src/App.tsx`, `backend/app/main.py`, `backend/app/database/schema.py`.
- **H4 — No isolated automated tests.** Authorization and scoring gaps have no tests; mutation testing against shared TiDB would violate policy. No test sources/configuration found.
- **H5 — Metric misrepresentation.** Verified-time card is backed by session count, not verified seconds; session API leaves valid duration at zero. Source: `frontend/src/App.tsx`, `backend/app/main.py` dashboard/session routes.
- **H6 — Agent sync is nonfunctional.** Client targets a missing endpoint and run loop never initializes queue or syncs. No device auth, pairing or event contract. Source: `agent/app/main.py`.

### Medium

- **M1 — API request/response contracts too loose/inconsistent.** Arbitrary dicts, raw row dumps, no response models/pagination/filter/error envelope; write validation delegated to DB.
- **M2 — Database outages reported as unauthorized.** Broad exception handling in current-user dependency. Startup reflection failure is swallowed.
- **M3 — Frontend deployment configuration and page wiring.** Loopback API constant, no role-specific routes, AI UI path calls a nonexistent GET route, dead controls.
- **M4 — Incomplete SRS workflows.** No invitations/sessions, complete CRUD, submissions/materials, Guardian approval, policy, notifications, analytics, WebSockets, or retention.
- **M5 — SRS/database capability gaps require design.** Pairing/credential lifecycle, task criteria, quiz version/approval, per-user PIN/invitations, Agent event lifecycle, object storage/privacy. No schema change until gap review and approval.
- **M6 — Documentation drift.** Several claims were stale at audit start; `DATABASE_GAPS.md` was aligned for quiz routes during this audit. Keep API/README/security docs synchronized with implementation.
- **M7 — No Git metadata.** Cannot determine user changes or establish safe commit/rollback history.

### Low

- **L1 — Maintainability/formatting.** Main API and UI are compressed into very long lines/modules; route-specific ownership rules are hard to review.
- **L2 — UI date, locale and accessibility maturity.** Hard-coded date, no working language/theme switch, minimal semantic/test coverage.
- **L3 — Setup reproducibility.** Setup installs Python dependencies globally instead of a project virtual environment; no unified test command or local isolated database instructions.

## Audit disposition

No feature was marked done by this audit. No application behavior was modified. See `IMPLEMENTATION_ROADMAP.md` for the dependency-ordered work plan and test gates. Approval is only required later if a proposed step needs schema changes, production migrations/writes, or a change to monitoring/retention policy.


## Remediation update ? Phase 1 security foundation

Updated after the initial static findings; fixes are covered by isolated SQLite tests, not TiDB.

- **Resolved:** insecure static JWT fallback. Development now creates a process-local random secret; non-development requires a >=32-character, non-placeholder `JWT_SECRET`. `.env.example` documents the variable with a placeholder only.
- **Resolved:** quiz detail/start/submit scope now uses target task/subject ownership and Guardian-Student links; family-owned related subject/topic/schedule IDs are checked before inserts.
- **Resolved:** access JWT is 15 minutes and tied to an active `user_sessions` row; refresh is HttpOnly/SameSite Strict, hashed at rest, rotated and reuse revokes active user sessions. Logout and logout-all revoke sessions. Frontend no longer stores access tokens in localStorage.
- **Partial:** login failures are limited in process memory. This is not a distributed limiter; production multi-worker deployment still needs a shared rate-limit store or enforced single-worker/proxy policy.
- **Resolved:** current-user DB failures map to 503 instead of 401. CORS local origins are development-only. Dashboard no longer labels session counts as verified duration; verified-time calculation remains absent.
- **Added:** SQLite-only tests for cross-family quiz access, foreign subject/schedule rejection, answer-key hiding, refresh rotation/reuse, logout, invalid tokens, JWT config and login throttling.
- **Remaining schema/service gate:** invitation, password reset, Guardian PIN and email verification lack a safe token/security lifecycle in mapped schema; email delivery is not configured. See `AUTH_SCHEMA_PROPOSAL.md`. No schema action was taken.
- **Verification:** `pytest backend/tests -q` ? 11 passed; `python -m compileall -q backend/app backend/tests agent/app` ? passed; frontend build initially caught missing Vite env types, fixed with `frontend/src/vite-env.d.ts`, then production build passed. Deprecation warning remains for FastAPI `on_event` startup hook.
- No production database connection or write was used for these tests.
