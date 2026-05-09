import type { GenerateResponse, Platform, ApprovalState } from '../types';

interface Props {
  data: GenerateResponse;
  approval: ApprovalState;
  isSubmitting: boolean;
  onApprove: (contentId: string, platforms: Platform[]) => void;
  onReject: () => void;
  onRegenerate: () => void;
}

export function ApprovalWorkflow({ data, approval, isSubmitting, onApprove, onReject, onRegenerate }: Props) {
  const allPlatforms = data.platforms.map(p => p.platform);

  if (approval.status === 'approved') {
    return (
      <div className="approval-status approval-status--approved" role="status">
        <span className="status-icon">✓</span>
        <div>
          <p className="status-title">Content approved and queued</p>
          <p className="status-sub">n8n automation triggered — Slack notified, Google Doc created, CMS scheduled.</p>
        </div>
      </div>
    );
  }

  if (approval.status === 'rejected') {
    return (
      <div className="approval-status approval-status--rejected" role="status">
        <p className="status-title">Content rejected.</p>
        <button className="btn-primary" onClick={onRegenerate}>Regenerate</button>
      </div>
    );
  }

  return (
    <div className="approval-workflow">
      <p className="approval-hint">Review the content above, then approve to trigger the automation pipeline.</p>
      <div className="approval-actions">
        <button className="btn-primary" onClick={() => onApprove(data.id, allPlatforms)} disabled={isSubmitting}>
          {isSubmitting ? 'Approving…' : 'Approve & publish'}
        </button>
        <button className="btn-secondary" onClick={onRegenerate}>Regenerate</button>
        <button className="btn-danger" onClick={onReject}>Reject</button>
      </div>
    </div>
  );
}