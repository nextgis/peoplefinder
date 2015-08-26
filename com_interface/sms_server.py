# -*- coding: utf-8 -*-
import cgi
import SocketServer

from BaseHTTPServer import BaseHTTPRequestHandler

import logging_utils


class PostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.logger.info("do_POST!")

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        self.server.logger.info("Get info about unrichable sms: {0}".format(postvars))
        if 'source' in postvars:
            self.server.comms_model.put_unknown_adresses_sms(postvars)
        else:
            self.server.logger.warning("Bad sms info!")

        self.send_response(200)


class SMSServer(SocketServer.TCPServer):
    def __init__(self, configuration, comms_model):
        port = 8085

        self.comms_model = comms_model
        self.logger = logging_utils.get_logger("SMSServer")

        SocketServer.TCPServer.__init__(self, ("", port), PostHandler)


# for tests
# import urllib, urllib2
# url = 'localhost:8085/sms'
# values = dict(source='49949', destination='10002', charset='UTF-8', coding='0', text='NextGIS')
# data = urllib.urlencode(values)
# req = urllib2.Request(url, data)
# rsp = urllib2.urlopen(req)
# or
# curl -d "source=49949&destination=10002&charset=UTF-8&coding=0&text=NextGIS" http://localhost:8085
