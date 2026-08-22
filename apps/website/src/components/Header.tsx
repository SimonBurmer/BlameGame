import { app } from '@blame-game/brand';
import { locales, pathFor, type Locale, type Messages } from '../i18n';
import { Logo } from './Logo';

interface HeaderProps {
  readonly locale: Locale;
  readonly m: Messages;
  readonly logoSvg: string;
}

const LANGUAGE_NAMES: Record<Locale, string> = { en: 'EN', de: 'DE' };

export function Header({ locale, m, logoSvg }: HeaderProps) {
  return (
    <header className="site-header">
      <a className="brand" href={pathFor(locale)}>
        <Logo svg={logoSvg} size={34} />
        <span className="brand-name">{app.name}</span>
      </a>

      <nav className="site-nav" aria-label={app.name}>
        <a href="#how-it-works">{m.nav.howItWorks}</a>
        <a href="#features">{m.nav.features}</a>
        <a href="#faq">{m.nav.faq}</a>
      </nav>

      {/* Real links, not a script-driven switch: crawlers follow them and they
          work with JavaScript disabled, which is all of the time here. */}
      <nav className="lang-switch" aria-label={m.nav.languageLabel}>
        {locales.map((other) => (
          <a
            key={other}
            href={pathFor(other)}
            hrefLang={other}
            lang={other}
            aria-current={other === locale ? 'true' : undefined}
            className={other === locale ? 'is-current' : undefined}
          >
            {LANGUAGE_NAMES[other]}
          </a>
        ))}
      </nav>
    </header>
  );
}
