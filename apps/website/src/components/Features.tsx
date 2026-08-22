import type { Messages } from '../i18n';

export function Features({ m }: { readonly m: Messages }) {
  return (
    <section id="features" className="section">
      <h2>{m.features.heading}</h2>
      <p className="section-sub">{m.features.sub}</p>
      <ul className="cards">
        {m.features.items.map((feature) => (
          <li key={feature.title} className="card">
            <h3>{feature.title}</h3>
            <p>{feature.body}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
