import { useState } from 'react';
import type { GenerateResponse, Platform } from '../types';
import { PlatformSelector } from './PlatformSelector';

interface Props {
  data: GenerateResponse;
}

export function ContentPreview({ data }: Props) {
  const [activePlatform, setActivePlatform] = useState<Platform>(
    data.platforms[0]?.platform ?? 'youtube'
  );
  const [copied, setCopied] = useState(false);

  const activeContent = data.platforms.find(p => p.platform === activePlatform);

  const copyToClipboard = async () => {
    if (!activeContent) return;
    try {
      await navigator.clipboard.writeText(activeContent.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard unavailable */ }
  };

  return (
    <section className="content-preview" aria-label="Generated content">
      <div className="preview-header">
        <div className="preview-meta">
          <span className="badge badge--tone">{data.metadata.tone}</span>
          <span className="badge">{data.metadata.length} min</span>
          <span className="badge badge--muted">{data.metadata.tokensUsed} tokens</span>
        </div>
        <button className="btn-secondary" onClick={copyToClipboard}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <PlatformSelector
        platforms={data.platforms}
        activePlatform={activePlatform}
        onSelect={setActivePlatform}
      />
      <div className="preview-body" aria-live="polite">
        <pre className="script-text">{activeContent?.content}</pre>
      </div>
    </section>
  );
}