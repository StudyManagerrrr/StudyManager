# Timetable import guide

1. Guardian selects a Student.
2. The user enters text or uploads CSV/XLSX/TXT/PDF/DOCX.
3. The API normalizes weekday and time values.
4. Duplicate schedules are marked before confirmation.
5. Guardian reviews and edits preview rows.
6. Guardian confirms import.
7. Backend validates ownership and writes schedules in a transaction.

## Supported time formats
- `7h`, `7:00`
- `13h30`, `13:30`
- `từ 7h đến 9h`
- `7:00-9:00`

## Schema limits
- Standard weekday or date schedules use existing `study_schedules`.
- Recurrence rules, weekly parity and import history are not claimed as implemented.
