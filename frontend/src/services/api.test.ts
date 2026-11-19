import { describe, expect, it } from 'vitest';
import { ApiError, localizedApiMessage, parseApiError } from './api';
import vi from '../locales/vi';
import en from '../locales/en';

const translate = (language: 'vi' | 'en') => (key: string, values?: Record<string, string | number>) => {
  let message = (language === 'vi' ? vi : en)[key] || key;
  for (const [name, value] of Object.entries(values || {})) message = message.replace(`{{${name}}}`, String(value));
  return message;
};

describe('central API error handling', () => {
  it('reads the unified contract, request ID, code and safe details', () => {
    const error = parseApiError({ success: false, error: {
      code: 'AUTH_INVALID_CREDENTIALS', message: 'localized server message',
      details: null, request_id: 'request-123',
    } }, 401, 'header-id');
    expect(error).toBeInstanceOf(ApiError);
    expect(error.code).toBe('AUTH_INVALID_CREDENTIALS');
    expect(error.requestId).toBe('request-123');
    expect(localizedApiMessage(error, translate('vi'))).toContain('Email hoặc mật khẩu');
    expect(localizedApiMessage(error, translate('en'))).toContain('Invalid email or password');
  });

  it('maps legacy responses and validation details without exposing raw exceptions', () => {
    const error = parseApiError({ detail: [{ loc: ['body', 'email'], msg: 'bad email', input: 'secret' }] }, 422);
    expect(error.code).toBe('VALIDATION_INVALID_VALUE');
    expect(localizedApiMessage(error, translate('vi'))).not.toContain('secret');
    const unknown = parseApiError({ error: { code: 'INTERNAL_SERVER_ERROR', request_id: 'req-2' } }, 500);
    expect(localizedApiMessage(unknown, translate('en'))).toContain('unexpected system error');
    expect(localizedApiMessage(new Error('database password leaked?'), translate('en'))).toContain('Something went wrong');
  });

  it('uses stable endpoint-aware fallback codes for older servers', () => {
    expect(parseApiError({ detail: 'Invalid username or password' }, 401, undefined, '/auth/login').code).toBe('AUTH_INVALID_CREDENTIALS');
    expect(parseApiError({ detail: 'failure' }, 429).code).toBe('RATE_LIMIT_EXCEEDED');
    expect(parseApiError({ detail: 'failure' }, 503).code).toBe('DATABASE_UNAVAILABLE');
  });
});
