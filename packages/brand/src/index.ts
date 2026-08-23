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
 * Store links.
 *
 * `appStore` is intentionally an empty string: the button is on the page and
 * wired up, but there is no listing behind it yet. Paste the URL here and it
 * lights up everywhere at once. `playStore` stays null until there is an
 * Android build to point at, and the button for it is not rendered.
 */
export const stores: { readonly appStore: string; readonly playStore: string | null } = {
  appStore: '',
  playStore: null,
};

/** Canonical origin, used to build absolute URLs for SEO tags. */
export const siteOrigin = 'https://blamegame.app';

export type Palette = typeof palette;
