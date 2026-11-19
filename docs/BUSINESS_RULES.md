# Business rules

## Roles
- A `GUARDIAN` may manage linked Students and Guardian-owned records.
- A `STUDENT` may access only records owned by or assigned to that Student.
- An `ADMIN` workspace is not implemented.

## Relationships
- Student data is scoped through `guardian_student_links`.
- Backend identity, not a client-supplied role or Student ID, defines access scope.
- Guardian-created Students are immediately linked to the creating Guardian.

## Tasks
- Existing statuses are constrained to `TODO`, `IN_PROGRESS`, `ASSIGNED`, and `COMPLETED` for the implemented workflow.
- Only a Student may start or complete an owned task.
- Completing a task creates a Guardian notification when `notifications` is available.
- SRS states without persisted schema fields are not inferred or synthesized.

## Sessions
- One active session is resolved by `ended_at IS NULL` for the Student.
- Session duration is calculated by the backend from `started_at` and completion time.
- Browser state is not a source of duration truth.

## Notes and AI
- Students own note records.
- Submitted notes cannot be edited or deleted.
- AI analysis is provider-backed and validated before persistence.
- No fabricated AI result is returned.

## Quizzes
- Student quiz access requires ownership or an active linked Guardian relationship.
- Objective scoring is performed at the backend.
- Quiz answer keys are omitted from Student quiz reads.

## Assignments
- Submission/revision/history workflow remains blocked until its missing schema contract is approved.
