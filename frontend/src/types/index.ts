export type Tone = 'Dramatic' | 'Neutral' | 'Uplifting';
export type Length = '1' | '3' | '5' | '10';
export type Platform = 'linkedin' | 'twitter' | 'youtube' | 'newsletter' | 'blog';
export type Status = 'idle' | 'loading' | 'success' | 'error';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface GenerateRequest {
  idea: string;
  tone: Tone;
  length: Length;
  platforms: Platform[];
}

export interface PlatformContent {
  platform: Platform;
  content: string;
  wordCount: number;
}

export interface GenerateResponse {
  id: string;
  script: string;
  platforms: PlatformContent[];
  metadata: {
    tone: Tone;
    length: Length;
    generatedAt: string;
    tokensUsed: number;
  };
}

export interface ApprovalState {
  status: ApprovalStatus;
  contentId: string | null;
  approvedPlatforms: Platform[];
}