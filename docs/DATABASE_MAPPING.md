# TiDB schema mapping (live metadata)

Verified: 2026-11-20. Source: TiDB Cloud `information_schema` via verified TLS. Only metadata and `SELECT 1` were queried; no application rows or DDL. ORM access reflects the live schema at startup using SQLAlchemy `MetaData.reflect`; mappings must filter against reflected columns.

Tables: 38; columns: 364; indexes: 143; foreign-key columns: 70.

In the generated tables below, `?` is a placeholder for an absent metadata value (NULL default or no index key); it is not a literal database default.

## Tables and columns

### `achievements` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `code` | `varchar(100)` | NO | ? | UNI |
| `name` | `varchar(150)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `icon` | `varchar(100)` | YES | ? | ? |
| `points` | `int` | NO | 0 | ? |
| `criteria` | `json` | YES | ? | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `activity_logs` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `session_id` | `char(36)` | YES | ? | MUL |
| `device_id` | `char(36)` | YES | ? | ? |
| `application_id` | `char(36)` | YES | ? | MUL |
| `window_title` | `varchar(500)` | YES | ? | ? |
| `started_at` | `datetime(3)` | NO | ? | MUL |
| `ended_at` | `datetime(3)` | YES | ? | ? |
| `duration_seconds` | `int` | NO | 0 | ? |
| `activity_type` | `varchar(50)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `ai_analyses` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `note_id` | `char(36)` | NO | ? | MUL |
| `reference_content` | `longtext` | YES | ? | ? |
| `extracted_content` | `longtext` | YES | ? | ? |
| `summary` | `longtext` | YES | ? | ? |
| `key_concepts` | `json` | YES | ? | ? |
| `missing_topics` | `json` | YES | ? | ? |
| `weak_topics` | `json` | YES | ? | ? |
| `recommendations` | `json` | YES | ? | ? |
| `formulas` | `json` | YES | ? | ? |
| `model_name` | `varchar(150)` | YES | ? | ? |
| `provider_name` | `varchar(100)` | YES | ? | ? |
| `status` | `varchar(30)` | NO | PENDING | MUL |
| `error_message` | `text` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `application_policies` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `device_id` | `char(36)` | YES | ? | MUL |
| `application_id` | `char(36)` | YES | ? | MUL |
| `application_name` | `varchar(200)` | NO | ? | ? |
| `policy_type` | `varchar(30)` | NO | ? | ? |
| `action` | `varchar(30)` | NO | ? | ? |
| `start_time` | `time` | YES | ? | ? |
| `end_time` | `time` | YES | ? | ? |
| `allowed_minutes` | `int` | YES | ? | ? |
| `is_enabled` | `tinyint(1)` | NO | 1 | ? |
| `created_by` | `char(36)` | NO | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `applications` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `device_id` | `char(36)` | YES | ? | MUL |
| `application_name` | `varchar(200)` | NO | ? | MUL |
| `executable_name` | `varchar(255)` | YES | ? | ? |
| `executable_path` | `varchar(1000)` | YES | ? | ? |
| `publisher` | `varchar(255)` | YES | ? | ? |
| `category` | `varchar(50)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `audit_logs` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `user_id` | `char(36)` | YES | ? | MUL |
| `action` | `varchar(100)` | NO | ? | MUL |
| `entity_type` | `varchar(100)` | YES | ? | MUL |
| `entity_id` | `char(36)` | YES | ? | ? |
| `old_values` | `json` | YES | ? | ? |
| `new_values` | `json` | YES | ? | ? |
| `ip_address` | `varchar(45)` | YES | ? | ? |
| `user_agent` | `varchar(500)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | MUL |

