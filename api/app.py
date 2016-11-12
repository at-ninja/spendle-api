"""
Andrew Thomas, Jake Zarobsky, Emily Huynh
Vandy Hacks 2016
Back end API support/ logic
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

CONN = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
)

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global CONN
        self._set_headers()
        s = "<html><body><h1>'"
        cur = CONN.cursor()
        cur.execute("SELECT * FROM Users;")
        s += str(cur.fetchall())
        s += "'</h1></body></html>"
        self.wfile.write(s)

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        
def run(server_class=HTTPServer, handler_class=Server):

    port = int(os.environ.get("PORT", 5000))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    run()