'use client';

import { useState } from 'react';

import {
  MobileNav,
  NavbarButton,
  MobileNavHeader,
  MobileNavMenu,
  MobileNavToggle,
  Navbar,
  NavBody,
  NavItems,
} from '@/components/ui/resizable-navbar';
import { AppStoreButton } from '@/components/site/app-store-button';
import { Wordmark } from '@/components/site/logo';
import { stores } from '@blame-game/brand';
import { locales, pathFor, type Locale, type Messages } from '@/i18n';

function LanguageSwitch({
  locale,
  label,
  className,
}: {
  locale: Locale;
  label: string;
  className?: string;
}) {
  return (
    <div className={className} role="group" aria-label={label}>
      {locales.map((l) => (
        <a
          key={l}
          href={pathFor(l)}
          hrefLang={l}
          aria-current={l === locale ? 'true' : undefined}
          className={`px-1.5 text-xs font-semibold tracking-widest uppercase transition-colors ${
            l === locale ? 'text-white' : 'text-white/40 hover:text-white/80'
          }`}
        >
          {l}
        </a>
      ))}
    </div>
  );
}

export function SiteNav({ locale, m }: { locale: Locale; m: Messages }) {
  const [open, setOpen] = useState(false);
  const items = [
    { name: m.nav.howItWorks, link: '#how' },
    { name: m.nav.features, link: '#features' },
    { name: m.nav.faq, link: '#faq' },
  ];

  return (
    <Navbar className="fixed top-0 inset-x-0 z-50 pt-4">
      <NavBody className="max-w-[88rem] rounded-full border border-white/10 bg-ink/70 px-6 backdrop-blur-md">
        <a href={pathFor(locale)} className="relative z-20 shrink-0 px-2">
          <Wordmark />
        </a>
        <NavItems items={items} className="text-white/60" />
        <div className="relative z-20 flex shrink-0 items-center gap-5">
          <LanguageSwitch
            locale={locale}
            label={m.nav.languageLabel}
            className="flex items-center gap-1 border-r border-white/10 pr-4"
          />
          {/* The full store button is too wide for the pill once it has
              shrunk; in here it is a plain call to action and the real one is
              a screen away in either direction. */}
          <NavbarButton
            href={stores.appStore || undefined}
            aria-disabled={stores.appStore ? undefined : true}
            variant="secondary"
            className="rounded-full bg-brand px-4 py-2 text-sm font-semibold text-white shadow-none dark:text-white"
          >
            {m.hero.primaryCta}
          </NavbarButton>
        </div>
      </NavBody>

      <MobileNav className="bg-ink/80 backdrop-blur-md">
        <MobileNavHeader>
          <a href={pathFor(locale)} className="px-2">
            <Wordmark />
          </a>
          <MobileNavToggle isOpen={open} onClick={() => setOpen((v) => !v)} />
        </MobileNavHeader>
        <MobileNavMenu isOpen={open} onClose={() => setOpen(false)} className="bg-ink-2 text-white">
          {items.map((item) => (
            <a
              key={item.link}
              href={item.link}
              onClick={() => setOpen(false)}
              className="w-full py-2 text-base text-white/80"
            >
              {item.name}
            </a>
          ))}
          <LanguageSwitch locale={locale} label={m.nav.languageLabel} className="flex w-full gap-2 py-2" />
          <AppStoreButton eyebrow={m.hero.primaryCtaEyebrow} label={m.hero.primaryCta} />
        </MobileNavMenu>
      </MobileNav>
    </Navbar>
  );
}
