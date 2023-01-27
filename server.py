#  coding: utf-8 

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

import socketserver
import os

class MyWebServer(socketserver.BaseRequestHandler):

    # all the error handlers return an HTML body for an error page with a rickroll
    def handle_404(self):
        body = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n"
        body += "<HTML><body>Error 404: Page not found!"
        body += "<p>Maybe you were looking for <a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>this page?</a></p></body></HTML>\n"

        return body

    def handle_405(self):
        body = "HTTP/1.1 405 Method Not Allowed\nContent-Type: text/html\n\n"
        body += "<HTML><body>Error 405: Method not allowed! But you can bet that Rick is allowed!<br>"
        body += "<iframe width='420' height='345' src='https://www.youtube.com/watch?v=dQw4w9WgXcQ'></iframe></body></HTML>\n"

        return body

    def handle_301(self,path):
        body = "HTTP/1.1 301 Moved Permanently\nContent-Type: text/html\n\n"
        body += "<HTML><body>Error 301: Moved Permanently!<br>"
        body += "New location: <a href='/{path}/'>127.0.0.1/{path}/</a><br>".format(path=path[-1])
        body += "You should also move permanently to Rick instead!<br>"
        body += "<iframe width='420' height='345' src='https://www.youtube.com/watch?v=dQw4w9WgXcQ'></iframe></body></HTML>\n"

        return body

    # maybe the rickroll is getting old...
    # just trying to get back at Hindle for getting us in class smh

    # anyways here the HTML is returned if it's all good, or a 404 if you're naughty
    def handle_html(self,path):
        body = ""
        try:
            html = open(path)
            if html:
                body += "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
                body += html.read()
                html.close()
        except:
            body += self.handle_404()
        return body

    # and here is the handler for CSS
    def handle_css(self,path):
        body = ""
        try:
            css = open(path)
            if css:
                body += "HTTP/1.1 200 OK\nContent-Type: text/css\n\n"
                body += css.read()
                css.close()
        except:
            body += self.handle_404()
        return body

    # returns the body
    def handle_get(self):

        current_path = os.path.dirname(os.path.realpath(__file__))
        requested_path = current_path + "/www" + str(self.path, "utf-8")

        # split by the /
        split_path = requested_path.split("/")

        # prevent root access
        if "../" in requested_path:
            return self.handle_404()

        # 301 on *almost* correct path
        if os.path.isdir(requested_path) and requested_path[-1] != "/":
            return self.handle_301(split_path)

        body = ""

        # this probably could be a switch statement
        # but that is way above my paygrade
        # requests to ""
        if split_path[-1] == "":
            body += self.handle_html(requested_path + "/index.html")
        
        # request to index.html
        elif "html" in split_path[-1]:
            body += self.handle_html(requested_path)

        # time for css
        elif "css" in requested_path:
            body += self.handle_css(requested_path)

        elif not os.path.isdir(requested_path):
            return self.handle_404()

        return body


    def handle(self):
        self.data = self.request.recv(1024).strip()
        
        self.data = self.data.split(b" ")
        self.http_request = self.data[0]
        self.path = self.data[1]

        # GET received
        if self.http_request == b"GET":
            body = self.handle_get()
            self.request.sendall(bytearray(body,'utf-8'))
        # 405 when not GET
        else:
            body = self.handle_405()
            self.request.sendall(bytearray(body,'utf-8'))
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    print("Now serving on {HOST}:{PORT}".format(HOST=HOST,PORT=PORT))

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
