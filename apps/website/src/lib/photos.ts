/**
 * The demo camera roll, as served from `public/photos`.
 *
 * These are the same twelve photographs the app is holding in the screenshots
 * — `scripts/generate-demo-photos.sh` writes both from `assets/demo-photos`,
 * so the roll on the page and the roll in the phone cannot drift apart. See
 * that folder's README for the photographers.
 */
export const photos: readonly string[] = [
  '01-cat',
  '02-santorini',
  '03-party-lights',
  '04-sunglasses',
  '05-bench-sunset',
  '06-hiker',
  '07-leopard',
  '08-bridge-night',
  '09-kitchen',
  '10-market',
  '11-balloon',
  '12-coffee',
].map((n) => `/photos/${n}.jpg`);
