import http.server
import socketserver
import os
import sys
import json
import traceback
import urllib.parse

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from analytics.keyword_service import KeywordSearchService

PORT = 8050
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Handle REST API route: /api/search?q=keyword
        if path == "/api/search":
            keyword = query_params.get("q", [""])[0]
            if not keyword:
                self.send_json_response({"error": "No keyword provided"}, status=400)
                return

            print(f"[API SERVER] Received Live Search Request for: '{keyword}'")
            try:
                service = KeywordSearchService()
                results = service.execute_keyword_etl(keyword, max_results=12)
                self.send_json_response(results)
            except Exception as e:
                traceback.print_exc()
                self.send_json_response({"error": str(e)}, status=500)
            return

        # Default static file serving
        return super().do_GET()

    def send_json_response(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving GitHub Analytics & Keyword API at http://localhost:{PORT}")
        httpd.serve_forever()
