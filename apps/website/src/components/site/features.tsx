'use client';

import {
  IconClockBolt,
  IconEye,
  IconFlame,
  IconPhoto,
  IconRepeat,
  IconUsersGroup,
  type IconProps,
} from '@tabler/icons-react';
import type { ComponentType } from 'react';

import { BentoGrid, BentoGridItem } from '@/components/ui/bento-grid';
import { GlowingEffect } from '@/components/ui/glowing-effect';
import { Phone } from '@/components/site/phone';
import { photos } from '@/lib/photos';
import type { Messages } from '@/i18n';

const icons: ComponentType<IconProps>[] = [
  IconUsersGroup,
  IconClockBolt,
  IconEye,
  IconFlame,
  IconRepeat,
  IconPhoto,
];

/** Wide cells carry a picture; narrow ones would only crush it. */
const spans = [
  'md:col-span-2',
  'md:col-span-1',
  'md:col-span-1',
  'md:col-span-2',
  'md:col-span-1',
  'md:col-span-2',
];

function PhotoStrip() {
  return (
    <div className="flex h-full min-h-[7rem] gap-2 overflow-hidden rounded-xl">
      {photos.slice(0, 5).map((src) => (
        // eslint-disable-next-line @next/next/no-img-element -- static export, no optimiser
        <img
          key={src}
          src={src}
          alt=""
          aria-hidden
          loading="lazy"
          className="h-full w-1/5 rounded-lg object-cover opacity-70 transition-opacity duration-500 group-hover/bento:opacity-100"
        />
      ))}
    </div>
  );
}

export function Features({ m }: { m: Messages }) {
  const altFor = (file: string) => m.shots.items.find((s) => s.file === file)?.alt ?? '';

  return (
    <section id="features" className="relative mx-auto max-w-7xl px-6 py-24 sm:py-32">
      <h2 className="display max-w-3xl text-4xl sm:text-6xl">{m.features.heading}</h2>
      <p className="mt-4 max-w-xl text-sm text-white/55 sm:text-base">{m.features.sub}</p>

      <BentoGrid className="mt-14 md:auto-rows-[16rem]">
        {m.features.items.map((item, i) => {
          const Icon = icons[i % icons.length]!;
          // Only the wide cells get a picture; a phone in a one-column cell is
          // a thumbnail nobody can read.
          // Hardcore mode is 'whatever the shuffle picked is what the room sees' —
          // so the picture for it is what the room sees.
          const shot = i === 0 ? 'results' : i === 3 ? 'round' : null;
          // A phone is much taller than a cell, so in the wide cells it stands
          // down the right-hand side, tilted and bled off the bottom edge,
          // with the copy keeping to the left half. Squeezing the whole device
          // into the cell would have made it a thumbnail nobody can read.
          const header = shot ? (
            <div
              aria-hidden={false}
              className="pointer-events-none absolute inset-y-0 right-0 hidden w-[42%] items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-l from-brand/15 to-transparent sm:flex"
            >
              <Phone
                shot={shot}
                alt={altFor(shot)}
                className="w-[150px] translate-y-8 rotate-3 transition-transform duration-500 group-hover/bento:translate-y-4 group-hover/bento:rotate-1"
              />
            </div>
          ) : i === 5 ? (
            <PhotoStrip />
          ) : null;
          // Keep the words clear of the phone.
          const textWidth = shot ? 'block sm:max-w-[56%]' : 'block';

          return (
            <BentoGridItem
              key={item.title}
              className={`group/bento relative overflow-hidden rounded-2xl border-white/10 bg-white/[0.03] shadow-none dark:border-white/10 dark:bg-white/[0.03] ${spans[i]}`}
              header={
                <>
                  <GlowingEffect
                    disabled={false}
                    glow
                    spread={44}
                    proximity={72}
                    inactiveZone={0.01}
                    borderWidth={1.5}
                  />
                  {header}
                </>
              }
              icon={<Icon className="h-5 w-5 text-brand" stroke={1.6} />}
              title={<span className={`text-base text-white ${textWidth}`}>{item.title}</span>}
              description={
                <span className={`text-[0.82rem] leading-relaxed text-white/55 ${textWidth}`}>
                  {item.body}
                </span>
              }
            />
          );
        })}
      </BentoGrid>
    </section>
  );
}
