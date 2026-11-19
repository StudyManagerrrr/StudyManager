# AI Learning Guardian — Web Platform
## Software Requirements Specification & Codex Implementation Blueprint

**Document version:** 2.0  
**Date:** 20/11/2026  
**Migration source:** AI Learning Guardian SRS v1.0 (19/11/2026)  
**Target:** Full-stack Web Application + Windows Monitoring Agent  
**Workspace target:** `D:\Project_Study_Management`

---

# 0. Instructions for Codex

This document is the product specification and implementation contract for rebuilding the original AI Learning Guardian as a Web platform.

You are expected to **implement the product**, not merely produce an audit, architecture proposal, task list, mockup, or Markdown documentation.

The original SRS describes a Windows desktop application with two roles:
- **Guardian:** the parent/manager who configures schedules, learning requirements, policies, materials, and reviews the student's progress.
- **Student:** the learner who follows schedules, completes learning tasks, submits notes, takes quizzes, and reviews their own progress.

Preserve this product identity and its business workflows. Do not replace it with a generic personal Study Planner or a generic Todo application.

The target product is:
1. A responsive Web application with Guardian and Student portals.
2. A FastAPI backend that owns business rules, authentication, authorization, data access, AI orchestration, and realtime events.
3. A separate Windows Monitoring Agent for operating-system capabilities that browsers cannot provide.
4. The existing TiDB Cloud database, whose actual schema must be inspected before ORM mapping or migrations.

## Mandatory execution rules

- Work directly in `D:\Project_Study_Management`.
- Read this document completely before implementation.
- Inspect existing workspace files and configuration.
- The old desktop source code is not present in the workspace. Do not block waiting for it. Build the new Web codebase.
- Existing TiDB Cloud contains 38 tables according to the current project context. Verify the actual live schema; never assume table names or columns from this document.
- Do not DROP, TRUNCATE, reset, recreate, or destructively migrate the existing database.
- Do not run writes against production data merely to test connectivity.
- Do not invent successful integrations. If an API key, Windows Agent, certificate, or provider is unavailable, implement the integration boundary and report the exact missing configuration.
- Do not use fake monitoring events, fake AI responses, or fabricated analytics in production flows.
- Do not stop after Phase 1 or after writing documentation. Continue implementing all phases that can be completed safely.
- Do not ask for approval after every file. Make reasonable engineering decisions and proceed.
- Ask only when a genuinely missing secret, access permission, or irreversible decision blocks progress.
- Run tests and fix errors before marking a feature complete.
- Keep `IMPLEMENTATION_STATUS.md` current, but never treat status documents as a substitute for working code.

---

# 1. Product Vision

## 1.1 Product definition

**AI Learning Guardian** is an AI-assisted learning management and transparent computer-use supervision platform.

It connects a Guardian and a Student in one learning environment. Guardian assigns learning objectives, schedules, reference materials, and policies. Student follows the plan, studies, submits learning notes or documents, completes AI-generated assessments, and reviews progress. The system records verifiable study activity and uses AI to identify knowledge gaps and recommend the next learning steps.

The main product outcome is not simply to keep a learner sitting at a computer. It is to help the learner understand, retain, and demonstrate knowledge while providing the Guardian with clear, explainable progress information.

## 1.2 Product principles

1. **Learning first:** knowledge acquisition and demonstrated understanding are the primary outcomes.
2. **Transparent monitoring:** the Student can always see whether monitoring is active, what categories of data are collected, and why.
3. **Guardian-configurable:** Guardian controls learning assignments and approved supervision policies.
4. **AI-assisted, human-approved:** AI can analyze and recommend; consequential plans, policy changes, and assignments require authorized confirmation.
5. **Web-first:** everyday management and learning workflows happen in a browser.
6. **Agent-assisted:** operating-system monitoring and enforcement are delegated to an explicitly installed Windows Agent.
7. **Reliable records:** study duration, quiz results, and progress must be derived from traceable events, not fabricated client-side values.
8. **Privacy by design:** collect the minimum data needed, provide retention controls, and never implement keylogging or covert surveillance.
9. **Resilient synchronization:** the Windows Agent can queue permitted events while offline and synchronize them safely when connectivity returns.
10. **Extensible tenancy:** the first deployment may serve one Guardian and one Student, but data ownership and authorization should not prevent future multiple families/devices.

## 1.3 Initial operating scope

The initial release should support:
- One Guardian account linked to one Student account, while avoiding hard-coded assumptions that prevent multiple linked users later.
- One or more registered Windows devices per Student, even if the first rollout uses one PC.
- Guardian and Student Web portals.
- Windows 10/11 64-bit Monitoring Agent.
- TiDB Cloud as the existing shared database.
- AI provider integration through a server-side adapter.
- Local Agent event buffering during temporary network loss.

## 1.4 Out of scope for the first release

- Native iOS or Android applications.
- Kernel-level Windows drivers.
- Keylogging, password capture, clipboard surveillance, or covert recording.
- Emotion recognition, face identification, gaze tracking, or claims that webcam presence proves attention.
- Microservices architecture.
- Public marketplace or multi-school administration.
- Automatic AI decisions that punish or lock out a learner without a Guardian-approved rule and a clear appeal/override path.

---

# 2. Target Architecture

## 2.1 High-level architecture

```text
                         INTERNET / HTTPS
                                |
                +---------------+----------------+
                |                                |
        Guardian Web Portal              Student Web Portal
        React + TypeScript               React + TypeScript
                |                                |
                +---------------+----------------+
                                |
                       FastAPI Application
                         /api/v1 + WebSocket
                                |
        +-----------------------+------------------------+
        |              |              |                 |
   Auth & Access   Learning Core   AI Orchestrator   Monitoring API
        |              |              |                 |
        +--------------+--------------+-----------------+
                                |
                         SQLAlchemy 2.x
                                |
                         TiDB Cloud (TLS)
                                |
                 Object Storage / File Storage
                                ^
                                |
                      HTTPS outbound + WSS
                                |
                    Windows Monitoring Agent
                                |
         +----------------------+----------------------+
         |             |              |               |
   App/Window      Idle State     Webcam Presence   Policy Executor
   Tracking        Detection      (opt-in)          (Guardian policy)
```

## 2.2 Component responsibilities

