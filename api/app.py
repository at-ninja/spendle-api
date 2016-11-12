"""
Andrew Thomas, Jake Zarobsky, Emily Huynh
Vandy Hacks 2016
Back end API support/ logic
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import urlparse
import psycopg2

urlparse.uses_netloc.append("postgres")
URL = urlparse.urlparse(os.environ["DATABASE_URL"])

CONN = psycopg2.connect(
    database=URL.path[1:],
    user=URL.username,
    password=URL.password,
    host=URL.hostname,
    port=URL.port
)


class Server(BaseHTTPRequestHandler):
    """Class that controls POST requests"""

    def _set_headers(self):
        """IDK"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """A handler for GET requests"""

        self._set_headers()
        response = "<html><body><h1>'"
        cur = CONN.cursor()
        cur.execute("SELECT * FROM Users;")
        response += str(cur.fetchall())
        response += "'</h1></body></html>"
        self.wfile.write(response)

    def do_HEAD(self):
        """A handler for HEAD requests"""
        self._set_headers()

    def do_POST(self):
        """A handler for POST requests"""
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

def run(server_class=HTTPServer, handler_class=Server):
    """Starts the server"""

    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    import sys
    sys.exit(run())
