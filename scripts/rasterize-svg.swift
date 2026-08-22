import AppKit

// Rasterizes an SVG to square PNGs. AppKit is the only decoder on macOS that
// reads SVG (ImageIO has no SVG type), and drawing through an explicit CGContext
// is what lets us emit the opaque PNGs the iOS AppIcon set requires — sips can
// render the SVG but always writes an alpha channel.
_ = NSApplication.shared

let a = CommandLine.arguments
guard a.count >= 4 else {
    fputs("usage: rast <svg> <opaque|alpha> <out.png:size|out.png:WxH>...\n", stderr); exit(2)
}

/// A spec is either `file.png:512` (square) or `file.png:1200x630`.
func parse(_ spec: String) -> (path: String, w: Int, h: Int)? {
    let parts = spec.split(separator: ":")
    guard parts.count == 2 else { return nil }
    let dims = parts[1].split(separator: "x")
    if dims.count == 1, let n = Int(dims[0]) { return (String(parts[0]), n, n) }
    if dims.count == 2, let w = Int(dims[0]), let h = Int(dims[1]) { return (String(parts[0]), w, h) }
    return nil
}
let opaque = a[2] == "opaque"
guard let img = NSImage(contentsOf: URL(fileURLWithPath: a[1])) else {
    fputs("rast: cannot read \(a[1])\n", stderr); exit(1)
}
// Rasterize once at the largest edge asked for, then scale down from that.
let maxSize = a.dropFirst(3).compactMap { parse($0).map { max($0.w, $0.h) } }.max() ?? 1024
var box = NSRect(x: 0, y: 0, width: maxSize, height: maxSize)
guard let master = img.cgImage(forProposedRect: &box, context: nil, hints: nil) else {
    fputs("rast: cannot rasterize \(a[1])\n", stderr); exit(1)
}

for spec in a.dropFirst(3) {
    guard let (path, w, h) = parse(spec) else { fputs("rast: bad spec \(spec)\n", stderr); exit(2) }
    let info: CGImageAlphaInfo = opaque ? .noneSkipLast : .premultipliedLast
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: info.rawValue) else {
        fputs("rast: cannot make a \(w)x\(h) context\n", stderr); exit(1)
    }
    ctx.interpolationQuality = .high
    ctx.draw(master, in: CGRect(x: 0, y: 0, width: w, height: h))
    let out = URL(fileURLWithPath: path)
    guard let scaled = ctx.makeImage(),
          let dest = CGImageDestinationCreateWithURL(out as CFURL, "public.png" as CFString, 1, nil) else {
        fputs("rast: cannot write \(out.path)\n", stderr); exit(1)
    }
    CGImageDestinationAddImage(dest, scaled, nil)
    guard CGImageDestinationFinalize(dest) else { fputs("rast: write failed \(out.path)\n", stderr); exit(1) }
}
