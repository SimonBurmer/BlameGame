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
  /** Screenshot shown beside the step. */
  readonly shot: 'home' | 'lobby' | 'round' | 'guessed' | 'reveal' | 'results';
  readonly shotAlt: string;
}

export interface Feature {
  readonly title: string;
  readonly body: string;
}

export interface Shot {
  /** Basename in public/screenshots, without extension. */
  readonly file: 'home' | 'lobby' | 'round' | 'guessed' | 'reveal' | 'results';
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
    /**
     * The verdict line under the headline, with the suspects' names cycling
     * through the gap. Split into two halves because the name sits in a
     * different place in each language: English puts a possessive on the end
     * of it, German puts a preposition in front.
     */
    readonly verdictBefore: string;
    readonly verdictAfter: string;
    readonly suspects: readonly string[];
    readonly scrollCue: string;
  };
  /** The scroll-driven phone, between the hero and the explanation. */
  readonly moment: {
    readonly heading: string;
    readonly sub: string;
    readonly caption: string;
  };
  readonly stats: readonly [Stat, Stat, Stat];
  /**
   * Alt text and captions for the screenshots, keyed by file. The screens are
   * shown inside the sections that explain them rather than in a gallery of
   * their own, but their descriptions still have to be translated.
   */
  readonly shots: {
    readonly items: readonly Shot[];
  };
  readonly steps: {
    readonly heading: string;
    readonly sub: string;
    /** Step labels shown on the timeline's rail, e.g. "01". */
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
