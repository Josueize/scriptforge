import { useState } from 'react';
import type { Tone, Length, Platform, GenerateRequest } from '../types';

interface Props {
  onSubmit: (payload: GenerateRequest) => void;
  isLoading: boolean;
}

const TONES: Tone[] = ['Dramatic', 'Neutral', 'Uplifting'];
const LENGTHS: { value: Length; label: string }[] = [
  { value: '1', label: '1 min' },
  { value: '3', label: '3 min' },
  { value: '5', label: '5 min' },
  { value: '10', label: '10 min' },
];
const PLATFORMS: { value: Platform; label: string }[] = [
  { value: 'youtube', label: 'YouTube Script' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'twitter', label: 'X / Twitter' },
  { value: 'newsletter', label: 'Newsletter' },
  { value: 'blog', label: 'SEO Blog' },
];

export function PromptForm({ onSubmit, isLoading }: Props) {
  const [idea, setIdea] = useState('');
  const [tone, setTone] = useState<Tone>('Dramatic');
  const [length, setLength] = useState<Length>('3');
  const [platforms, setPlatforms] = useState<Platform[]>(['youtube']);

  const togglePlatform = (platform: Platform) => {
    setPlatforms(prev =>
      prev.includes(platform) ? prev.filter(p => p !== platform) : [...prev, platform]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!idea.trim() || platforms.length === 0) return;
    onSubmit({ idea: idea.trim(), tone, length, platforms });
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-form">
      <div className="field">
        <label htmlFor="idea" className="field-label">Content idea</label>
        <textarea
          id="idea"
          value={idea}
          onChange={e => setIdea(e.target.value)}
          placeholder="e.g. The life and death of Cleopatra"
          maxLength={500}
          required
          className="textarea"
        />
      </div>

      <div className="field-row">
        <div className="field">
          <span className="field-label">Tone</span>
          <div className="pill-group" role="radiogroup" aria-label="Tone">
            {TONES.map(t => (
              <button key={t} type="button" role="radio" aria-checked={tone === t}
                className={`pill ${tone === t ? 'pill--active' : ''}`}
                onClick={() => setTone(t)}>
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <span className="field-label">Length</span>
          <div className="pill-group" role="radiogroup" aria-label="Length">
            {LENGTHS.map(({ value, label }) => (
              <button key={value} type="button" role="radio" aria-checked={length === value}
                className={`pill ${length === value ? 'pill--active' : ''}`}
                onClick={() => setLength(value)}>
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="field">
        <span className="field-label">Output platforms</span>
        <div className="pill-group" role="group" aria-label="Platforms">
          {PLATFORMS.map(({ value, label }) => (
            <button key={value} type="button" aria-pressed={platforms.includes(value)}
              className={`pill ${platforms.includes(value) ? 'pill--active' : ''}`}
              onClick={() => togglePlatform(value)}>
              {label}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" className="btn-primary"
        disabled={isLoading || !idea.trim() || platforms.length === 0}>
        {isLoading ? (
          <><span className="spinner" aria-hidden="true" /> Generating…</>
        ) : 'Generate content'}
      </button>
    </form>
  );
}