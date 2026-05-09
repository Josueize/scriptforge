import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { GenerateRequest, GenerateResponse, Status } from '../types';

interface UseGenerateReturn {
  status: Status;
  data: GenerateResponse | null;
  error: string | null;
  generate: (payload: GenerateRequest) => Promise<void>;
  reset: () => void;
}

export function useGenerate(): UseGenerateReturn {
  const [status, setStatus] = useState<Status>('idle');
  const [data, setData] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generate = useCallback(async (payload: GenerateRequest) => {
    setStatus('loading');
    setError(null);
    setData(null);

    try {
      const result = await api.generate(payload);
      setData(result);
      setStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
      setStatus('error');
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setData(null);
    setError(null);
  }, []);

  return { status, data, error, generate, reset };
}