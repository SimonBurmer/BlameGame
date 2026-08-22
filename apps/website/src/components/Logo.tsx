interface LogoProps {
  /** Raw SVG source, read from assets/branding at build time. */
  readonly svg: string;
  readonly size: number;
}

/**
 * The app mark, inlined rather than linked: it is small, it needs to inherit
 * nothing, and one fewer request on a landing page is one fewer thing between
 * the visitor and the first paint.
 */
export function Logo({ svg, size }: LogoProps) {
  const sized = svg.replace(
    /width="\d+" height="\d+"/,
    `width="${size}" height="${size}"`,
  );
  return <span className="logo" aria-hidden="true" dangerouslySetInnerHTML={{ __html: sized }} />;
}