### `daily_reports` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `report_date` | `date` | NO | ? | MUL |
| `total_study_seconds` | `int` | NO | 0 | ? |
| `valid_study_seconds` | `int` | NO | 0 | ? |
| `break_seconds` | `int` | NO | 0 | ? |
| `completed_tasks` | `int` | NO | 0 | ? |
| `total_tasks` | `int` | NO | 0 | ? |
| `average_quiz_score` | `decimal(5,2)` | YES | ? | ? |
| `report_data` | `json` | YES | ? | ? |
| `generated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `device_settings` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `device_id` | `char(36)` | NO | ? | MUL |
| `setting_key` | `varchar(150)` | NO | ? | ? |
| `setting_value` | `json` | YES | ? | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `devices` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `owner_user_id` | `char(36)` | NO | ? | MUL |
| `device_name` | `varchar(150)` | NO | ? | ? |
| `device_identifier` | `varchar(255)` | NO | ? | UNI |
| `operating_system` | `varchar(100)` | YES | ? | ? |
| `os_version` | `varchar(100)` | YES | ? | ? |
| `agent_version` | `varchar(50)` | YES | ? | ? |
| `agent_status` | `varchar(30)` | NO | DISCONNECTED | MUL |
| `last_heartbeat_at` | `datetime(3)` | YES | ? | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `registered_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `flashcard_reviews` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `flashcard_id` | `char(36)` | NO | ? | MUL |
| `student_id` | `char(36)` | NO | ? | MUL |
| `rating` | `varchar(20)` | NO | ? | ? |
| `reviewed_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `flashcards` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `subject_id` | `char(36)` | YES | ? | ? |
| `topic_id` | `char(36)` | YES | ? | MUL |
| `front_content` | `longtext` | NO | ? | ? |
| `back_content` | `longtext` | NO | ? | ? |
| `difficulty` | `varchar(20)` | YES | MEDIUM | ? |
| `source_type` | `varchar(30)` | YES | MANUAL | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `guardian_student_links` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `guardian_id` | `char(36)` | NO | ? | MUL |
| `student_id` | `char(36)` | NO | ? | UNI |
| `relationship` | `varchar(50)` | YES | ? | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `knowledge_progress` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `topic_id` | `char(36)` | NO | ? | ? |
| `mastery_score` | `decimal(5,2)` | NO | 0 | ? |
| `total_attempts` | `int` | NO | 0 | ? |
| `correct_attempts` | `int` | NO | 0 | ? |
| `last_reviewed_at` | `datetime(3)` | YES | ? | ? |
| `next_review_at` | `datetime(3)` | YES | ? | MUL |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `learning_materials` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `subject_id` | `char(36)` | YES | ? | MUL |
| `topic_id` | `char(36)` | YES | ? | MUL |
| `uploaded_by` | `char(36)` | NO | ? | MUL |
| `title` | `varchar(255)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `file_name` | `varchar(255)` | YES | ? | ? |
| `file_path` | `varchar(1000)` | YES | ? | ? |
| `mime_type` | `varchar(150)` | YES | ? | ? |
| `file_size_bytes` | `bigint` | YES | ? | ? |
| `material_type` | `varchar(50)` | YES | ? | ? |
| `extracted_text` | `longtext` | YES | ? | ? |
| `processing_status` | `varchar(30)` | YES | PENDING | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `learning_notes` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `subject_id` | `char(36)` | YES | ? | MUL |
| `topic_id` | `char(36)` | YES | ? | MUL |
| `schedule_id` | `char(36)` | YES | ? | MUL |
| `title` | `varchar(255)` | NO | ? | ? |
| `content` | `longtext` | YES | ? | ? |
| `analysis_status` | `varchar(30)` | YES | PENDING | ? |
| `submitted_at` | `datetime(3)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `learning_point_transactions` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `user_id` | `char(36)` | NO | ? | MUL |
| `points` | `int` | NO | ? | ? |
| `transaction_type` | `varchar(50)` | NO | ? | ? |
| `description` | `varchar(255)` | YES | ? | ? |
| `reference_id` | `char(36)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | MUL |

### `learning_tasks` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `subject_id` | `char(36)` | YES | ? | ? |
| `schedule_id` | `char(36)` | YES | ? | MUL |
| `created_by` | `char(36)` | NO | ? | ? |
| `title` | `varchar(255)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `priority` | `varchar(20)` | NO | MEDIUM | ? |
| `status` | `varchar(30)` | NO | TODO | MUL |
| `due_at` | `datetime(3)` | YES | ? | MUL |
| `completed_at` | `datetime(3)` | YES | ? | ? |
| `estimated_minutes` | `int` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `monitoring_events` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `device_id` | `char(36)` | YES | ? | MUL |
| `session_id` | `char(36)` | YES | ? | ? |
| `event_type` | `varchar(100)` | NO | ? | MUL |
| `severity` | `varchar(20)` | YES | INFO | ? |
| `description` | `text` | YES | ? | ? |
| `metadata` | `json` | YES | ? | ? |
| `occurred_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | MUL |

