import { app } from '@blame-game/brand';

import { LogoMark } from '@/components/site/logo';
import { cn, shell } from '@/lib/utils';
import { locales, pathFor, type Locale, type Messages } from '@/i18n';

export function Footer({ locale, m }: { locale: Locale; m: Messages }) {
  return (
    <footer className="border-t border-white/10 py-14">
      <div className={cn(shell, 'flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between')}>
        <div>
          <div className="flex items-center gap-3">
            <LogoMark className="h-8 w-8" />
            <span className="display text-lg uppercase">{app.name}</span>
          </div>
          <p className="mt-3 text-sm text-white/55">{m.footer.tagline}</p>
        </div>

        <div className="flex flex-col gap-3 text-sm text-white/45 sm:items-end">
          <nav aria-label={m.nav.languageLabel} className="flex gap-4">
            {locales.map((l) => (
              <a
                key={l}
                href={pathFor(l)}
                hrefLang={l}
                aria-current={l === locale ? 'true' : undefined}
                className={l === locale ? 'text-white' : 'transition-colors hover:text-white/80'}
              >
                {l === 'en' ? 'English' : 'Deutsch'}
              </a>
            ))}
          </nav>
          <p>{m.footer.builtWith}</p>
          {/* The demo roll is licensed, not ours. Crediting it is the deal. */}
          <p className="text-xs text-white/30">
            Photographs on this page from{' '}
            <a
              href="https://unsplash.com/license"
              rel="noopener noreferrer"
              className="underline underline-offset-2 transition-colors hover:text-white/60"
            >
              Unsplash
            </a>
            .
          </p>
        </div>
      </div>
    </footer>
  );
}
