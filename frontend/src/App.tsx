
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { PromptForm } from './components/PromptForm';
import { ContentPreview } from './components/ContentPreview';
import { ApprovalWorkflow } from './components/ApprovalWorkflow';
import { RegenerateOptions } from './components/RegenerateOptions';

import { useGenerate } from './hooks/useGenerate';
import { useApproval } from './hooks/useApproval';

import { api } from './services/api';

import type { GenerateRequest, Tone } from './types';

import './App.css';

type AuthStatus =
  | 'checking'
  | 'authenticated'
  | 'unauthenticated';

export default function App() {
  // =====================================
  // AUTHENTICATION STATE
  // =====================================

  const [authStatus, setAuthStatus] =
    useState<AuthStatus>('checking');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [adminName, setAdminName] = useState('');

  const [authError, setAuthError] = useState('');
  const [isAuthenticating, setIsAuthenticating] =
    useState(false);

  const [isLoggingOut, setIsLoggingOut] =
    useState(false);

  // =====================================
  // EXISTING CONTENT GENERATION
  // =====================================

  const {
    status,
    data,
    error,
    generate,
    reset: resetGenerate,
  } = useGenerate();

  const {
    approval,
    approvalError,
    isSubmitting,
    approve,
    reject,
    reset: resetApproval,
  } = useApproval();

  const [lastRequest, setLastRequest] =
    useState<GenerateRequest | null>(null);

  const isLoading = status === 'loading';

  // =====================================
  // RESTORE ADMINISTRATOR SESSION
  // =====================================

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      try {
        const session = await api.me();

        if (!active) return;

        setAdminName(session.username);
        setAuthStatus('authenticated');
      } catch {
        if (!active) return;

        setAdminName('');
        setAuthStatus('unauthenticated');
      }
    };

    void restoreSession();

    return () => {
      active = false;
    };
  }, []);

  // =====================================
  // ADMINISTRATOR LOGIN
  // =====================================

  const handleLogin = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (isAuthenticating) return;

    setAuthError('');
    setIsAuthenticating(true);

    try {
      const session = await api.login(
        username.trim(),
        password,
      );

      setAdminName(session.username);
      setPassword('');
      setAuthStatus('authenticated');
    } catch {
      setAuthError(
        'Login failed. Check your credentials and backend connection.',
      );
    } finally {
      setIsAuthenticating(false);
    }
  };

  // =====================================
  // ADMINISTRATOR LOGOUT
  // =====================================

  const handleLogout = async () => {
    if (isLoggingOut || isSubmitting || isLoading) {
      return;
    }

    setIsLoggingOut(true);
    setAuthError('');

    try {
      await api.logout();

      resetGenerate();
      resetApproval();

      setLastRequest(null);
      setAdminName('');
      setUsername('');
      setPassword('');

      setAuthStatus('unauthenticated');
    } catch {
      setAuthError(
        'Logout failed. Your session may still be active.',
      );
    } finally {
      setIsLoggingOut(false);
    }
  };

  // =====================================
  // GENERATE CONTENT
  // =====================================

  const handleGenerate = (payload: GenerateRequest) => {
    if (
      authStatus !== 'authenticated' ||
      isSubmitting ||
      isLoading
    ) {
      return;
    }

    setLastRequest(payload);
    resetApproval();
    generate(payload);
  };

  // =====================================
  // REGENERATE CONTENT
  // =====================================

  const handleRegenerate = () => {
    if (
      authStatus !== 'authenticated' ||
      !lastRequest ||
      isSubmitting ||
      isLoading
    ) {
      return;
    }

    resetGenerate();
    resetApproval();
    generate(lastRequest);
  };

  // =====================================
  // CHANGE CONTENT TONE
  // =====================================

  const handleToneChange = (tone: Tone) => {
    if (
      authStatus !== 'authenticated' ||
      !lastRequest ||
      isSubmitting ||
      isLoading
    ) {
      return;
    }

    const updated: GenerateRequest = {
      ...lastRequest,
      tone,
    };

    setLastRequest(updated);
    resetGenerate();
    resetApproval();

    generate(updated);
  };

  // =====================================
  // CHECKING SESSION
  // =====================================

  if (authStatus === 'checking') {
    return (
      <div className="app">
        <div className="loading-state" role="status">
          <div
            className="loading-spinner"
            aria-hidden="true"
          />

          <p>Checking administrator session...</p>
        </div>
      </div>
    );
  }

  // =====================================
  // ADMINISTRATOR LOGIN SCREEN
  // =====================================

  if (authStatus === 'unauthenticated') {
    return (
      <div className="app">
        <header className="site-header">
          <div className="wordmark">
            ScriptForge
          </div>

          <h1 className="headline">
            Administrator <em>Login</em>
          </h1>

          <p className="subline">
            Secure access to ScriptForge AI
            content management.
          </p>
        </header>

        <main
          style={{
            display: 'flex',
            justifyContent: 'center',
            padding: '40px 20px',
          }}
        >
          <form
            onSubmit={handleLogin}
            style={{
              width: '100%',
              maxWidth: '440px',
              padding: '32px',
              backgroundColor: '#ffffff',
              color: '#111827',
              border: '1px solid #d1d5db',
              borderRadius: '12px',
              boxSizing: 'border-box',
            }}
          >
            <h2>Administrator Sign In</h2>

            <p style={{ color: '#4b5563' }}>
              Enter your administrator credentials.
            </p>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                marginTop: '24px',
                marginBottom: '20px',
              }}
            >
              <label htmlFor="admin-username">
                Administrator Username
              </label>

              <input
                id="admin-username"
                type="text"
                autoComplete="username"
                required
                value={username}
                disabled={isAuthenticating}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="Enter username"
                style={{
                  padding: '12px',
                  border: '1px solid #9ca3af',
                  borderRadius: '8px',
                  backgroundColor: '#ffffff',
                  color: '#111827',
                }}
              />
            </div>

            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                marginBottom: '24px',
              }}
            >
              <label htmlFor="admin-password">
                Administrator Password
              </label>

              <input
                id="admin-password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                disabled={isAuthenticating}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter password"
                style={{
                  padding: '12px',
                  border: '1px solid #9ca3af',
                  borderRadius: '8px',
                  backgroundColor: '#ffffff',
                  color: '#111827',
                }}
              />
            </div>

            {authError && (
              <p
                role="alert"
                style={{
                  color: '#b91c1c',
                  marginBottom: '16px',
                }}
              >
                {authError}
              </p>
            )}

            <button
              type="submit"
              className="btn-primary"
              disabled={isAuthenticating}
              style={{
                width: '100%',
                minHeight: '44px',
              }}
            >
              {isAuthenticating
                ? 'Signing in...'
                : 'Sign In to ScriptForge'}
            </button>
          </form>
        </main>
      </div>
    );
  }

  // =====================================
  // AUTHENTICATED DASHBOARD
  // =====================================

  return (
    <div className="app">
      <header className="site-header">
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            flexWrap: 'wrap',
          }}
        >
          <div className="wordmark">
            ScriptForge
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <span>
              Administrator: {adminName}
            </span>

            <button
              type="button"
              className="btn-secondary"
              onClick={handleLogout}
              disabled={
                isLoggingOut ||
                isSubmitting ||
                isLoading
              }
            >
              {isLoggingOut
                ? 'Signing out...'
                : 'Sign Out'}
            </button>
          </div>
        </div>

        {authError && (
          <p className="error-message" role="alert">
            {authError}
          </p>
        )}

        <h1 className="headline">
          One idea. <em>Every platform.</em>
        </h1>

        <p className="subline">
          AI-powered content generation for the
          Blue Foxes creative team.
        </p>
      </header>

      <main className="main-layout">
        <aside className="sidebar">
          <PromptForm
            onSubmit={handleGenerate}
            isLoading={isLoading || isSubmitting}
          />

          {data && status === 'success' && (
            <RegenerateOptions
              currentTone={data.metadata.tone}
              onRegenerate={handleToneChange}
            />
          )}
        </aside>

        <section className="content-area">
          {isLoading && (
            <div
              className="loading-state"
              role="status"
              aria-live="polite"
            >
              <div
                className="loading-spinner"
                aria-hidden="true"
              />

              <p>Running AI pipeline...</p>

              <p className="loading-sub">
                OpenAI generating - Claude refining -
                Formatting outputs
              </p>
            </div>
          )}

          {error && (
            <div
              className="error-state"
              role="alert"
            >
              <p className="error-title">
                Generation failed
              </p>

              <p className="error-message">
                {error}
              </p>

              <button
                type="button"
                className="btn-secondary"
                onClick={resetGenerate}
              >
                Try again
              </button>
            </div>
          )}

          {data && status === 'success' && (
            <>
              <ContentPreview data={data} />

              <ApprovalWorkflow
                data={data}
                approval={approval}
                approvalError={approvalError}
                isSubmitting={isSubmitting}
                onApprove={approve}
                onReject={reject}
                onRegenerate={handleRegenerate}
              />
            </>
          )}

          {status === 'idle' && (
            <div className="empty-state">
              <p>
                Enter an idea and select your platforms
                to get started.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