### `note_attachments` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `note_id` | `char(36)` | NO | ? | MUL |
| `file_name` | `varchar(255)` | NO | ? | ? |
| `file_path` | `varchar(1000)` | NO | ? | ? |
| `mime_type` | `varchar(150)` | YES | ? | ? |
| `file_size_bytes` | `bigint` | YES | ? | ? |
| `extracted_text` | `longtext` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `notifications` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `user_id` | `char(36)` | NO | ? | MUL |
| `title` | `varchar(255)` | NO | ? | ? |
| `message` | `text` | NO | ? | ? |
| `notification_type` | `varchar(50)` | NO | ? | ? |
| `priority` | `varchar(20)` | YES | NORMAL | ? |
| `related_entity_type` | `varchar(50)` | YES | ? | ? |
| `related_entity_id` | `char(36)` | YES | ? | ? |
| `is_read` | `tinyint(1)` | NO | 0 | ? |
| `read_at` | `datetime(3)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | MUL |

### `presence_logs` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `session_id` | `char(36)` | NO | ? | MUL |
| `status` | `varchar(30)` | NO | ? | ? |
| `source` | `varchar(50)` | NO | ? | ? |
| `detected_at` | `datetime(3)` | NO | ? | MUL |
| `duration_seconds` | `int` | NO | 0 | ? |
| `confidence` | `decimal(5,4)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `question_options` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `question_id` | `char(36)` | NO | ? | MUL |
| `option_text` | `longtext` | NO | ? | ? |
| `option_label` | `varchar(10)` | YES | ? | ? |
| `is_correct` | `tinyint(1)` | NO | 0 | ? |
| `sort_order` | `int` | NO | 0 | ? |

### `questions` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `quiz_id` | `char(36)` | NO | ? | MUL |
| `topic_id` | `char(36)` | YES | ? | MUL |
| `question_text` | `longtext` | NO | ? | ? |
| `question_type` | `varchar(30)` | NO | ? | ? |
| `difficulty` | `varchar(20)` | YES | MEDIUM | ? |
| `explanation` | `longtext` | YES | ? | ? |
| `correct_answer` | `json` | YES | ? | ? |
| `points` | `decimal(7,2)` | NO | 1.00 | ? |
| `sort_order` | `int` | NO | 0 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `quiz_answers` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `attempt_id` | `char(36)` | NO | ? | MUL |
| `question_id` | `char(36)` | NO | ? | MUL |
| `selected_option_id` | `char(36)` | YES | ? | ? |
| `answer_text` | `longtext` | YES | ? | ? |
| `answer_data` | `json` | YES | ? | ? |
| `is_correct` | `tinyint(1)` | YES | ? | ? |
| `awarded_points` | `decimal(7,2)` | NO | 0 | ? |
| `answered_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `quiz_attempts` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `quiz_id` | `char(36)` | NO | ? | MUL |
| `student_id` | `char(36)` | NO | ? | MUL |
| `attempt_number` | `int` | NO | 1 | ? |
| `score` | `decimal(7,2)` | NO | 0 | ? |
| `correct_count` | `int` | NO | 0 | ? |
| `total_count` | `int` | NO | 0 | ? |
| `status` | `varchar(30)` | NO | IN_PROGRESS | ? |
| `started_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `completed_at` | `datetime(3)` | YES | ? | ? |

