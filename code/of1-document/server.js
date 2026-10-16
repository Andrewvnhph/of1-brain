// Static file server + CORS proxy cho demo of1-document.
// Chạy: node server.js  →  http://localhost:8765
//
// 2 endpoint:
//   /                     — serve index.html
//   /proxy?url=<xlsx-url> — fetch url server-side, stream về client + CORS headers
//
// Zero deps (Node 18+ built-in fetch).

const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = 8765;
const ROOT = __dirname;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
};

async function handleProxy(req, res, reqUrl) {
  const target = reqUrl.searchParams.get('url');
  if (!target) {
    res.writeHead(400, { 'Access-Control-Allow-Origin': '*' });
    res.end('missing ?url=');
    return;
  }
  try {
    console.log('[proxy] GET', target);
    const t0 = Date.now();
    const upstream = await fetch(target, { redirect: 'follow' });
    const buf = Buffer.from(await upstream.arrayBuffer());
    const elapsed = Date.now() - t0;
    console.log('[proxy]', upstream.status, buf.length, 'bytes', elapsed, 'ms');
    res.writeHead(upstream.status, {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': upstream.headers.get('content-type') || 'application/octet-stream',
      'Content-Length': buf.length,
      'X-Proxy-Elapsed-Ms': String(elapsed),
    });
    res.end(buf);
  } catch (e) {
    console.error('[proxy] FAIL', e.message);
    res.writeHead(502, { 'Access-Control-Allow-Origin': '*' });
    res.end('proxy fail: ' + e.message);
  }
}

function serveStatic(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('not found');
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const reqUrl = new URL(req.url, `http://localhost:${PORT}`);

  if (reqUrl.pathname === '/proxy') {
    handleProxy(req, res, reqUrl);
    return;
  }

  // Static
  const relPath = reqUrl.pathname === '/' ? '/index.html' : reqUrl.pathname;
  const filePath = path.join(ROOT, relPath);
  // Prevent path traversal
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403);
    res.end('forbidden');
    return;
  }
  serveStatic(res, filePath);
});

server.listen(PORT, () => {
  console.log(`of1-document demo running at http://localhost:${PORT}`);
  console.log(`  static  → ${ROOT}`);
  console.log(`  proxy   → http://localhost:${PORT}/proxy?url=<xlsx-url>`);
});