### Web frontend
- Render Guardian and Student experiences.
- Handle forms, navigation, filters, tables, calendar, charts, and user interactions.
- Call the backend through a centralized typed API client.
- Display realtime monitoring and study-session state.
- Never connect directly to TiDB.
- Never contain AI provider secrets.
- Never claim to monitor desktop applications or enforce Windows policies by itself.

### FastAPI backend
- Authenticate users and enforce authorization.
- Enforce Guardian/Student relationship boundaries.
- Own all learning and assessment business rules.
- Persist schedules, tasks, notes, materials metadata, quiz results, logs, and analytics source records.
- Orchestrate AI provider calls and validate AI output.
- Register and authenticate Windows Agents.
- Receive, validate, deduplicate, and persist Agent events.
- Publish authorized realtime updates.
- Calculate verified study time on the server.

### Windows Monitoring Agent
- Run as a visible, user-installed Windows application/process.
- Pair with a user account and registered device.
- Report app/window metadata according to Guardian-approved policy.
- Detect idle/active state.
- Optionally detect human presence through webcam when explicitly enabled.
- Optionally capture screenshots only under explicit, visible, configurable consent and retention rules.
- Execute supported application/website policies only after a clear policy has been delivered and acknowledged.
- Queue permitted events locally while offline.
- Retry synchronization without duplicating records.
- Show connection, monitoring, camera, and policy status.
- Provide a clear pause/stop control according to the configured authorization model.

### TiDB Cloud
- Remains the system of record.
- Existing 38 tables must be inspected and mapped.
- No destructive schema changes.
- Existing records must remain intact.

### Object storage
- Store uploaded PDFs, images, documents, and optional screenshots outside relational rows where appropriate.
- Database stores metadata, owner, object key/path, MIME type, size, timestamps, retention state, and access scope.
- Use signed URLs or authenticated streaming endpoints for private files.

## 2.3 Important Web-vs-Windows boundary

A normal browser cannot reliably:
- Read the foreground Windows application or process list.
- Inspect arbitrary desktop window titles.
- Detect system-wide idle state.
- Enforce Windows application restrictions.
- Enforce device-wide website filtering.
- Run webcam presence checks continuously when the Web page is closed.

These capabilities must be implemented by the Windows Agent. The Web app provides configuration, status, history, and reports.

Do not attempt to bypass browser sandbox restrictions. Do not pretend that a browser-only implementation provides system-level monitoring.

---

# 3. Technology Stack

Use stable, mutually compatible versions. Pin dependencies after verifying compatibility.

## 3.1 Frontend

- React
- TypeScript with strict mode
- Vite
- Tailwind CSS
- shadcn/ui and Radix UI
- React Router
- TanStack Query
- Zustand only for genuinely shared client state
- React Hook Form
- Zod
- Recharts
- FullCalendar or a suitable calendar library
- dnd-kit for accessible drag/drop where required
- date-fns
- Lucide React
- i18next or an equivalent localization solution

## 3.2 Backend

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- PyMySQL or a verified TiDB-compatible MySQL driver
- Alembic, only after schema inspection and safe migration planning
- Argon2id password hashing
- JWT access tokens and rotating refresh tokens, or secure server sessions where architecture supports them
- HTTPX for external APIs
- WebSocket support
- Pytest and HTTPX test client

## 3.3 Windows Agent

- Python 3.11+
- Windows APIs through well-maintained Python bindings
- OpenCV for optional webcam processing
- MediaPipe or another maintained person-presence model only if needed and validated
- Local SQLite queue for offline event buffering
- HTTPS/WSS outbound connection to backend
- Windows DPAPI for locally stored device secrets where feasible
- Pytest with mocked Windows integrations

Do not build a kernel driver. Do not run hidden processes. Do not install a Windows service with invasive privileges unless a future, separately approved requirement justifies it.

## 3.4 Infrastructure

- TiDB Cloud
- TLS certificate and hostname verification
- Object storage adapter (provider can be selected through configuration)
- Docker Compose for local backend/frontend development where useful
- `.env` for local secrets, never committed
- `.env.example` with placeholders only
- Structured application logging

---

# 4. Roles, Permissions, and Account Relationships

## 4.1 Guardian

Guardian can:
- Manage the linked Student profile.
- Create and manage subjects, topics, schedules, and learning assignments.
- Upload reference materials.
- Define learning requirements and assessment rules.
- Generate AI study plans and quizzes.
- Review Student submissions and quiz attempts.
- View study sessions and authorized monitoring summaries.
- Configure application/website policies.
- Configure monitoring consent, camera options, screenshot settings, and retention.
- Approve temporary permissions and emergency overrides.
- View analytics and reports.
- Manage device pairing and revoke a device.
- Review audit history.
- Configure notifications.

Guardian cannot:
- Read unrelated users' data.
- Access raw webcam feeds or screenshots unless the configured feature explicitly permits it and the access is logged.
- Change historical quiz answers or study records without an auditable correction process.

## 4.2 Student

Student can:
- View their own dashboard and schedule.
- View assigned tasks and learning objectives.
- Start and finish study sessions.
- Submit learning notes and permitted attachments.
- View AI feedback.
- Take quizzes and review explanations after submission.
- Use flashcards and review schedules.
- View their own learning progress.
- Request temporary application access.
- See Agent connection and monitoring status.
- See the monitoring categories and policies currently active.
- Pause/stop optional camera monitoring where policy permits.
- View relevant data collection and retention notices.

Student cannot:
- Modify Guardian-owned policies.
- Change required pass thresholds.
- Change or fabricate quiz scores.
- Delete or edit immutable monitoring events.
- Access another Student's records.

## 4.3 Authorization rules

- Enforce authorization in backend services and database queries, not only by hiding frontend controls.
- Resolve current user identity from the authenticated token/session.
- Never trust `user_id`, `student_id`, or `guardian_id` supplied by the browser without verifying the relationship.
- Every family-scoped record must be checked against the authenticated user's relationship.
- Guardian-only mutations require Guardian role and a valid relationship.
- Student reads/writes must be scoped to their own records.
- Device credentials are separate from user access tokens.
- Sensitive Guardian actions require re-authentication or Guardian PIN confirmation as configured.

## 4.4 Initial pairing workflow

