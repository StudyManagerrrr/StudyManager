# API reference (current implementation)

Base path: `/api/v1`. Interactive OpenAPI: `/api/docs` when enabled. TiDB schema is reflected at runtime; see `DATABASE_MAPPING.md`. Authentication and scope limitations are tracked in `IMPLEMENTATION_STATUS.md`.

## Authentication

- `POST /auth/login` — JSON `{username,password}`; returns short-lived `access_token` and sets refresh cookie.
- `POST /auth/register` — JSON `{username,email,full_name,password}`; creates a Guardian account only. Password length is 12–128 characters. Returns 201; user signs in afterward. Student account invitations are not available yet.
- `POST /auth/refresh` — rotates refresh cookie and returns a new access token.
- `POST /auth/logout` — revokes current session and clears cookie.
- `POST /auth/logout-all` — revokes active sessions for current user.
- `GET /auth/me`, `GET /relationships` — bearer access token required.
- Guardian: `POST /auth/students` — create a Student account and activate a Guardian–Student relationship.

## Learning resources

- `GET /{resource}` for the fixed resource allowlist. Results are scoped to the current Student or linked Students. Collection pagination and stable response envelopes are not yet provided.
- Guardian: `POST /subjects`, `/schedules`, `/assignments`; `GET/PATCH/DELETE /subjects/{id}` and `/schedules/{id}`; `POST /topics`; `GET/PATCH /topics/{id}`.
- Student: `POST /notes`; `POST /study-sessions/start`; `POST /study-sessions/{id}/finish`.
- Dashboard: `GET /dashboard/{role}`. Monitoring status: `GET /monitoring/status`.
- Quiz: `GET /quizzes/{id}`, `POST /quizzes/{id}/attempts`, `POST /quiz-attempts/{attempt_id}/submit`.
- AI: `POST /ai/analyze-note/{note_id}`.

Mutation endpoints generally accept `{ "data": { ... } }`; note/session/auth endpoints use dedicated request bodies. Consult generated OpenAPI for exact current fields and validation. Response models are not yet consistently declared and the API contract is still evolving.

## Known gaps

- Assignment task lifecycle and student submission/review routes are missing.
- SRS task statuses/completion criteria do not map to current `learning_tasks` columns; see `DATABASE_GAPS.md`.
- Topic deletion/archive is omitted because current schema has no archival flag.
- Agent client targets `POST /agent/events/batch`, which is not implemented; synchronization is unavailable.
- AI requires configured `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL`; provider errors are returned and no fabricated result is used.
- File upload, recurring schedule expansion, reminders and stable error/pagination contracts are not implemented.
