import { stores } from '@blame-game/brand';
import Magnet from './reactbits/Magnet';
import type { Messages } from '../i18n';

/** Apple's mark, drawn rather than linked so the button needs no asset. */
function AppleGlyph() {
  return (
    <svg width="26" height="30" viewBox="0 0 26 30" aria-hidden="true" focusable="false">
      <path
        fill="currentColor"
        d="M21.3 15.9c0-3.5 2.8-5.1 2.9-5.2-1.6-2.3-4-2.6-4.9-2.7-2.1-.2-4.1 1.2-5.2 1.2-1.1 0-2.7-1.2-4.4-1.2-2.3 0-4.4 1.3-5.6 3.4-2.4 4.1-.6 10.2 1.7 13.6 1.1 1.6 2.5 3.5 4.3 3.4 1.7-.1 2.3-1.1 4.4-1.1s2.6 1.1 4.4 1.1c1.8 0 2.9-1.7 4-3.3 1.3-1.9 1.8-3.7 1.8-3.8-.1 0-3.4-1.3-3.4-5.4zM17.9 5.3c.9-1.1 1.5-2.7 1.4-4.3-1.4.1-3.1.9-4 2-.8 1-1.6 2.6-1.4 4.2 1.6.1 3.1-.8 4-1.9z"
      />
    </svg>
  );
}

/**
 * Magnet makes the button lean toward the cursor. It is a wrapper, so the
 * anchor inside is a plain link: keyboard, right-click and crawlers all get
 * the real thing.
 */
export function AppStoreButton({ m }: { readonly m: Messages }) {
  return (
    <Magnet padding={90} magnetStrength={6}>
      <a className="app-store-button" href={stores.appStore}>
        <AppleGlyph />
        <span>
          <span className="store-eyebrow">{m.hero.primaryCtaEyebrow}</span>
          <span className="store-name">{m.hero.primaryCta}</span>
        </span>
      </a>
    </Magnet>
  );
}
