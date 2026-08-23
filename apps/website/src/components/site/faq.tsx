import type { Messages } from '@/i18n';

/**
 * Native `<details>`: it is open-on-search, keyboard-operable and printable
 * without a line of JavaScript, and the answers are in the markup whether or
 * not anything runs. Adding a disclosure library to reproduce that would be a
 * step backwards.
 */
export function Faq({ m }: { m: Messages }) {
  return (
    <section id="faq" className="mx-auto max-w-3xl px-6 py-24 sm:py-32">
      <h2 className="display text-4xl sm:text-6xl">{m.faq.heading}</h2>
      <div className="mt-12 divide-y divide-white/10 border-y border-white/10">
        {m.faq.items.map((item) => (
          <details key={item.question} className="group py-5">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-6 text-left text-base font-medium text-white/90 transition-colors marker:content-none hover:text-white sm:text-lg">
              {item.question}
              <span
                aria-hidden
                className="shrink-0 text-2xl leading-none font-light text-brand transition-transform duration-300 group-open:rotate-45"
              >
                +
              </span>
            </summary>
            <p className="mt-3 max-w-2xl pr-10 text-sm leading-relaxed text-white/55 sm:text-base">
              {item.answer}
            </p>
          </details>
        ))}
      </div>
    </section>
  );
}
