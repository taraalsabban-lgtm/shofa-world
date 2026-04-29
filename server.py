import http.server
import socketserver
import os
import urllib.parse

PORT = 5000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        parsed_path = urllib.parse.urlparse(self.path).path
        parts = parsed_path.split('/')
        for part in parts:
            if part.startswith('.'):
                self.send_error(404, "Not Found")
                return
        return super().do_GET()

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
