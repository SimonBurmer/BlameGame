import { app } from '@blame-game/brand';
import type { Messages } from '../i18n';

export function Footer({ m }: { readonly m: Messages }) {
  return (
    <footer className="site-footer">
      <p className="footer-tagline">{m.footer.tagline}</p>
      <p className="footer-meta">
        <span>
          © {new Date().getFullYear()} {app.name}
        </span>
        <span aria-hidden="true">·</span>
        <span>{m.footer.builtWith}</span>
      </p>
    </footer>
  );
}
