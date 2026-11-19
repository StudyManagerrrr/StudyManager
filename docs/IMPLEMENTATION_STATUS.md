# Implementation status

Updated: 2026-11-20

## Overall

**IN PROGRESS. The product is not DONE.** The bilingual UI, shared notification foundation, centralized API error envelope, and their isolated tests are implemented. Several SRS workflows remain partial or absent. Work has not written to TiDB. Runtime schema inspection remains read-only at startup.

## Module status

| Module | Status | Evidence / remaining work |
|---|---|---|
| Repository and technical audit | Complete | `TECHNICAL_AUDIT.md`, `IMPLEMENTATION_ROADMAP.md` |
| Authentication foundation | Partial | JWT access + refresh rotation, logout/revocation, rate limited Guardian self-registration, login throttling, audit events, and isolated tests. Student invitations, password recovery, PIN controls, distributed throttling and production configuration review remain. |
| Authorization | Partial | Guardian/Student scopes on core records and quiz access; isolated cross-family checks exist. Full endpoint-by-endpoint coverage and frontend role workflows remain. |
| Subjects/topics/schedules | Partial | Backend list/detail/create/update and safe archive where schema supports it. Basic frontend create/list only; recurrence, conflict/timezone handling and calendar UX are missing. Topic archive is unavailable because `topics` has no active/archive field. |
| Assignments/tasks | Partial | Guardian create/list exists; dashboard lists scoped tasks. SRS completion criteria, student start/submit/revision/review flow are absent; schema stores only a small subset of SRS fields. |
| Notes/materials | Partial | Student note creation and AI note analysis backend exist. No complete submission/revision/attachment UI or file storage workflow. |
| Quizzes | Partial | Scoped read/start/submit and objective scoring exist. Authoring, review, publication, versioning and broad question-type coverage remain. |
| AI | Partial | Provider-backed note analysis persists validated result. No complete UI/job/review workflow; provider configuration is required. |
| Windows Monitoring Agent | Incomplete | Python/SQLite scaffold; pairing, reliable queue initialization, sync API, collectors and policy controls remain. |
| Analytics/notifications | Incomplete | Some dashboard aggregates; no validated analytics pipeline or notification workflow. |
| Bilingual UI and localization | Implemented with tests | Vietnamese default, English/Vietnamese switching, localStorage persistence, Intl date/number/time formatting, and synchronized translation dictionaries. Remaining coverage: a full hardcoded-text audit of every route and server-preference synchronization. |
| API error and notification foundation | Implemented with tests | Stable JSON envelope, localized backend messages, request IDs, centralized frontend API error mapping, deduplicated toasts, and confirmation dialogs. |
| Session restoration | Implemented with tests | Refresh cookie restores the access session after reload; network failures do not immediately clear authentication, while expired/revoked refresh sessions clear the UI. |
| Login identity normalization | Implemented with tests | Login username/email is trimmed and lowercased at frontend and backend; uppercase or surrounding whitespace no longer prevents valid credentials. |
| Dashboard RBAC and encoding | Implemented with tests | Guardian/Student role mismatch is rejected; unlinked Guardians receive an unverified/empty dashboard instead of a 403; JSON is UTF-8 and mojibake placeholders are removed. |
| Modern UX/UI redesign | Implemented | Design tokens, accessible controls, collapsible/mobile sidebar, account menu, bilingual header, loading skeletons, responsive dashboard cards, improved forms/modals/toasts and reduced-motion support. |
| Student task/session vertical slice | Implemented with tests | Student can view scoped task detail and transition existing TODO/IN_PROGRESS states to IN_PROGRESS/COMPLETED; active study session is isolated and recoverable. Assignment/submission schema remains partial. |
| Student notes and notifications | Partial | Student note create/detail/edit/delete routes exist where schema supports them; AI analysis is provider-backed. Notification read/read-all routes and UI are implemented. File attachments, preference APIs and full submission history remain blocked. |
| Student AI note workspace | Implemented with tests | Student can open a note and request provider-backed AI analysis through the existing backend endpoint; loading/error states and actual persisted/provider results are represented. |
| Task completion notification | Implemented with tests | Completing an owned Student task creates a Guardian notification in the same database transaction when the notifications table is available. |
| Windows Agent core | Implemented with isolated tests | Agent has visible-process mode, local SQLite queue, platform heartbeat, sync retry, Guardian pairing API and device-scoped batch ingestion. Pairing token uses JWT signed server secret. No keylogging, app/window collectors, screenshots or presence collectors are implemented. |
| Smart timetable import | Implemented with isolated tests | Guardian can parse natural Vietnamese/English text, preview rows, detect existing overlaps and import schedules by transaction. CSV, XLSX, TXT, PDF and DOCX file parsing are API-supported where parser dependencies are available; image OCR is not configured. |
| Document upload and library | Implemented with isolated tests | Authenticated users can upload supported documents to local server storage, validate size/type and extract TXT/CSV/PDF/DOCX/XLSX text. PDF/DOCX/XLSX require their parser dependency. Image OCR and object-storage download remain blocked. |
| Guardian-created Student accounts | Implemented with tests | Guardian can create a Student account and an active Guardian–Student link using existing `users` and `guardian_student_links` tables. Student and Guardian login use the existing auth/session flow. |
| Automated tests | Partial | Isolated SQLite authorization/error/dashboard suite and frontend Vitest suites pass. E2E, full endpoint, and Agent tests remain incomplete. |

