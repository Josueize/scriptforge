import type { Tone } from '../types';

interface Props {
  currentTone: Tone;
  onRegenerate: (tone: Tone) => void;
}

const TONES: Tone[] = ['Dramatic', 'Neutral', 'Uplifting'];

export function RegenerateOptions({ currentTone, onRegenerate }: Props) {
  return (
    <div className="regen-options">
      <span className="field-label">Try a different tone</span>
      <div className="pill-group">
        {TONES.filter(t => t !== currentTone).map(tone => (
          <button key={tone} className="pill" onClick={() => onRegenerate(tone)}>
            {tone}
          </button>
        ))}
      </div>
    </div>
  );
}