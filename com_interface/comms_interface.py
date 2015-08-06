# -*- coding: utf-8 -*-
import os
import sys
import argparse
import ConfigParser
import time
import datetime
import multiprocessing
from multiprocessing.managers import BaseManager
import transaction

import logging_utils
from model.models import bind_session, DBSession, Measure
from model.hlr import bind_session as bind_hlr_session, HLRDBSession, Subscriber, Sms

from meas_json_client import MeasJsonListenerProcess
from osmo_nitb_utils import VTYClient
from xmlrpc_server import XMLRPCProcess

default_config_file = os.path.join(os.path.dirname(__file__), "config.ini")

wellcome_message = "You are connected to a mobile search and rescue team. \
                    Please SMS to 10001 to communicate. \
                    Your temporary phone number is %s"


# Read queue measurements.
# Add measurement in MeasurementsModel.
# Send welcome message for new imsi.
class MeasHandler(multiprocessing.Process):
    def __init__(self, configuration, queue_measurement, pf_db_connection_string, hlr_db_connection_string):
        self.queue_measurement = queue_measurement
        super(MeasHandler, self).__init__()
        self.__time_to_shutdown = multiprocessing.Event()

        self._pf_db_connection_string = pf_db_connection_string
        self._hlr_db_connection_string = hlr_db_connection_string

        try:
            self._vty_client = VTYClient(configuration)
        except ValueError as err:
            raise err

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def run(self):
        self.logger = logging_utils.get_logger("MeasHandler")

        bind_session(self._pf_db_connection_string)
        self.pf_session = DBSession

        bind_hlr_session(self._hlr_db_connection_string)
        self.hlr_session = HLRDBSession

        self.try_to_connect_to_vty()

        self.start_loop()

    def try_to_connect_to_vty(self):
        self.logger.info("Try to connect to vty...")
        if self._vty_client.try_connect():
            self.logger.info("Success connect to vty!")
        else:
            self.logger.info("Fail to connect to vty!")

    def start_loop(self):
        while not self.__time_to_shutdown.is_set():

            if self._vty_client.is_active() is False:
                self.try_to_connect_to_vty()

            meas = self.queue_measurement.get_measurement()
            if meas is not None:
                self.process_measure(meas)
            else:
                time.sleep(0.1)

    def process_measure(self, meas):
        self.logger.info("Process meas: IMSI {0}".format(meas['imsi']))

        imsi = meas['imsi']

        extensions = self.hlr_session.query(Subscriber.extension).filter(Subscriber.imsi == imsi).all()
        if len(extensions) != 1:
            self.logger.error("HLR struct ERROR imsi {0} not one".format(imsi))
            return
        extension = extensions[0][0]

        # sms_comms = self.hlr_session.query(Sms.text).filter(
        #     ((Sms.src_addr == extension) & (Sms.dest_addr == "10001")) |
        #     ((Sms.src_addr == "10001") & (Sms.dest_addr == extension))
        # ).all()

        # self.logger.info("sms_comms: {0}".format(sms_comms))

        if self.is_imsi_already_detected(imsi):
            self.logger.info("IMSI already detected.")
        else:
            self.logger.info("Detect new IMSI. Send welcome message.")
            if not self._vty_client.send_sms(imsi, wellcome_message % extension):
                self.logger.error("Welcome message not send.")

        self.save_measure_to_db(meas, extension)

    def is_imsi_already_detected(self, imsi):
        if self.pf_session.query(Measure).filter(Measure.imsi == imsi).count() > 0:
            return True
        return False

    def save_measure_to_db(self, meas, extension):
        distance = self.__calculate_distance(long(meas['meas_rep']['L1_TA']))

        with transaction.manager:
            obj = Measure(imsi=meas['imsi'],
                          timestamp=datetime.datetime.fromtimestamp(meas['time']),
                          timing_advance=meas['meas_rep']['L1_TA'],
                          distance=distance,
                          phone_number=extension,
                          gps_lat=55.69452,
                          gps_lon=37.56702,
                          )
            self.pf_session.add(obj)

    def __calculate_distance(self, ta, te=1.0):
        return ta * 553 + 553

    def __is_there_sms_from_to(self, src_addr, dest_addr):
        self.hlr_session.query(Sms.text).filter(
            (Sms.src_addr == src_addr) & (Sms.dest_addr == dest_addr)).count()


