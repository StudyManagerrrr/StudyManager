import type { Language } from '../i18n';

let apiLanguage: Language = 'vi';
let accessTokenUpdated: ((token: string) => void) | null = null;
let authFailure: (() => void) | null = null;
let refreshInFlight: Promise<{ access_token: string }> | null = null;
export function setApiLanguage(language: Language) { apiLanguage = language; }
export function setAccessTokenUpdated(callback: (token: string) => void) { accessTokenUpdated = callback; }
export function setAuthFailureHandler(callback: () => void) { authFailure = callback; }

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly status: number,
    public readonly requestId?: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export function parseApiError(payload: any, status: number, requestId?: string, path = ''): ApiError {
  const error = payload?.error;
  const legacy = payload?.detail;
  const code = error?.code || (
    status === 401 ? (path.endsWith('/auth/login') ? 'AUTH_INVALID_CREDENTIALS' : 'AUTH_UNAUTHORIZED') :
    status === 403 ? 'AUTH_FORBIDDEN' : status === 404 ? 'RESOURCE_NOT_FOUND' :
    status === 409 ? 'RESOURCE_CONFLICT' : status === 422 ? 'VALIDATION_INVALID_VALUE' :
    status === 429 ? 'RATE_LIMIT_EXCEEDED' : status === 503 ? 'DATABASE_UNAVAILABLE' :
    status === 504 ? 'AI_REQUEST_TIMEOUT' : status === 502 ? 'AI_GENERATION_FAILED' :
    status >= 500 ? 'INTERNAL_SERVER_ERROR' : 'UNKNOWN'
  );
  const message = error?.message || (typeof legacy === 'string' ? legacy : '');
  const details = error?.details ?? (Array.isArray(legacy) ? legacy : undefined);
  return new ApiError(message, code, status, error?.request_id || requestId, details);
}

function apiBase() { return import.meta.env.VITE_API_BASE_URL || '/api/v1'; }

async function request(path: string, token: string, options: RequestInit = {}) {
  try {
    const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
    return await fetch(apiBase() + path, {
      credentials: 'include', ...options,
      headers: {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }), 'Accept-Language': apiLanguage,
        ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers,
      },
    });
  } catch {
    throw new ApiError('', 'NETWORK_ERROR', 0);
  }
}

async function parseResponse(response: Response, path: string) {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw parseApiError(payload, response.status, response.headers.get('X-Request-ID') || undefined, path);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function refreshAccessToken() {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const response = await request('/auth/refresh', '', { method: 'POST' });
      return parseResponse(response, '/auth/refresh');
    })();
  }
  try { return await refreshInFlight; }
  finally { refreshInFlight = null; }
}

export async function api(path: string, token: string, options: RequestInit = {}) {
  let response = await request(path, token, options);
  if (response.status === 401 && !['/auth/login', '/auth/register', '/auth/refresh'].includes(path)) {
    try {
      const refreshed = await refreshAccessToken();
      accessTokenUpdated?.(refreshed.access_token);
      response = await request(path, refreshed.access_token, options);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) authFailure?.();
      throw error;
    }
    if (response.status === 401) authFailure?.();
  }
  return parseResponse(response, path);
}

export function localizedApiMessage(error: unknown, t: (key: string, values?: Record<string, string | number>) => string) {
  if (!(error instanceof ApiError)) return t('errors.UNKNOWN');
  const key = `errors.${error.code}`;
  let message = t(key);
  if (message === key) message = t('errors.UNKNOWN');
  if (error.code.startsWith('VALIDATION_') && Array.isArray(error.details) && error.details.length) {
    const detail = error.details[0] as { field?: string; code?: string };
    const fieldKey = detail.code === 'required' ? 'errors.VALIDATION_REQUIRED' :
      detail.code === 'format' ? 'errors.VALIDATION_INVALID_FORMAT' : key;
    message = t(fieldKey, { field: detail.field || '' });
  }
  if (error.requestId) message += ` (${t('errors.requestId', { id: error.requestId })})`;
  return message;
}
