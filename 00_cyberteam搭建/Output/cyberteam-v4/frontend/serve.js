/**
 * CyberTeam V4 Frontend Dev Server
 * - Serves pre-built static files from dist/
 * - Proxies /api/* requests to backend (port 8000)
 * Usage: node serve.js [--port PORT]
 */
import http from 'http';
import fs from 'fs';
import path from 'path';
import url from 'url';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Parse arguments
const args = process.argv.slice(2);
const portArg = args.find(a => a.startsWith('--port='));
const PORT = portArg ? parseInt(portArg.split('=')[1]) : 5173;
const BACKEND_PORT = 8000;
const DIST_DIR = path.join(__dirname, 'dist');

// MIME types
const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.mjs': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.map': 'application/json',
};

function getContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return mimeTypes[ext] || 'application/octet-stream';
}

function proxyRequest(req, res, pathname) {
  const options = {
    hostname: 'localhost',
    port: BACKEND_PORT,
    path: pathname,
    method: req.method,
    headers: {
      ...req.headers,
      'X-Forwarded-For': req.socket.remoteAddress,
      'X-Forwarded-Proto': 'http',
    },
  };
  delete options.headers.host;

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (err) => {
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Backend unavailable', detail: err.message }));
  });

  req.pipe(proxyReq);
}

function serveStatic(req, res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        const indexPath = path.join(DIST_DIR, 'index.html');
        fs.readFile(indexPath, (err2, indexData) => {
          if (err2) {
            res.writeHead(404);
            res.end('404 Not Found');
          } else {
            res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
            res.end(indexData);
          }
        });
      } else {
        res.writeHead(500);
        res.end('500 Internal Server Error');
      }
      return;
    }

    const contentType = getContentType(filePath);
    const headers = { 'Content-Type': contentType, 'Cache-Control': 'public, max-age=31536000' };
    res.writeHead(200, headers);
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  const pathname = parsed.pathname;

  if (pathname.startsWith('/api/')) {
    proxyRequest(req, res, pathname);
    return;
  }

  let filePath = (pathname === '/' || pathname === '')
    ? path.join(DIST_DIR, 'index.html')
    : path.join(DIST_DIR, pathname.replace(/^\//, ''));

  if (!filePath.startsWith(DIST_DIR)) {
    res.writeHead(403);
    res.end('403 Forbidden');
    return;
  }

  serveStatic(req, res, filePath);
});

server.listen(PORT, () => {
  console.log(`\n🚀 CyberTeam V4 Frontend  |  http://localhost:${PORT}/  |  Backend: localhost:${BACKEND_PORT}\n`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`❌ Port ${PORT} in use. Try: node serve.js --port=5174`);
  }
  process.exit(1);
});
