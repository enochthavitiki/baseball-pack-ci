"""Tiny HTTP wrapper (standard library only) so the pack can run in a container."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.baseball_pack import InvalidSituation, evaluate


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"status": "ok", "pack": "baseball", "synthetic": True})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/decide":
            return self._send(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            situation = json.loads(self.rfile.read(length) or b"{}")
            self._send(200, evaluate(situation))
        except (InvalidSituation, json.JSONDecodeError) as e:
            self._send(400, {"error": str(e)})

    def log_message(self, fmt, *args):
        print("[server]", fmt % args)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Baseball pack (synthetic) listening on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
