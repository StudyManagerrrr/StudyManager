# Deployment guide

## Backend
The FastAPI process requires:
- `DATABASE_URL`
- `JWT_SECRET`
- Optional AI provider settings
- `FRONTEND_ORIGIN`
- `APP_ENV`

Production requires `JWT_SECRET` with at least 32 characters and must not contain placeholder markers.

## Frontend
Set `VITE_API_BASE_URL` only if the frontend and API are served on separate origins. Vite development proxy is for local development.

## Database
The application reflects the TiDB schema at startup and does not issue DDL. Do not run reset, DROP, TRUNCATE or autogenerate migration commands against production.

## Local verification
- Run frontend and backend test suites.
- Verify `/health`.
- Verify refresh-cookie policy for the deployed origin.
- Replace process-local rate limiting before multi-worker deployment.
