'use client';

import { app } from '@blame-game/brand';

import { BackgroundBeamsWithCollision } from '@/components/ui/background-beams-with-collision';
import { TextHoverEffect } from '@/components/ui/text-hover-effect';
import { AppStoreButton } from '@/components/site/app-store-button';
import type { Messages } from '@/i18n';

export function Cta({ m }: { m: Messages }) {
  return (
    <section className="relative">
      <BackgroundBeamsWithCollision className="h-auto min-h-[26rem] bg-gradient-to-b from-ink via-navy/40 to-ink md:h-auto">
        <div className="relative z-10 mx-auto max-w-3xl px-6 py-20 text-center">
          {/* The name, drawn rather than set: the outline traces itself in on
              load, and filling it in is what a cursor moving across it does. */}
          <div className="mx-auto -mb-4 h-24 w-full max-w-3xl sm:h-36" aria-hidden>
            <TextHoverEffect text={app.name.toUpperCase()} duration={0.25} />
          </div>
          <h2 className="display text-4xl sm:text-6xl">{m.cta.heading}</h2>
          <p className="mx-auto mt-5 max-w-xl text-sm leading-relaxed text-white/60 sm:text-base">
            {m.cta.body}
          </p>
          <div className="mt-9 flex justify-center">
            <AppStoreButton eyebrow={m.hero.primaryCtaEyebrow} label={m.hero.primaryCta} />
          </div>
        </div>
      </BackgroundBeamsWithCollision>
    </section>
  );
}
