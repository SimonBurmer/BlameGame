'use client';

import { PointerHighlight } from '@/components/ui/pointer-highlight';
import type { Messages } from '@/i18n';

/**
 * The three numbers the game is actually built around. They come from
 * `packages/brand`'s `limits`, which is read off the server rules — so the
 * page cannot advertise a cap the backend does not enforce.
 */
export function Numbers({ m }: { m: Messages }) {
  return (
    <section className="border-y border-white/[0.07] bg-white/[0.015]">
      <div className="mx-auto grid max-w-5xl grid-cols-1 divide-y divide-white/[0.07] px-6 sm:grid-cols-3 sm:divide-x sm:divide-y-0">
        {m.stats.map((stat) => (
          <div key={stat.label} className="flex flex-col items-center gap-2 py-10 text-center">
            {/* The pointer is drawn past the bottom-right corner of the
                rectangle, so the number needs room under it or the arrow lands
                on the label. */}
            <div className="pr-7 pb-6">
              <PointerHighlight
                rectangleClassName="border-brand/50"
                pointerClassName="text-brand"
                containerClassName="inline-block"
              >
                <span className="display block px-3 text-5xl text-white sm:text-6xl">
                  {stat.value}
                  {stat.suffix}
                </span>
              </PointerHighlight>
            </div>
            <span className="font-mono text-[0.65rem] tracking-[0.22em] text-white/45 uppercase">
              {stat.label}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
