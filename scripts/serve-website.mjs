// Tiny static server for previewing apps/website/dist locally.
// Node's http module only — the site is static files, nothing more is needed.
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve } from 'node:path';

const root = resolve(process.argv[2] ?? 'apps/website/dist');
const port = Number(process.env.PORT ?? 4173);

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
};

async function resolveFile(urlPath) {
  // normalize() collapses ".." before we join, so a crafted URL cannot escape root.
  const candidate = join(root, normalize(decodeURIComponent(urlPath)));
  if (!candidate.startsWith(root)) return null;
  try {
    const info = await stat(candidate);
    if (info.isDirectory()) return resolveFile(join(urlPath, 'index.html'));
    return candidate;
  } catch {
    return null;
  }
}

createServer(async (req, res) => {
  const file = await resolveFile(new URL(req.url ?? '/', 'http://localhost').pathname);
  if (!file) {
    res.writeHead(404, { 'content-type': 'text/plain' });
    res.end('not found');
    return;
  }
  res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' });
  createReadStream(file).pipe(res);
}).listen(port, () => console.log(`serving ${root} on http://localhost:${port}`));
