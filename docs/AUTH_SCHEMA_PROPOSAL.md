# Authentication schema and service proposal (approval required before DDL)

**Status:** proposal only. No migration has been created or run. The configured TiDB remains unchanged.

## Existing mapping

- `users` contains identity, password hash, role, active flag, and timestamps; it has no reset/invitation state, email verification, or Guardian PIN fields.
- `guardian_student_links` represents an accepted relationship, with a unique `student_id` index.
- `user_sessions` contains session ID, user ID, unique token hash, expiry, revocation time, creation time and request metadata. It is now used for refresh-session rotation and revocation.
- `system_settings` is global key/value metadata, not a per-user security credential store.
- No email delivery provider/environment is configured in the checked-in example.

## Unimplemented requirements and why they need design

1. **Student invitations:** an invitation must have an intended email, token purpose/hash, expiration, one-time consumption state, creator, and pending-account/relationship lifecycle. Reusing `user_sessions` would conflate login sessions with invitations; a pending `users` row plus a refresh-session row would not persist purpose or consumption safely. Guardian self-registration is implemented with current `users` columns and creates no relationship; this proposal still blocks Student invitations only.
2. **Password reset:** requires a one-time purpose-scoped token, expiry/consumed state and delivery channel. Returning reset tokens from an unauthenticated endpoint or logging them is not safe. Email delivery is not configured.
3. **Guardian PIN:** requires a per-Guardian Argon2id hash and, if required, durable failed-attempt lockout state. A global `system_settings` record is not an acceptable credential boundary without an explicit security review.

## Additive options for review

- Add a narrowly scoped `account_tokens` table with user/invitation target, `purpose`, unique `token_hash`, expiry, consumed/revoked timestamps, creator/request metadata; use it for invitation/reset tokens only.
- Add a `guardian_security` table keyed by user ID with `pin_hash`, failure count/lock time, and updated timestamp, or add reviewed user columns if that better matches operational practice.
- Configure an email provider through secret-managed environment settings; do not return or log reset tokens in production.
- Keep the existing `user_sessions` table for refresh sessions and revoke them after password reset.

## Required review before implementation

Review which additive schema option fits existing application data and operational backup/restore. The user must explicitly approve the migration before any DDL. Until then, Student invitation acceptance, password reset, Guardian PIN, and email verification stay blocked; unrelated features can continue without those flows. Guardian self-registration does not require a schema change and is implemented separately.
