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
from model.models import bind_session, DBSession, Measure, Settings
from model.hlr import bind_session as bind_hlr_session, HLRDBSession, Subscriber, Sms

from meas_json_client import MeasJsonListenerProcess
from gpsd_client import GPSDListenerProcess
from comms_interface_server import CommsInterfaceServer
from sms_server import SMSServer


class GPSCoordinatesCollection(object):
    def __init__(self):
        self.__gps_times = []
        self.__gps_coordinates = []
        self.__count = 0
        self.__max_for_save = 100

        self.logger = logging_utils.get_logger("GPSCoordinatesCollection")

        self.add(time.time(), None, None)

    def add(self, time, lat, log):
        if self.__count == self.__max_for_save:
            self.__gps_times.pop(0)
            self.__gps_coordinates.pop(0)
            self.__count -= 1

        self.__gps_times.append(time)
        self.__gps_coordinates.append((lat, log))

        self.__count += 1

    def get_coordinates(self, time):
        for index in xrange(0, self.__count):
            if time <= self.__gps_times[index]:
                return self.__gps_coordinates[index]

        return self.__gps_coordinates[self.__count - 1]


class CommsModel(object):

    def __init__(self):
        self.queue = []
        self.unknown_adresses_sms = []

        self.__cc = GPSCoordinatesCollection()
        self.current_gps = (None, None)

        self.logger = logging_utils.get_logger("CommsModel")

    def put_measurement(self, obj):
        self.logger.debug("put_measurement: imsi={0}".format(obj['imsi']))

        lat, lon = self.__cc.get_coordinates(obj['time'])
        obj['lat'] = lat
        obj['lon'] = lon

        self.logger.debug("put_measurement: imsi={0} lat={1}, lon={2}".format(obj['imsi'], lat, lon))

        self.queue.append(obj)

    def get_measurement(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            return None

    def put_unknown_adresses_sms(self, sms_info):
        self.unknown_adresses_sms.append(sms_info)

    def get_unknown_adresses_sms(self):
        if len(self.unknown_adresses_sms) > 0:
            return self.unknown_adresses_sms.pop(0)
        else:
            return None

    def number_of_measurements_in_queue(self):
        return len(self.queue)

    def add_gps_meas(self, time, lat, lon):
        self.__cc.add(time, lat, lon)
        self.current_gps = (lat, lon)

    def get_current_gps(self):
        return self.current_gps


class CommsModelManager(BaseManager):
    pass
CommsModelManager.register('CommsModel', CommsModel)


def start_comms_interface_server_process(configuration, comms_model):
    logger = logging_utils.get_logger(multiprocessing.current_process().name)
    try:
        srv = CommsInterfaceServer(configuration, comms_model, multiprocessing.Event(), logger)
        srv.serve_forever()
    except ValueError as err:
        logger.error("Cann't init comms interface server: {0}".format(err.message))
        sys.exit(1)


def start_sms_server(configuration, comms_model):
    logger = logging_utils.get_logger(multiprocessing.current_process().name)
    try:
        srv = SMSServer(configuration, comms_model, logger)
        srv.serve_forever()
    except ValueError as err:
        print "Cann't init sms server: {0}".format(err.message)
        logger.error("Cann't init sms server: {0}".format(err.message))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='People finder. Comm interface.')
    parser.add_argument('-c', '--configuration', type=file, required=True)
    parser.add_argument('-t', '--test_mode', action='store_true')
    args = parser.parse_args()

    configuration = ConfigParser.ConfigParser()
    configuration.readfp(args.configuration)

    logger = logging_utils.get_logger("main")
    logger.info("Comm interface started! pid: {0}".format(os.getpid()))

    # Init DB ================================================================
    pf_db_conn_str = None
    try:
        pf_db_conn_str = configuration.get('app:main', 'sqlalchemy.pf.url')
    except ConfigParser.Error as err:
        logger.error("Identification People Finder DB fail: {0}".format(err.message))
        sys.exit(1)

    logger.info("PF db sqlite path: {0}".format(pf_db_conn_str))
    try:
        bind_session(pf_db_conn_str)
        DBSession.query(Measure).count()
        DBSession.query(Settings).count()
    except:
        logger.error("People finder DB connection err")
        raise

    hlr_db_conn_str = None
    try:
        hlr_db_conn_str = configuration.get('app:main', 'sqlalchemy.hlr.url')
    except ConfigParser.Error as err:
        logger.error("Identification HLR fail: {0}".format(err.message))
        sys.exit(1)

    logger.info("HLR db sqlite path: {0}".format(hlr_db_conn_str))
    try:
        bind_hlr_session(hlr_db_conn_str)
        HLRDBSession.query(Subscriber).count()
        HLRDBSession.query(Sms).count()
    except:
        logger.error("HLR DB connection err")
        raise

    # Init shared objects ====================================================
    manager = CommsModelManager()
    manager.start()
    comms_model = manager.CommsModel()

    # Init processes =========================================================
    logger.info("Init comms interface server")
    try:
        srv = CommsInterfaceServer(configuration, comms_model, multiprocessing.Event())
        comms_interface_server_process = multiprocessing.Process(target=srv.serve_forever)
    except ValueError as err:
        logger.error("Cann't init comms interface server: {0}".format(err.message))
        sys.exit(1)

    
    logger.info("Init gpsd listener")
    gpsd_listener = GPSDListenerProcess(comms_model)

    logger.info("Init sms server")
    try:
        srv = SMSServer(comms_model)
        sms_server_process = multiprocessing.Process(target=srv.serve_forever)
    except ValueError as err:
        logger.error("Cann't init sms server: {0}".format(err.message))
        sys.exit(1)

    logger.info("Init meas_json listener")
    meas_json_listener = MeasJsonListenerProcess(comms_model, args.test_mode)

    # Start processes ========================================================
    comms_interface_server_process.start()
    logger.info("Comms interface server STARTED with pid: {0}".format(
        comms_interface_server_process.pid))

    gpsd_listener.start()
    logger.info("GPSD listener STARTED with pid: {0}".format(
        gpsd_listener.pid))

    sms_server_process.start()
    logger.info("Sms server STARTED with pid: {0}".format(
        sms_server_process.pid))

    meas_json_listener.start()
    logger.info("meas_json listener STARTED with pid: {0}".format(
        meas_json_listener.pid))

    # Queue statistic ========================================================
    try:
        queue_measurement_size_prev = 0
        while True:
            if gpsd_listener.is_alive() is False:
                gpsd_listener.terminate()
                gpsd_listener.join()
                gpsd_listener = GPSDListenerProcess(comms_model)
                gpsd_listener.start()
                logger.info("GPSD listener RESTARTED with pid: {0}".format(
                    gpsd_listener.pid))
            queue_measurement_size = comms_model.number_of_measurements_in_queue()
            if queue_measurement_size != queue_measurement_size_prev:
                queue_measurement_size_prev = queue_measurement_size
                logger.info(
                    "Number of measurements in queue change: {0}".format(
                        queue_measurement_size))

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

        comms_interface_server_process.terminate()
        comms_interface_server_process.join()
        gpsd_listener.terminate()
        gpsd_listener.join()
        sms_server_process.terminate()
        sms_server_process.join()
        meas_json_listener.terminate()
        meas_json_listener.join()
        manager.shutdown()
        manager.join()
