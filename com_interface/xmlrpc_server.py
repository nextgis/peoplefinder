import multiprocessing
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import logging_utils


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class XMLRPCProcess(multiprocessing.Process):
    def __init__(self):
        super(XMLRPCProcess, self).__init__()

    def run(self):
        self.logger = logging_utils.getLogger("XMLRPCProcess")

        # Create server
        server = SimpleXMLRPCServer(("localhost", 8123),
                                    requestHandler=RequestHandler)
        server.register_introspection_functions()

        server.register_function(self.send_sms)

        server.serve_forever()

    def send_sms(self, msg):
        self.logger.info("Process send sms command: %s" % msg)
        return True