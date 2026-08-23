# Demo photos

Stand-in camera-roll photos for the marketing-screenshot run
(`scripts/capture-app-screenshots.sh`).

They are drawn rather than real on purpose: a screenshot of a game about
people's private photos should not contain anybody's private photos.

`scripts/generate-demo-photos.sh` rasterizes these and regenerates
`integration_test/demo_photos.g.dart`, which is how the bytes reach the test —
the test runs on the device and cannot read files from this machine.
