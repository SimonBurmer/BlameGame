/**
 * Brand tokens, shared so the website cannot drift from the app.
 *
 * The palette is a transcription of `AppColors.dark` in
 * `lib/theme/app_theme.dart`. If a colour changes there, change it here —
 * these are the same brand, not two that happen to match.
 */

export const palette = {
  /** Background gradient, top-left to bottom-right. */
  bgTop: '#1A1A2E',
  bgMid: '#16213E',
  bgBottom: '#0F3460',
  /** Brand red — primary actions. */
  brand: '#E94560',
  /** Teal accent — secondary actions. */
  accent: '#4ECDC4',
  /** Muted slate — the figure inside the mark. */
  figure: '#8E97B8',
  gold: '#FFD700',
  onSurfaceStrong: '#FFFFFF',
  onSurfaceMuted: 'rgba(255, 255, 255, 0.70)',
  onSurfaceFaint: 'rgba(255, 255, 255, 0.50)',
  surfaceTint: 'rgba(255, 255, 255, 0.08)',
  surfaceTintStrong: 'rgba(255, 255, 255, 0.15)',
} as const;

/**
 * The app's name lives here and nowhere else, so renaming it is one edit.
 * It has changed twice already.
 */
export const app = {
  name: 'Blame Game',
  /** Reverse-DNS identifier, matching the shipped iOS/Android bundle. */
  bundleId: 'com.blamegame.app',
} as const;

/**
 * Limits the game actually enforces server-side. The website quotes these, so
 * they are sourced from the rules rather than retyped into marketing copy.
 * See `backend/app/game.py` and `backend/app/store.py`.
 */
export const limits = {
  maxPlayers: 12,
  maxPhotosPerPlayer: 10,
  roomCodeLength: 5,
} as const;

/**
 * Store links. Both are null until the app is actually listed — a landing page
 * that links to a store page that does not exist is worse than one that says
 * "not yet".
 */
export const stores: { readonly appStore: string | null; readonly playStore: string | null } = {
  appStore: null,
  playStore: null,
};

/** Canonical origin, used to build absolute URLs for SEO tags. */
export const siteOrigin = 'https://blamegame.app';

export type Palette = typeof palette;
