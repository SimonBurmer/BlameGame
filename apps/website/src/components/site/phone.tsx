import { cn } from '@/lib/utils';

/**
 * A phone bezel around a screenshot.
 *
 * The captures already contain the status bar and the Dynamic Island, because
 * they are what the simulator actually displayed — this only adds the hardware
 * around them, so the pictures still read as a phone once they are off a phone.
 */
export function Phone({
  shot,
  alt,
  className,
  priority = false,
}: {
  shot: string;
  alt: string;
  className?: string;
  priority?: boolean;
}) {
  return (
    <div
      className={cn(
        'relative aspect-[9/19.5] w-[240px] shrink-0 rounded-[2.2rem] border border-white/15 bg-black p-[3px] shadow-[0_30px_80px_-20px_rgba(0,0,0,0.85)]',
        className,
      )}
    >
      <div className="absolute inset-0 rounded-[2.2rem] ring-1 ring-white/5 ring-inset" />
      {/* eslint-disable-next-line @next/next/no-img-element -- the export has no image optimiser; these are pre-sized by scripts/prepare-screenshots.sh */}
      <img
        src={`/screenshots/${shot}.jpg`}
        alt={alt}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        className="h-full w-full rounded-[2rem] object-cover"
      />
    </div>
  );
}
