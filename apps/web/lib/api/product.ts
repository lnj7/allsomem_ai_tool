import { apiGet, apiPost, apiPut } from "./client";

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
};

export const authApi = {
  me: () => apiGet<User>("/api/v1/auth/me"),
  register: (body: { email: string; password: string; full_name: string }) =>
    apiPost<User>("/api/v1/auth/register", body),
  login: (body: { email: string; password: string }) => apiPost<User>("/api/v1/auth/login", body),
  logout: () => apiPost<{ status: string }>("/api/v1/auth/logout"),
};

export type Creator = {
  id: string;
  display_name: string;
  creator_type: string | null;
  niche: string | null;
  bio: string | null;
  onboarding_step: number;
  onboarding_completed: boolean;
  onboarding_data: Record<string, unknown>;
};

export type YouTubeVideo = {
  video_id: string;
  title: string;
  url: string;
  views: number | null;
  views_label: string | null;
  published_label: string | null;
  thumbnail_url: string | null;
};

export type YouTubeSnapshot = {
  title: string;
  handle: string | null;
  url: string;
  description: string;
  subscriber_count: number | null;
  subscriber_label: string | null;
  video_count: number | null;
  videos: YouTubeVideo[];
  progress: { current: number; next_milestone: number; percent: number };
  next_actions: { id: string; title: string; detail: string }[];
  note: string;
  synced_at: string | null;
};

export type YouTubeConnection = {
  connected: boolean;
  platform: string;
  snapshot: YouTubeSnapshot | null;
};

export type Profile = {
  niche: string;
  positioning: string;
  audience: { description: string; pain_points: string[]; interests: string[] };
  brand_personality: string[];
  tone: string;
  content_pillars: { name: string; description: string; percentage: number }[];
  content_strategy: string;
  recommended_formats: string[];
  recommended_platforms: string[];
  initial_strategy: string[];
};

export const productApi = {
  creator: () => apiGet<Creator>("/api/v1/creators/me"),
  onboarding: () =>
    apiGet<{ step: number; completed: boolean; data: Record<string, unknown> }>("/api/v1/onboarding"),
  saveOnboarding: (body: { step: number; data: Record<string, unknown>; complete?: boolean }) =>
    apiPost("/api/v1/onboarding", body),
  generateProfile: () => apiPost<{ status: string; profile: Profile }>("/api/v1/onboarding/generate-profile"),
  strategy: () => apiGet<{ status: string; profile: Profile | null }>("/api/v1/strategy"),
  youtube: () => apiGet<YouTubeConnection>("/api/v1/platforms/youtube"),
  connectYouTube: (url: string) => apiPost<YouTubeConnection>("/api/v1/platforms/youtube", { url }),
  refreshYouTube: () => apiPost<YouTubeConnection>("/api/v1/platforms/youtube/refresh"),
  saveProfile: (profile: Profile, accept = false) =>
    apiPut<{ status: string; profile: Profile }>("/api/v1/strategy", { profile, accept }),
  dashboard: () => apiGet<Record<string, unknown>>("/api/v1/dashboard"),
  generateContent: (body: Record<string, string | undefined>) =>
    apiPost("/api/v1/content/generate", body),
  assets: () => apiGet<Array<Record<string, unknown>>>("/api/v1/content/assets"),
  ideas: () => apiGet<Array<Record<string, unknown>>>("/api/v1/content/ideas"),
  schedule: (id: string, scheduled_at: string, platform: string) =>
    apiPost(`/api/v1/content/assets/${id}/schedule`, { scheduled_at, platform }),
  approve: (id: string) => apiPost(`/api/v1/content/assets/${id}/approve`),
  analytics: () => apiGet<Record<string, unknown>>("/api/v1/analytics/overview"),
  comments: () => apiGet<Array<Record<string, unknown>>>("/api/v1/community/comments"),
  addComment: (body: { author_name: string; body: string; platform?: string }) =>
    apiPost("/api/v1/community/comments", body),
  replyComment: (id: string, reply: string) =>
    apiPost(`/api/v1/community/comments/${id}/reply`, { reply }),
  brand: () => apiGet<Record<string, unknown>>("/api/v1/brand-center"),
  settings: () => apiGet<{ approval_mode: string }>("/api/v1/settings"),
  saveSettings: (approval_mode: string) => apiPut("/api/v1/settings", { approval_mode }),
  assistantHistory: () => apiGet<Array<{ role: string; content: string }>>("/api/v1/assistant/messages"),
  askAssistant: (message: string) => apiPost<{ reply: string }>("/api/v1/assistant/ask", { message }),
};
