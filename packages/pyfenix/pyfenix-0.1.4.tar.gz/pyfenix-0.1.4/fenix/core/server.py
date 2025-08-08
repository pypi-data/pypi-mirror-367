from http.server import BaseHTTPRequestHandler, HTTPServer

def run_server(app_ref, host="localhost", port=8000):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in app_ref.routes:
                content = app_ref.routes[self.path]()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")

    server = HTTPServer((host, port), Handler)
    print(f"🚀 FeniX running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
