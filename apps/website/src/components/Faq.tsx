import type { Messages } from '../i18n';

export function Faq({ m }: { readonly m: Messages }) {
  return (
    <section id="faq" className="section">
      <h2>{m.faq.heading}</h2>
      <div className="faq">
        {/* <details> gives an accordion with no JavaScript, and crawlers read
            the answer whether or not it is open. */}
        {m.faq.items.map((item) => (
          <details key={item.question} className="faq-item">
            <summary>
              <h3>{item.question}</h3>
            </summary>
            <p>{item.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
