#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        if port == None:
            port = 80
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        split_data = data.split(" ")
        #***IMPORTANT*** CODE MUST BE AN INT
        return int(split_data[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        #get stuff after \r\n\r\n
        split_data = data.split("\r\n\r\n")
        return split_data[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    #do the get request and return the response from the server
    #connect to socket first (self.connect(host, port) - given when httpclient.py is called?)
    #build get request
    #send get request (self.sendall(data))
    #receive something from socket  (self.recvall(self.socket))
    #   Note that recvall does the s.recv(BUFFER_SIZE) thing from lab 2
    #parse output of recvall into code and body (self.get_code(), self.get(body))
    #feed into HTTPResponse
    def GET(self, url, args=None):
        #print("url is: " + url)
        #print()
        parsed_url = urllib.parse.urlparse(url)
        #print("Parsed url is: " + parsed_url.geturl())
        host = parsed_url.hostname
        port = parsed_url.port
        #print("host is: " + host)
        #print("port is: " + str(port))
        #remember to close this
        self.connect(host, port)

        #get path for building HTTP request
        path = parsed_url.path

        #NOTE FOR JAN 31: SLASHDOT DOES NOT LIKE THIS...WHY!?!?!?!
        #Build GET request
        request = "GET " + path + " HTTP/1.1\r\n"
        request += "Host: " + host + "\r\n"
        request += "Accept-Language: en-us\r\n"
        request += "Connection: close\r\n\r\n"

        #send request
        self.sendall(request)

        #read what we received
        received = self.recvall(self.socket)

        #close socket
        self.close()

        #print("received is: " + received)
        #print("the path is: " + path)
        code = self.get_code(received)
        #print("THE CODE IS: " + code)
        body = self.get_body(received)
        #print("THE BODY IS: " + body)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        parsed_url = urllib.parse.urlparse(url)
        #print("Parsed url is: " + parsed_url.geturl())
        host = parsed_url.hostname
        port = parsed_url.port
        #print("host is: " + host)
        #print("port is: " + str(port))
        #remember to close this
        self.connect(host, port)

        #get path for building HTTP request
        path = parsed_url.path

        #parse args
        if args:
            #https://stackoverflow.com/questions/4163263/transferring-dictionary-via-post-request
            encoded_args = urllib.parse.urlencode(args)
            length = len(encoded_args)
        else:
            encoded_args = ""
            length = 0

        #Build POST request
        #CONTENT-LENGTH REQUIRED?
        request = "POST " + path + " HTTP/1.1\r\n"
        request += "Host: " + host + "\r\n"
        #can content type be anything else?
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: " + str(length) + "\r\n"
        request += "Accept-Language: en-us\r\n"
        request += "Connection: close\r\n\r\n"
        request += encoded_args

        #send request
        self.sendall(request)

        #read what we received
        received = self.recvall(self.socket)

        #print("RECEIVED IS: " + received)

        #close socket
        self.close()

        code = self.get_code(received)
        body = self.get_body(received)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
