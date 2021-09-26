#  coding: utf-8 
import socketserver
import os
from urllib.parse import unquote

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request_data = self.data.decode('utf-8').split()
        self.request_path = self.request_data[1]
        if self.request_path[-1] == "/":
            self.request_path = self.request_path + "index.html"
        self.method = self.request_data[0]
        self.host = self.request_data[4]
        self.root = os.path.abspath("www")
        self.path = os.path.abspath(self.root + self.request_path)

        if self.path.lower().endswith(".html") or self.path.lower().endswith(".htm"):
            self.mimetype = "text/html"
        elif self.path.lower().endswith(".css"):
            self.mimetype = "text/css"
        else:
            self.mimetype = "application/octet-stream"

        if self.method != "GET" and self.method != "HEAD":
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed\r\nAllow: GET, HEAD\r\nContent-Type: text/html\r\n\r\n<html><head><title>405 Method Not Allowed</title></head><body><center><h1>405 Method Not Allowed</h1></center><hr></body></html>','utf-8'))

        # Checks for directory traversal attack
        if not os.path.abspath(self.path).startswith(self.root):
            self.error404()

        try:
            with open(self.path, "r") as f:
                self.request.sendall(bytearray('HTTP/1.1 200 OK\r\nContent-Type: ' + self.mimetype + '\r\n\r\n'+f.read(), 'utf-8'))
        except FileNotFoundError:
            self.error404()
        except IsADirectoryError:
            self.error301()
                

    def error404(self):
        self.request.sendall(bytearray('HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<html><head><title>404 Not Found</title></head><body><center><h1>404 Not Found</h1></center><hr></body></html>','utf-8'))

    def error301(self):
        self.request.sendall(bytearray('HTTP/1.1 301 Moved Permanently\r\nLocation: http://' + self.host + self.request_path + '/\r\nContent-Type: text/html\r\n\r\n<html><head><title>301 Moved Permanently</title></head><body><center><h1>301 Moved Permanently</h1></center><hr></body></html>','utf-8'))



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
