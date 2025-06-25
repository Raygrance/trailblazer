#from HTTPServer import BaseHTTPRequestHandler, HTTPServer
import http.server
import socketserver
import json
from urllib.parse import urlparse
import psycopg2


DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "openapi"
DB_USER = "openapi"
DB_PASS = "password"


LONG_RESPONSE = {"too long":True}

def my_json_processor(msg):
    host = msg["host"]
    url = msg["url"]
    method = msg["method"]
    query = msg["query"]
    request = msg["request"]
    response = msg["response"]
    responsecode = msg["responsecode"]

    result = urlparse(url)
    if result.netloc:
        host = result.netloc
    if result.path:
        url = result.path
    if result.query:
        query = result.query

    #if len(json.dumps(request)) > len(json.dumps(response)):
    #    print("Response object smaller than request.")
    #    return
    #print("Request:", request)
    #print("Response:", response)
    print(host, url, method, query, str(request)[:20], str(response)[:20], responsecode)
    
    # only capture requests in the local network (comment out if needed)
    if not (host.startswith("192.168.") or host.startswith("127.0.0")):
        print("===== external request, abort =====")
        return
    
    if len(json.dumps(request)) > 10000:# or 
        print("===== req too long, abort =====")
        return
    
    if len(json.dumps(response)) > 10000:
        response = LONG_RESPONSE
        print("===== resp too long, reduce size =====")
    
    conn = psycopg2.connect(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASS, port=DB_PORT)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    cursor.execute("INSERT INTO requests (host, url, method, query, request, response, responsecode) VALUES (%s, %s, %s, %s, %s, %s, %s)", (host, url, method, query, json.dumps(request), json.dumps(response), responsecode))
    conn.commit()
    print("+++++++++++++++++++++++++")


class Server(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'world', 'received': 'ok'}).encode())
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        #message['received'] = 'ok'
        if "request" in message and "response" in message:
            if message["request"] != None or message["response"] != None:
                my_json_processor(message)
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps({"completed": 1}).encode())
        
def run(server_class=http.server.HTTPServer, handler_class=Server, port=8086):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()