# Security review

## Implemented controls
- Argon2id/bcrypt password verification.
- Short-lived bearer access tokens and rotating HttpOnly refresh cookies.
- Guardian/Student role checks.
- Guardian–Student relationship scoping.
- Stable sanitized error responses with request IDs.
- Login and registration rate limiting in process memory.
- No password hashes or refresh tokens in API success responses.
- Notification and task mutations use backend-authenticated identity.

## Remaining risks
- Process-local rate limits are not shared across workers.
- Shared notification delivery does not use a durable event table workflow.
- AI provider timeout/retry limits require deployment tuning.
- File object storage and upload authorization remain unimplemented.
- Device pairing and batch synchronization are unimplemented.
- The startup hook is deprecated and should move to lifespan state.

## Testing note
No production credentials, TiDB data, or secrets are used by the test suite.
