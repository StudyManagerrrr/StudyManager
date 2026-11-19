# Test report

Date: 2026-11-20

## Results

- Backend syntax check: `python -m compileall -q backend/app backend/tests agent/app` — passed.
- Backend tests: `pytest backend/tests -q` from repository root — 33 passed, 2 deprecation warnings from FastAPI `@app.on_event` startup registration. Coverage includes natural timetable preview/import, Agent pairing/batch heartbeat, Guardian-created Student accounts, auth, authorization, task lifecycle with notifications, active-session isolation, unified errors and empty/role-mismatch dashboards.
- Frontend tests: `npm test` in `frontend` — 12 tests passed across i18n, notifications, and API error handling.
- Frontend production build: `npm run build` in `frontend` — passed.
- UX verification: live login page reviewed at `http://127.0.0.1:5173` at desktop viewport; sidebar, language switcher and form rendered without overflow.

## Isolation and limitations

Backend tests use a temporary SQLite file and inject test SQLAlchemy engine/metadata. They do not use TiDB credentials, connect to TiDB, or write production data. Frontend tests run in jsdom and do not call the live API. There is no browser E2E or Agent test. Runtime verification used read-only `/health` through the active tunnel; no registration request was sent to TiDB.

## Follow-up

Add endpoint tests for subject/topic/schedule create/update/archive, assignment submission/revision once schema is approved, quiz edge scoring and AI provider failures. Replace deprecated startup hook with lifespan handling and test startup/reflection failure behavior.
