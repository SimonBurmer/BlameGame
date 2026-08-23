'use client';

import { Timeline } from '@/components/ui/timeline';
import { Phone } from '@/components/site/phone';
import type { Messages } from '@/i18n';

/**
 * The rules, on a rail that fills in as you scroll past it. Each step is shown
 * next to the screen it happens on, so the explanation and the evidence are
 * never more than an inch apart.
 */
export function Steps({ m }: { m: Messages }) {
  const data = m.steps.items.map((step, i) => ({
    title: String(i + 1).padStart(2, '0'),
    content: (
      <div className="flex flex-col gap-8 pb-4 md:flex-row md:items-center md:gap-12">
        <div className="max-w-xl">
          <h3 className="display text-2xl sm:text-3xl">{step.title}</h3>
          <p className="mt-4 text-sm leading-relaxed text-white/60 sm:text-base">{step.body}</p>
        </div>
        <Phone shot={step.shot} alt={step.shotAlt} className="w-[190px] md:w-[220px]" />
      </div>
    ),
  }));

  return (
    <section id="how" className="relative">
      <Timeline
        data={data}
        heading={<h2 className="display text-4xl sm:text-6xl">{m.steps.heading}</h2>}
        sub={<p className="mt-4 max-w-lg text-sm text-white/55 sm:text-base">{m.steps.sub}</p>}
      />
    </section>
  );
}
