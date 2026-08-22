import AppKit

// Rasterizes an SVG to square PNGs. AppKit is the only decoder on macOS that
// reads SVG (ImageIO has no SVG type), and drawing through an explicit CGContext
// is what lets us emit the opaque PNGs the iOS AppIcon set requires — sips can
// render the SVG but always writes an alpha channel.
_ = NSApplication.shared

let a = CommandLine.arguments
guard a.count >= 4 else {
    fputs("usage: rast <svg> <opaque|alpha> <out.png:size>...\n", stderr); exit(2)
}
let opaque = a[2] == "opaque"
guard let img = NSImage(contentsOf: URL(fileURLWithPath: a[1])) else {
    fputs("rast: cannot read \(a[1])\n", stderr); exit(1)
}
// Rasterize once at the largest size asked for, then scale down from that.
let maxSize = a.dropFirst(3).compactMap { Int($0.split(separator: ":").last ?? "") }.max() ?? 1024
var box = NSRect(x: 0, y: 0, width: maxSize, height: maxSize)
guard let master = img.cgImage(forProposedRect: &box, context: nil, hints: nil) else {
    fputs("rast: cannot rasterize \(a[1])\n", stderr); exit(1)
}

for spec in a.dropFirst(3) {
    let p = spec.split(separator: ":")
    guard p.count == 2, let n = Int(p[1]) else { fputs("rast: bad spec \(spec)\n", stderr); exit(2) }
    let info: CGImageAlphaInfo = opaque ? .noneSkipLast : .premultipliedLast
    guard let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: info.rawValue) else {
        fputs("rast: cannot make a \(n)px context\n", stderr); exit(1)
    }
    ctx.interpolationQuality = .high
    ctx.draw(master, in: CGRect(x: 0, y: 0, width: n, height: n))
    let out = URL(fileURLWithPath: String(p[0]))
    guard let scaled = ctx.makeImage(),
          let dest = CGImageDestinationCreateWithURL(out as CFURL, "public.png" as CFString, 1, nil) else {
        fputs("rast: cannot write \(out.path)\n", stderr); exit(1)
    }
    CGImageDestinationAddImage(dest, scaled, nil)
    guard CGImageDestinationFinalize(dest) else { fputs("rast: write failed \(out.path)\n", stderr); exit(1) }
}
