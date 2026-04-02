#!/usr/bin/env python3
"""Simple static file server with API proxy for CyberTeam Studio."""
import http.server
import urllib.request
import urllib.error
import socketserver
import os
import re

PORT = 3000
API_BASE = "http://localhost:8000"

class CyberTeamProxy(http.server.SimpleHTTPRequestHandler):
    """Proxy API requests to backend, serve static files otherwise."""

    def do_GET(self):
        if self.path.startswith('/api/'):
            # Proxy to backend
            url = f"{API_BASE}{self.path}"
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    self.send_response(response.status)
                    self.send_headers(response.headers)
                    self.wfile.write(response.read())
            except urllib.error.URLError as e:
                self.send_error(502, f"Backend error: {e.reason}")
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            # Proxy to backend
            url = f"{API_BASE}{self.path}"
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            try:
                req = urllib.request.Request(url, data=body, method='POST')
                req.headers['Content-Type'] = self.headers.get('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=30) as response:
                    self.send_response(response.status)
                    self.send_headers(response.headers)
                    self.wfile.write(response.read())
            except urllib.error.URLError as e:
                self.send_error(502, f"Backend error: {e.reason}")
        else:
            self.send_error(405)

    def send_headers(self, headers):
        for key, value in headers.items():
            if key.lower() not in ('transfer-encoding', 'connection'):
                self.send_header(key, value)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[CyberTeam] {args[0]}")

# Change to dist directory
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/dist')

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

print(f"Starting CyberTeam Studio on http://localhost:{PORT}")
print(f"API proxy to {API_BASE}")
print(f"Serving static files from {os.getcwd()}")

with ReuseAddrTCPServer(("", PORT), CyberTeamProxy) as httpd:
    httpd.serve_forever()
