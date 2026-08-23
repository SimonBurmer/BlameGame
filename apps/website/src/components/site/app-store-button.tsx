'use client';

import { stores } from '@blame-game/brand';

import { HoverBorderGradient } from '@/components/ui/hover-border-gradient';
import { cn } from '@/lib/utils';

/** Apple's mark, drawn rather than fetched: it is one path and no request. */
function AppleGlyph({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 384 512" aria-hidden="true" className={className} fill="currentColor">
      <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
    </svg>
  );
}

/**
 * The store button.
 *
 * `stores.appStore` in packages/brand is an empty string, because there is no
 * listing yet — so this renders an anchor with no `href`, which is not a link:
 * it cannot be tabbed to and it cannot navigate anywhere. Paste the URL into
 * packages/brand and every one of these becomes a real link at once.
 */
export function AppStoreButton({
  label,
  eyebrow,
  className,
}: {
  label: string;
  eyebrow: string;
  className?: string;
}) {
  const href = stores.appStore || undefined;
  // `as="span"` because the whole thing is wrapped in the link: the component
  // renders a <button> by default, and a button inside an anchor is not markup
  // a browser is required to make sense of.
  const button = (
    <HoverBorderGradient
      as="span"
      containerClassName={cn('rounded-xl', className)}
      className="flex items-center gap-3 bg-ink px-5 py-3 text-left"
    >
      <AppleGlyph className="h-7 w-7" />
      <span className="leading-tight">
        <span className="block text-[0.62rem] tracking-[0.18em] text-white/55 uppercase">
          {eyebrow}
        </span>
        <span className="block text-lg font-semibold">{label}</span>
      </span>
    </HoverBorderGradient>
  );

  if (!href) {
    return (
      <span aria-disabled="true" className="inline-flex w-fit">
        {button}
      </span>
    );
  }
  return (
    <a href={href} className="inline-flex w-fit">
      {button}
    </a>
  );
}
