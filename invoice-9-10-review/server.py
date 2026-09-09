"""Local server for the Invoice 9 / Invoice 10 review tool.

Chrome blocks local JSON and PDF fetches from file://.
From this folder:

    python server.py

Then open http://127.0.0.1:8770/
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PORT = 8770


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".css": "text/css",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Invoice 9 / 10 review: {url}")
    print("Leave this window open.")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
