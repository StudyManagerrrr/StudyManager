# Next implementation steps

Continue in small, testable modules. All database-facing tests must inject temporary SQLite or another isolated database. Do not connect tests to production TiDB. No schema change is authorized by this plan.

1. **Assignment submission contract:** implement the reviewed SRS submission/revision/history workflow only after missing schema fields are approved. Existing task status transitions now cover only persisted TODO/IN_PROGRESS/COMPLETED states.
2. **Learning task vertical slice:** detail and Student start/complete transitions are implemented and isolated. Remaining work: deadline groups, Guardian review, cancelled/needs-revision states and explicit progress history require a schema contract.
3. **Subjects/topics/schedules UI:** add real edit/archive flows against implemented APIs; then recurrence, conflict handling and timezone behavior according to SRS.
4. **Notes/materials:** add Student note submission and AI result UI; investigate attachment storage and submission/revision schema before upload implementation.
5. **Quiz workflow:** Guardian authoring/review/publish and broader scoring; test attempts, limits and ownership.
6. **Windows Agent:** pairing/enrollment design, local queue hardening, authenticated batch endpoint and explicit permitted collectors; document privacy and retention controls.
7. **Reliability/security:** shared rate limiter, centralized response contract, route/service modularization, frontend tests, Agent tests, deployment guide, and production-readiness review.

Schema changes remain gated on an explicit approval after impact analysis and written proposal. Update `IMPLEMENTATION_STATUS.md`, `DATABASE_GAPS.md`, API docs, and `TEST_REPORT.md` as each module lands.
