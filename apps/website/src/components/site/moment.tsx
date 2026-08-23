'use client';

import { ContainerScroll } from '@/components/ui/container-scroll-animation';
import { Phone } from '@/components/site/phone';
import type { Messages } from '@/i18n';

/**
 * The centre of the page: scrolling into this section tips a screen flat, and
 * what is on it is one real round of the game. The photograph behind the phone
 * is the same one the phone is showing, thrown out of focus — the room the
 * picture came from, and the picture, in one frame.
 */
export function Moment({ m }: { m: Messages }) {
  const alt = (file: string) => m.shots.items.find((s) => s.file === file)?.alt ?? '';

  return (
    <section className="relative -mt-24 overflow-hidden">
      <ContainerScroll
        titleComponent={
          <div className="mx-auto max-w-3xl px-6 pb-10">
            <h2 className="display text-3xl sm:text-5xl">{m.moment.heading}</h2>
            <p className="mx-auto mt-5 max-w-xl text-sm leading-relaxed text-white/60 sm:text-base">
              {m.moment.sub}
            </p>
          </div>
        }
      >
        <div className="relative flex h-full w-full items-center justify-center overflow-hidden rounded-2xl">
          <div
            aria-hidden
            className="absolute inset-0 scale-110 bg-[url('/photos/03-party-lights.jpg')] bg-cover bg-center opacity-90 blur-[36px]"
          />
          <div aria-hidden className="absolute inset-0 bg-ink/35" />
          {/* Three phones, one round: the picture goes up on everybody's
              screen at the same instant, and this is what that looks like from
              across the table. Every one of them is a real capture. */}
          <div className="relative flex items-center justify-center">
            <Phone
              shot="guessed"
              alt={alt('guessed')}
              className="absolute right-[96%] hidden w-[150px] -rotate-6 opacity-55 blur-[1px] sm:block md:w-[180px]"
            />
            <Phone
              shot="round"
              alt={alt('round')}
              priority
              className="relative z-10 w-[190px] sm:w-[218px] md:w-[252px]"
            />
            <Phone
              shot="reveal"
              alt={alt('reveal')}
              className="absolute left-[96%] hidden w-[150px] rotate-6 opacity-55 blur-[1px] sm:block md:w-[180px]"
            />
          </div>
          <span className="absolute bottom-3 left-1/2 -translate-x-1/2 font-mono text-[0.6rem] tracking-[0.25em] text-white/45 uppercase">
            {m.moment.caption}
          </span>
        </div>
      </ContainerScroll>
    </section>
  );
}
