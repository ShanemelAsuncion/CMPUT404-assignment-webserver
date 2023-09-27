#  coding: utf-8 
import socketserver
import os
import re

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
        self.data_string = str(self.data, encoding='utf-8') # convert the bytes -> str 
        self.data_list = self.data_string.splitlines()
        file = get_path(self.data_list[0]) 

        flag, msg = check_method_validity(self.data_string)
        if flag == 1:
              self.request.sendall(bytearray(msg, 'utf-8'))
              return 
        
        # Handle css files and html files
        cssfile = get_path(self.data_list[0])[1:]   # remove /
        if len(cssfile) > 1:
            temp = cssfile.split(".")     # get extension
            if len(temp) >= 2:
                ext = temp[1]
                if ext == "css" or "html":
                    msg = getContent(self.data_string,ext)
                    self.request.sendall(bytearray(msg, 'utf-8'))
                 
        # Passed all filters. Valid path
        self.request.sendall(bytearray(msg,'utf-8'))


def get_path(data):
        """
        Returns the path of the requested data
        """
        path = data.split(" ")
        return path[1]

def get_full_path(data):
        return os.getcwd() + "/www/" + get_path(data)

def check_method_validity(data):
        """
        Check if the method is GET. Otherwise, method is invalid and send a 405 header response.
        Also checks if the path given exists. Otherwise, raise 404 error and send appropriate header response.
        Returns: a tuple (x,y)
            x (digit) : 0 if valid, 1 is not
            y (str) : Header message
        """
        method = data.split(" ")[0]
        base = "HTTP/1.1 "
        
        if method != "GET":
              # If method is PUT/POST/DELETE, then request is invalid
              error = "405 Method Not Allowed"
              error_message =  base + error + "\n"
              return(1, error_message)
        
        # Check if the path exists
        path = get_full_path(data)
        print("checking:",path,os.path.exists(path))  

        # Filter the paths that do not use valid ending
        pattern = r"(.css|.html|/|/deep|/hardcode)$"
        m = re.findall(pattern, path)
        if len(m) == 0:
            error = "404 Not Found" 
            error_message = base + error + "\n"
            return(1, error_message)

        if not os.path.exists(path):
            error = "404 Not Found" 
            error_message = base + error + "\n"
            return(1, error_message) 
        
        return (0, base + "200 Ok" + "\n")   # valid path and method

def getContent(data,type):
    """
    Creates the header responses for html and css files. It includes the status code and message along with the content
    type and actual content of the files.
    """
    path = get_full_path(data)
    content = ""
    content_type = f'Content-Type: text/{type}; charset=UTF-8\r\n'
    with open(path) as file:
       content = file.read()  
    msg = "HTTP/1.1 200 Ok\n" + content_type + content + "\n"
    return msg
    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
