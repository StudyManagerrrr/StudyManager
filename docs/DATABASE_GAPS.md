# Database gaps and implementation notes

Verified against live TiDB metadata on 2026-11-20. The schema provides 38 tables and 364 columns for accounts/relationships, schedules, assignments, notes, AI analysis records, quizzes/answers, devices, monitoring, presence, policy rules, analytics reports, notifications, review cards, achievements, and audit history. Exact columns, indexes, and foreign keys are in `DATABASE_MAPPING.md`.

Schema capabilities needing application workflows or new-schema review (no DDL applied):

- `devices` has no pairing-code or credential hash fields; `device_settings` can hold JSON but should not be repurposed for long-lived secrets without a security review. Pairing code issuance, token rotation/revocation, device auth, and event ingestion remain unimplemented.
- There is no obvious AI job table; `ai_analyses` is note-linked and can store outcomes but not robust job lifecycle/provider prompt version/approval state.
- The `devices` table has no long-lived credential/token hash or pairing-state fields. The first implementation uses a signed JWT credential validated against active device ownership; revocation requires `is_active=0`. A migration may later be needed for rotation families and server-side credential revocation.
- `monitoring_events` has no event ID/idempotency column. Batch events carry `event_id` inside JSON metadata; duplicate idempotency is not durably guaranteed until a dedicated unique key/index or event-ID column is approved.
- Document uploads use local server storage and `learning_materials.file_path`; no object-storage abstraction, signed URL, retention policy or malware scanning is implemented. Production deployments need durable shared storage and approval for that policy.
- Timetable import does not add recurrence/weekly parity columns or import-batch tables. Natural text and file preview create standard `study_schedules` rows only after Guardian confirmation. Existing recurring schedules and import history require schema review.
- Storage tables contain paths and metadata but do not define object storage, signed access, retention workflow, or upload boundaries.
- Quiz tables support questions, attempts, and answers. The current API implements basic read/start/submit and objective scoring, but authorization gaps remain; Guardian create/review/publish, quiz versioning, multiple-select, explanation timing, and complete retry/completion criteria are not implemented.
- Existing reports and analytics tables are present; generation and verified-duration reconciliation remain incomplete.
- `device_settings` is a key/value table (5 columns), not a wide settings model. Use its actual shape if this feature is implemented.

No schema additions are required for safe read-only discovery or the current implemented routes. Any needed additions require an isolated development schema and a separately reviewed migration plan.

## SRS task and topic lifecycle gaps (reviewed 2026-11-20)

- SRS FR-06 describes statuses `DRAFT`, `ASSIGNED`, `IN_PROGRESS`, `SUBMITTED`, `NEEDS_REVISION`, `PASSED`, `OVERDUE`, and `CANCELLED`, with objectives, materials, completion criteria, required note/quiz, minimum valid duration, passing score, and retry rules. Mapped `learning_tasks` contains only title/description, subject/schedule, priority, status (default `TODO`), due time, completed time and estimated minutes. It has no topic/objective/completion-criteria/submission/revision/retry fields. Do not infer a transition from `TODO` to an SRS state or mark a task passed from elapsed time.
- `learning_notes` has no task foreign key in the mapping, so a note cannot be reliably attached to a task/submission through the existing task schema. Existing `quiz_attempts` can link quiz/student, but there is no task-level completion evaluation record.
- `topics` has no `is_active`/archive field. The API intentionally does not expose topic deletion; adding an archive column or cascading delete requires a proposal and approval.
- Current basic assignment creation/list remains possible using mapped columns, but SRS task lifecycle implementation is blocked on an explicit mapping contract and likely schema additions. `AUTH_SCHEMA_PROPOSAL.md` remains unrelated proposal-only material; no schema action was taken.

## Authentication-specific schema review

The existing `user_sessions` mapping provides `id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`, creation time and request metadata. The implementation now uses it for hashed refresh-token sessions, rotation, revocation and reuse detection without schema changes. It does **not** include a token-purpose/family column; the current implementation differentiates refresh purpose in the signed token and stores one refresh token per session row.

The mapping does not list invitation/reset token purpose, intended email, consumed timestamp, delivery status, Guardian PIN hash/failure lockout fields, or email verification state. `system_settings` is a global key/value table and is not currently approved as a per-user security credential store. Guardian self-registration now uses the existing `users` columns; it creates only GUARDIAN accounts and does not create a Student relationship. Student invitation/acceptance, password reset and Guardian PIN remain unimplemented pending a reviewed design. See `AUTH_SCHEMA_PROPOSAL.md`; it remains proposal-only and no DDL was run.
