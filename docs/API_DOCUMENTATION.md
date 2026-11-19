# API documentation

Interactive documentation is available at `/api/docs`.

## Authentication
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/students`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## Student and Guardian core routes
- `GET /api/v1/dashboard/{role}`
- `GET/PATCH/DELETE /api/v1/notes/{note_id}`
- `POST /api/v1/notes`
- `POST /api/v1/ai/analyze-note/{note_id}`
- `GET /api/v1/assignments/{task_id}`
- `PATCH /api/v1/assignments/{task_id}/status`
- `POST /api/v1/study-sessions/start`
- `GET /api/v1/study-sessions/active`
- `POST /api/v1/study-sessions/{sid}/finish`
- `PATCH /api/v1/notifications/{notification_id}/read`
- `POST /api/v1/notifications/read-all`

All protected routes require a bearer access token unless explicitly described as public.
Every handled error uses the stable envelope in `API_ERROR_CONTRACT.md` and includes `X-Request-ID`.