1. Guardian creates or invites a Student account.
2. Student verifies the invitation or receives a one-time pairing code.
3. Guardian installs the Windows Agent on the target PC.
4. Agent displays a pairing code.
5. Guardian signs into the Web portal and approves the device.
6. Backend issues a device-specific credential.
7. Agent stores the secret securely and connects outbound over HTTPS/WSS.
8. Guardian and Student can see device status.
9. Guardian can revoke the device; revoked credentials must stop synchronizing.

Pairing codes must expire, be single-use, and be rate-limited.

---

# 5. Information Architecture and Web UI

## 5.1 Shared application shell

- Responsive sidebar.
- Top header with breadcrumbs.
- Global search.
- Notifications.
- Language selector (Vietnamese/English).
- Light/Dark/System theme.
- User profile menu.
- Context-aware quick actions.
- Toast messages.
- Loading skeletons.
- Empty states.
- Error and retry states.
- Confirmation dialogs for destructive actions.

Use a professional, calm, education-focused SaaS design. Avoid making the Student portal feel like a surveillance console.

## 5.2 Guardian navigation

1. Overview
2. Student Monitoring
3. Study Schedule
4. Learning Assignments
5. Subjects & Topics
6. Learning Materials
7. AI Learning Analysis
8. Quiz Management
9. Application & Website Policies
10. Devices
11. Learning Analytics
12. Notifications
13. Audit History
14. Settings

## 5.3 Student navigation

1. My Dashboard
2. Today's Schedule
3. My Tasks
4. Learning Notes
5. Materials
6. AI Learning Assistant
7. Review & Quizzes
8. Flashcards
9. My Progress
10. Monitoring Status
11. Notifications
12. Settings

## 5.4 Guardian Dashboard

### Summary cards
- Student status: online/offline/unknown.
- Agent connection status.
- Current study session.
- Verified study time today.
- Scheduled study time today.
- Tasks completed / assigned.
- Latest quiz score.
- Upcoming deadlines.

### Main panels
- Today's timeline.
- Current monitoring state.
- Recent activity summary.
- Learning completion trend.
- Knowledge strengths and gaps.
- Upcoming schedule.
- Alerts requiring Guardian attention.
- AI recommendations with evidence and confidence/limitations.

### Guardian actions
- Create assignment.
- Create schedule.
- Upload reference material.
- Generate study plan.
- Generate quiz.
- Review Student submission.
- Open device/policy settings.

## 5.5 Student Dashboard

### Welcome section
- Greeting and date.
- Today's learning objective.
- Start/continue study button.
- Progress toward daily target.

### Main panels
- Today's schedule.
- Assigned tasks.
- Next deadline.
- Current study session.
- Verified study time.
- Learning streak (if enabled).
- Recent quiz results.
- Topics requiring review.
- AI study recommendations.

The Student dashboard must emphasize clear next actions, not monitoring pressure.

## 5.6 Monitoring page

Display:
- Device name and operating system.
- Agent version.
- Last heartbeat.
- Online/offline/unknown.
- Monitoring enabled/paused.
- Active policy version.
- Foreground application category/name when collection is enabled.
- Idle/present/away/unknown state.
- Current session.
- Recent events timeline.
- Camera status and explicit consent state.
- Screenshot status and retention policy, if enabled.

Do not display a green “focused” status solely because a person is detected by webcam. Presence is not proof of attention.

## 5.7 Responsive behavior

- Desktop: full sidebar and data tables.
- Tablet: collapsible navigation and responsive grids.
- Mobile: drawer navigation, stacked cards, compact calendar/agenda.
- Forms must remain usable on touch screens.
- Charts must resize without clipping.
- Tables should transform into readable cards or horizontal-scroll layouts where appropriate.

---

# 6. Functional Requirements

## FR-01 Authentication and User Management

### Login
- Email/username and password.
- Show/hide password.
- Remember session where safe.
- Validation and rate limiting.
- Generic authentication error messages.
- Redirect by role after login.

### Registration/invitation
- Guardian account creation if enabled.
- Student invitation and acceptance.
- Email verification if email delivery is configured.
- Password policy and secure reset.

### Sessions
- Access token short lifetime.
- Refresh token rotation and revocation.
- Logout current session.
- Logout all sessions.
- Device/session list where supported.
- Detect refresh token reuse.

### Guardian PIN
- Hashed PIN, never plaintext.
- Rate limiting and lockout delay.
- Re-authentication for sensitive policy changes.
- Audit successful and failed sensitive actions.

## FR-02 Computer Monitoring

The Agent may collect the following according to an explicit policy:
- Foreground application identifier/name.
- Window title only if enabled and necessary.
- Active/idle transitions.
- Agent heartbeat.
- Study session state.
- Optional presence status.
- Optional screenshots under explicit configuration.

Requirements:
- No keylogger.
- No password capture.
- No arbitrary keystroke collection.
- No hidden webcam operation.
- No continuous raw video upload.
- No inference of emotion, attention, or identity from camera.
- Agent must expose a visible monitoring indicator.
- Student must be able to see current monitoring state.
- Unknown device/camera state must not be counted as verified presence.
- Agent events must have timestamps, device identity, event ID, and policy version.

## FR-03 Application and Website Policies

Guardian can configure:
- Allowlist.
- Blocklist.
- Application category.
- Website domain allow/block rules.
- Time windows.
- Day-of-week schedules.
- Temporary permission duration.
- Emergency override.
- Policy enable/disable.
- Policy history and audit trail.

Policy execution:
- The backend stores desired policy.
- Agent receives versioned policy.
- Agent validates and acknowledges applied version.
- UI distinguishes “configured”, “sent”, “acknowledged”, and “enforced” states.
- If Agent is offline, show that the new policy is pending.
- Do not claim a policy is enforced until the Agent confirms it.
- Do not use fragile repeated process-killing as the only enforcement mechanism.
- Use supported Windows APIs/firewall/DNS mechanisms only after validating scope and permissions.
- Provide safe recovery and emergency override.

## FR-04 Webcam Presence Detection

States:
- PRESENT
- AWAY
- IDLE
- UNKNOWN
- DISABLED

Default proposed behavior:
- Check presence every 3–5 seconds while an authorized study session is active.
- 30 seconds without presence may mark AWAY.
- 2 minutes away may create an away event.
- Camera unavailable or permission denied becomes UNKNOWN, not PRESENT.
- Webcam monitoring is opt-in and visible.
- Allow manual verification fallback when camera is unavailable.
- Process frames locally; do not upload raw video.
- Store only necessary state transitions and durations by default.

