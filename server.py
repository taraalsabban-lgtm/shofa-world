import http.server
import socketserver
import os
import time
import json
import threading
import urllib.parse
import urllib.request
from collections import defaultdict

PORT = 5000

# ── Formspree endpoint IDs (server-side only, not exposed in public HTML) ──
_FS_NEWSLETTER = "mgorgdkv"
_FS_SHOFA      = "mbdqnwga"

# ── IP-based rate limiter: max 5 submissions per 60 s per IP per form ──
_rate_lock  = threading.Lock()
_rate_store = defaultdict(list)   # key: (ip, form) → [timestamps]

_RATE_LIMIT   = 5
_RATE_WINDOW  = 60   # seconds

def _is_rate_limited(ip, form):
    key = (ip, form)
    now = time.time()
    with _rate_lock:
        timestamps = [t for t in _rate_store[key] if now - t < _RATE_WINDOW]
        _rate_store[key] = timestamps
        if len(timestamps) >= _RATE_LIMIT:
            return True
        _rate_store[key].append(now)
    return False

def _forward_to_formspree(form_id, post_bytes, content_type, forwarded_headers=None):
    """Forward raw form bytes to Formspree and return (status_code, json_body)."""
    url = f"https://formspree.io/f/{form_id}"
    fwd = forwarded_headers or {}
    req = urllib.request.Request(
        url,
        data=post_bytes,
        headers={
            "Content-Type":  content_type,
            "Accept":        "application/json",
            "User-Agent":    fwd.get("User-Agent",  "Mozilla/5.0"),
            "Origin":        fwd.get("Origin",      ""),
            "Referer":       fwd.get("Referer",     ""),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except Exception:
            body = {"error": str(exc)}
        return exc.code, body
    except Exception as exc:
        return 502, {"error": str(exc)}


class Handler(http.server.SimpleHTTPRequestHandler):

    # ── GET: serve public files ──────────────────────────────────────────────
    def do_GET(self):
        if self.path in ('/', ''):
            self.path = '/index.html'
        parsed_path = urllib.parse.urlparse(self.path).path
        for part in parsed_path.split('/'):
            if part.startswith('.'):
                self.send_error(404, "Not Found")
                return
        return super().do_GET()

    # ── POST: proxy form submissions ─────────────────────────────────────────
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == '/api/submit/newsletter':
            form_id = _FS_NEWSLETTER
        elif path == '/api/submit/shofa':
            form_id = _FS_SHOFA
        else:
            self.send_error(404, "Not Found")
            return

        # Determine caller IP (respects Replit's reverse-proxy header)
        ip = (
            self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or self.client_address[0]
        )

        if _is_rate_limited(ip, form_id):
            self._json_response(429, {"error": "Too many requests. Please wait a moment."})
            return

        # Read and forward the body as-is
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        ctype  = self.headers.get("Content-Type", "application/x-www-form-urlencoded")

        fwd_headers = {
            "User-Agent": self.headers.get("User-Agent", "Mozilla/5.0"),
            "Origin":     self.headers.get("Origin", ""),
            "Referer":    self.headers.get("Referer", ""),
        }
        status, payload = _forward_to_formspree(form_id, body, ctype, fwd_headers)
        self._json_response(status, payload)

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _json_response(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def list_directory(self, path):
        self.send_error(403, "Forbidden")
        return None

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        pass


os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
