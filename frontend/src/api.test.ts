// @vitest-environment jsdom
import { describe, expect, it } from 'vitest';
import { ApiError, localizedApiMessage, parseApiError } from './services/api';

describe('centralized API error handling', () => {
  it('preserves the stable code and request ID from the response envelope', () => {
    const error = parseApiError({
      success: false,
      error: {
        code: 'AUTH_INVALID_CREDENTIALS',
        message: 'Invalid email or password.',
        details: null,
        request_id: 'request-123',
      },
    }, 401);

    expect(error).toBeInstanceOf(ApiError);
    expect(error.code).toBe('AUTH_INVALID_CREDENTIALS');
    expect(error.status).toBe(401);
    expect(error.requestId).toBe('request-123');
  });

  it('maps unknown codes to a generic localized fallback', () => {
    const t = (key: string) => ({
      'errors.UNKNOWN': 'An unknown error occurred.',
      'errors.requestId': 'Request ID: {{id}}',
    } as Record<string, string>)[key] || key;
    const error = new ApiError('', 'NOT_A_REAL_CODE', 500, 'request-456');
    expect(localizedApiMessage(error, t)).toContain('An unknown error occurred.');
  });

  it('derives legacy status codes without exposing raw backend text', () => {
    const error = parseApiError({ detail: 'database password and SQL statement' }, 503);
    expect(error.code).toBe('DATABASE_UNAVAILABLE');
  });
});
