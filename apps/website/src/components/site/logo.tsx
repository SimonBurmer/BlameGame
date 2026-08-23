import { app } from '@blame-game/brand';

import { cn } from '@/lib/utils';

/**
 * The launcher mark, inlined from `assets/branding/logo_mark.svg`. Inline
 * rather than an <img> so it is crisp at any size and costs no request; the
 * SVG there stays the source, and `scripts/generate-app-icons.sh` still
 * rasterises every icon from it.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 1024 1024" role="img" aria-label={app.name} className={className}>
      <defs>
        <clipPath id="bg-mark-card">
          <rect x="347" y="322" width="330" height="380" rx="40" />
        </clipPath>
      </defs>
      <g transform="translate(512 512) scale(1.28) translate(-512 -512)">
        <rect x="347" y="322" width="330" height="380" rx="40" fill="#FFFFFF" />
        <g clipPath="url(#bg-mark-card)">
          <circle cx="512" cy="459" r="54" fill="#8E97B8" />
          <ellipse cx="512" cy="725" rx="122" ry="137" fill="#8E97B8" />
        </g>
        <circle cx="512" cy="512" r="252" fill="none" stroke="#E94560" strokeWidth="52" />
        {[0, 90, 180, 270].map((deg) => (
          <rect
            key={deg}
            x="491"
            y="150"
            width="42"
            height="100"
            rx="21"
            fill="#E94560"
            transform={`rotate(${deg} 512 512)`}
          />
        ))}
      </g>
    </svg>
  );
}

export function Wordmark({ className }: { className?: string }) {
  return (
    <span className={cn('flex items-center gap-2.5', className)}>
      <LogoMark className="h-7 w-7 shrink-0" />
      <span className="display text-[1.05rem] tracking-tight whitespace-nowrap text-white uppercase">
        {app.name}
      </span>
    </span>
  );
}
