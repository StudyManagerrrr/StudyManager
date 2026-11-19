# API error contract

## Response

All handled FastAPI errors return the following stable envelope and a matching `X-Request-ID` header:

```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không chính xác.",
    "details": null,
    "request_id": "d5d4be6d-0c4d-4427-9bb8-3673a1d56498"
  },
  "detail": "Email hoặc mật khẩu không chính xác."
}
```

The top-level `detail` is a temporary compatibility field for existing clients. It contains the same localized, sanitized user message; it never includes a traceback, SQL, credentials, or submitted field values. New clients must read `error.code`, `error.message`, `error.details`, and `error.request_id`.

## Localization and validation

- The API reads `Accept-Language: vi` or `en`; unsupported/missing preferences fall back to Vietnamese.
- Request validation details are limited to field paths and safe categories (`required`, `format`, `value`). Pydantic `input` values are omitted so secrets are not reflected.
- The frontend sends the current locale and maps stable codes to the matching controlled translation dictionary. Unknown/network failures use a localized generic message, not raw exception text.

## Status and handling

- `HTTPException`: status is preserved; message/code are mapped centrally.
- `RequestValidationError`: 422 with sanitized field details.
- SQLAlchemy exceptions: 503 `DATABASE_UNAVAILABLE`.
- Unexpected exceptions: 500 `INTERNAL_SERVER_ERROR`; server logs include request ID and exception class only.
- Rate limiting: 429. AI gateway failures use 502/503/504 according to cause.
- Every API response receives an `X-Request-ID`; error responses include the same ID in the envelope and logs.

Current handlers retain HTTP status and safe `detail` for backward compatibility. The catalog includes reserved SRS codes; a reserved code does not imply its feature route is implemented. See `ERROR_CODE_CATALOG.md`.
