'use client';

import { IconEyeCheck, IconShieldLock, IconTrash, type IconProps } from '@tabler/icons-react';
import type { ComponentType } from 'react';

import { GlowingEffect } from '@/components/ui/glowing-effect';
import { Phone } from '@/components/site/phone';
import { band, cn, shell } from '@/lib/utils';
import type { Messages } from '@/i18n';

const icons: ComponentType<IconProps>[] = [IconTrash, IconShieldLock, IconEyeCheck];

/**
 * What happens to the photos.
 *
 * Every claim here is one the code actually keeps: `store.delete_room` fires
 * `on_evict`, which is wired to `_delete_room_uploads` in `backend/app/main.py`,
 * and a room nobody has touched for `ROOM_TTL_SECONDS` is swept the same way.
 * There is no account system, no analytics on the site and no cookies. If any
 * of that changes, this section is wrong and has to change with it.
 */
export function Privacy({ m }: { m: Messages }) {
  return (
    <section id="privacy" className={cn(band, 'relative overflow-hidden')}>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-accent/40 to-transparent"
      />
      <div className={cn(shell)}>
        <div className="grid gap-12 lg:grid-cols-[1.4fr_auto] lg:items-center">
          <div>
            <p className="font-mono text-[0.65rem] tracking-[0.28em] text-accent uppercase">GDPR</p>
            <h2 className="display mt-5 max-w-3xl text-4xl sm:text-6xl">{m.privacy.heading}</h2>
            <p className="mt-5 max-w-2xl text-sm leading-relaxed text-white/60 sm:text-base">
              {m.privacy.sub}
            </p>
          </div>

          {/* The app says it on screen, so the screen is the evidence. */}
          <div className="relative flex justify-center lg:justify-end">
            <div
              aria-hidden
              className="absolute inset-0 scale-150 bg-[radial-gradient(circle_at_center,rgba(78,205,196,0.16),transparent_65%)]"
            />
            <Phone shot="lobby" alt={m.privacy.shotAlt} className="relative w-[210px] sm:w-[240px]" />
          </div>
        </div>

        <ul className="mt-14 grid gap-4 md:grid-cols-3">
          {m.privacy.items.map((item, i) => {
            const Icon = icons[i % icons.length]!;
            return (
              <li
                key={item.title}
                className="relative rounded-2xl border border-white/10 bg-white/[0.03] p-6"
              >
                <GlowingEffect
                  disabled={false}
                  glow
                  spread={40}
                  proximity={64}
                  inactiveZone={0.01}
                  borderWidth={1.5}
                />
                <Icon className="h-5 w-5 text-accent" stroke={1.6} />
                <h3 className="mt-4 text-base font-semibold text-white">{item.title}</h3>
                <p className="mt-2 text-[0.85rem] leading-relaxed text-white/55">{item.body}</p>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
