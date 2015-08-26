# -*- coding: utf-8 -*-
import os
import time
import Queue
import socket
import datetime
import threading
import telnetlib
import transaction
import ConfigParser

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from sqlalchemy import func

import logging_utils
from model.models import (
    bind_session,
    DBSession,
    Measure
)
from model.hlr import (
    bind_session as bind_hlr_session,
    HLRDBSession,
    Subscriber,
    Sms,
)


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class CommsInterfaceServer(object):
    def __init__(self, configuration, measure_model, time_to_shutdown_event):
        self.measure_model = measure_model
        self.time_to_shutdown_event = time_to_shutdown_event

        self.logger = logging_utils.get_logger("CommsInterfaceServer")

        try:
            self.vty_host = configuration.get('osmo_nitb_vty', 'host')
            self.vty_port = configuration.getint('osmo_nitb_vty', 'port')
            self.vty_readtimeout_secs = configuration.getint('osmo_nitb_vty', 'timeout')

            self.xmlrpc_server_host = configuration.get('app:main', 'xmlrpc.host')
            self.xmlrpc_server_port = configuration.getint('app:main', 'xmlrpc.port')

            self.pf_db_conn_str = configuration.get('app:main', 'sqlalchemy.pf.url')
            self.hlr_db_conn_str = configuration.get('app:main', 'sqlalchemy.hlr.url')

        except ConfigParser.Error as err:
            raise ValueError('Configuration error: {0}'.format(err.message))

        self.vty_client_connection = None
        self.xmlrpc_thread = None
        self.proc_measure_thread = None
        self.proc_unknow_adress_sms_thread = None

        self.pf_phone_number = "10001"
        self.pf_wellcome_message =  "You are connected to a mobile search and rescue team. " + \
                                    "Please SMS to {ph_phone_number} to communicate. " + \
                                    "Your temporary phone number is {ms_phone_number}"
        self.pf_reply_message = "Your SMSs are being sent to a mobile search and rescue team." + \
                                "Reply to this message to communicate."
        self.pf_editable_parameters_save_path = "/var/lib/peoplefinder/pf_editable_parameters"
        self.editable_parameters_load()

        self.measure_update_period = 3

        bind_session(self.pf_db_conn_str)
        self.pf_session = DBSession

        bind_hlr_session(self.hlr_db_conn_str)
        self.hlr_session = HLRDBSession

        self.vty_use_send_sms_rlock = threading.RLock()

    def editable_parameters_load(self):
        if os.path.exists(self.pf_editable_parameters_save_path):
            self.logger.info("File with stored editable parameters found! Try read...!")
            config = ConfigParser.ConfigParser()

            try:
                config.read(self.pf_editable_parameters_save_path)

                self.pf_wellcome_message = config.get('editable_parameters', 'wellcome_message')
                self.pf_reply_message = config.get('editable_parameters', 'reply_message')

            except ConfigParser.Error as err:
                self.logger.error("Read file with stored editable parameters FAILD! Error: ".format(err.message))

            self.logger.info("Read file with stored editable parameters SUCCESS!")
        else:
            self.logger.info("File with stored editable parameters not found! Use default!")

        self.logger.info(
            "Editable parameters:" +
            ""
        )

    def editable_parameters_save(self):
        dir_name = os.path.dirname(self.pf_editable_parameters_save_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        config = ConfigParser.ConfigParser()
        config.add_section('editable_parameters')
        config.set('editable_parameters', 'wellcome_message', self.pf_wellcome_message)
        config.set('editable_parameters', 'reply_message', self.pf_reply_message)

        with open(self.pf_editable_parameters_save_path, 'wb') as configfile:
            config.write(configfile)

    def serve_forever(self):
        self.try_run_xmlrpc_server()
        self.try_run_vty_client()

        self.proc_measure_thread = threading.Thread(target=self.process_measure_worker)
        self.proc_measure_thread.daemon = True
        self.proc_measure_thread.start()

        self.proc_unknow_adress_sms_thread = threading.Thread(target=self.process_unknown_adress_sms_worker)
        self.proc_unknow_adress_sms_thread.daemon = True
        self.proc_unknow_adress_sms_thread.start()

        while not self.time_to_shutdown_event.is_set():
            if self.try_run_vty_client is None:
                self.try_run_vty_client()

            time.sleep(0.1)

    def try_run_xmlrpc_server(self):
        try:
            self.xmlrpc_server = SimpleXMLRPCServer(
                (self.xmlrpc_server_host, self.xmlrpc_server_port),
                requestHandler=RequestHandler
            )
        except socket.error as err:
            self.xmlrpc_server = None
            self.logger.error("Create XMLRPC server failed! Error message: {0}".format(err.message))
            return False

        self.xmlrpc_server.register_introspection_functions()

        self.xmlrpc_server.register_function(self.vty_send_sms, "send_sms")
        self.xmlrpc_server.register_function(self.vty_send_silent_sms, "send_silent_sms")
        self.xmlrpc_server.register_function(lambda: self.pf_phone_number, "get_peoplefinder_number")
        self.xmlrpc_server.register_function(self.start_tracking)
        self.xmlrpc_server.register_function(self.stop_tracking)
        self.xmlrpc_server.register_function(self.measure_model.get_current_gps)
        self.xmlrpc_server.register_function(lambda: self.pf_wellcome_message, "get_wellcome_message")
        self.xmlrpc_server.register_function(self.xmlrpc_set_welcome_message, "set_wellcome_message")
        self.xmlrpc_server.register_function(self.xmlrpc_set_parameters, "set_parameters")

        self.xmlrpc_thread = threading.Thread(target=self.xmlrpc_server.serve_forever)
        self.xmlrpc_thread.daemon = True
        self.xmlrpc_thread.start()

    def xmlrpc_set_welcome_message(self, msg):
        self.pf_wellcome_message = msg
        self.editable_parameters_save()
        return True

    def xmlrpc_set_parameters(self, parameters):
        self.logger.info("Parameters to save: {0}".format(parameters) )
        if "wellcome_message" in parameters:
            self.pf_wellcome_message = parameters["wellcome_message"]
        
        if "reply_message" in parameters:
            self.pf_wellcome_message = parameters["reply_message"]

        self.editable_parameters_save()
        return True

    def try_run_vty_client(self):
        self.logger.info("Try to create connection to VTY!")

        try:
            self.vty_client_connection = telnetlib.Telnet(self.vty_host, self.vty_port, self.vty_readtimeout_secs)
        except:
            self.vty_client_connection = None
            self.logger.error("Create VTY connection failed!")
            return False

        try:
            self.vty_client_connection.read_until("OpenBSC>", self.vty_readtimeout_secs)
        except:
            self.vty_client_connection.close()
            self.vty_client_connection = None
            self.logger.error("Read VTY wellcom message failed!")
            return False

        self.logger.info("Connection to VTY is established!")
        return True

    def process_measure_worker(self):
        self.logger.info("Process measurement thread START!")
        while not self.time_to_shutdown_event.is_set():
            meas = self.measure_model.get_measurement()
            if meas is not None:
                self.process_measure(meas)
            else:
                time.sleep(0.1)
        self.logger.info("Process measurement thread FINISH!")

    def process_measure(self, meas):
        self.logger.info("Process meas: IMSI {0}".format(meas['imsi']))

        imsi = meas['imsi']

        extensions = self.hlr_session.query(Subscriber.extension).filter(Subscriber.imsi == imsi).all()
        if len(extensions) != 1:
            self.logger.error("HLR struct ERROR imsi {0} not one".format(imsi))
            return
        extension = extensions[0][0]

        last_measure = self.get_last_measure(imsi)

        if last_measure is not None:
            self.logger.info("IMSI already detected.")

            last_measure_timestamp = time.mktime(last_measure.timestamp.timetuple())

            if meas['time'] < last_measure_timestamp:
                self.logger.info("Ignore measure because: measure is older then one in DB!")
                return

            if ((meas['time'] - last_measure_timestamp) < self.measure_update_period) and (last_measure.timing_advance == meas['meas_rep']['L1_TA']):
                self.logger.info("Ignore measure because: TA is no different from the last mesaure done less then {0} seconds!".format(self.measure_update_period))
                return

        else:
            self.logger.info("Detect new IMSI.")
            welcome_msg = self.get_formated_welcome_message(ms_phone_number=extension)
            self.logger.debug("Send welcome message: {0}".format(welcome_msg))
            if not self.vty_send_sms(imsi, welcome_msg):
                self.logger.error("Welcome message not send.")

        self.save_measure_to_db(meas, extension)

    def get_formated_welcome_message(self, **wargs):
        wargs["ph_phone_number"] = self.pf_phone_number
        return self.pf_wellcome_message.format(**wargs)

    def get_last_measure(self, imsi):
        last_measures = self.pf_session.query(Measure).filter(Measure.imsi == imsi).order_by(Measure.id.desc()).limit(1).all()
        if len(last_measures) == 0:
            return None
        return last_measures[0]

    def save_measure_to_db(self, meas, extension):
        self.logger.debug("Save measure to DB!")

        distance = self.__calculate_distance(long(meas['meas_rep']['L1_TA']))

        self.logger.debug("distance: {0}".format(distance))

        with transaction.manager:
            obj = Measure(imsi=meas['imsi'],
                          timestamp=datetime.datetime.fromtimestamp(meas['time']),
                          timing_advance=meas['meas_rep']['L1_TA'],
                          distance=distance,
                          phone_number=extension,
                          gps_lat=meas['lat'],
                          gps_lon=meas['lon'],
                          )
            self.logger.info("Add measure: imsi={0}, ta={1}, lat={2}, lon={3}".format(meas['imsi'], meas['meas_rep']['L1_TA'], meas['lat'], meas['lon']))
            self.pf_session.add(obj)

    def __calculate_distance(self, ta):
        return ta * 553 + 533

    def process_unknown_adress_sms_worker(self):
        self.logger.info("Process unknown adressing sms thread START!")
        while not self.time_to_shutdown_event.is_set():
            sms_info = self.measure_model.get_unknown_adresses_sms()
            if sms_info is not None:
                self.logger.info("Process sms {0}".format(sms_info))
                reply_msg = self.pf_reply_message

                self.logger.debug("Send reply message: {0}".format(reply_msg))

                if not self.vty_send_sms_by_phone_number(sms_info['source'][0], reply_msg):
                    self.logger.error("Reply message not send.")
            else:
                time.sleep(0.1)
        self.logger.info("Process unknown adressing sms thread FINISH!")

    def get_wellcome_message(self):
        return self.measure_model.get_wellcome_message()

    def set_wellcome_message(self, msg):
        self.measure_model.set_wellcome_message(msg)
        return True

    def get_peoplefinder_number(self):
        return self.pf_phone_number

    def start_tracking(self):
        self.__imis_reday_for_silent_sms_list = Queue.Queue()
        self.__tracking_cicle_number = 0

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
                if self.vty_send_silent_sms(imsi):
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
                Subscriber.extension != self.pf_phone_number
            ).all()

            for (imsi, dest_addr, sent, created) in sub_sms:
                if dest_addr is not None:
                    self.logger.debug(" sub: {0}, sms: {1}!".format(imsi, dest_addr))
                    if (sent is not None) or (self.__tracking_cicle_number == 0):
                        self.__imis_reday_for_silent_sms_list.put(imsi)
                else:
                    self.logger.debug(" No silent sms for sub: {0}!".format(imsi))
                    self.__imis_reday_for_silent_sms_list.put(imsi)

            time.sleep(3)
            self.__tracking_cicle_number += 1

    def vty_conf_meas_feed(self):
        if self.vty_client_connection is None:
            return False

        try:
            self.vty_client_connection.write("enable\n")

            self.vty_client_connection.read_until("OpenBSC#", self.__readtimeout_secs)
            self.vty_client_connection.write("configure terminal\n")

            self.vty_client_connection.read_until("OpenBSC(config)#", self.__readtimeout_secs)
            self.vty_client_connection.write("mncc-int\n")

            self.vty_client_connection.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.vty_client_connection.write("meas-feed destination 127.0.0.1 8888\n")

            self.vty_client_connection.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.vty_client_connection.write("write file\n")

            self.vty_client_connection.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)

            return True
        except:
            self.vty_client_connection = None
            return False

    def vty_send_silent_sms(self, imsi):
        self.logger.debug("XMLRPC command: send silent sms to imsi: {0}".format(imsi))
        if self.vty_client_connection is None:
            self.logger.error("Connection to VTY is not established")
            return False

        cmd = 'subscriber imsi {0}  silent-sms sender extension {1} send "silent hello"\n'.format(imsi, self.pf_phone_number)
        self.logger.debug("VTY command: {0}".format(cmd))
        try:
            self.vty_client_connection.write(cmd)
            res = self.vty_client_connection.read_until("OpenBSC>", self.vty_readtimeout_secs)
            self.logger.debug("VTY answer: {0}".format(res))
            return True
        except:
            self.logger.error("Cann't read answer from VTY")
            self.vty_client_connection = None
            return False

    def vty_send_sms(self, imsi, text):
        with self.vty_use_send_sms_rlock:
            self.logger.debug("XMLRPC command: send sms to imsi: {0}".format(imsi))
            if self.vty_client_connection is None:
                self.logger.error("Connection to VTY is not established")
                return False

            cmd = 'subscriber imsi {0} sms sender extension {1} send {2}\n'.format(imsi, self.pf_phone_number, text)
            self.logger.debug("VTY command: {0}".format(cmd))
            try:
                self.vty_client_connection.write(cmd)
                res = self.vty_client_connection.read_until("OpenBSC>", self.vty_readtimeout_secs)
                self.logger.debug("VTY answer: {0}".format(res))
                return True
            except:
                self.logger.error("Cann't read answer from VTY")
                self.vty_client_connection = None
                return False

    def vty_send_sms_by_phone_number(self, extension, text):
        self.logger.debug("XMLRPC command: send sms to extension: {0}".format(extension))
        if self.vty_client_connection is None:
            self.logger.error("Connection to VTY is not established")
            return False

        cmd = 'subscriber extension {0} sms sender extension {1} send {2}\n'.format(extension, self.pf_phone_number, text)
        self.logger.debug("VTY command: {0}".format(cmd))
        try:
            self.vty_client_connection.write(cmd)
            res = self.vty_client_connection.read_until("OpenBSC>", self.vty_readtimeout_secs)
            self.logger.debug("VTY answer: {0}".format(res))
            return True
        except:
            self.logger.error("Cann't read answer from VTY")
            self.vty_client_connection = None
            return False
