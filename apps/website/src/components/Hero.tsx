import { limits } from '@blame-game/brand';
import type { Messages } from '../i18n';
import { Logo } from './Logo';

/** Illustrative only. Uses the real alphabet, which drops I, O, 0 and 1 so a
 *  code read aloud cannot be misheard. */
const SAMPLE_ROOM_CODE = 'K7QM2'.slice(0, limits.roomCodeLength);

interface HeroProps {
  readonly m: Messages;
  readonly logoSvg: string;
}

export function Hero({ m, logoSvg }: HeroProps) {
  return (
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">{m.hero.eyebrow}</p>
        <h1>{m.hero.headline}</h1>
        <p className="lede">{m.hero.sub}</p>

        <div className="hero-actions">
          {/* No store buttons until there are store pages to point at. */}
          <p className="availability" role="status">
            {m.hero.availability}
          </p>
          <a className="button-secondary" href="#how-it-works">
            {m.hero.secondaryCta}
          </a>
        </div>
      </div>

      <div className="hero-art" aria-hidden="true">
        <div className="phone">
          <div className="phone-screen">
            <Logo svg={logoSvg} size={72} />
            <p className="phone-title">
              BLAME
              <br />
              GAME
            </p>
            <p className="phone-sub">{m.footer.tagline}</p>
            <span className="phone-code">{SAMPLE_ROOM_CODE}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
