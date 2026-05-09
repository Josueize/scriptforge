import type { Platform, PlatformContent } from '../types';

const PLATFORM_LABELS: Record<Platform, string> = {
  youtube: 'YouTube Script',
  linkedin: 'LinkedIn',
  twitter: 'X / Twitter',
  newsletter: 'Newsletter',
  blog: 'SEO Blog',
};

interface Props {
  platforms: PlatformContent[];
  activePlatform: Platform;
  onSelect: (platform: Platform) => void;
}

export function PlatformSelector({ platforms, activePlatform, onSelect }: Props) {
  return (
    <nav className="platform-nav" aria-label="Platform outputs">
      {platforms.map(({ platform, wordCount }) => (
        <button key={platform}
          className={`platform-tab ${activePlatform === platform ? 'platform-tab--active' : ''}`}
          onClick={() => onSelect(platform)}
          aria-selected={activePlatform === platform}>
          <span className="platform-tab__name">{PLATFORM_LABELS[platform]}</span>
          <span className="platform-tab__meta">{wordCount}w</span>
        </button>
      ))}
    </nav>
  );
}