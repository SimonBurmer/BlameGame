import TiltedCard from './reactbits/TiltedCard';
import type { Messages } from '../i18n';

/**
 * Real captures from a simulator, taken by scripts/capture-app-screenshots.sh
 * rather than mocked up — what is on these phones is what the app renders.
 */
export function Shots({ m }: { readonly m: Messages }) {
  return (
    <section id="screenshots" className="section">
      <h2>{m.shots.heading}</h2>
      <p className="section-sub">{m.shots.sub}</p>
      <div className="shot-grid">
        {m.shots.items.map((shot) => (
          <figure className="shot" key={shot.file}>
            <div className="shot-frame">
              <TiltedCard
                imageSrc={`/screenshots/${shot.file}.jpg`}
                altText={shot.alt}
                containerHeight="420px"
                containerWidth="100%"
                imageHeight="420px"
                imageWidth="194px"
                rotateAmplitude={10}
                scaleOnHover={1.04}
                showMobileWarning={false}
                showTooltip={false}
              />
            </div>
            <figcaption className="shot-caption">{shot.caption}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
