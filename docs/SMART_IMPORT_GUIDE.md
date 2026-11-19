# Smart import guide

## Document upload
- Endpoint: `POST /api/v1/materials/upload`
- Form fields: `file`
- Optional: `subject_id`, `topic_id`, `student_id`
- Maximum size: 20 MB
- Supported: PDF, DOCX, DOC, XLSX, XLS, CSV, TXT, PNG, JPG/JPEG, WEBP
- Actual extraction: TXT/CSV; PDF/DOCX/XLSX with installed parsers
- Image OCR: blocked until a provider is configured
- Storage: local server `storage/documents` in this development implementation

## Timetable text preview
- Endpoint: `POST /api/v1/timetable/parse-text`
- Guardian may select a linked Student; Student scope is resolved automatically.
- Example: `Thứ 2 học Toán từ 7h đến 9h tại phòng A101`
- The API returns normalized preview rows, parse errors and duplicate count.
- Preview never writes schedules.

## Timetable file preview
- Endpoint: `POST /api/v1/timetable/parse-file`
- Supported: CSV, XLSX, TXT, PDF, DOCX
- CSV/XLSX headers recognized: title/subject, start/start_at, end/end_at, location/room, weekday/day/date
- Images are intentionally rejected as OCR is not configured

## Confirmation import
- Endpoint: `POST /api/v1/timetable/import`
- Guardian only
- Existing schedule overlap is skipped
- Rows are inserted in one transaction
- The response reports created, skipped and per-line errors
