
import type {
  GenerateRequest,
  GenerateResponse,
} from '../types';

// -----------------------------------------
// API configuration
// -----------------------------------------

const BASE_URL = (
  import.meta.env.VITE_API_URL ?? ''
).replace(/\/$/, '');

// -----------------------------------------
// API error handling
// -----------------------------------------

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// -----------------------------------------
// Authentication types
// -----------------------------------------

export interface AuthSession {
  authenticated: boolean;
  username: string;
  csrf_token: string;
}

export interface ApprovalResponse {
  success: boolean;
  message?: string;
}

// Keep the CSRF token in application memory.
// Never store administrator JWTs in localStorage.
let csrfToken: string | null = null;

// -----------------------------------------
// Centralized API request
// -----------------------------------------

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const method = (options.method ?? 'GET').toUpperCase();

  if (
    csrfToken &&
    !['GET', 'HEAD', 'OPTIONS'].includes(method)
  ) {
    headers.set('X-CSRF-Token', csrfToken);
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({}));

    const message =
      typeof body.detail === 'string'
        ? body.detail
        : `Request failed (${response.status})`;

    if (response.status === 401) {
      csrfToken = null;
    }

    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

// -----------------------------------------
// ScriptForge API
// -----------------------------------------

export const api = {
  // Administrator login
  login: async (
    username: string,
    password: string,
  ): Promise<AuthSession> => {
    const session = await request<AuthSession>(
      '/api/auth/login',
      {
        method: 'POST',
        body: JSON.stringify({
          username,
          password,
        }),
      },
    );

    csrfToken = session.csrf_token;

    return session;
  },

  // Restore administrator session
  me: async (): Promise<AuthSession> => {
    const session = await request<AuthSession>(
      '/api/auth/me',
    );

    csrfToken = session.csrf_token;

    return session;
  },

  // Administrator logout
  logout: async (): Promise<void> => {
    try {
      await request<{ success: boolean }>(
        '/api/auth/logout',
        {
          method: 'POST',
        },
      );
    } finally {
      csrfToken = null;
    }
  },

  // Generate AI content
  generate: (
    payload: GenerateRequest,
  ): Promise<GenerateResponse> =>
    request('/api/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Approve generated content
  approve: async (
    contentId: string,
    platforms: string[],
  ): Promise<ApprovalResponse> => {
    if (!csrfToken) {
      await api.me();
    }

    return request('/api/approve', {
      method: 'POST',
      body: JSON.stringify({
        content_id: contentId,
        platforms,
      }),
    });
  },

  // Backend health check
  health: (): Promise<{ status: string }> =>
    request('/api/health'),
};
