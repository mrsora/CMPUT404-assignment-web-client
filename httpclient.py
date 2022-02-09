#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust
# and Darren Wang
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
from urllib import parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):

    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # get code from middle of first line returned
        firstLine = data.split('\r\n')[0]
        return int(firstLine.split(" ")[1])

    def get_headers(self, data):
        # getting headers from before \r\n\r\n
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        # getting body from after \r\n\r\n
        return data.split('\r\n\r\n')[1]

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

    def GET(self, url, args=None):
        code = 500
        body = ""

        # parse input url to get host, path, port
        parsedUrl = parse.urlparse(url)

        # if not closed properly, close it (like assignment 1)
        path = parsedUrl.path
        if path == '':
            path = '/'

        # determine port if not given
        port = parsedUrl.port
        scheme = parsedUrl.scheme
        if port == None and scheme == 'https':
            port = 443
        elif port == None and scheme == 'http':
            port = 80

        # connect
        host = parsedUrl.hostname
        self.connect(host, port)

        # create and send request
        # GET
        # Host
        # Accept
        # Connection: close
        request = (
            f'GET {path} HTTP/1.1\r\n'
            f'Host: {host}\r\n'
            f'User-Agent: MoreFunAssignment\r\n'
            f'Accept-Charset: UTF-8\r\n'  # I know there isnt a need for f string but it looks nicer like this
            f'Connection: close\r\n\r\n')
        self.sendall(request)

        # get response
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)

        # close connection and return response
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # parse input url to get host, path, port
        parsedUrl = parse.urlparse(url)

        # if not closed properly, close it (like assignment 1)
        path = parsedUrl.path
        if path == '':
            path = '/'

        # determine port if not given
        port = parsedUrl.port
        scheme = parsedUrl.scheme
        if port == None and scheme == 'https':
            port = 443
        elif port == None and scheme == 'http':
            port = 80

        # POST - need to parse args
        if args:
            args = parse.urlencode(args)
        else:
            args = parse.urlencode('')

        # connect
        host = parsedUrl.hostname
        self.connect(host, port)

        # create POST request
        # POST
        # Host
        # Content Type
        # Content Length
        # Connection Close
        # Args
        request = (f'POST {path} HTTP/1.1\r\n'
                   f'Host: {host}\r\n'
                   f'User-Agent: MoreFunAssignment\r\n'
                   f'Content-Type: application/x-www-form-urlencoded\r\n'
                   f'Content-Length: {str(len(args))}\r\n'
                   f'Connection: close\r\n\r\n'
                   f'{args}')
        self.sendall(request)

        # get response
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)

        # close connection and return response
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
