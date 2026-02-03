from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import os

LOG_FILE = "visits.log"
OWNER_TOKEN = os.environ.get("OWNER_TOKEN", "change-this-token")

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/__owner__/logs"):
            token = ""
            if "?" in self.path:
                qs = self.path.split("?", 1)[1]
                for kv in qs.split("&"):
                    if kv.startswith("token="):
                        token = kv.split("=", 1)[1]

            if token != OWNER_TOKEN:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"No visits yet.")
            return

        if self.path in ("/", "/index.html"):
            ip = self.client_address[0]
            ua = self.headers.get("User-Agent", "")
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{t} | ip={ip} | ua={ua}\n")

        return super().do_GET()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    httpd.serve_forever()
