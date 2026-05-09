import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { ApprovalState, Platform } from '../types';

interface UseApprovalReturn {
  approval: ApprovalState;
  isSubmitting: boolean;
  approve: (contentId: string, platforms: Platform[]) => Promise<void>;
  reject: () => void;
  reset: () => void;
}

const DEFAULT_STATE: ApprovalState = {
  status: 'pending',
  contentId: null,
  approvedPlatforms: [],
};

export function useApproval(): UseApprovalReturn {
  const [approval, setApproval] = useState<ApprovalState>(DEFAULT_STATE);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const approve = useCallback(async (contentId: string, platforms: Platform[]) => {
    setIsSubmitting(true);
    try {
      await api.approve(contentId, platforms);
      setApproval({ status: 'approved', contentId, approvedPlatforms: platforms });
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  const reject = useCallback(() => {
    setApproval(prev => ({ ...prev, status: 'rejected' }));
  }, []);

  const reset = useCallback(() => setApproval(DEFAULT_STATE), []);

  return { approval, isSubmitting, approve, reject, reset };
}