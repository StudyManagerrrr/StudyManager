# Vietnamese / English language guide

## Current design

- React uses the shared `I18nProvider` and `useI18n()` helper in `frontend/src/i18n.tsx`; this is a small equivalent i18n layer suited to the current single-shell frontend.
- Translation keys are namespaced by feature (`common.*`, `auth.*`, `dashboard.*`, `quizzes.*`, `errors.*`, etc.) in `frontend/src/locales/vi.ts` and `en.ts`. UI strings belong in these dictionaries, not JSX.
- New visitors default to Vietnamese. The selected language is stored under `guardian_language` in localStorage; this key is separate from authentication and survives logout. No sensitive data is stored there.
- There is no mapped per-user language field or existing server preference API. The frontend sends `Accept-Language` for server error localization. Language preference remains local until a schema/API preference design is approved; no TiDB change was made.
- Changing language updates the provider without reload or route changes. Current form and authenticated state live above the switcher and remain mounted.

## Locale formatting

Use the provider's `formatDate`, `formatTime`, `formatDateTime`, and `formatNumber` helpers. They use `vi-VN` or `en-US` with the browser timezone unchanged. For deterministic display requirements, supply explicit `Intl` options such as `timeZone`; changing language must not rewrite stored UTC timestamps.

## Adding translation keys

1. Add the same namespaced key to both locale dictionaries.
2. Use `t('namespace.key', { name, count })` for dynamic values.
3. Keep user-authored names, note content and quiz content unchanged.
4. Run `npm test` to detect dictionary drift and exercise switching/persistence; run `npm run build` for type checks.

## Coverage boundary

The implemented shell covers sign-in, Guardian registration, navigation, dashboard, schedules/subjects/assignments create forms, AI and monitoring empty/status views, quiz flows, shared feedback and API errors. Password reset, student invitation, rich notes/materials/settings/profile workflows do not yet exist in the frontend, so they cannot be translated until implemented.