Presence does not prove learning or attention. It is one signal used with activity and session data.

## FR-05 Study Schedule Management

Schedule types:
- SCHOOL
- EXTRA
- SELF_STUDY
- REVIEW
- EXAM

Schedule fields:
- Title.
- Subject.
- Topic.
- Type.
- Start/end datetime.
- Timezone.
- Location.
- Description.
- Learning objective.
- Recurrence rule.
- Reminder settings.
- Attached materials.
- Status.

Features:
- Day/week/month/agenda views.
- Recurring weekly schedule.
- Conflict detection.
- Reminder before start.
- Link schedule to tasks and materials.
- Create follow-up task from a schedule.
- Sync schedule to Student portal.
- Edit one occurrence or entire recurring series.
- Handle timezone and daylight-saving correctly.

## FR-06 Learning Assignments and Tasks

Guardian creates tasks with:
- Title and instructions.
- Subject/topic.
- Related schedule.
- Learning objectives.
- Required materials.
- Estimated duration.
- Due date.
- Priority.
- Completion criteria.
- Required note/submission.
- Required quiz.
- Minimum valid study duration.
- Passing score.
- Retry rules.
- Status.

Suggested statuses:
- DRAFT
- ASSIGNED
- IN_PROGRESS
- SUBMITTED
- NEEDS_REVISION
- PASSED
- OVERDUE
- CANCELLED

Student can:
- View instructions.
- Start task.
- Start a related study session.
- Submit notes/files.
- Take required quiz.
- View feedback.
- Resubmit if allowed.

A task is not automatically PASSED merely because a timer elapsed. Evaluate all configured completion criteria.

## FR-07 Learning Notes and Materials

Student submissions:
- Rich text/Markdown notes.
- PDF, DOCX, PPTX, image and text attachments where supported.
- Submission timestamp.
- Linked schedule/task/subject/topic.
- Analysis status.
- Revision history.

Guardian reference materials:
- Upload files.
- Assign to subject/topic/task.
- Set visibility.
- Set required/optional.
- Add description and tags.

File security:
- Validate extension, MIME type, and size.
- Generate safe object keys.
- Do not trust user-supplied filenames.
- Scan uploads if an available scanner is configured.
- Private files must not be publicly addressable.
- Enforce ownership/relationship checks on every download.
- Store metadata in database, binary content in object storage.

## FR-08 AI Learning and Note Analysis

AI analysis workflow:
1. Receive note text or uploaded document.
2. Extract text from supported files.
3. Run OCR for supported images/PDF pages when configured.
4. Normalize and segment content.
5. Compare against Guardian's reference materials and learning objectives.
6. Identify covered topics.
7. Identify missing topics.
8. Identify possible misconceptions.
9. Generate summary and key concepts.
10. Recommend follow-up learning.
11. Propose quiz questions.
12. Save versioned analysis result and provider/model metadata.

AI output must distinguish:
- Source/reference facts.
- Student-submitted content.
- AI inference.
- Uncertain or low-confidence extraction.

AI must not present a missing topic as definitely unknown if the submitted material simply did not mention it. Use wording such as “not demonstrated in this submission”.

Guardian can review and approve generated assignments/quizzes before publishing.

## FR-09 AI Quiz Engine

Supported question types:
- Multiple choice.
- Multiple select.
- True/False.
- Short answer.

Quiz settings:
- Difficulty: EASY, MEDIUM, HARD, MIXED.
- Question count: configurable, recommended 5–50.
- Time limit optional.
- Passing score configurable.
- Retry policy.
- Shuffle questions/answers.
- Explanation visibility timing.
- Coverage of learning objectives.

Assessment rules from original SRS:
- School learning: default 60 minutes verified study time and at least 70% quiz score, configurable by Guardian.
- Extra class: completion of all required questions/requirements; retries may be required until pass.
- Self-study: Guardian-configurable completion criteria.

Important:
- The 60-minute and 70% values are defaults, not hard-coded universal rules.
- Do not lock a student out indefinitely.
- Provide clear feedback and retry paths.
- Backend owns answer validation and scoring.
- Correct answers must not be exposed before submission.
- AI-generated quiz must be validated against schema before saving.
- Record quiz version so historical attempts remain interpretable if a quiz changes.

## FR-10 Learning Analytics

Dashboard/report metrics:
- Total scheduled time.
- Total elapsed session time.
- Verified study time.
- Away/idle time.
- Completed sessions.
- Completed/assigned tasks.
- Quiz count.
- Average score.
- Pass rate.
- Topic strengths and topics needing review.
- Weekly/monthly progress trend.
- Planned vs actual time.
- Agent uptime and monitoring data completeness.

Rules:
- Do not count overlapping intervals twice.
- Do not count UNKNOWN presence as verified presence.
- Do not infer attention from presence alone.
- Distinguish missing monitoring data from zero activity.
- Include date range and timezone in reports.
- Explain metric definitions in the UI.

## FR-11 Notifications and Reminders

Types:
- Upcoming schedule.
- Task due soon.
- Overdue task.
- Study reminder.
- Away event.
- Agent disconnected.
- Policy not acknowledged.
- AI analysis completed.
- Quiz result.
- Review reminder.
- Daily/weekly report.

Features:
- In-app notification center.
- Read/unread.
- Mark all read.
- Preferences by type.
- Browser notifications only with permission.
- Avoid duplicate notifications using idempotency keys.
- Email delivery optional and provider-configured.

## FR-12 Security and Settings

- User profile.
- Language.
- Theme.
- Timezone.
- Notification preferences.
- Guardian PIN.
- Active sessions.
- Paired devices.
- Device revocation.
- Monitoring consent/configuration.
- Data retention settings.
- Export personal data where supported.
- Delete account/data workflow with appropriate confirmation and retention/legal checks.
- Backup/restore for operational data where supported.
- Audit history for sensitive changes.

---

# 7. Business Workflows

## 7.1 School study workflow