### `quizzes` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `task_id` | `char(36)` | YES | ? | MUL |
| `subject_id` | `char(36)` | YES | ? | MUL |
| `created_by` | `char(36)` | NO | ? | ? |
| `title` | `varchar(255)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `difficulty` | `varchar(30)` | YES | MIXED | ? |
| `question_count` | `int` | NO | 0 | ? |
| `passing_score` | `decimal(5,2)` | NO | 70.00 | ? |
| `time_limit_seconds` | `int` | YES | ? | ? |
| `max_attempts` | `int` | YES | ? | ? |
| `is_mandatory` | `tinyint(1)` | NO | 0 | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `review_schedules` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `flashcard_id` | `char(36)` | YES | ? | ? |
| `topic_id` | `char(36)` | YES | ? | ? |
| `next_review_at` | `datetime(3)` | NO | ? | MUL |
| `interval_days` | `int` | NO | 1 | ? |
| `ease_factor` | `decimal(5,2)` | NO | 2.50 | ? |
| `repetitions` | `int` | NO | 0 | ? |
| `status` | `varchar(30)` | NO | PENDING | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `screenshots` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `session_id` | `char(36)` | NO | ? | MUL |
| `file_path` | `varchar(1000)` | NO | ? | ? |
| `file_size_bytes` | `bigint` | YES | ? | ? |
| `captured_at` | `datetime(3)` | NO | ? | MUL |
| `retention_until` | `datetime(3)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `study_schedules` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `subject_id` | `char(36)` | YES | ? | MUL |
| `created_by` | `char(36)` | NO | ? | ? |
| `title` | `varchar(200)` | NO | ? | ? |
| `study_type` | `varchar(30)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `location` | `varchar(255)` | YES | ? | ? |
| `start_at` | `datetime(3)` | NO | ? | MUL |
| `end_at` | `datetime(3)` | NO | ? | MUL |
| `recurrence_rule` | `json` | YES | ? | ? |
| `reminder_minutes` | `int` | YES | 10 | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `study_sessions` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `schedule_id` | `char(36)` | YES | ? | MUL |
| `device_id` | `char(36)` | YES | ? | ? |
| `started_at` | `datetime(3)` | NO | ? | MUL |
| `ended_at` | `datetime(3)` | YES | ? | ? |
| `total_duration_seconds` | `int` | NO | 0 | ? |
| `valid_duration_seconds` | `int` | NO | 0 | ? |
| `break_duration_seconds` | `int` | NO | 0 | ? |
| `status` | `varchar(30)` | NO | ACTIVE | MUL |
| `session_type` | `varchar(30)` | YES | SCHEDULED | ? |
| `notes` | `text` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `subjects` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `name` | `varchar(150)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `color` | `varchar(20)` | YES | ? | ? |
| `icon` | `varchar(100)` | YES | ? | ? |
| `is_active` | `tinyint(1)` | NO | 1 | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `system_settings` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `setting_key` | `varchar(150)` | NO | ? | UNI |
| `setting_value` | `json` | YES | ? | ? |
| `description` | `varchar(500)` | YES | ? | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `topics` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `subject_id` | `char(36)` | NO | ? | MUL |
| `parent_topic_id` | `char(36)` | YES | ? | MUL |
| `name` | `varchar(200)` | NO | ? | ? |
| `description` | `text` | YES | ? | ? |
| `difficulty` | `varchar(20)` | YES | MEDIUM | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `user_achievements` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `user_id` | `char(36)` | NO | ? | MUL |
| `achievement_id` | `char(36)` | NO | ? | ? |
| `unlocked_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `user_sessions` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `user_id` | `char(36)` | NO | ? | MUL |
| `token_hash` | `varchar(255)` | NO | ? | UNI |
| `ip_address` | `varchar(45)` | YES | ? | ? |
| `user_agent` | `varchar(500)` | YES | ? | ? |
| `expires_at` | `datetime(3)` | NO | ? | MUL |
| `revoked_at` | `datetime(3)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `users` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `username` | `varchar(100)` | NO | ? | UNI |
| `email` | `varchar(255)` | YES | ? | UNI |
| `password_hash` | `varchar(255)` | NO | ? | ? |
| `full_name` | `varchar(150)` | NO | ? | ? |
| `role` | `varchar(20)` | NO | ? | MUL |
| `avatar_url` | `varchar(500)` | YES | ? | ? |
| `is_active` | `tinyint(1)` | NO | 1 | MUL |
| `last_login_at` | `datetime(3)` | YES | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |
| `updated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `website_policies` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `device_id` | `char(36)` | YES | ? | MUL |
| `domain` | `varchar(255)` | NO | ? | MUL |
| `policy_type` | `varchar(30)` | NO | ? | ? |
| `action` | `varchar(30)` | NO | ? | ? |
| `start_time` | `time` | YES | ? | ? |
| `end_time` | `time` | YES | ? | ? |
| `is_enabled` | `tinyint(1)` | NO | 1 | ? |
| `created_by` | `char(36)` | NO | ? | ? |
| `created_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

### `weekly_reports` (BASE TABLE)

