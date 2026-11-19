# Architecture

- `frontend/`: React/TypeScript role aware portal. All persistence goes through FastAPI.
- `backend/`: FastAPI, authorization boundary, SQLAlchemy Core metadata reflection, AI provider adapter.
- `agent/`: separate visible Windows process, local SQLite event queue and outbound client boundary. It currently reports diagnostics only; system monitoring requires explicit collectors and approved device policy.
- TiDB: current 38-table database; schema is reflected, no migrations on startup.
- Local object storage directory reserved; upload/download authorization not implemented yet.
