"""Stable, localized API error envelopes for the current FastAPI routes."""

from __future__ import annotations

from typing import Any


ERROR_MESSAGES: dict[str, dict[str, str]] = {
    'AUTH_INVALID_CREDENTIALS': {'vi': 'Email hoặc mật khẩu không chính xác.', 'en': 'Invalid email or password.'},
    'AUTH_UNAUTHORIZED': {'vi': 'Vui lòng đăng nhập để tiếp tục.', 'en': 'Please sign in to continue.'},
    'AUTH_FORBIDDEN': {'vi': 'Bạn không có quyền thực hiện thao tác này.', 'en': 'You are not allowed to perform this action.'},
    'AUTH_TOKEN_EXPIRED': {'vi': 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'en': 'Your session has expired. Please sign in again.'},
    'AUTH_TOKEN_INVALID': {'vi': 'Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.', 'en': 'Your session is invalid. Please sign in again.'},
    'AUTH_TOKEN_REVOKED': {'vi': 'Phiên đăng nhập đã bị thu hồi. Vui lòng đăng nhập lại.', 'en': 'Your session was revoked. Please sign in again.'},
    'AUTH_REFRESH_FAILED': {'vi': 'Không thể khôi phục phiên đăng nhập. Vui lòng đăng nhập lại.', 'en': 'Could not restore your session. Please sign in again.'},
    'AUTH_ACCOUNT_DISABLED': {'vi': 'Tài khoản đã bị vô hiệu hóa.', 'en': 'This account is disabled.'},
    'AUTH_EMAIL_ALREADY_EXISTS': {'vi': 'Email hoặc tên đăng nhập đã được sử dụng.', 'en': 'This email or username is already in use.'},
    'AUTH_PASSWORD_TOO_WEAK': {'vi': 'Mật khẩu cần có từ 12 đến 128 ký tự.', 'en': 'Password must be 12 to 128 characters.'},
    'INVITATION_NOT_FOUND': {'vi': 'Không tìm thấy lời mời.', 'en': 'Invitation not found.'},
    'INVITATION_EXPIRED': {'vi': 'Lời mời đã hết hạn.', 'en': 'This invitation has expired.'},
    'INVITATION_ALREADY_USED': {'vi': 'Lời mời đã được sử dụng.', 'en': 'This invitation has already been used.'},
    'INVITATION_INVALID': {'vi': 'Lời mời không hợp lệ.', 'en': 'This invitation is invalid.'},
    'INVITATION_REJECTED': {'vi': 'Lời mời không thể được chấp nhận.', 'en': 'This invitation cannot be accepted.'},
    'VALIDATION_REQUIRED': {'vi': 'Vui lòng điền các trường bắt buộc.', 'en': 'Please complete the required fields.'},
    'VALIDATION_INVALID_FORMAT': {'vi': 'Định dạng chưa hợp lệ. Vui lòng kiểm tra và thử lại.', 'en': 'The format is invalid. Check it and try again.'},
    'VALIDATION_INVALID_VALUE': {'vi': 'Giá trị nhập chưa hợp lệ. Vui lòng kiểm tra lại.', 'en': 'The submitted value is invalid. Please check it.'},
    'VALIDATION_OUT_OF_RANGE': {'vi': 'Giá trị nằm ngoài phạm vi cho phép.', 'en': 'The value is outside the allowed range.'},
    'VALIDATION_DUPLICATE_VALUE': {'vi': 'Giá trị này đã tồn tại.', 'en': 'This value already exists.'},
    'SUBJECT_NOT_FOUND': {'vi': 'Không tìm thấy môn học.', 'en': 'Subject not found.'},
    'SUBJECT_ACCESS_DENIED': {'vi': 'Bạn không có quyền truy cập môn học này.', 'en': 'You do not have access to this subject.'},
    'SUBJECT_ALREADY_EXISTS': {'vi': 'Môn học này đã tồn tại.', 'en': 'This subject already exists.'},
    'TOPIC_NOT_FOUND': {'vi': 'Không tìm thấy chủ đề.', 'en': 'Topic not found.'},
    'TOPIC_ACCESS_DENIED': {'vi': 'Bạn không có quyền truy cập chủ đề này.', 'en': 'You do not have access to this topic.'},
    'SCHEDULE_CONFLICT': {'vi': 'Lịch học bị trùng với một lịch khác.', 'en': 'This schedule conflicts with another one.'},
    'SCHEDULE_INVALID_TIME': {'vi': 'Thời gian kết thúc phải sau thời gian bắt đầu.', 'en': 'End time must be later than start time.'},
    'TASK_NOT_FOUND': {'vi': 'Không tìm thấy nhiệm vụ.', 'en': 'Task not found.'},
    'TASK_ACCESS_DENIED': {'vi': 'Bạn không có quyền truy cập nhiệm vụ này.', 'en': 'You do not have access to this task.'},
    'TASK_ALREADY_COMPLETED': {'vi': 'Nhiệm vụ này đã hoàn thành.', 'en': 'This task has already been completed.'},
    'TASK_INVALID_STATUS': {'vi': 'Trạng thái nhiệm vụ không hợp lệ.', 'en': 'The task status is invalid.'},
    'ASSIGNMENT_NOT_FOUND': {'vi': 'Không tìm thấy bài tập.', 'en': 'Assignment not found.'},
    'ASSIGNMENT_ALREADY_SUBMITTED': {'vi': 'Bài tập này đã được nộp.', 'en': 'This assignment has already been submitted.'},
    'ASSIGNMENT_REVIEW_FAILED': {'vi': 'Không thể duyệt bài tập lúc này.', 'en': 'The assignment could not be reviewed.'},
    'ASSIGNMENT_INVALID_STATUS': {'vi': 'Trạng thái bài tập không hợp lệ.', 'en': 'The assignment status is invalid.'},
    'NOTE_NOT_FOUND': {'vi': 'Không tìm thấy ghi chú học tập.', 'en': 'Learning note not found.'},
    'NOTE_ACCESS_DENIED': {'vi': 'Bạn không có quyền truy cập ghi chú này.', 'en': 'You do not have access to this note.'},
    'NOTE_SUBMISSION_FAILED': {'vi': 'Không thể gửi ghi chú lúc này.', 'en': 'The note could not be submitted.'},
    'QUIZ_NOT_FOUND': {'vi': 'Không tìm thấy bài kiểm tra.', 'en': 'Quiz not found.'},
    'QUIZ_NOT_PUBLISHED': {'vi': 'Bài kiểm tra chưa được phát hành.', 'en': 'This quiz has not been published.'},
    'QUIZ_ATTEMPT_LIMIT_REACHED': {'vi': 'Bạn đã đạt giới hạn số lần làm bài.', 'en': 'You have reached the attempt limit.'},
    'QUIZ_ATTEMPT_NOT_FOUND': {'vi': 'Không tìm thấy lượt làm bài.', 'en': 'Quiz attempt not found.'},
    'QUIZ_INVALID_OPTION': {'vi': 'Lựa chọn trả lời không hợp lệ.', 'en': 'The selected answer is invalid.'},
    'QUIZ_ALREADY_SUBMITTED': {'vi': 'Bài kiểm tra này đã được nộp.', 'en': 'This quiz has already been submitted.'},
    'QUIZ_SCORING_FAILED': {'vi': 'Không thể chấm điểm bài kiểm tra.', 'en': 'The quiz could not be scored.'},
    'QUIZ_REVIEW_REQUIRED': {'vi': 'Bài kiểm tra cần được phụ huynh xem xét.', 'en': 'Guardian review is required for this quiz.'},
    'AI_PROVIDER_UNAVAILABLE': {'vi': 'Dịch vụ AI hiện không khả dụng.', 'en': 'The AI service is currently unavailable.'},
    'AI_REQUEST_TIMEOUT': {'vi': 'Yêu cầu AI đã hết thời gian chờ.', 'en': 'The AI request timed out.'},
    'AI_INVALID_RESPONSE': {'vi': 'Dịch vụ AI trả về kết quả không hợp lệ.', 'en': 'The AI service returned an invalid response.'},
    'AI_GENERATION_FAILED': {'vi': 'Không thể hoàn tất phân tích AI. Vui lòng thử lại sau.', 'en': 'AI analysis could not be completed. Try again later.'},
    'AI_CONFIGURATION_MISSING': {'vi': 'Dịch vụ AI chưa được cấu hình.', 'en': 'The AI service has not been configured.'},
    'AI_QUOTA_EXCEEDED': {'vi': 'Dịch vụ AI đã đạt giới hạn sử dụng.', 'en': 'The AI service has reached its usage limit.'},
    'DEVICE_NOT_FOUND': {'vi': 'Không tìm thấy thiết bị.', 'en': 'Device not found.'},
    'DEVICE_PAIRING_FAILED': {'vi': 'Không thể ghép nối thiết bị.', 'en': 'Device pairing failed.'},
    'DEVICE_REVOKED': {'vi': 'Thiết bị đã bị thu hồi quyền truy cập.', 'en': 'This device access has been revoked.'},
    'DEVICE_UNAUTHORIZED': {'vi': 'Thiết bị chưa được cấp quyền.', 'en': 'This device is not authorized.'},
    'DEVICE_SYNC_FAILED': {'vi': 'Không thể đồng bộ thiết bị.', 'en': 'Device synchronization failed.'},
    'DEVICE_POLICY_REJECTED': {'vi': 'Thiết bị từ chối chính sách này.', 'en': 'The device rejected this policy.'},
    'FILE_NOT_FOUND': {'vi': 'Không tìm thấy tệp.', 'en': 'File not found.'},
    'FILE_TOO_LARGE': {'vi': 'Tệp vượt quá dung lượng cho phép.', 'en': 'The file exceeds the allowed size.'},
    'FILE_TYPE_NOT_ALLOWED': {'vi': 'Định dạng tệp này chưa được hỗ trợ.', 'en': 'This file type is not supported.'},
    'FILE_UPLOAD_FAILED': {'vi': 'Không thể tải tệp lên.', 'en': 'The file could not be uploaded.'},
    'FILE_ACCESS_DENIED': {'vi': 'Bạn không có quyền truy cập tệp này.', 'en': 'You do not have access to this file.'},
    'RESOURCE_NOT_FOUND': {'vi': 'Không tìm thấy dữ liệu yêu cầu.', 'en': 'The requested item was not found.'},
    'RESOURCE_CONFLICT': {'vi': 'Thao tác bị xung đột với dữ liệu hiện tại.', 'en': 'This action conflicts with the current data.'},
    'RATE_LIMIT_EXCEEDED': {'vi': 'Bạn thao tác quá nhanh. Vui lòng thử lại sau.', 'en': 'You are doing that too often. Please try again later.'},
    'DATABASE_UNAVAILABLE': {'vi': 'Dịch vụ dữ liệu tạm thời không khả dụng.', 'en': 'The data service is temporarily unavailable.'},
    'INTERNAL_SERVER_ERROR': {'vi': 'Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.', 'en': 'An unexpected system error occurred. Please try again later.'},
    'NETWORK_ERROR': {'vi': 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng.', 'en': 'Unable to connect to the server. Check your network connection.'},
}


def preferred_language(request: Any) -> str:
    value = request.headers.get('accept-language', '').lower()
    return 'en' if value.startswith('en') else 'vi'


def message_for(code: str, language: str) -> str:
    return ERROR_MESSAGES.get(code, ERROR_MESSAGES['INTERNAL_SERVER_ERROR']).get(language, ERROR_MESSAGES['INTERNAL_SERVER_ERROR']['vi'])


def code_for_http(status: int, detail: Any) -> str:
    raw = detail.get('message', '') if isinstance(detail, dict) else str(detail or '')
    text = raw.lower()
    if status == 401:
        if 'username or password' in text: return 'AUTH_INVALID_CREDENTIALS'
        if 'reuse detected' in text or 'revok' in text: return 'AUTH_TOKEN_REVOKED'
        if 'refresh' in text: return 'AUTH_REFRESH_FAILED'
        if 'expired' in text: return 'AUTH_TOKEN_EXPIRED'
        if 'authentication required' in text: return 'AUTH_UNAUTHORIZED'
        return 'AUTH_TOKEN_INVALID'
    if status == 403: return 'AUTH_FORBIDDEN'
    if status == 404:
        if 'quiz attempt' in text: return 'QUIZ_ATTEMPT_NOT_FOUND'
        if 'quiz' in text: return 'QUIZ_NOT_FOUND'
        if 'note' in text: return 'NOTE_NOT_FOUND'
        if 'subject' in text: return 'SUBJECT_NOT_FOUND'
        if 'topic' in text: return 'TOPIC_NOT_FOUND'
        if 'task' in text: return 'TASK_NOT_FOUND'
        return 'RESOURCE_NOT_FOUND'
    if status == 409:
        if 'already exists' in text or 'already in use' in text: return 'AUTH_EMAIL_ALREADY_EXISTS'
        if 'attempt limit' in text: return 'QUIZ_ATTEMPT_LIMIT_REACHED'
        if 'already been submitted' in text: return 'QUIZ_ALREADY_SUBMITTED'
        return 'RESOURCE_CONFLICT'
    if status == 422:
        if 'password' in text: return 'AUTH_PASSWORD_TOO_WEAK'
        if 'end_at' in text or 'start_at' in text: return 'SCHEDULE_INVALID_TIME'
        if 'option' in text: return 'QUIZ_INVALID_OPTION'
        if 'format' in text or 'valid email' in text: return 'VALIDATION_INVALID_FORMAT'
        return 'VALIDATION_INVALID_VALUE'
    if status == 429: return 'RATE_LIMIT_EXCEEDED'
    if status in {502, 504}:
        if status == 504: return 'AI_REQUEST_TIMEOUT'
        return 'AI_GENERATION_FAILED'
    if status == 503:
        if 'configure ai' in text or 'ai_api_key' in text: return 'AI_CONFIGURATION_MISSING'
        if 'ai' in text: return 'AI_PROVIDER_UNAVAILABLE'
        return 'DATABASE_UNAVAILABLE'
    if status == 404: return 'RESOURCE_NOT_FOUND'
    return 'INTERNAL_SERVER_ERROR' if status >= 500 else 'RESOURCE_CONFLICT'
