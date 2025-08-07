import re
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

class App:
    def __init__(self):
        self.routes = {}
        self.templates = {}
        self._load_templates()

    def route(self, path):
        """Decorator to register routes"""
        def wrapper(func):
            self.routes[path] = func
            return func
        return wrapper

    def render(self, template_name, **kwargs):
        """Render HTML from loaded templates"""
        if template_name not in self.templates:
            return f"Template '{template_name}' not found!"
        html = self.templates[template_name]
        for k, v in kwargs.items():
            html = html.replace(f"{{{{ {k} }}}}", str(v))
        return html

    def _load_templates(self):
        """Read templates.html and split by {% template %}"""
        if not os.path.exists("templates.html"):
            print("templates.html not found!")
            return
        with open("templates.html", "r", encoding="utf-8") as f:
            content = f.read()

        matches = re.findall(r"\{\% template \"(.*?)\" \%\}(.*?)(?=\{\% template|$)", content, re.S)
        for name, html in matches:
            self.templates[name.strip()] = html.strip()

    def run(self, host="localhost", port=8000):
        """Run the HTTP server"""
        app_ref = self

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
