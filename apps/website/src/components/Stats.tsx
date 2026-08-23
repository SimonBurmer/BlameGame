import CountUp from './reactbits/CountUp';
import type { Messages } from '../i18n';

/** The numbers are the game's real server-side limits, from packages/brand. */
export function Stats({ m }: { readonly m: Messages }) {
  return (
    <section className="section">
      <div className="stats">
        {m.stats.map((stat) => (
          <div className="stat" key={stat.label}>
            <div className="stat-value" data-animates>
              <CountUp to={stat.value} duration={1.4} />
              {stat.suffix}
            </div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