1. Student opens Web portal and views today's schedule.
2. Student selects the school session/task.
3. Backend checks task requirements and linked Agent status.
4. Student starts study session.
5. Agent reports authorized app/activity/presence events.
6. Backend calculates elapsed and verified durations.
7. Student finishes the session.
8. Student submits lesson notes/materials.
9. AI extracts and analyzes content against Guardian references.
10. AI proposes quiz questions.
11. Guardian reviews/publishes the quiz when required.
12. Student completes quiz.
13. Backend scores attempt.
14. Backend evaluates configured completion criteria.
15. Knowledge progress and review schedule update.
16. Guardian and Student dashboards refresh.

## 7.2 Extra-class workflow

1. Guardian creates an extra-class assignment.
2. Guardian attaches reference materials and learning objectives.
3. Student views assignment.
4. Student submits what was covered in class.
5. AI compares submission with the reference.
6. AI highlights coverage and un-demonstrated objectives.
7. AI generates an assessment proposal.
8. Guardian approves or edits the quiz if approval is enabled.
9. Student completes quiz.
10. If failed, Student receives explanations and a retry path.
11. On pass and other configured criteria, task becomes PASSED.

## 7.3 Generate tomorrow's learning plan

1. Guardian enters tomorrow's subject/topics/objectives.
2. Backend retrieves authorized prior learning progress, recent quiz results, and current schedule.
3. AI creates a proposed plan with:
   - Learning objectives.
   - Prerequisite review.
   - New topics.
   - Estimated durations.
   - Practice activities.
   - Quiz/review suggestions.
4. Backend validates output.
5. Guardian reviews and edits.
6. Guardian publishes.
7. Student sees the plan in their portal and calendar.

AI suggestions must not silently overwrite existing schedules.

## 7.4 Temporary application permission

1. Student requests temporary access and provides a reason.
2. Backend creates a request.
3. Guardian receives notification.
4. Guardian approves or rejects with optional duration.
5. Backend issues a versioned temporary policy.
6. Agent receives and acknowledges the policy.
7. UI shows actual enforcement state.
8. Permission expires automatically.
9. Audit record is retained.

## 7.5 Agent offline workflow

1. Agent detects backend connectivity loss.
2. UI/Agent indicates OFFLINE or SYNC_PENDING.
3. Agent queues only permitted events locally with stable event IDs.
4. Agent continues only policy behavior allowed by its last acknowledged policy.
5. Agent does not invent server confirmation.
6. When reconnected, Agent uploads batches.
7. Backend deduplicates by event ID/device.
8. Backend acknowledges accepted/rejected events.
9. Agent marks acknowledged records synchronized.
10. UI shows last sync and any data gap.

---

# 8. Data and Database Strategy

## 8.1 Existing database is authoritative

The project context indicates that TiDB Cloud already contains 38 tables. The original SRS contains an earlier conceptual list of approximately 35 entities. These are not interchangeable facts.

Codex must inspect the live database before writing ORM models.

Inspect metadata only initially:
- `information_schema.tables`
- `information_schema.columns`
- `information_schema.key_column_usage`
- `information_schema.statistics`
- Foreign keys and indexes.
- Column types, defaults, nullability, collation, and generated columns where relevant.

Create:
- `docs/DATABASE_MAPPING.md`
- `docs/DATABASE_GAPS.md`
- `docs/MIGRATION_SAFETY.md`

For each existing table, record:
- Actual table name.
- Actual columns and types.
- Primary key.
- Foreign keys.
- Indexes.
- Related module.
- ORM mapping status.
- Compatibility issues.
- Whether it is safe to use without migration.

Do not assume the conceptual table names in this document exist.

## 8.2 Schema safety rules

Forbidden without explicit, separately reviewed approval:
- DROP TABLE.
- DROP COLUMN.
- TRUNCATE.
- Database reset.
- Recreate existing tables.
- Rename existing columns.
- Change primary keys.
- Destructive data conversion.
- Migration that loses or rewrites user data.

If schema changes are needed:
1. Explain the gap.
2. Design an additive migration.
3. Make it backward-compatible where possible.
4. Create a backup/rollback plan.
5. Test on a separate test database.
6. Do not apply destructive changes to production.
7. Report migration commands and expected impact.

## 8.3 ORM mapping

- Map existing tables accurately.
- Use explicit column names/types where necessary.
- Avoid accidental table creation on application startup.
- Never call `Base.metadata.create_all()` against the existing production database as a shortcut.
- Keep models, schemas, repositories, and services separate.
- Use transactions for multi-record workflows.
- Use UTC timestamps internally and convert for display.
- Use stable identifiers compatible with actual schema.
- Do not assume UUID storage format until verified.

## 8.4 Candidate domain entities

These are logical concepts, not instructions to create duplicate tables:
- Users and roles.
- Guardian–Student relationship.
- User sessions.
- Devices and device credentials.
- Device settings.
- Subjects and topics.
- Study schedules and recurrence.
- Learning tasks/assignments.
- Study sessions.
- Activity/application logs.
- Presence logs.
- Monitoring events.
- Application and website policies.
- Learning materials and attachments.
- Student notes/submissions.
- AI analyses.
- Quizzes and questions/options.
- Quiz attempts and answers.
- Knowledge progress.
- Flashcards and review schedules.
- Notifications.
- Daily/weekly reports.
- Audit logs.
- Achievements/points if existing and required.

Use existing schema where possible. If a concept has no compatible table, document the gap rather than silently creating a duplicate.

---

# 9. Backend Architecture

Recommended structure:

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      permissions.py
      exceptions.py
      logging.py
    database/
      connection.py
      session.py
      metadata_inspection.py
    api/
      v1/
        auth.py
        users.py
        relationships.py
        devices.py
        dashboard.py
        schedules.py
        subjects.py
        topics.py
        assignments.py
        study_sessions.py
        monitoring.py
        policies.py
        materials.py
        notes.py
        ai.py
        quizzes.py
        analytics.py
        notifications.py
        settings.py
    models/
    schemas/
    repositories/
    services/
    integrations/
      ai/
      object_storage/
      email/
    websocket/
    workers/
    tests/
  migrations/
  requirements.txt
  .env.example
