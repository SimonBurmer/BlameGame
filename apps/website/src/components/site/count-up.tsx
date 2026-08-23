'use client';

import { animate, useInView } from 'motion/react';
import { useEffect, useRef } from 'react';

/**
 * A number that counts up the first time it is scrolled into view.
 *
 * Written here rather than pulled from the Aceternity registry: the registry's
 * number ticker is one of the paid blocks and ships no source. It animates with
 * `motion`, which is what every vendored component on this page uses, so it
 * moves like the rest of them.
 *
 * The digits are written straight to the text node instead of through React
 * state — sixty renders a second to change one string is work for nothing, and
 * it keeps the whole animation out of the render path. The server emits the
 * finished number, so the figure is in the HTML for a crawler and is what a
 * reader with scripting off is left looking at; the client blanks it to zero as
 * it mounts, which is long before this band can be scrolled to.
 */
export function CountUp({
  to,
  suffix = '',
  locale = 'en',
  duration = 1.8,
  className,
}: {
  to: number;
  suffix?: string;
  /** BCP-47 tag: the thousands separator is not the same in every language. */
  locale?: string;
  duration?: number;
  className?: string;
}) {
  const wrapRef = useRef<HTMLSpanElement>(null);
  const numRef = useRef<HTMLSpanElement>(null);
  const inView = useInView(wrapRef, { once: true, amount: 0.6 });

  useEffect(() => {
    const node = numRef.current;
    if (!node) return;
    const format = new Intl.NumberFormat(locale);

    if (!inView) {
      node.textContent = format.format(0);
      return;
    }
    const controls = animate(0, to, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => {
        node.textContent = format.format(Math.round(v));
      },
    });
    return () => controls.stop();
  }, [inView, to, duration, locale]);

  return (
    <span ref={wrapRef} className={className}>
      <span ref={numRef}>{new Intl.NumberFormat(locale).format(to)}</span>
      {suffix}
    </span>
  );
}
