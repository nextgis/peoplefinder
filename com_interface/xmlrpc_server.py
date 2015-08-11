import multiprocessing
import threading
import time
import ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import logging_utils
from osmo_nitb_utils import VTYClient


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class XMLRPCProcess(multiprocessing.Process):
    def __init__(self, configuration, comms_model):
        super(XMLRPCProcess, self).__init__()

        try:
            self._xmlrpc_server_host = configuration.get('xmlrpc_server', 'host')
            self._xmlrpc_server_port = configuration.getint('xmlrpc_server', 'port')

        except ConfigParser.Error as err:
            raise ValueError('Configuration error: {0}'.format(err.message))

        self.__comms_model = comms_model
        self.__time_to_shutdown = multiprocessing.Event()

        try:
            self._vty_client = VTYClient(configuration)
        except ValueError as err:
            raise err

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def try_to_connect_to_vty(self):
        self.logger.info("Try to connect to vty...")
        if self._vty_client.try_connect():
            self.logger.info("Success connect to vty!")
        else:
            self.logger.info("Fail to connect to vty!")

    def run(self):
        self.logger = logging_utils.get_logger("XMLRPCProcess")
        self.try_to_connect_to_vty()

        # Create server
        server = SimpleXMLRPCServer((self._xmlrpc_server_host, self._xmlrpc_server_port),
                                    requestHandler=RequestHandler)
        server.register_introspection_functions()

        server.register_function(self.send_sms)
        server.register_function(self.send_silent_sms)
        server.register_function(self.get_peoplefinder_number)
        server.register_function(self.start_tracking)
        server.register_function(self.stop_tracking)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        while not self.__time_to_shutdown.is_set():
            if self._vty_client.is_active() is False:
                self.try_to_connect_to_vty()

            time.sleep(0.1)

    def get_peoplefinder_number(self):
        return self.__comms_model.get_pf_phone_number()

    def send_sms(self, imsi, msg):
        self.logger.info("Process send sms command. IMSI: %s, sms text: %s" % (imsi, msg))
        return self._vty_client.send_sms(imsi, msg)

    def send_silent_sms(self, imsi):
        self.logger.info("Process send silent sms command. IMSI: %s" % (imsi))
        return self._vty_client.send_silent_sms(imsi)

    def start_tracking(self, imsi):
        self.__comms_model.set_tracking_imsi(imsi)

        self.__stop_trackin_event = threading.Event()
        self.__stop_trackin_event.clear()
        self.__tracking_process = threading.Thread(target=self.tracking_process)
        self.__tracking_process.start()
        self.logger.info("Start tracking IMSI %s!" % imsi)
        return True

    def stop_tracking(self):
        self.__stop_trackin_event.set()
        self.__comms_model.clear_tracking_imsi()
        return True

    def tracking_process(self):
        while self.__stop_trackin_event.is_set() is False:
            tracking_imsi = self.__comms_model.get_tracking_imsi()
            if self._vty_client.send_silent_sms(tracking_imsi):
                self.logger.info("Send silent sms to IMSI %s!" % tracking_imsi)
            else:
                self.logger.error("Silent sms to IMSI %s NOT SEND!" % tracking_imsi)
            time.sleep(3)
