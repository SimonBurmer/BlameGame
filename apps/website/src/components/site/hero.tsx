'use client';

import { FlipWords } from '@/components/ui/flip-words';
import { Spotlight } from '@/components/ui/spotlight-new';
import { TextGenerateEffect } from '@/components/ui/text-generate-effect';
import { ThreeDMarquee } from '@/components/ui/3d-marquee';
import { AppStoreButton } from '@/components/site/app-store-button';
import { photos } from '@/lib/photos';
import type { Messages } from '@/i18n';

/**
 * The hero is the wall of everybody's photos, seen from an angle, with the
 * page's question over it. The photographs are the same ones the app is
 * holding two screens further down, which is the whole point: this is what the
 * game is made of.
 */
export function Hero({ m }: { m: Messages }) {
  // The marquee splits its input into four columns; three passes give each
  // column depth without needing thirty-six separate photographs.
  const wall = [...photos, ...photos, ...photos];

  return (
    <section id="top" className="vignette relative flex min-h-[100svh] items-center overflow-hidden">
      {/* No negative z-index here: <body> carries an opaque background,
          and a -z child of the root stacking context paints underneath it. */}
      <div className="absolute inset-0">
        <ThreeDMarquee images={wall} className="h-full w-full rounded-none opacity-90" />
      </div>
      {/* Wide: a horizontal pass clears a dark bed on the left for the type
          and leaves the photo field standing on the right, and a vertical pass
          sinks the top into the navbar and the bottom into the next section.
          Narrow: there is no "beside", so the split runs top-to-bottom instead
          — otherwise the copy sits over the photographs and the photographs
          have to be dimmed to nothing to keep it readable. */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-ink/60 via-ink/80 to-ink sm:bg-gradient-to-r sm:from-ink sm:via-ink/90 sm:to-ink/25" />
      <div className="pointer-events-none absolute inset-0 hidden bg-gradient-to-b from-ink via-transparent to-ink sm:block" />
      <Spotlight
        gradientFirst="radial-gradient(68% 69% at 55% 31%, rgba(233,69,96,.16) 0, rgba(233,69,96,.04) 50%, transparent 80%)"
        gradientSecond="radial-gradient(50% 50% at 50% 50%, rgba(78,205,196,.10) 0, rgba(78,205,196,.02) 80%, transparent 100%)"
        gradientThird="radial-gradient(50% 50% at 50% 50%, rgba(233,69,96,.08) 0, transparent 80%)"
        duration={9}
      />

      <div className="relative z-10 mx-auto w-full max-w-6xl px-6 pt-36 pb-28 sm:pt-40">
        <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
          <p className="font-mono text-[0.7rem] tracking-[0.18em] text-accent uppercase sm:text-xs sm:tracking-[0.28em]">
            {m.hero.eyebrow}
          </p>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-white/70">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-70" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-accent" />
            </span>
            {m.hero.availability}
          </p>
        </div>

        <h1 className="display mt-6 max-w-4xl text-[2.75rem] leading-[0.95] sm:text-6xl lg:text-[5.5rem]">
          {m.hero.headline}
        </h1>

        {/* The verdict the game ends every round with, running on a loop.
            A <div>, not a <p>: FlipWords renders a <div> of its own, and a
            block element inside a paragraph is re-parented by the parser,
            which breaks hydration. Its <div> is `inline-block`, so the
            sentence still sets as a sentence — which matters, because the name
            is followed by a possessive in English and by nothing but a full
            stop in German. */}
        <div className="mt-6 text-xl text-white/45 sm:text-3xl">
          {m.hero.verdictBefore}{' '}
          <FlipWords
            words={[...m.hero.suspects]}
            duration={1900}
            className="!px-0 font-semibold text-brand"
          />
          {m.hero.verdictAfter}
        </div>

        <TextGenerateEffect
          words={m.hero.sub}
          duration={0.6}
          className="mt-8 max-w-2xl text-base leading-relaxed font-normal text-white/65 sm:text-lg"
        />

        <div className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-4">
          <AppStoreButton eyebrow={m.hero.primaryCtaEyebrow} label={m.hero.primaryCta} />
          <a
            href="#how"
            className="group inline-flex items-center gap-2 text-sm font-medium text-white/60 transition-colors hover:text-white"
          >
            {m.hero.secondaryCta}
            <span aria-hidden className="transition-transform group-hover:translate-x-1">
              →
            </span>
          </a>
        </div>
      </div>

      <span
        aria-hidden
        className="absolute bottom-6 left-1/2 hidden -translate-x-1/2 font-mono text-[0.6rem] tracking-[0.3em] text-white/30 uppercase sm:block"
      >
        {m.hero.scrollCue}
      </span>
    </section>
  );
}
