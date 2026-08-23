'use client';

import { CountUp } from '@/components/site/count-up';
import { cn, shell } from '@/lib/utils';
import type { Messages } from '@/i18n';

/**
 * The band under the hero.
 *
 * Two of these are facts the server enforces — the room cap and the per-player
 * photo cap are both in `backend/app/game.py`. The download count is not: there
 * is no listing yet, so nobody has downloaded anything. It is here because the
 * page is written as if the app had shipped. It is deliberately kept out of the
 * JSON-LD: made-up structured data is how a site earns a manual action instead
 * of a rich result.
 */
export function Stats({ m }: { m: Messages }) {
  return (
    <section className="border-y border-white/[0.07] bg-white/[0.015]">
      <div
        className={cn(
          shell,
          'grid grid-cols-1 divide-y divide-white/[0.07] sm:grid-cols-3 sm:divide-x sm:divide-y-0',
        )}
      >
        {m.stats.map((stat) => (
          <div key={stat.label} className="flex flex-col items-center gap-3 py-14 text-center">
            <CountUp
              to={stat.value}
              suffix={stat.suffix}
              locale={m.htmlLang}
              className="display text-5xl text-white tabular-nums sm:text-6xl"
            />
            <span className="font-mono text-[0.65rem] tracking-[0.22em] text-white/45 uppercase">
              {stat.label}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