| Column | Type | Null | Default | Key |
|---|---|---:|---|---|
| `id` | `char(36)` | NO | ? | PRI |
| `student_id` | `char(36)` | NO | ? | MUL |
| `week_start` | `date` | NO | ? | MUL |
| `week_end` | `date` | NO | ? | ? |
| `total_study_seconds` | `int` | NO | 0 | ? |
| `valid_study_seconds` | `int` | NO | 0 | ? |
| `completed_tasks` | `int` | NO | 0 | ? |
| `average_quiz_score` | `decimal(5,2)` | YES | ? | ? |
| `report_data` | `json` | YES | ? | ? |
| `generated_at` | `datetime(3)` | NO | CURRENT_TIMESTAMP(3) | ? |

## Indexes

| Table | Index | Unique | Columns |
|---|---|---:|---|
| `achievements` | `PRIMARY` | No | `id` |
| `achievements` | `code` | No | `code` |
| `activity_logs` | `PRIMARY` | No | `id` |
| `activity_logs` | `fk_activity_device` | No | `device_id` |
| `activity_logs` | `idx_activity_application` | No | `application_id` |
| `activity_logs` | `idx_activity_session` | No | `session_id` |
| `activity_logs` | `idx_activity_started` | No | `started_at` |
| `activity_logs` | `idx_activity_student` | No | `student_id` |
| `ai_analyses` | `PRIMARY` | No | `id` |
| `ai_analyses` | `idx_ai_analyses_note` | No | `note_id` |
| `ai_analyses` | `idx_ai_analyses_status` | No | `status` |
| `application_policies` | `PRIMARY` | No | `id` |
| `application_policies` | `fk_app_policy_creator` | No | `created_by` |
| `application_policies` | `idx_app_policy_application` | No | `application_id` |
| `application_policies` | `idx_app_policy_device` | No | `device_id` |
| `applications` | `PRIMARY` | No | `id` |
| `applications` | `idx_applications_device` | No | `device_id` |
| `applications` | `idx_applications_name` | No | `application_name` |
| `audit_logs` | `PRIMARY` | No | `id` |
| `audit_logs` | `idx_audit_action` | No | `action` |
| `audit_logs` | `idx_audit_created` | No | `created_at` |
| `audit_logs` | `idx_audit_entity` | No | `entity_type,entity_id` |
| `audit_logs` | `idx_audit_user` | No | `user_id` |
| `daily_reports` | `PRIMARY` | No | `id` |
| `daily_reports` | `idx_daily_report_date` | No | `report_date` |
| `daily_reports` | `uq_daily_report` | No | `student_id,report_date` |
| `device_settings` | `PRIMARY` | No | `id` |
| `device_settings` | `uq_device_setting` | No | `device_id,setting_key` |
| `devices` | `PRIMARY` | No | `id` |
| `devices` | `device_identifier` | No | `device_identifier` |
| `devices` | `idx_devices_owner` | No | `owner_user_id` |
| `devices` | `idx_devices_status` | No | `agent_status` |
| `flashcard_reviews` | `PRIMARY` | No | `id` |
| `flashcard_reviews` | `idx_flashcard_reviews_card` | No | `flashcard_id` |
| `flashcard_reviews` | `idx_flashcard_reviews_student` | No | `student_id` |
| `flashcards` | `PRIMARY` | No | `id` |
| `flashcards` | `fk_flashcards_subject` | No | `subject_id` |
| `flashcards` | `idx_flashcards_student` | No | `student_id` |
| `flashcards` | `idx_flashcards_topic` | No | `topic_id` |
| `guardian_student_links` | `PRIMARY` | No | `id` |
| `guardian_student_links` | `uq_guardian_student` | No | `guardian_id,student_id` |
| `guardian_student_links` | `uq_student_guardian` | No | `student_id` |
| `knowledge_progress` | `PRIMARY` | No | `id` |
| `knowledge_progress` | `fk_knowledge_topic` | No | `topic_id` |
| `knowledge_progress` | `idx_knowledge_next_review` | No | `next_review_at` |
| `knowledge_progress` | `uq_student_topic` | No | `student_id,topic_id` |
| `learning_materials` | `PRIMARY` | No | `id` |
| `learning_materials` | `idx_material_subject` | No | `subject_id` |
| `learning_materials` | `idx_material_topic` | No | `topic_id` |
| `learning_materials` | `idx_material_uploader` | No | `uploaded_by` |
| `learning_notes` | `PRIMARY` | No | `id` |
| `learning_notes` | `idx_notes_schedule` | No | `schedule_id` |
| `learning_notes` | `idx_notes_student` | No | `student_id` |
| `learning_notes` | `idx_notes_subject` | No | `subject_id` |
| `learning_notes` | `idx_notes_topic` | No | `topic_id` |
| `learning_point_transactions` | `PRIMARY` | No | `id` |
| `learning_point_transactions` | `idx_points_created` | No | `created_at` |
| `learning_point_transactions` | `idx_points_user` | No | `user_id` |
| `learning_tasks` | `PRIMARY` | No | `id` |
| `learning_tasks` | `fk_tasks_creator` | No | `created_by` |
| `learning_tasks` | `fk_tasks_subject` | No | `subject_id` |
| `learning_tasks` | `idx_tasks_due` | No | `due_at` |
| `learning_tasks` | `idx_tasks_schedule` | No | `schedule_id` |
| `learning_tasks` | `idx_tasks_status` | No | `status` |
| `learning_tasks` | `idx_tasks_student` | No | `student_id` |
| `monitoring_events` | `PRIMARY` | No | `id` |
| `monitoring_events` | `fk_monitoring_session` | No | `session_id` |
| `monitoring_events` | `idx_monitoring_device` | No | `device_id` |
| `monitoring_events` | `idx_monitoring_occurred` | No | `occurred_at` |
| `monitoring_events` | `idx_monitoring_student` | No | `student_id` |
| `monitoring_events` | `idx_monitoring_type` | No | `event_type` |
| `note_attachments` | `PRIMARY` | No | `id` |
| `note_attachments` | `idx_note_attachments_note` | No | `note_id` |
| `notifications` | `PRIMARY` | No | `id` |
| `notifications` | `idx_notifications_created` | No | `created_at` |
| `notifications` | `idx_notifications_read` | No | `user_id,is_read` |
| `notifications` | `idx_notifications_user` | No | `user_id` |
| `presence_logs` | `PRIMARY` | No | `id` |
| `presence_logs` | `idx_presence_detected` | No | `detected_at` |
| `presence_logs` | `idx_presence_session` | No | `session_id` |
| `question_options` | `PRIMARY` | No | `id` |
| `question_options` | `idx_question_options_question` | No | `question_id` |
| `questions` | `PRIMARY` | No | `id` |
| `questions` | `idx_questions_quiz` | No | `quiz_id` |
| `questions` | `idx_questions_topic` | No | `topic_id` |
| `quiz_answers` | `PRIMARY` | No | `id` |
| `quiz_answers` | `fk_quiz_answers_option` | No | `selected_option_id` |
| `quiz_answers` | `idx_quiz_answers_question` | No | `question_id` |
| `quiz_answers` | `uq_attempt_question` | No | `attempt_id,question_id` |
| `quiz_attempts` | `PRIMARY` | No | `id` |
| `quiz_attempts` | `idx_quiz_attempts_quiz` | No | `quiz_id` |
| `quiz_attempts` | `idx_quiz_attempts_student` | No | `student_id` |
| `quiz_attempts` | `uq_quiz_attempt_number` | No | `quiz_id,student_id,attempt_number` |
| `quizzes` | `PRIMARY` | No | `id` |
| `quizzes` | `fk_quizzes_creator` | No | `created_by` |
| `quizzes` | `idx_quizzes_subject` | No | `subject_id` |
| `quizzes` | `idx_quizzes_task` | No | `task_id` |
| `review_schedules` | `PRIMARY` | No | `id` |
| `review_schedules` | `fk_review_flashcard` | No | `flashcard_id` |
| `review_schedules` | `fk_review_topic` | No | `topic_id` |
| `review_schedules` | `idx_review_next` | No | `next_review_at` |
| `review_schedules` | `idx_review_student` | No | `student_id` |
| `screenshots` | `PRIMARY` | No | `id` |
| `screenshots` | `idx_screenshots_captured` | No | `captured_at` |
| `screenshots` | `idx_screenshots_session` | No | `session_id` |
| `study_schedules` | `PRIMARY` | No | `id` |
| `study_schedules` | `fk_schedules_creator` | No | `created_by` |
| `study_schedules` | `idx_schedules_end` | No | `end_at` |
| `study_schedules` | `idx_schedules_start` | No | `start_at` |
| `study_schedules` | `idx_schedules_student` | No | `student_id` |
| `study_schedules` | `idx_schedules_subject` | No | `subject_id` |
| `study_sessions` | `PRIMARY` | No | `id` |
| `study_sessions` | `fk_sessions_device` | No | `device_id` |
| `study_sessions` | `idx_sessions_schedule` | No | `schedule_id` |
| `study_sessions` | `idx_sessions_started` | No | `started_at` |
| `study_sessions` | `idx_sessions_status` | No | `status` |
| `study_sessions` | `idx_sessions_student` | No | `student_id` |
| `subjects` | `PRIMARY` | No | `id` |
| `subjects` | `idx_subjects_student` | No | `student_id` |
| `system_settings` | `PRIMARY` | No | `id` |
| `system_settings` | `setting_key` | No | `setting_key` |
| `topics` | `PRIMARY` | No | `id` |
| `topics` | `idx_topics_parent` | No | `parent_topic_id` |
| `topics` | `idx_topics_subject` | No | `subject_id` |
| `user_achievements` | `PRIMARY` | No | `id` |
| `user_achievements` | `fk_user_achievements_achievement` | No | `achievement_id` |
| `user_achievements` | `uq_user_achievement` | No | `user_id,achievement_id` |
| `user_sessions` | `PRIMARY` | No | `id` |
| `user_sessions` | `idx_user_sessions_expiry` | No | `expires_at` |
| `user_sessions` | `idx_user_sessions_user` | No | `user_id` |
| `user_sessions` | `token_hash` | No | `token_hash` |
| `users` | `PRIMARY` | No | `id` |
| `users` | `email` | No | `email` |
| `users` | `idx_users_active` | No | `is_active` |
| `users` | `idx_users_role` | No | `role` |
| `users` | `username` | No | `username` |
| `website_policies` | `PRIMARY` | No | `id` |
| `website_policies` | `fk_website_policy_creator` | No | `created_by` |
| `website_policies` | `idx_website_policy_device` | No | `device_id` |
| `website_policies` | `idx_website_policy_domain` | No | `domain` |
| `weekly_reports` | `PRIMARY` | No | `id` |
| `weekly_reports` | `idx_weekly_report_period` | No | `week_start,week_end` |
| `weekly_reports` | `uq_weekly_report` | No | `student_id,week_start` |