```

## 9.1 Layer rules

- Routers handle HTTP, dependency injection, and response mapping.
- Schemas validate requests/responses.
- Services own business rules.
- Repositories own persistence queries.
- Integrations wrap external providers.
- Models reflect actual database schema.
- Permissions are checked in service/API boundaries.
- No direct SQL or business logic inside React components.
- Avoid circular imports and oversized modules.

## 9.2 API conventions

Base path: `/api/v1`

Use consistent response/error contracts. Example:

```json
{
  "data": {},
  "meta": {}
}
```

Error example:

```json
{
  "code": "VALIDATION_ERROR",
  "detail": "The supplied data is invalid",
  "errors": []
}
```

Use:
- Correct HTTP status codes.
- Pagination for collections.
- Filter/sort query parameters.
- Request validation.
- Consistent timezone handling.
- Idempotency for Agent event ingestion and critical submissions.
- OpenAPI documentation.

## 9.3 Proposed API groups

### Auth and accounts
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/logout-all`
- `GET /auth/me`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `POST /students/invitations`
- `POST /students/invitations/accept`
- `GET /relationships`

### Dashboard
- `GET /dashboard/guardian`
- `GET /dashboard/student`

### Devices and monitoring
- `POST /devices/pairing-codes`
- `POST /devices/pair`
- `GET /devices`
- `GET /devices/{device_id}`
- `DELETE /devices/{device_id}`
- `GET /monitoring/status`
- `GET /monitoring/events`
- `POST /agent/heartbeat`
- `POST /agent/events/batch`
- `POST /agent/policies/acknowledge`

### Learning management
- `GET/POST /subjects`
- `GET/PATCH/DELETE /subjects/{id}`
- `GET/POST /topics`
- `GET/PATCH/DELETE /topics/{id}`
- `GET/POST /schedules`
- `GET/PATCH/DELETE /schedules/{id}`
- `GET/POST /assignments`
- `GET/PATCH/DELETE /assignments/{id}`
- `POST /assignments/{id}/submit`
- `GET /assignments/{id}/submissions`

### Study sessions
- `POST /study-sessions/start`
- `POST /study-sessions/{id}/pause`
- `POST /study-sessions/{id}/resume`
- `POST /study-sessions/{id}/finish`
- `GET /study-sessions`
- `GET /study-sessions/{id}`

### Materials and notes
- `POST /materials/upload`
- `GET /materials`
- `GET /materials/{id}`
- `DELETE /materials/{id}`
- `POST /notes`
- `PATCH /notes/{id}`
- `POST /notes/{id}/attachments`
- `POST /notes/{id}/submit`

### AI
- `POST /ai/analyze-note`
- `POST /ai/generate-study-plan`
- `POST /ai/generate-quiz`
- `POST /ai/learning-insights`
- `GET /ai/jobs/{job_id}`

### Quiz
- `GET /quizzes/{id}`
- `POST /quizzes/{id}/attempts`
- `POST /quiz-attempts/{id}/submit`
- `GET /quiz-attempts/{id}/result`

### Policies
- `GET /policies`
- `POST /policies`
- `PATCH /policies/{id}`
- `POST /policies/{id}/publish`
- `POST /access-requests`
- `POST /access-requests/{id}/decision`

### Analytics and notifications
- `GET /analytics/daily`
- `GET /analytics/weekly`
- `GET /analytics/monthly`
- `GET /notifications`
- `PATCH /notifications/{id}/read`

This list is a contract direction, not permission to duplicate existing endpoints or create meaningless routes. Align endpoints with the actual schema and use cases.

## 9.4 WebSocket channels

- `/ws/v1/monitoring`
- `/ws/v1/study-sessions`
- `/ws/v1/notifications`

Requirements:
- Authenticate WebSocket connections.
- Authorize each subscription.
- Do not broadcast one Student's data to unrelated users.
- Reconnect with backoff.
- Use sequence IDs or event IDs where ordering matters.
- Fall back to HTTP polling when WebSocket is unavailable.
- Never treat a WebSocket event as persisted until backend confirms it.

---

# 10. Windows Monitoring Agent

The Agent is a companion component, not part of the browser.

Suggested structure:

```text
agent/
  app/
    main.py
    core/
      config.py
      device_identity.py
      secure_store.py
    client/
      api_client.py
      websocket_client.py
    collectors/
      foreground_app.py
      idle_state.py
      presence.py
      screenshot.py
    policy/
      policy_sync.py
      application_rules.py
      website_rules.py
    queue/
      local_store.py
      sync_worker.py
    ui/
      status_tray.py
      consent_dialog.py
    tests/
  requirements.txt
```

## 10.1 Agent requirements

- Visible startup and status.
- Device pairing.
- Device credential storage.
- Heartbeat.
- Policy synchronization.
- App/window event collection according to configuration.
- Idle-state collection.
- Optional camera presence.
- Optional screenshot capture.
- Local event queue.
- Retry/backoff.
- Deduplication.
- Safe shutdown.
- Agent version reporting.
- Health diagnostics.
- Explicit monitoring pause/stop behavior.

## 10.2 Agent security

- Agent authenticates as a device, not as a Guardian.
- Device secrets must be revocable.
- Pairing token is short-lived and single-use.
- All remote traffic uses TLS.
- Do not expose the Agent's local control API to the public Internet.
- Do not accept arbitrary executable commands from the backend.
- Policy messages must be typed, versioned, and schema-validated.
- Agent accepts only supported policy actions.
- Log policy changes and acknowledgments.
- Do not execute arbitrary scripts received from server.

## 10.3 Monitoring data model

Every event should include, where appropriate:
- `event_id` (stable unique identifier).
- `device_id`.
- `event_type`.
- `occurred_at` (UTC).
- `received_at` (server UTC).
- `session_id` (nullable).
- `policy_version`.
- `payload` validated against event type.
- `agent_version`.

Use idempotent ingestion based on stable event IDs.

## 10.4 Verified study duration

Keep these concepts separate:
- Elapsed session duration.
- Active device duration.
- Presence-confirmed duration.
- Verified study duration.
- Away duration.
- Unknown/unverified duration.

Never claim webcam presence equals attention. Calculate verified duration using the configured policy and available signals. Document the exact formula and expose it in the UI.

---

# 11. AI Architecture

## 11.1 Provider abstraction

Create a provider adapter interface. Provider/model/API key must be configured server-side.

- Never expose API keys in frontend bundles.
- Never hardcode secrets.
- Support the configured Gemini/OpenAI-compatible provider if the existing project configuration indicates one.
- If no key is available, implement adapter contracts, validation, tests with mocked providers, and clear configuration instructions.
- Do not return fake generated content as if it came from AI.

