import type { GenerateRequest, GenerateResponse } from '../types';

const BASE_URL = (import.meta as any).env?.VITE_API_URL ?? '';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail ?? `Request failed (${response.status})`);
  }

  return response.json();
}

export const api = {
  generate: (payload: GenerateRequest): Promise<GenerateResponse> =>
    request('/api/generate', { method: 'POST', body: JSON.stringify(payload) }),

  approve: (contentId: string, platforms: string[]): Promise<{ success: boolean }> =>
    request('/api/approve', { method: 'POST', body: JSON.stringify({ content_id: contentId, platforms }) }),

  health: (): Promise<{ status: string }> =>
    request('/api/health'),
};