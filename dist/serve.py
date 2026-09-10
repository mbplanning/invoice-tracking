from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        return SimpleHTTPRequestHandler.end_headers(self)


if __name__ == "__main__":
    print("Serving http://127.0.0.1:18911/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18911), NoCacheHandler).serve_forever()
