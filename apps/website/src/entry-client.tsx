import { hydrateRoot } from 'react-dom/client';

import { App } from './App';
import { messages, type Locale } from './i18n';

/**
 * Hydrates the prerendered markup.
 *
 * The page is fully readable before this runs — every animated component
 * renders its content on the server and only starts moving once mounted — so
 * this is enhancement, not delivery.
 */
const root = document.getElementById('root');
const payload = document.getElementById('__APP_DATA__')?.textContent;

if (root && payload) {
  const data = JSON.parse(payload) as { locale: Locale; logoSvg: string };
  hydrateRoot(root, <App locale={data.locale} m={messages[data.locale]} logoSvg={data.logoSvg} />);
}
