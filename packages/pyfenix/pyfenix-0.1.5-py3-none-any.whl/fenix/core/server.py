# Fenix/fenix/core/server.py

import os
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

def monitor_py_files():
    py_files = {f: os.path.getmtime(f) for f in Path(".").rglob("*.py")}

    while True:
        time.sleep(1)
        for f, old_mtime in list(py_files.items()):
            if not os.path.exists(f):
                continue
            new_mtime = os.path.getmtime(f)
            if new_mtime != old_mtime:
                print(f"🔄 Python file changed: {f}")
                print("♻️ Restarting server...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

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

    def start():
        server = HTTPServer((host, port), Handler)
        print(f"🚀 FeniX running at http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server shutting down gracefully... Bye!")
            server.server_close()
            sys.exit(0)

    # Background watcher for .py file changes
    threading.Thread(target=monitor_py_files, daemon=True).start()
    start()
