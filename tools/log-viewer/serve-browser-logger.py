#!/usr/bin/env python3
"""
Serves the browser logger JavaScript and acts as a simple CORS proxy
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/browser-logger.js':
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            with open('browser-logger.js', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), CORSRequestHandler)
    print('Serving browser logger at http://localhost:8080/browser-logger.js')
    print('\nAdd this to your HTML:')
    print('<script>')
    print('  window.PERSONAKIT_APP_NAME = "your-app-name";')
    print('</script>')
    print('<script src="http://localhost:8080/browser-logger.js"></script>')
    server.serve_forever()