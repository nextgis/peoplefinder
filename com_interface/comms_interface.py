# -*- coding: utf-8 -*-
import os
import argparse
import ConfigParser
import time
import datetime
import multiprocessing
from multiprocessing.managers import BaseManager
import transaction

import logging_utils
from model.models import get_session, Measure, Subscriber, Sms

from meas_json_client import MeasJsonListenerProcess
from osmo_nitb_utils import VTYClient
from xmlrpc_server import XMLRPCProcess

default_config_file = os.path.join(os.getcwd(), "config.ini")

wellcome_message = "You are connected to a mobile search and rescue team. \
                    Please SMS to 10001 to communicate. \
                    Your temporary phone number is %s"


# Read queue measurements.
# Add measurement in MeasurementsModel.
# Send welcome message for new imsi.
class MeasHandler(multiprocessing.Process):
    def __init__(self, queue_measurement, pf_db_connection_string, hlr_db_connection_string):
        self.queue_measurement = queue_measurement

        super(MeasHandler, self).__init__()
        self.__time_to_shutdown = multiprocessing.Event()

        self._pf_db_connection_string = pf_db_connection_string
        self._hlr_db_connection_string = hlr_db_connection_string

        self._vty_client = None

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def run(self):
        self.logger = logging_utils.get_logger("MeasHandler")

        self.pf_session = get_session(self._pf_db_connection_string)
        self.hlr_session = get_session(self._hlr_db_connection_string)

        self.try_to_create_vty_client()

        self.start_loop()

    def try_to_create_vty_client(self):
        host = 'localhost'
        port = 4242
        timeout = 5
        try:
            self.logger.info("Try to create vty client; host: {0}, port: {1}, timeout: {2}".format(host, port, timeout))
            self._vty_client = VTYClient(host, port, timeout)
            self.logger.info("Vty client created!")
        except ValueError as err:
            self.logger.error("Failed to create vty client: {0}".format(err))
            self._vty_client = None

    def start_loop(self):
        while not self.__time_to_shutdown.is_set():
            if self._vty_client is None:
                self.try_to_create_vty_client()
                time.sleep(1)
                continue

            meas = self.queue_measurement.get()
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
            self._vty_client.send_sms(imsi, wellcome_message % extension)

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
                          gps_lat=0.0,
                          gps_lon=0.0,
                          )
            self.pf_session.add(obj)

    def __calculate_distance(self, ta, te=1.0):
        return ta * 553 + 553


class MeasurementQueue(object):
    def __init__(self):
        self.objects = {}
        self.queue = []
        self.high_priority_objects_count = 0
        self.rlock = multiprocessing.RLock()
        self.__prior_imsi = None

    def set_prior_imsi(self, imsi):
        self.__prior_imsi = imsi

    def clear_prior_imsi(self):
        self.__prior_imsi = None

    def put(self, obj):
        with self.rlock:
            imsi = obj['imsi']

            with_priority = self.__prior_imsi == imsi

            if imsi in self.queue:
                cur_index = self.queue.index(imsi)
                cur_with_prior = cur_index <= self.high_priority_objects_count

                if cur_with_prior is False and with_priority is True:
                    self.queue.remove(imsi)
                    self.queue.insert(obj, self.high_priority_objects_count)
            else:
                if with_priority is True:
                    self.queue.insert(obj, self.high_priority_objects_count)
                else:
                    self.queue.append(obj)

            self.objects[imsi] = obj

    def get(self):
        with self.rlock:
            if len(self.queue) > 0:
                return self.queue.pop(0)
            else:
                return None

    def qsize(self):
        with self.rlock:
            return len(self.queue)


class MeasurementQueueManager(BaseManager):
    pass
MeasurementQueueManager.register('MeasurementQueue', MeasurementQueue)


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
    pf_db_conn_str = "sqlite:///{0}".format(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'storage',
            'pf.sqlite'))
    logger.info("pf db sqlite path: {0}".format(pf_db_conn_str))

    hlr_db_path = "/etc/osmocom/hlr.sqlite3"
    if not os.path.exists(hlr_db_path):
        hlr_db_path = os.path.join(os.getcwd(), "hlr.sqlite3")
    hlr_db_conn_str = "sqlite:///{0}".format(hlr_db_path)
    logger.info("hlr db sqlite path: {0}".format(hlr_db_conn_str))

    # Init shared objects ====================================================
    manager = MeasurementQueueManager()
    manager.start()
    queue_measurement = manager.MeasurementQueue()

    # Init processes =========================================================
    logger.info("Init meas heandler writer")
    meas_handler = MeasHandler(queue_measurement, pf_db_conn_str, hlr_db_conn_str)

    logger.info("Init meas_json listener")
    meas_json_listener = MeasJsonListenerProcess(queue_measurement, args.test_mode)

    logger.info("Init xml-rpc server")
    requsets_server = XMLRPCProcess()

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
            queue_measurement_size = queue_measurement.qsize()
            if queue_measurement_size != queue_measurement_size_prev:
                queue_measurement_size_prev = queue_measurement_size
                logger.info(
                    "queue_measurement size change: {0}".format(
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
