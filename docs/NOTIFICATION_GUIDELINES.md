# Notification and confirmation guidelines

## Feedback types

- **Success:** short toast; closes after 4.5 seconds.
- **Error:** accessible alert toast; stays for 9 seconds, with an explicit close control.
- **Warning / info:** polite status toast; closes after 4.5 seconds.
- **Confirmation:** modal `alertdialog`; requires an explicit choice and resolves false on Escape or backdrop click.

The shared provider is `frontend/src/notifications.tsx`. Messages are translated before passing to `notify`/`confirm`; duplicate identical notices are suppressed while visible. The stack is capped at four visible messages and exposes `role`, `aria-live`, and a close button. No `window.alert` or `window.confirm` is used.

Use confirmation for destructive actions, quiz submission, logout, and discarding unsaved changes. Do not show a success message until the API confirms success. Keep actionable API errors in the shared localized error mapping and include the request ID when available.

Current implementation uses the shared toast and confirmation primitives for sign-in/registration, save, logout, quiz submission, session expiration, and API failures. Future workflows should use the same provider rather than adding per-component banners or browser dialogs.