## Foreign keys

| Table | Column | Constraint | Referenced table.column |
|---|---|---|---|
| `activity_logs` | `application_id` | `fk_activity_application` | `applications.id` |
| `activity_logs` | `device_id` | `fk_activity_device` | `devices.id` |
| `activity_logs` | `session_id` | `fk_activity_session` | `study_sessions.id` |
| `activity_logs` | `student_id` | `fk_activity_student` | `users.id` |
| `ai_analyses` | `note_id` | `fk_ai_analyses_note` | `learning_notes.id` |
| `application_policies` | `application_id` | `fk_app_policy_application` | `applications.id` |
| `application_policies` | `created_by` | `fk_app_policy_creator` | `users.id` |
| `application_policies` | `device_id` | `fk_app_policy_device` | `devices.id` |
| `applications` | `device_id` | `fk_applications_device` | `devices.id` |
| `audit_logs` | `user_id` | `fk_audit_user` | `users.id` |
| `daily_reports` | `student_id` | `fk_daily_report_student` | `users.id` |
| `device_settings` | `device_id` | `fk_device_settings_device` | `devices.id` |
| `devices` | `owner_user_id` | `fk_devices_owner` | `users.id` |
| `flashcard_reviews` | `flashcard_id` | `fk_flashcard_reviews_card` | `flashcards.id` |
| `flashcard_reviews` | `student_id` | `fk_flashcard_reviews_student` | `users.id` |
| `flashcards` | `student_id` | `fk_flashcards_student` | `users.id` |
| `flashcards` | `subject_id` | `fk_flashcards_subject` | `subjects.id` |
| `flashcards` | `topic_id` | `fk_flashcards_topic` | `topics.id` |
| `guardian_student_links` | `guardian_id` | `fk_link_guardian` | `users.id` |
| `guardian_student_links` | `student_id` | `fk_link_student` | `users.id` |
| `knowledge_progress` | `student_id` | `fk_knowledge_student` | `users.id` |
| `knowledge_progress` | `topic_id` | `fk_knowledge_topic` | `topics.id` |
| `learning_materials` | `subject_id` | `fk_material_subject` | `subjects.id` |
| `learning_materials` | `topic_id` | `fk_material_topic` | `topics.id` |
| `learning_materials` | `uploaded_by` | `fk_material_uploader` | `users.id` |
| `learning_notes` | `schedule_id` | `fk_notes_schedule` | `study_schedules.id` |
| `learning_notes` | `student_id` | `fk_notes_student` | `users.id` |
| `learning_notes` | `subject_id` | `fk_notes_subject` | `subjects.id` |
| `learning_notes` | `topic_id` | `fk_notes_topic` | `topics.id` |
| `learning_point_transactions` | `user_id` | `fk_points_user` | `users.id` |
| `learning_tasks` | `created_by` | `fk_tasks_creator` | `users.id` |
| `learning_tasks` | `schedule_id` | `fk_tasks_schedule` | `study_schedules.id` |
| `learning_tasks` | `student_id` | `fk_tasks_student` | `users.id` |
| `learning_tasks` | `subject_id` | `fk_tasks_subject` | `subjects.id` |
| `monitoring_events` | `device_id` | `fk_monitoring_device` | `devices.id` |
| `monitoring_events` | `session_id` | `fk_monitoring_session` | `study_sessions.id` |
| `monitoring_events` | `student_id` | `fk_monitoring_student` | `users.id` |
| `note_attachments` | `note_id` | `fk_note_attachments_note` | `learning_notes.id` |
| `notifications` | `user_id` | `fk_notifications_user` | `users.id` |
| `presence_logs` | `session_id` | `fk_presence_session` | `study_sessions.id` |
| `question_options` | `question_id` | `fk_question_options_question` | `questions.id` |
| `questions` | `quiz_id` | `fk_questions_quiz` | `quizzes.id` |
| `questions` | `topic_id` | `fk_questions_topic` | `topics.id` |
| `quiz_answers` | `attempt_id` | `fk_quiz_answers_attempt` | `quiz_attempts.id` |
| `quiz_answers` | `selected_option_id` | `fk_quiz_answers_option` | `question_options.id` |
| `quiz_answers` | `question_id` | `fk_quiz_answers_question` | `questions.id` |
| `quiz_attempts` | `quiz_id` | `fk_quiz_attempts_quiz` | `quizzes.id` |
| `quiz_attempts` | `student_id` | `fk_quiz_attempts_student` | `users.id` |
| `quizzes` | `created_by` | `fk_quizzes_creator` | `users.id` |
| `quizzes` | `subject_id` | `fk_quizzes_subject` | `subjects.id` |
| `quizzes` | `task_id` | `fk_quizzes_task` | `learning_tasks.id` |
| `review_schedules` | `flashcard_id` | `fk_review_flashcard` | `flashcards.id` |
| `review_schedules` | `student_id` | `fk_review_student` | `users.id` |
| `review_schedules` | `topic_id` | `fk_review_topic` | `topics.id` |
| `screenshots` | `session_id` | `fk_screenshots_session` | `study_sessions.id` |
| `study_schedules` | `created_by` | `fk_schedules_creator` | `users.id` |
| `study_schedules` | `student_id` | `fk_schedules_student` | `users.id` |
| `study_schedules` | `subject_id` | `fk_schedules_subject` | `subjects.id` |
| `study_sessions` | `device_id` | `fk_sessions_device` | `devices.id` |
| `study_sessions` | `schedule_id` | `fk_sessions_schedule` | `study_schedules.id` |
| `study_sessions` | `student_id` | `fk_sessions_student` | `users.id` |
| `subjects` | `student_id` | `fk_subjects_student` | `users.id` |
| `topics` | `parent_topic_id` | `fk_topics_parent` | `topics.id` |
| `topics` | `subject_id` | `fk_topics_subject` | `subjects.id` |
| `user_achievements` | `achievement_id` | `fk_user_achievements_achievement` | `achievements.id` |
| `user_achievements` | `user_id` | `fk_user_achievements_user` | `users.id` |
| `user_sessions` | `user_id` | `fk_user_sessions_user` | `users.id` |
| `website_policies` | `created_by` | `fk_website_policy_creator` | `users.id` |
| `website_policies` | `device_id` | `fk_website_policy_device` | `devices.id` |
| `weekly_reports` | `student_id` | `fk_weekly_report_student` | `users.id` |