## 11.2 AI job handling

Long-running OCR/analysis/quiz generation should use background jobs or a safe task mechanism.

States:
- PENDING
- RUNNING
- SUCCEEDED
- FAILED
- CANCELLED

Persist:
- Provider.
- Model.
- Prompt/template version.
- Input references.
- Output.
- Error summary (without secrets).
- Created/completed timestamps.
- Requesting user.
- Approval state where applicable.

## 11.3 Structured output

Validate AI output with Pydantic schemas before saving. Reject malformed output and retry safely within limits.

AI should produce:
- Summary.
- Key concepts.
- Topics demonstrated.
- Topics not demonstrated.
- Possible misconceptions.
- Suggested review items.
- Proposed questions.
- Explanation and evidence references where possible.

AI must not invent facts or claim that a learner lacks knowledge based solely on an incomplete note.

## 11.4 Human approval

Require Guardian approval before:
- Publishing AI-generated assignments.
- Publishing mandatory quizzes, unless a per-assignment setting explicitly permits auto-publication.
- Changing schedules automatically.
- Changing device/application policies.
- Applying consequential recommendations.

---

# 12. UI/UX Design Requirements

## 12.1 Visual direction

Use a premium, modern education SaaS aesthetic:
- Clean white/light surfaces and carefully balanced dark mode.
- Deep indigo/blue primary color.
- Restrained accent color.
- Clear typography.
- Consistent spacing and border radius.
- Subtle shadows.
- Purposeful animation.
- Strong information hierarchy.
- Accessible contrast.
- No unnecessary gradients or decorative clutter.

Suggested tokens:
- Light background: `#F8FAFC`
- Light surface: `#FFFFFF`
- Primary: `#4F46E5`
- Primary hover: `#4338CA`
- Text: `#172033`
- Muted: `#64748B`
- Border: `#E2E8F0`
- Dark background: `#0B1120`
- Dark surface: `#111827`
- Dark elevated: `#1E293B`
- Dark primary: `#818CF8`

Typography:
- Be Vietnam Pro for Vietnamese.
- Inter for English.
- Fallback fonts.

## 12.2 Shared components

Build reusable:
- AppShell.
- Sidebar.
- Header.
- Breadcrumbs.
- PageHeader.
- StatCard.
- StatusBadge.
- DataTable.
- FilterBar.
- SearchInput.
- DateRangePicker.
- Calendar.
- Timeline.
- EmptyState.
- ErrorState.
- LoadingSkeleton.
- ConfirmDialog.
- FormField.
- FileUploader.
- NotificationPopover.
- UserMenu.
- ThemeToggle.
- LanguageSwitcher.

## 12.3 Functional UI standard

Every visible interactive element must work:
- Buttons execute real actions.
- Forms validate and submit.
- Filters affect results.
- Search queries backend or filters loaded data intentionally.
- Calendar events open detail views.
- Loading states appear during requests.
- Errors are actionable.
- Destructive operations require confirmation.
- Mutations invalidate or update relevant cached queries.
- No dead links or decorative controls pretending to be features.

---

# 13. Security, Privacy, and Reliability

## 13.1 Security

- Argon2id password hashing.
- Secure access/refresh token strategy.
- Refresh token rotation/revocation.
- HTTPS in deployed environments.
- CORS allowlist.
- CSRF protection if cookie-based auth is used.
- Rate limiting for login, pairing, password reset, and sensitive endpoints.
- SQLAlchemy parameterized queries.
- Strict input validation.
- Private file storage.
- Signed, short-lived download URLs where applicable.
- Device credential revocation.
- Guardian/Student data isolation.
- Audit sensitive operations.
- Never log passwords, tokens, API keys, or raw secrets.

## 13.2 Privacy

- Explain monitoring to Student.
- Display monitoring state.
- Provide consent/configuration controls for camera and screenshots.
- Minimize collected window title/content.
- No keylogging.
- No covert recording.
- No raw webcam video upload.
- Define retention and deletion policies.
- Restrict screenshot access and audit every access.
- Treat presence data as a limited signal, not proof of attention.
- Provide a safe pause/stop behavior consistent with approved policy.

## 13.3 Reliability

- Handle Agent disconnects.
- Persist in-progress study sessions.
- Recover interrupted sessions.
- Deduplicate event ingestion.
- Avoid double-counting duration.
- Use transactions for task/quiz completion workflows.
- Retry transient provider errors with backoff.
- Surface permanent failures.
- Back up database and object storage according to an operational plan.

---

# 14. Testing and Acceptance Criteria

Use a separate test database or isolated test fixtures. Do not run write/delete tests against production TiDB.

## 14.1 Backend tests

- Login and token refresh.
- Guardian/Student authorization.
- Guardian cannot access unrelated Student.
- Student cannot update Guardian policy.
- Pairing code expiry and one-time use.
- Device revocation.
- Event ingestion idempotency.
- Study duration calculations.
- Schedule conflict detection.
- Assignment completion criteria.
- Quiz scoring and retry rules.
- AI output schema validation.
- File access authorization.
- Notification deduplication.

## 14.2 Frontend tests

- Role-specific routing.
- Login forms.
- Guardian dashboard.
- Student dashboard.
- Schedule CRUD.
- Assignment CRUD.
- Note submission.
- Quiz flow.
- Realtime status display.
- Error/loading/empty states.
- Light/dark mode.
- Vietnamese/English localization.
- Responsive navigation.

## 14.3 Agent tests

Mock Windows APIs where necessary:
- Pairing.
- Heartbeat.
- Offline queue.
- Event retry.
- Duplicate event handling.
- Policy version update.
- Policy acknowledgment.
- Revoked device behavior.
- Camera unavailable state.
- Safe shutdown.

## 14.4 End-to-end acceptance flow

1. Guardian logs in.
2. Guardian invites/links Student.
3. Student accepts invitation and logs in.
4. Guardian creates subject and topic.
5. Guardian creates schedule.
6. Guardian creates assignment and attaches reference material.
7. Student sees the assignment.
8. Student starts a study session.
9. Agent connects and reports status, if installed.
10. Student submits notes.
11. AI analyzes the note when provider is configured.
12. Guardian reviews/publishes quiz.
13. Student takes quiz.
14. Backend scores quiz.
15. Task status updates according to configured criteria.
16. Guardian and Student dashboards show consistent results.
17. Analytics reflect persisted records without double-counting.
18. Agent disconnect/reconnect does not duplicate events.