## Implemented API surface

- Health: `GET /health`.
- Auth: `POST /api/v1/auth/register` (Guardian only), `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `POST /api/v1/auth/logout-all`, `GET /api/v1/auth/me`, `GET /api/v1/relationships`.
- Scoped collections: `GET /api/v1/{subjects|topics|schedules|assignments|notes|sessions|materials|quizzes|devices|policies|website-policies|monitoring-events|analytics}`.
- Subjects: `POST /api/v1/subjects`, `GET/PATCH/DELETE /api/v1/subjects/{id}` (DELETE archives via `is_active=0`).
- Topics: `POST /api/v1/topics`, `GET/PATCH /api/v1/topics/{id}`. No delete/archive route until schema supports safe archival.
- Schedules: `POST /api/v1/schedules`, `GET/PATCH/DELETE /api/v1/schedules/{id}` (DELETE archives).
- Assignments: `POST /api/v1/assignments`; current task state/submission/review workflow is not implemented.
- Notes and sessions: `POST /api/v1/notes`, `POST /api/v1/study-sessions/start`, `POST /api/v1/study-sessions/{id}/finish`.
- Dashboard/monitoring: `GET /api/v1/dashboard/{role}`, `GET /api/v1/monitoring/status`.
- Quiz: `GET /api/v1/quizzes/{id}`, `POST /api/v1/quizzes/{id}/attempts`, `POST /api/v1/quiz-attempts/{id}/submit`.
- AI: `POST /api/v1/ai/analyze-note/{id}`.

See `API.md` and OpenAPI for live request schemas. Several generic collection responses still lack explicit response models and pagination; this is not a stable public API contract yet.

## Database and safety

- TiDB is authoritative; the mapping documents 38 tables / 364 columns. The running backend's `/health` check used read-only `SELECT 1` and runtime reflection (38 tables); no application rows were queried or written.
- All automated backend tests use a temporary SQLite database and inject its reflected metadata.
- No production data writes, DDL, migrations, or destructive SQL were executed.
- Schema mismatches and proposed auth schema needs are documented in `DATABASE_GAPS.md` and `AUTH_SCHEMA_PROPOSAL.md`. Approval is required before any schema modification.

## Security and reliability

- Refresh tokens are HttpOnly cookies; access tokens are held in memory by the frontend. Existing local-storage access token is removed on startup.
- Remaining material risks: process-local rate limit is not shared between workers; app still has legacy startup event and monolithic route module; no full authorization matrix; Agent enrollment/secrets are unfinished; file uploads do not exist; production deployment configuration is unverified. Registration is Guardian-only and creates real accounts in the configured database.
- Do not claim monitoring, task completion, or AI recommendations as verified without their actual data workflow.

## Verification

- `python -m compileall -q backend/app backend/tests agent/app`: passed in the preceding implementation pass.
- `pytest backend/tests -q` from repository root: 33 passed, 2 FastAPI lifecycle deprecation warnings.
- `npm test` in `frontend`: 12 passed.
- `npm run build` in `frontend`: passed.
- No live TiDB/API smoke test was run. See `TEST_REPORT.md`.

## Next phase

Continue with a schema-aware task workflow analysis, then implement only operations represented unambiguously in existing columns. Student task status semantics currently differ between SRS and database (`TODO` vs `ASSIGNED` etc.); record and resolve this gap before transitioning task states. Follow `NEXT_STEPS.md`.
