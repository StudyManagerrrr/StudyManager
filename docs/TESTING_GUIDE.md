# Testing guide

## Backend
Run from the repository root:

```powershell
python -m pytest backend/tests -q
python -m compileall -q backend/app backend/tests agent/app
```

Backend tests use temporary SQLite and reflected test metadata. They do not use TiDB credentials or write production data.

## Frontend
Run from `frontend/`:

```powershell
npm test
npm run build
```

## Manual smoke checks
- `/health` must return HTTP 200.
- `/api/v1/auth/me` must require a valid bearer token.
- Guardian can create a Student only in a logged-in Guardian session.
- Student can update only owned tasks and active sessions.
- Guardian must not read an unlinked Student.

## Live process
Frontend: `http://127.0.0.1:5173`
Backend: `http://127.0.0.1:8765`
