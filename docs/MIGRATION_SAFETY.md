# Database safety

- Existing TiDB Cloud is the source of truth.
- Startup only reflects metadata from `information_schema`; it never creates or alters schema.
- Do not run Alembic autogeneration, `create_all`, seed scripts, destructive tests, or migrations against the configured TiDB.
- A schema change requires a separately provisioned development database, reviewed forward migration, verified backup, and explicit operational change window.
- The live mapping file is produced from metadata only; user records are not included.
- Current app writes occur only through user-triggered authenticated API workflows.
