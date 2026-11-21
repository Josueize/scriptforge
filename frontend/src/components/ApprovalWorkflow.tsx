
import type {
  GenerateResponse,
  Platform,
  ApprovalState,
} from '../types';

interface Props {
  data: GenerateResponse;
  approval: ApprovalState;
  approvalError: string | null;
  isSubmitting: boolean;
  onApprove: (contentId: string, platforms: Platform[]) => void;
  onReject: () => void;
  onRegenerate: () => void;
}

export function ApprovalWorkflow({
  data,
  approval,
  approvalError,
  isSubmitting,
  onApprove,
  onReject,
  onRegenerate,
}: Props) {
  const allPlatforms = data.platforms.map(
    (platform) => platform.platform
  );

  if (approval.status === 'approved') {
    return (
      <div
        className="approval-status approval-status--approved"
        role="status"
        aria-live="polite"
      >
        <span className="status-icon" aria-hidden="true">
          {'\u2713'}
        </span>

        <div>
          <p className="status-title">
            Content approved successfully!
          </p>

          <p className="status-sub">
            Your content has been sent to n8n, and the
            Google Docs automation has been triggered.
          </p>
        </div>
      </div>
    );
  }

  if (approval.status === 'rejected') {
    return (
      <div
        className="approval-status approval-status--rejected"
        role="status"
      >
        <p className="status-title">
          Content rejected.
        </p>

        <button
          type="button"
          className="btn-primary"
          onClick={onRegenerate}
          disabled={isSubmitting}
        >
          Regenerate
        </button>
      </div>
    );
  }

  return (
    <div className="approval-workflow">
      <p className="approval-hint">
        Review the content above, then approve to
        trigger the automation pipeline.
      </p>

      <div className="approval-actions">
        <button
          type="button"
          className="btn-primary"
          onClick={() => onApprove(data.id, allPlatforms)}
          disabled={isSubmitting || allPlatforms.length === 0}
        >
          {isSubmitting ? 'Approving...' : 'Approve & send'}
        </button>

        <button
          type="button"
          className="btn-secondary"
          onClick={onRegenerate}
          disabled={isSubmitting}
        >
          Regenerate
        </button>

        <button
          type="button"
          className="btn-danger"
          onClick={onReject}
          disabled={isSubmitting}
        >
          Reject
        </button>
      </div>

      {approvalError && (
        <div className="error-state" role="alert">
          <p className="error-title">
            Approval failed
          </p>

          <p className="error-message">
            {approvalError}
          </p>
        </div>
      )}
    </div>
  );
}
