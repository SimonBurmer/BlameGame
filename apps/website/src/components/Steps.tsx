import type { Messages } from '../i18n';

export function Steps({ m }: { readonly m: Messages }) {
  return (
    <section id="how-it-works" className="section">
      <h2>{m.steps.heading}</h2>
      <ol className="steps">
        {m.steps.items.map((step, i) => (
          <li key={step.title} className="step">
            <span className="step-number" aria-hidden="true">
              {i + 1}
            </span>
            <h3>{step.title}</h3>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
