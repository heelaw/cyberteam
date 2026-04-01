#!/usr/bin/env python3
"""CyberTeam Studio - Combined Server (Static + API Proxy + SSE)

Architecture:
  3000 → Static Files (webui/dist)
  3000 → /api/* → Proxy to localhost:8000 (FastAPI Backend)
  3000 → /api/v1/sse/* → Proxy to localhost:8000 (SSE Stream)

Uses ThreadingHTTPServer to avoid SSE blocking all requests.
"""
from __future__ import annotations

import os
import sys
import json
import mimetypes
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# --- Config ---
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
BACKEND = "http://localhost:8000"
DIST = str(Path(__file__).parent / "webui" / "dist")

# SPA routes - serve index.html for these paths
SPA_ROUTES = ["/", "/chat", "/agents", "/projects", "/skills", "/settings", "/login"]

# MIME types
MIME_MAP = {
    ".html": "text/html",
    ".js": "application/javascript",
    ".mjs": "application/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}


class Handler(BaseHTTPRequestHandler):
    """Combined handler: static files + API proxy + SSE."""

    def log_message(self, fmt, *args):
        # Quiet logs for health checks
        msg = fmt % args
        if "/health" not in msg:
            print(f"  [{self.command}] {msg}")

    # ---- CORS ----
    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ---- GET ----
    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy("GET")
        elif self.path == "/health":
            self._json_response(200, {"status": "ok", "service": "cyberteam-studio"})
        else:
            self._serve_static()

    # ---- POST ----
    def do_POST(self):
        if self.path.startswith("/api/"):
            self._proxy("POST")
        else:
            self._error(405, "Method not allowed")

    # ---- PUT ----
    def do_PUT(self):
        if self.path.startswith("/api/"):
            self._proxy("PUT")
        else:
            self._error(405, "Method not allowed")

    # ---- DELETE ----
    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._proxy("DELETE")
        else:
            self._error(405, "Method not allowed")

    # ---- Static Files ----
    def _serve_static(self):
        path = self.path.split("?")[0]  # strip query string

        # SPA fallback: if no file extension, serve index.html
        if path in SPA_ROUTES or (not Path(DIST + path).suffix and path != "/"):
            file_path = os.path.join(DIST, "index.html")
        else:
            # Security: prevent path traversal
            file_path = os.path.normpath(os.path.join(DIST, path.lstrip("/")))
            if not file_path.startswith(DIST):
                self._error(403, "Forbidden")
                return

        if not os.path.isfile(file_path):
            # Final fallback to index.html for SPA routing
            file_path = os.path.join(DIST, "index.html")

        if not os.path.isfile(file_path):
            self._error(404, "Not found")
            return

        # Determine MIME type
        ext = os.path.splitext(file_path)[1]
        mime = MIME_MAP.get(ext, mimetypes.guess_type(file_path)[0] or "application/octet-stream")

        with open(file_path, "rb") as f:
            data = f.read()

        self.send_response(200)
        self.send_header("Content-Type", f"{mime}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    # ---- API Proxy ----
    def _proxy(self, method: str):
        url = f"{BACKEND}{self.path}"

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        # Build upstream headers
        headers = {}
        for h in ["Authorization", "Content-Type", "Accept"]:
            v = self.headers.get(h)
            if v:
                headers[h] = v

        req = Request(url, data=body, headers=headers, method=method)

        try:
            resp = urlopen(req, timeout=30)
            self._stream_response(resp)
        except HTTPError as e:
            # Forward backend error responses
            error_body = e.read() if e.fp else b""
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(error_body)
        except URLError as e:
            self._error(502, f"Backend unreachable: {e.reason}")
        except Exception as e:
            self._error(502, str(e))

    def _stream_response(self, resp):
        """Stream response from backend, supports both regular and SSE."""
        content_type = resp.headers.get("Content-Type", "")

        self.send_response(resp.status)

        # Forward headers
        for k, v in resp.headers.items():
            k_lower = k.lower()
            if k_lower not in ("transfer-encoding", "connection", "server"):
                self.send_header(k, v)
        self._cors_headers()
        self.end_headers()

        # Stream body in chunks
        try:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except Exception:
            pass  # Client disconnected, that's fine

    # ---- Helpers ----
    def _json_response(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _error(self, code: int, msg: str):
        self._json_response(code, {"error": msg})


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"""
┌─────────────────────────────────────────────────┐
│  🚀 CyberTeam Studio                           │
├─────────────────────────────────────────────────┤
│  Frontend: http://localhost:{PORT}               │
│  Backend:  {BACKEND}                            │
│  Static:   {DIST}   │
├─────────────────────────────────────────────────┤
│  ThreadingHTTPServer · SSE Safe                  │
└─────────────────────────────────────────────────┘
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
