# Demo photos

Real photographs, used as the camera-roll contents when the app is driven for
the marketing screenshots (`scripts/capture-app-screenshots.sh`) and shown on the
website. They are **not** shipped in the app bundle — nothing here is referenced
from `pubspec.yaml`.

A game about people's camera rolls should be photographed with photographs, not
with drawings. These replaced a set of generated SVG gradients that looked
exactly like what they were.

## Where they go

- `scripts/generate-demo-photos.sh` downscales them and writes
  `integration_test/demo_photos.g.dart`, the fixture the screenshot driver
  uploads to the backend, so the photos inside the app screenshots are these.
- The same script copies web-sized copies into `apps/website/public/photos/`,
  so the site and the screenshots show the same roll.
- `scripts/capture-app-screenshots.sh` also loads them into the simulator's
  photo library with `xcrun simctl addmedia`, so the in-app picker has real
  photos in it too.

Re-running the generator is what keeps those three in sync; do not hand-edit the
generated files.

## Credits

All twelve are from Unsplash, via <https://picsum.photos>, and are used under the
[Unsplash licence](https://unsplash.com/license) (free for commercial use, no
permission needed, attribution appreciated — hence this table).

| File | Photographer | Source |
| --- | --- | --- |
| 01-cat.jpg | Ryan Mcguire | <https://unsplash.com/photos/N-1XGL54pQg> |
| 02-santorini.jpg | Margaret Barley | <https://unsplash.com/photos/Qo51KwK1dKg> |
| 03-party-lights.jpg | Sebastian Muller | <https://unsplash.com/photos/VLdaxYyXJvw> |
| 04-sunglasses.jpg | Alexander Shustov | <https://unsplash.com/photos/AHBiSKaENwc> |
| 05-bench-sunset.jpg | Charlie Foster | <https://unsplash.com/photos/A88emaZe7d8> |
| 06-hiker.jpg | Danka & Peter | <https://unsplash.com/photos/tvicgTdh7Fg> |
| 07-leopard.jpg | Martyn Seddon | <https://unsplash.com/photos/7iB4OZDlRok> |
| 08-bridge-night.jpg | Anders Jildén | <https://unsplash.com/photos/nrLtvA05jk8> |
| 09-kitchen.jpg | Webvilla | <https://unsplash.com/photos/hv1MrBzGGNY> |
| 10-market.jpg | Steven Lewis | <https://unsplash.com/photos/r4He4Btlsro> |
| 11-balloon.jpg | Austin Ban | <https://unsplash.com/photos/0fjGQmYCRW8> |
| 12-coffee.jpg | Carli Jean | <https://unsplash.com/photos/UWRqlJcDCXA> |
