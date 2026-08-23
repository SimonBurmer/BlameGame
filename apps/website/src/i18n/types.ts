/**
 * The shape every locale must fill in.
 *
 * `en.ts` and `de.ts` are both annotated `: Messages`, so a key that exists in
 * one language and not the other is a compile error rather than a blank spot
 * on the page.
 */

export type Locale = 'en' | 'de';

export const locales = ['en', 'de'] as const satisfies readonly Locale[];

/** `en` is served from the root; every other locale gets a path prefix. */
export function pathFor(locale: Locale): string {
  return locale === 'en' ? '/' : `/${locale}/`;
}

export interface Step {
  readonly title: string;
  readonly body: string;
}

export interface Feature {
  readonly title: string;
  readonly body: string;
}

export interface Shot {
  /** Basename in public/screenshots, without extension. */
  readonly file: 'lobby' | 'round' | 'guessed' | 'reveal' | 'results';
  readonly caption: string;
  readonly alt: string;
}

export interface Stat {
  readonly value: number;
  readonly suffix: string;
  readonly label: string;
}

export interface QandA {
  readonly question: string;
  readonly answer: string;
}

export interface Messages {
  /** Value for the document's `lang` attribute, e.g. `en` or `de`. */
  readonly htmlLang: string;
  /** BCP-47 tag used for `og:locale`, e.g. `en_US`. */
  readonly ogLocale: string;
  readonly meta: {
    readonly title: string;
    readonly description: string;
    readonly ogImageAlt: string;
    /** Comma-free list; used only for the `keywords` hint some crawlers read. */
    readonly keywords: readonly string[];
  };
  readonly nav: {
    readonly howItWorks: string;
    readonly features: string;
    readonly faq: string;
    /** Accessible label on the language switch. */
    readonly languageLabel: string;
    readonly skipToContent: string;
  };
  readonly hero: {
    readonly eyebrow: string;
    readonly headline: string;
    readonly sub: string;
    readonly availability: string;
    readonly primaryCta: string;
    readonly primaryCtaEyebrow: string;
    readonly secondaryCta: string;
  };
  readonly stats: readonly [Stat, Stat, Stat];
  readonly shots: {
    readonly heading: string;
    readonly sub: string;
    readonly items: readonly Shot[];
  };
  readonly steps: {
    readonly heading: string;
    readonly items: readonly [Step, Step, Step];
  };
  readonly features: {
    readonly heading: string;
    readonly sub: string;
    readonly items: readonly Feature[];
  };
  readonly faq: {
    readonly heading: string;
    readonly items: readonly QandA[];
  };
  readonly cta: {
    readonly heading: string;
    readonly body: string;
  };
  readonly footer: {
    readonly tagline: string;
    readonly builtWith: string;
  };
}
