# Error code catalog

Codes are stable API identifiers. The canonical localized values are in `backend/app/errors.py`. Routes emit a code only when the corresponding condition is implemented.

| Error code | HTTP | Vietnamese | English | Cause | Resolution |
|---|---:|---|---|---|---|
| `AUTH_INVALID_CREDENTIALS` | 401 | Email hoặc mật khẩu không chính xác. | Invalid email or password. | Credentials are invalid. | Re-enter credentials or sign in again. |
| `AUTH_UNAUTHORIZED` | 401 | Vui lòng đăng nhập để tiếp tục. | Please sign in to continue. | Authentication is missing or invalid. | Sign in and retry. |
| `AUTH_FORBIDDEN` | 403 | Bạn không có quyền thực hiện thao tác này. | You are not allowed to perform this action. | The account role cannot perform the action. | Switch to an authorized account or contact the Guardian. |
| `AUTH_TOKEN_EXPIRED` | 401 | Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại. | Your session has expired. Please sign in again. | Access token is expired. | Refresh the session or sign in again. |
| `AUTH_TOKEN_INVALID` | 401 | Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại. | Your session is invalid. Please sign in again. | Access or refresh token is malformed or revoked. | Sign in again. |
| `AUTH_TOKEN_REVOKED` | 401 | Phiên đăng nhập đã bị thu hồi. Vui lòng đăng nhập lại. | Your session was revoked. Please sign in again. | Refresh-token reuse or explicit revocation occurred. | Sign in again. |
| `AUTH_REFRESH_FAILED` | 401 | Không thể khôi phục phiên đăng nhập. Vui lòng đăng nhập lại. | Could not restore your session. Please sign in again. | Refresh session is missing or invalid. | Sign in again. |
| `AUTH_ACCOUNT_DISABLED` | 403 | Tài khoản đã bị vô hiệu hóa. | This account is disabled. | The account is inactive. | Contact an administrator or Guardian. |
| `AUTH_EMAIL_ALREADY_EXISTS` | 409 | Email hoặc tên đăng nhập đã được sử dụng. | This email or username is already in use. | Identity is duplicated. | Use a different email or username. |
| `AUTH_PASSWORD_TOO_WEAK` | 422 | Mật khẩu cần có từ 12 đến 128 ký tự. | Password must be 12 to 128 characters. | Password length is invalid. | Enter a 12–128 character password. |
| `INVITATION_NOT_FOUND` | 404 | Không tìm thấy lời mời. | Invitation not found. | Invitation does not exist or is outside scope. | Request a valid invitation. |
| `INVITATION_EXPIRED` | 410 | Lời mời đã hết hạn. | This invitation has expired. | Invitation deadline passed. | Ask for a new invitation. |
| `INVITATION_ALREADY_USED` | 409 | Lời mời đã được sử dụng. | This invitation has already been used. | Invitation was consumed. | Ask for a new invitation. |
| `INVITATION_INVALID` | 422 | Lời mời không hợp lệ. | This invitation is invalid. | Invitation value or state is invalid. | Verify the invitation link or code. |
| `INVITATION_REJECTED` | 403 | Lời mời không thể được chấp nhận. | This invitation cannot be accepted. | The invitation is not acceptable by policy. | Contact the Guardian. |
| `VALIDATION_REQUIRED` | 422 | Vui lòng điền các trường bắt buộc. | Please complete the required fields. | A required field is missing. | Complete fields listed in `details`. |
| `VALIDATION_INVALID_FORMAT` | 422 | Định dạng chưa hợp lệ. Vui lòng kiểm tra và thử lại. | The format is invalid. Check it and try again. | Submitted data is malformed. | Correct the format and resubmit. |
| `VALIDATION_INVALID_VALUE` | 422 | Giá trị nhập chưa hợp lệ. Vui lòng kiểm tra lại. | The submitted value is invalid. Please check it. | Submitted data is semantically invalid. | Review the field value and resubmit. |
| `VALIDATION_OUT_OF_RANGE` | 422 | Giá trị nằm ngoài phạm vi cho phép. | The value is outside the allowed range. | Data is below or above its allowed bounds. | Enter a value within the allowed range. |
| `VALIDATION_DUPLICATE_VALUE` | 409 | Giá trị này đã tồn tại. | This value already exists. | A unique value is reused. | Change the value and resubmit. |
| `SUBJECT_NOT_FOUND` | 404 | Không tìm thấy môn học. | Subject not found. | Subject is missing or outside account scope. | Select an accessible subject. |
| `SUBJECT_ACCESS_DENIED` | 403 | Bạn không có quyền truy cập môn học này. | You do not have access to this subject. | Account is not linked to the subject. | Contact the family Guardian. |
| `SUBJECT_ALREADY_EXISTS` | 409 | Môn học này đã tồn tại. | This subject already exists. | Duplicate subject name or record exists. | Choose another name or update the existing record. |
| `TOPIC_NOT_FOUND` | 404 | Không tìm thấy chủ đề. | Topic not found. | Topic is missing or outside scope. | Select an accessible topic. |
| `TOPIC_ACCESS_DENIED` | 403 | Bạn không có quyền truy cập chủ đề này. | You do not have access to this topic. | Account cannot access the topic. | Contact the family Guardian. |
| `SCHEDULE_NOT_FOUND` | 404 | Không tìm thấy lịch học. | Schedule not found. | Schedule is missing or outside scope. | Refresh and select an accessible schedule. |
| `SCHEDULE_CONFLICT` | 409 | Lịch học bị trùng với một lịch khác. | This schedule conflicts with another one. | Time blocks overlap. | Change the start or end time. |
| `SCHEDULE_INVALID_TIME` | 422 | Thời gian kết thúc phải sau thời gian bắt đầu. | End time must be later than start time. | Start/end ordering is invalid. | Correct the time range. |
| `TASK_NOT_FOUND` | 404 | Không tìm thấy nhiệm vụ. | Task not found. | Task is missing or outside scope. | Refresh and select an accessible task. |
| `TASK_ACCESS_DENIED` | 403 | Bạn không có quyền truy cập nhiệm vụ này. | You do not have access to this task. | Account cannot access the task. | Contact the family Guardian. |
| `TASK_ALREADY_COMPLETED` | 409 | Nhiệm vụ này đã hoàn thành. | This task has already been completed. | Transition repeats a completed state. | Refresh the task state. |
| `TASK_INVALID_STATUS` | 422 | Trạng thái nhiệm vụ không hợp lệ. | The task status is invalid. | Status value or transition is unsupported. | Use a supported task status. |
| `ASSIGNMENT_NOT_FOUND` | 404 | Không tìm thấy bài tập. | Assignment not found. | Assignment is missing or outside scope. | Refresh and select an accessible assignment. |
| `ASSIGNMENT_ALREADY_SUBMITTED` | 409 | Bài tập này đã được nộp. | This assignment has already been submitted. | Submission is duplicated. | Refresh the assignment state. |
| `ASSIGNMENT_REVIEW_FAILED` | 500 | Không thể duyệt bài tập lúc này. | The assignment could not be reviewed. | Review processing failed. | Retry later. |
| `ASSIGNMENT_INVALID_STATUS` | 422 | Trạng thái bài tập không hợp lệ. | The assignment status is invalid. | Status value or transition is unsupported. | Use a supported assignment status. |
| `NOTE_NOT_FOUND` | 404 | Không tìm thấy ghi chú học tập. | Learning note not found. | Note is missing or outside scope. | Refresh and select an accessible note. |
| `NOTE_ACCESS_DENIED` | 403 | Bạn không có quyền truy cập ghi chú này. | You do not have access to this note. | Account cannot access the note. | Contact the family Guardian. |
| `NOTE_SUBMISSION_FAILED` | 500 | Không thể gửi ghi chú lúc này. | The note could not be submitted. | Submission processing failed. | Retry later. |
| `QUIZ_NOT_FOUND` | 404 | Không tìm thấy bài kiểm tra. | Quiz not found. | Quiz is missing or inaccessible. | Refresh and select an accessible quiz. |
| `QUIZ_NOT_PUBLISHED` | 409 | Bài kiểm tra chưa được phát hành. | This quiz has not been published. | Quiz is still draft or rejected. | Ask a Guardian to publish it. |
| `QUIZ_ATTEMPT_LIMIT_REACHED` | 409 | Bạn đã đạt giới hạn số lần làm bài. | You have reached the attempt limit. | Maximum attempts were consumed. | Stop retries and request Guardian review. |
| `QUIZ_ATTEMPT_NOT_FOUND` | 404 | Không tìm thấy lượt làm bài. | Quiz attempt not found. | Attempt is missing or outside scope. | Start a new accessible attempt. |
| `QUIZ_INVALID_OPTION` | 422 | Lựa chọn trả lời không hợp lệ. | The selected answer is invalid. | Option is unknown or belongs to another question. | Select a listed answer for the question. |
| `QUIZ_ALREADY_SUBMITTED` | 409 | Bài kiểm tra này đã được nộp. | This quiz has already been submitted. | Attempt was submitted before. | View the existing result. |
| `QUIZ_SCORING_FAILED` | 500 | Không thể chấm điểm bài kiểm tra. | The quiz could not be scored. | Scoring processing failed. | Retry after the system is available. |
| `QUIZ_REVIEW_REQUIRED` | 403 | Bài kiểm tra cần được phụ huynh xem xét. | Guardian review is required for this quiz. | AI-generated or objective policy requires review. | Ask a Guardian to review it. |
| `AI_PROVIDER_UNAVAILABLE` | 503 | Dịch vụ AI hiện không khả dụng. | The AI service is currently unavailable. | Provider is offline or rejected the service. | Retry later or configure the provider. |
| `AI_REQUEST_TIMEOUT` | 504 | Yêu cầu AI đã hết thời gian chờ. | The AI request timed out. | Provider did not respond in time. | Retry with a smaller request. |
| `AI_INVALID_RESPONSE` | 502 | Dịch vụ AI trả về kết quả không hợp lệ. | The AI service returned an invalid response. | Provider response failed validation. | Retry or review provider configuration. |
| `AI_GENERATION_FAILED` | 502 | Không thể hoàn tất phân tích AI. Vui lòng thử lại sau. | AI analysis could not be completed. Try again later. | Analysis generation failed. | Retry later. |
| `AI_CONFIGURATION_MISSING` | 503 | Dịch vụ AI chưa được cấu hình. | The AI service has not been configured. | Server provider settings are absent. | Configure provider, model, and credentials server-side. |
| `AI_QUOTA_EXCEEDED` | 429 | Dịch vụ AI đã đạt giới hạn sử dụng. | The AI service has reached its usage limit. | Provider quota is exhausted. | Retry after quota/reset or change provider plan. |
| `DEVICE_NOT_FOUND` | 404 | Không tìm thấy thiết bị. | Device not found. | Device is missing or outside scope. | Pair or select an authorized device. |
| `DEVICE_PAIRING_FAILED` | 500 | Không thể ghép nối thiết bị. | Device pairing failed. | Pairing exchange failed. | Retry pairing. |
| `DEVICE_REVOKED` | 401 | Thiết bị đã bị thu hồi quyền truy cập. | This device access has been revoked. | Device authorization was revoked. | Pair the device again if authorized. |
| `DEVICE_UNAUTHORIZED` | 401 | Thiết bị chưa được cấp quyền. | This device is not authorized. | Device is unknown or unpaired. | Complete device authorization. |
| `DEVICE_SYNC_FAILED` | 502 | Không thể đồng bộ thiết bị. | Device synchronization failed. | Agent or sync transport failed. | Retry synchronization. |
| `DEVICE_POLICY_REJECTED` | 403 | Thiết bị từ chối chính sách này. | The device rejected this policy. | Device policy validation failed. | Review policy and approved device settings. |
| `FILE_NOT_FOUND` | 404 | Không tìm thấy tệp. | File not found. | File is missing or expired. | Upload or select the file again. |
| `FILE_TOO_LARGE` | 413 | Tệp vượt quá dung lượng cho phép. | The file exceeds the allowed size. | File is over the limit. | Reduce file size and retry. |
| `FILE_TYPE_NOT_ALLOWED` | 415 | Định dạng tệp này chưa được hỗ trợ. | This file type is not supported. | MIME or extension is rejected. | Use an allowed file format. |
| `FILE_UPLOAD_FAILED` | 500 | Không thể tải tệp lên. | The file could not be uploaded. | Storage or transfer failed. | Retry upload. |
| `FILE_ACCESS_DENIED` | 403 | Bạn không có quyền truy cập tệp này. | You do not have access to this file. | Account is outside file scope. | Contact the file owner or Guardian. |
| `RESOURCE_NOT_FOUND` | 404 | Không tìm thấy dữ liệu yêu cầu. | The requested item was not found. | Generic resource is missing. | Verify the identifier and retry. |
| `RESOURCE_CONFLICT` | 409 | Thao tác bị xung đột với dữ liệu hiện tại. | This action conflicts with the current data. | Current state prevents the operation. | Refresh and retry. |
| `RATE_LIMIT_EXCEEDED` | 429 | Bạn thao tác quá nhanh. Vui lòng thử lại sau. | You are doing that too often. Please try again later. | Request or auth attempt limit was exceeded. | Wait until the limit window expires. |
| `DATABASE_UNAVAILABLE` | 503 | Dịch vụ dữ liệu tạm thời không khả dụng. | The data service is temporarily unavailable. | Database connection or operation failed. | Retry later; do not expose database details. |
| `INTERNAL_SERVER_ERROR` | 500 | Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau. | An unexpected system error occurred. Please try again later. | An unexpected server exception occurred. | Retry later and use `request_id` for diagnostics. |
| `NETWORK_ERROR` | 0 | Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng. | Unable to connect to the server. Check your network connection. | The browser could not reach the API. | Check network connectivity and retry. |
