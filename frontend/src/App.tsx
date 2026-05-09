import { useState } from 'react';
import { PromptForm } from './components/PromptForm';
import { ContentPreview } from './components/ContentPreview';
import { ApprovalWorkflow } from './components/ApprovalWorkflow';
import { RegenerateOptions } from './components/RegenerateOptions';
import { useGenerate } from './hooks/useGenerate';
import { useApproval } from './hooks/useApproval';
import type { GenerateRequest, Tone } from './types';
import './App.css';

export default function App() {
  const { status, data, error, generate, reset: resetGenerate } = useGenerate();
  const { approval, isSubmitting, approve, reject, reset: resetApproval } = useApproval();
  const [lastRequest, setLastRequest] = useState<GenerateRequest | null>(null);

  const handleGenerate = (payload: GenerateRequest) => {
    setLastRequest(payload);
    resetApproval();
    generate(payload);
  };

  const handleRegenerate = () => {
    if (!lastRequest) return;
    resetGenerate();
    resetApproval();
    generate(lastRequest);
  };

  const handleToneChange = (tone: Tone) => {
    if (!lastRequest) return;
    const updated = { ...lastRequest, tone };
    setLastRequest(updated);
    resetGenerate();
    resetApproval();
    generate(updated);
  };

  const isLoading = status === 'loading';

  return (
    <div className="app">
      <header className="site-header">
        <div className="wordmark">ScriptForge</div>
        <h1 className="headline">One idea. <em>Every platform.</em></h1>
        <p className="subline">AI-powered content generation for the Blue Foxes creative team.</p>
      </header>

      <main className="main-layout">
        <aside className="sidebar">
          <PromptForm onSubmit={handleGenerate} isLoading={isLoading} />
          {data && status === 'success' && (
            <RegenerateOptions
              currentTone={data.metadata.tone}
              onRegenerate={handleToneChange}
            />
          )}
        </aside>

        <section className="content-area">
          {isLoading && (
            <div className="loading-state" role="status" aria-live="polite">
              <div className="loading-spinner" aria-hidden="true" />
              <p>Running AI pipeline…</p>
              <p className="loading-sub">OpenAI generating → Claude refining → Formatting outputs</p>
            </div>
          )}

          {error && (
            <div className="error-state" role="alert">
              <p className="error-title">Generation failed</p>
              <p className="error-message">{error}</p>
              <button className="btn-secondary" onClick={resetGenerate}>Try again</button>
            </div>
          )}

          {data && status === 'success' && (
            <>
              <ContentPreview data={data} />
              <ApprovalWorkflow
                data={data}
                approval={approval}
                isSubmitting={isSubmitting}
                onApprove={approve}
                onReject={reject}
                onRegenerate={handleRegenerate}
              />
            </>
          )}

          {status === 'idle' && (
            <div className="empty-state">
              <p>Enter an idea and select your platforms to get started.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}