## 14.5 Definition of Done

A module is complete only when:
- UI exists.
- API exists.
- Authorization is enforced.
- Database persistence works.
- Loading/error/empty states exist.
- Tests cover critical behavior.
- End-to-end flow is verified where practical.
- Documentation is updated.

A static page or mocked API is not a completed feature.

---

# 15. Implementation Roadmap

Work in phases, but do not stop after planning. Complete each phase, run tests, fix defects, and continue.

## Phase 0 — Workspace and Database Discovery

- Read this specification.
- Inspect workspace and existing documents.
- Inspect TiDB metadata.
- Produce database mapping and gap reports.
- Verify TLS configuration.
- Do not perform production writes.
- Create an implementation checklist.
- Continue directly to Phase 1.

## Phase 1 — Backend Foundation

- Create FastAPI project.
- Configure environment management.
- Configure TiDB connection with TLS verification.
- Implement health/readiness endpoints.
- Implement metadata-safe model mapping.
- Implement logging and centralized errors.
- Add backend test setup.
- Confirm no schema writes happen on startup.

## Phase 2 — Authentication and Relationships

- Guardian and Student login.
- User/relationship authorization.
- Invitation/pairing foundations.
- Sessions and token lifecycle.
- Guardian PIN.
- Security tests.

## Phase 3 — Frontend Foundation

- React/Vite/TypeScript.
- Tailwind and shadcn/ui.
- Router and protected routes.
- API client and query provider.
- Theme and localization.
- Shared AppShell.
- Login and invitation pages.
- Guardian and Student navigation.

## Phase 4 — Core Learning Management

- Subjects and topics.
- Schedules and recurring events.
- Assignments/tasks.
- Materials metadata and upload.
- Student submissions/notes.
- Calendar synchronization.
- Conflict detection.

## Phase 5 — Study Sessions and Monitoring Integration

- Study session lifecycle.
- Agent registration/pairing.
- Heartbeat.
- Event ingestion.
- Realtime monitoring.
- Idle/presence states.
- Offline queue protocol.
- Verified duration calculations.
- Monitoring transparency UI.

## Phase 6 — AI Learning and Quiz

- AI provider adapter.
- File text extraction/OCR boundary.
- Note analysis.
- Reference comparison.
- Study plan generation.
- Quiz generation.
- Guardian review/approval.
- Quiz attempts and scoring.
- Retry logic.

## Phase 7 — Policies and Windows Agent

- Application rules.
- Website rules.
- Time windows.
- Temporary permissions.
- Emergency override.
- Agent policy acknowledgment.
- Optional webcam presence.
- Optional screenshot feature with explicit consent.
- Device diagnostics.

## Phase 8 — Analytics and Notifications

- Daily/weekly/monthly metrics.
- Knowledge progress.
- Review recommendations.
- Notification center.
- Browser notification preferences.
- Reports.

## Phase 9 — Production Readiness

- Security review.
- Performance review.
- Responsive QA.
- End-to-end tests.
- Docker/local deployment.
- Production deployment guide.
- Backup/restore guide.
- Agent installation guide.
- README and environment documentation.

After each phase:
- Run relevant tests.
- Fix errors.
- Update `docs/IMPLEMENTATION_STATUS.md`.
- List completed features and unresolved blockers.
- Continue to the next phase unless a genuine external dependency blocks it.

---

# 16. Required Project Structure

Use a monorepo:

```text
D:\\Project_Study_Management\\
  frontend/
    src/
      app/
      components/
      layouts/
      features/
      pages/
      services/
      hooks/
      stores/
      types/
      utils/
      locales/
  backend/
    app/
      api/
      core/
      database/
      models/
      schemas/
      repositories/
      services/
      integrations/
      websocket/
      workers/
    tests/
    migrations/
  agent/
    app/
      client/
      collectors/
      policy/
      queue/
      ui/
    tests/
  docs/
    SRS_WEB.md
    ARCHITECTURE.md
    DATABASE_MAPPING.md
    DATABASE_GAPS.md
    MIGRATION_SAFETY.md
    API.md
    SECURITY_PRIVACY.md
    IMPLEMENTATION_STATUS.md
  scripts/
    setup.ps1
    run-backend.ps1
    run-frontend.ps1
    run-agent.ps1
  storage/                 # local development only; production object storage preferred
  .env.example
  .gitignore
  docker-compose.yml
  README.md
```

Adjust names when necessary, but preserve separation of frontend, backend, and Agent.

---

# 17. Required Developer Experience

Create PowerShell scripts:
- `scripts/setup.ps1`
- `scripts/run-backend.ps1`
- `scripts/run-frontend.ps1`
- `scripts/run-agent.ps1`

README must explain:
- Prerequisites.
- Python environment.
- Node version.
- Dependency installation.
- TiDB TLS setup.
- Environment variables.
- Running backend.
- Running frontend.
- Running Agent.
- Running tests.
- API docs.
- Troubleshooting.
- Production deployment.
- Agent pairing and revocation.

Do not commit `.env`, secrets, local database files, uploaded user documents, or monitoring artifacts.

---

# 18. Final Instruction to Codex

Start now.

1. Read this entire specification.
2. Inspect the current workspace.
3. Inspect the real TiDB schema and map all existing tables.
4. Create the Web monorepo structure.
5. Implement the backend foundation.
6. Implement authentication and role-based access.
7. Implement the Web frontend.
8. Implement Guardian and Student workflows.
9. Implement the Windows Agent integration boundary.
10. Continue through the roadmap.

Do not stop after Phase 0.
Do not return only a plan.
Do not return code snippets without writing files.
Do not build a generic Study Planner that discards Guardian/Student, AI analysis, quiz workflows, or Windows Agent integration.
Do not claim browser-only monitoring can control Windows.
Do not alter or reset the existing TiDB database.
Do not claim a feature is done until it has been tested.

**The required deliverable is a working AI Learning Guardian Web platform, with a companion Windows Agent for OS-level functions, based on the original SRS and the actual existing database schema.**
