import { Cta } from './components/Cta';
import { Faq } from './components/Faq';
import { Features } from './components/Features';
import { Footer } from './components/Footer';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { Steps } from './components/Steps';
import type { Locale, Messages } from './i18n';

interface AppProps {
  readonly locale: Locale;
  readonly m: Messages;
  readonly logoSvg: string;
}

export function App({ locale, m, logoSvg }: AppProps) {
  return (
    <>
      <a className="skip-link" href="#main">
        {m.nav.skipToContent}
      </a>
      <div className="page">
        <Header locale={locale} m={m} logoSvg={logoSvg} />
        <main id="main">
          <Hero m={m} logoSvg={logoSvg} />
          <Steps m={m} />
          <Features m={m} />
          <Faq m={m} />
          <Cta m={m} />
        </main>
        <Footer m={m} />
      </div>
    </>
  );
}
