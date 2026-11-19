# Security and privacy

## Current implementation

- Login verifies Argon2 hashes and legacy bcrypt hashes. New password creation/rehash workflow is not implemented.
- JWT bearer token is signed with `JWT_SECRET`, but current settings have an insecure built-in development fallback and do not refuse it in production.
- Frontend stores the access token in `localStorage`; the JWT is valid for 10 hours and has no refresh/revocation route.
- Some read/write routes scope records to linked Students. Quiz authorization and relation-ID ownership checks have gaps identified in `ARCHITECTURE_REVIEW.md`.
- No keylogging, hidden service, webcam, or screenshot collection is implemented. The Agent is a diagnostics/queue scaffold only.

## Required before production

Configure a unique, high-entropy JWT secret through secret management and make startup reject the fallback; use HTTPS and a strict deployed CORS allowlist; add refresh rotation/revocation and appropriate browser token storage; rate-limit login/pairing/sensitive actions; scope every query and foreign key against Guardian/Student relationships; audit sensitive changes; provide private object storage and retention controls; never log passwords, JWTs, API keys, or device credentials.

No actual camera/screenshot/OS monitoring feature should be enabled until visible consent, policy lifecycle, access auditing, and retention behavior are implemented and tested.
