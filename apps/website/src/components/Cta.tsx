import type { Messages } from '../i18n';

export function Cta({ m }: { readonly m: Messages }) {
  return (
    <section className="cta">
      <h2>{m.cta.heading}</h2>
      <p>{m.cta.body}</p>
    </section>
  );
}
