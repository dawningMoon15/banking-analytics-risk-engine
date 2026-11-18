#!/usr/bin/env python3
"""
Dashboard HTTP Server for Banking Customer Analytics & Risk Engine.
Serves the interactive dashboard on http://localhost:8080.
"""

import http.server
import socketserver
import os
import sys

PORT = 8080
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")

class DashboardHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def do_GET(self):
        # Redirect root or /dashboard to /dashboard/index.html
        if self.path in ('/', '', '/dashboard', '/dashboard/'):
            self.send_response(302)
            self.send_header('Location', '/dashboard/index.html')
            self.end_headers()
            return
        return super().do_GET()

def run_server():
    os.chdir(PROJECT_ROOT)
    handler = DashboardHTTPRequestHandler
    
    # Try PORT or subsequent ports
    port = PORT
    for attempt in range(10):
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                print("=" * 70)
                print("  BANKING CUSTOMER ANALYTICS & RISK ENGINE — DASHBOARD SERVER")
                print("=" * 70)
                print(f"  Dashboard is live at:  http://localhost:{port}/dashboard/index.html")
                print(f"  Short URL:             http://localhost:{port}/")
                print(f"  Serving files from:    {PROJECT_ROOT}")
                print("=" * 70)
                print("Press Ctrl+C to terminate the server.\n")
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                port += 1
            else:
                raise e

if __name__ == '__main__':
    run_server()
