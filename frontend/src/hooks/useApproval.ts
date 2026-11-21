
import { useState, useCallback, useRef } from 'react';
import { api } from '../services/api';

import type { ApprovalState, Platform } from '../types';

interface UseApprovalReturn {
  approval: ApprovalState;
  approvalError: string | null;
  isSubmitting: boolean;
  approve: (
    contentId: string,
    platforms: Platform[]
  ) => Promise<void>;
  reject: () => void;
  reset: () => void;
}

const DEFAULT_STATE: ApprovalState = {
  status: 'pending',
  contentId: null,
  approvedPlatforms: [],
};

export function useApproval(): UseApprovalReturn {
  const [approval, setApproval] =
    useState<ApprovalState>(DEFAULT_STATE);

  const [approvalError, setApprovalError] =
    useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Prevent duplicate requests before React updates the UI.
  const submittingRef = useRef(false);

  // Ignore responses belonging to an older approval session.
  const sessionRef = useRef(0);

  const approve = useCallback(
    async (contentId: string, platforms: Platform[]) => {
      if (submittingRef.current) return;

      setApprovalError(null);

      if (!contentId || platforms.length === 0) {
        setApprovalError(
          'A content ID and at least one platform are required.'
        );
        return;
      }

      const session = sessionRef.current;

      submittingRef.current = true;
      setIsSubmitting(true);

      try {
        const response = await api.approve(
          contentId,
          platforms
        );

        if (session !== sessionRef.current) return;

        if (response.success !== true) {
          throw new Error(
            'The backend did not confirm approval.'
          );
        }

        setApproval({
          status: 'approved',
          contentId,
          approvedPlatforms: platforms,
        });

      } catch (err) {
        if (session !== sessionRef.current) return;

        console.error('Approval failed:', err);

        setApprovalError(
          err instanceof Error
            ? err.message
            : 'Unable to approve content. Please try again.'
        );

      } finally {
        // Never overwrite the state of a newer session.
        if (session === sessionRef.current) {
          submittingRef.current = false;
          setIsSubmitting(false);
        }
      }
    },
    []
  );

  const reject = useCallback(() => {
    if (submittingRef.current) return;

    sessionRef.current += 1;
    setApprovalError(null);

    setApproval((prev) => ({
      ...prev,
      status: 'rejected',
    }));
  }, []);

  const reset = useCallback(() => {
    // Invalidate any previous request's UI updates.
    sessionRef.current += 1;

    setApproval(DEFAULT_STATE);
    setApprovalError(null);

    // Keep the request lock until its original request settles.
    if (!submittingRef.current) {
      setIsSubmitting(false);
    }
  }, []);

  return {
    approval,
    approvalError,
    isSubmitting,
    approve,
    reject,
    reset,
  };
}
