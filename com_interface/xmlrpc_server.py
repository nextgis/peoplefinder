import multiprocessing
import threading
import Queue
import time
import ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from sqlalchemy import func

import logging_utils
from osmo_nitb_utils import VTYClient
from model.hlr import bind_session as bind_hlr_session, HLRDBSession, Subscriber, Sms


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class XMLRPCProcess(multiprocessing.Process):
    def __init__(self, configuration, comms_model):
        super(XMLRPCProcess, self).__init__()

        try:
            self._xmlrpc_server_host = configuration.get('app:main', 'xmlrpc.host')
            self._xmlrpc_server_port = configuration.getint('app:main', 'xmlrpc.port')
            self._hlr_db_connection_string = configuration.get('app:main', 'sqlalchemy.hlr.url')
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
        bind_hlr_session(self._hlr_db_connection_string)

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
        server.register_function(self.get_current_gps)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        while not self.__time_to_shutdown.is_set():
            if self._vty_client.is_active() is False:
                self.try_to_connect_to_vty()

            time.sleep(0.1)

    def get_current_gps(self):
        return self.__comms_model.get_current_gps()

    def get_peoplefinder_number(self):
        return self.__comms_model.get_pf_phone_number()

    def send_sms(self, imsi, msg):
        self.logger.info("Process send sms command. IMSI: %s, sms text: %s" % (imsi, msg))
        return self._vty_client.send_sms(imsi, msg)

    def send_silent_sms(self, imsi):
        self.logger.info("Process send silent sms command. IMSI: %s" % (imsi))
        return self._vty_client.send_silent_sms(imsi)

    def start_tracking(self):
        self.__imis_reday_for_silent_sms_list = Queue.Queue()

        self.__stop_trackin_event = threading.Event()
        self.__stop_trackin_event.clear()

        self.__tracking_process = threading.Thread(target=self.tracking_process)
        self.__tracking_process.start()

        self.__prepare_imsi_process = threading.Thread(target=self.prepare_ready_for_silent_sms)
        self.__prepare_imsi_process.start()

        self.logger.info("Start tracking!")

        return True

    def stop_tracking(self):
        self.__stop_trackin_event.set()
        self.__tracking_process.join()
        self.__prepare_imsi_process.join()
        self.logger.info("Stop tracking!")
        return True

    def tracking_process(self):
        while self.__stop_trackin_event.is_set() is False:

            try:
                imsi = self.__imis_reday_for_silent_sms_list.get_nowait()
                if self._vty_client.send_silent_sms(imsi):
                    self.logger.info("Send silent sms to IMSI %s!" % imsi)
                else:
                    self.logger.error("Silent sms to IMSI %s NOT SEND!" % imsi)
            except Queue.Empty:
                time.sleep(0.1)

    def prepare_ready_for_silent_sms(self):
        while self.__stop_trackin_event.is_set() is False:
            sub_sms = HLRDBSession.query(
                Subscriber.imsi,
                Sms.dest_addr,
                Sms.sent,
                func.max(Sms.created)
            ).select_from(
                Subscriber
            ).outerjoin(
                Sms,
                (
                    (Sms.dest_addr == Subscriber.extension) and
                    (Sms.protocol_id == 64)
                )
            ).group_by(
                Sms.dest_addr
            ).filter(
                Subscriber.extension != self.__comms_model.get_pf_phone_number()
            ).all()

            for (imsi, dest_addr, sent, created) in sub_sms:
                if dest_addr is not None:
                    self.logger.debug(" sub: {0}, sms: {1}!".format(imsi, dest_addr))
                    if sent is not None:
                        self.__imis_reday_for_silent_sms_list.put(imsi)
                else:
                    self.logger.debug(" No silent sms for sub: {0}!".format(imsi))
                    self.__imis_reday_for_silent_sms_list.put(imsi)

            time.sleep(3)