class CommsModel(object):
    def __init__(self):
        self.objects = {}
        self.queue = []
        self.high_priority_objects_count = 0
        self.rlock = multiprocessing.RLock()

        self.__tracking_imsi = None

        self.logger = logging_utils.get_logger("CommsModel")

    def set_tracking_imsi(self, imsi):
        self.logger.info("set_tracking_imsi - START".format(imsi))
        self.__tracking_imsi = imsi
        self.logger.info("set_tracking_imsi - FINISH".format(imsi))

    def get_tracking_imsi(self):
        return self.__tracking_imsi

    def clear_tracking_imsi(self):
        self.__tracking_imsi = None

    def put_measurement(self, obj):
        with self.rlock:
            imsi = obj['imsi']

            with_priority = self.__tracking_imsi == imsi

            if imsi in self.queue:
                cur_index = self.queue.index(imsi)
                cur_with_prior = cur_index <= self.high_priority_objects_count

                if (cur_with_prior is False) and (with_priority is True):
                    self.queue.remove(imsi)
                    self.queue.insert(self.high_priority_objects_count, obj)
                    self.high_priority_objects_count += 1
            else:
                if with_priority is True:
                    self.queue.insert(self.high_priority_objects_count, obj)
                    self.high_priority_objects_count += 1
                else:
                    self.queue.append(obj)

            self.objects[imsi] = obj

    def get_measurement(self):
        with self.rlock:
            if len(self.queue) > 0:
                return self.queue.pop(0)
                if self.high_priority_objects_count > 0:
                    self.high_priority_objects_count -= 1
            else:
                return None

    def number_of_measurements_in_queue(self):
        with self.rlock:
            return len(self.queue)


class CommsModelManager(BaseManager):
    pass
CommsModelManager.register('CommsModel', CommsModel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='People finder. Comm interface.')
    parser.add_argument('-c', '--configuration', type=file)
    parser.add_argument('-t', '--test_mode', action='store_true')
    args = parser.parse_args()

    configuration = ConfigParser.ConfigParser()
    if args.configuration is None:
        configuration.read([default_config_file])
    else:
        configuration.readfp(args.configuration)

    logger = logging_utils.get_logger("main")
    logger.info("Comm interface started! pid: {0}".format(os.getpid()))

    # Init DB ================================================================
    pf_db_conn_str = None
    try:
        web_config_file = configuration.get('web_layer', 'config')
        web_configuration = ConfigParser.ConfigParser()
        web_configuration.read([web_config_file])
        pf_db_conn_str = web_configuration.get('app:main', 'sqlalchemy.url')
    except ConfigParser.Error as err:
        logger.error("Identification People Finder DB fail: {0}".format(err.message))
        sys.exit(1)

    logger.info("pf db sqlite path: {0}".format(pf_db_conn_str))
    try:
        bind_session(pf_db_conn_str)
        DBSession.query(Measure).count()
    except:
        logger.error("People finder DB connection err")
        raise

    hlr_db_conn_str = None
    try:
        hlr_db_conn_str = configuration.get('osmo_nitb', 'db')
    except ConfigParser.Error as err:
        logger.error("Identification HLR fail: {0}".format(err.message))
        sys.exit(1)

    logger.info("HLR db sqlite path: {0}".format(hlr_db_conn_str))
    bind_hlr_session(hlr_db_conn_str)
    try:
        bind_session(pf_db_conn_str)
        HLRDBSession.query(Subscriber).count()
        HLRDBSession.query(Sms).count()
    except:
        logger.error("HLR DB connection err")
        raise

    # Events =================================================================

    # Init shared objects ====================================================
    manager = CommsModelManager()
    manager.start()
    comms_model = manager.CommsModel()

    # Init processes =========================================================
    logger.info("Init meas heandler writer")
    try:
        meas_handler = MeasHandler(configuration, comms_model, pf_db_conn_str, hlr_db_conn_str)
    except ValueError as err:
        logger.error("Cann't init measurement handler process server: {0}".format(err.message))
        sys.exit(1)

    logger.info("Init meas_json listener")
    meas_json_listener = MeasJsonListenerProcess(comms_model, args.test_mode)

    logger.info("Init xml-rpc server")
    try:
        requsets_server = XMLRPCProcess(configuration, comms_model)
    except ValueError as err:
        logger.error("Cann't init xml-rpc server: {0}".format(err.message))
        sys.exit(1)

    # Start processes ========================================================

    meas_handler.start()
    logger.info("Meas heandler writer STARTED with pid: {0}".format(
        meas_handler.pid))

    meas_json_listener.start()
    logger.info("meas_json listener STARTED with pid: {0}".format(
        meas_json_listener.pid))

    requsets_server.start()
    logger.info("XML-RPC server STARTED with pid: {0}".format(
        requsets_server.pid))

    # Queue statistic ========================================================
    try:
        queue_measurement_size_prev = 0
        while True:
            queue_measurement_size = comms_model.number_of_measurements_in_queue()
            if queue_measurement_size != queue_measurement_size_prev:
                queue_measurement_size_prev = queue_measurement_size
                logger.info(
                    "Number of measurements in queue change: {0}".format(
                        queue_measurement_size))

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

        requsets_server.terminate()
        requsets_server.join()
        meas_json_listener.terminate()
        meas_json_listener.join()
        meas_handler.terminate()
        meas_handler.join()
        manager.shutdown()
        manager.join()
