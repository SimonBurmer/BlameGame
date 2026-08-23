import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // The site is a static artefact: a folder of HTML that any host can serve.
  // There is nothing here that needs a server, and `out/` keeps the deploy
  // story the same as it was before Next.
  output: 'export',
  // `next/image`'s optimiser needs a server. Exported builds serve the files
  // as they are, so the images are sized correctly at build time instead.
  images: { unoptimized: true },
  trailingSlash: true,
  // packages/brand is TypeScript source, not a built package.
  transpilePackages: ['@blame-game/brand'],
};

export default nextConfig;
