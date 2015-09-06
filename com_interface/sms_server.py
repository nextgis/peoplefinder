# -*- coding: utf-8 -*-
import sys
#import cgi
import urlparse
import SocketServer

from BaseHTTPServer import BaseHTTPRequestHandler

import logging_utils


class PostHandler(BaseHTTPRequestHandler):
    # def do_POST(self):
    #     self.server.logger.info("do_POST!")

    #     ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

    #     self.server.logger.info("ctype: {0}".format(ctype))
    #     self.server.logger.info("pdict: {0}".format(pdict))

    #     varLen = int(self.headers['Content-Length'])
    #     postVars = self.rfile.read(varLen)

    #     self.server.logger.info("self.headers: {0}".format(self.headers))

    #     self.send_response(200)
    #     self.end_headers()

    def do_GET(self):
        self.server.logger.info("Received http request from kannel: {0}".format(self.path))
        o = urlparse.urlparse(self.path)
        parameters = urlparse.parse_qs(o.query)

        if 'source' in parameters:
            self.server.comms_model.put_unknown_adresses_sms(parameters)
        else:
            self.server.logger.warning("Bad sms info!")

        self.send_response(200)
        self.end_headers()

class SMSServer(SocketServer.TCPServer):
    def __init__(self, comms_model):
        try:
            SocketServer.TCPServer.__init__(self, ("", 8085), PostHandler)
        except:
            raise ValueError(sys.exc_info()[0])

        self.comms_model = comms_model
        self.logger = logging_utils.get_logger("SMSServer")

# for tests
# curl "http://localhost:8085/sms?source=24664&destination=89158912171&charset=UTF-8&coding=0&text=NextGIS"
