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
from gpsd_client import GPSDListenerProcess


# Read queue measurements.
# Add measurement in MeasurementsModel.
# Send welcome message for new imsi.
class MeasHandler(multiprocessing.Process):
    def __init__(self, configuration, comms_model, pf_db_connection_string, hlr_db_connection_string):
        self.comms_model = comms_model
        super(MeasHandler, self).__init__(name="MeasHandler")
        self.__time_to_shutdown = multiprocessing.Event()

        self._pf_db_connection_string = pf_db_connection_string
        self._hlr_db_connection_string = hlr_db_connection_string

        self.__update_period = 3
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

            meas = self.comms_model.get_measurement()
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
        last_measure = self.get_last_measure(imsi)

        if last_measure is not None:
            self.logger.info("IMSI already detected.")

            last_measure_timestamp = time.mktime(last_measure.timestamp.timetuple())
            if meas['time'] < last_measure_timestamp:
                self.logger.info("Ignore measure because: measure is older then one in DB!")
                return

            if ((meas['time'] - last_measure_timestamp) < self.__update_period) and (last_measure.timing_advance == meas['meas_rep']['L1_TA']):
                self.logger.info("Ignore measure because: TA is no different from the last mesaure done less then {0} seconds!".format(self.__update_period))
                return
        else:
            self.logger.info("Detect new IMSI. Send welcome message.")
            if not self._vty_client.send_sms(imsi, self.comms_model.get_wellcome_message(ms_phone_number=extension)):
                self.logger.error("Welcome message not send.")

        self.save_measure_to_db(meas, extension)

    def is_imsi_already_detected(self, imsi):
        if self.pf_session.query(Measure).filter(Measure.imsi == imsi).count() > 0:
            return True
        return False

    def get_last_measure(self, imsi):
        last_measures = self.pf_session.query(Measure).filter(Measure.imsi == imsi).order_by(Measure.id.desc()).limit(1).all()
        if len(last_measures) == 0:
            return None
        return last_measures[0]

    def save_measure_to_db(self, meas, extension):
        distance = self.__calculate_distance(long(meas['meas_rep']['L1_TA']))

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

    def __calculate_distance(self, ta, te=1.0):
        return ta * 553 + 553

    def __is_there_sms_from_to(self, src_addr, dest_addr):
        self.hlr_session.query(Sms.text).filter(
            (Sms.src_addr == src_addr) & (Sms.dest_addr == dest_addr)).count()


class GPSCoordinatesCollection(object):
    def __init__(self):
        self.__gps_times = []
        self.__gps_coordinates = []
        self.__count = 0
        self.__max_for_save = 100

        self.logger = logging_utils.get_logger("GPSCoordinatesCollection")

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
        self.rlock = multiprocessing.RLock()

        self.__cc = GPSCoordinatesCollection()
        self.__cc.add(time.time(), None, None)

        self.logger = logging_utils.get_logger("CommsModel")

        self.pf_phone_number = "10001"

        self.current_gps = (None, None)

    def get_wellcome_message(self, **wargs):
        msg = ("You are connected to a mobile search and rescue team. " +
               "Please SMS to {ph_phone_number} to communicate. " +
               "Your temporary phone number is {ms_phone_number}")

        wargs["ph_phone_number"] = self.pf_phone_number

        return msg.format(**wargs)

    def get_pf_phone_number(self):
        return self.pf_phone_number

    def put_measurement(self, obj):
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

    def number_of_measurements_in_queue(self):
        with self.rlock:
            return len(self.queue)

    def add_gps_meas(self, time, lat, lon):
        self.__cc.add(time, lat, lon)
        self.current_gps = (lat, lon)

    def get_current_gps(self):
        return self.current_gps


class CommsModelManager(BaseManager):
    pass
CommsModelManager.register('CommsModel', CommsModel)


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

    # Configurate nitb =======================================================
    pf_phone_number = comms_model.get_pf_phone_number()
    pf_imsi = 1

    vty_client = VTYClient(configuration)
    if vty_client.try_connect() is False:
        logger.error("Connect to osmo nitb VTY FAIL!")
        manager.shutdown()
        manager.join()
        sys.exit(1)

    if vty_client.conf_meas_feed() is True:
        logger.info("Configurate osmo nitb measurements over VTY SUCCESS!")
    else:
        logger.error("Configurate osmo nitb measurements over VTY FAIL!")
        manager.shutdown()
        manager.join()
        sys.exit(1)

    vty_client = None

    pf_subscriber = HLRDBSession.query(Subscriber).filter(Subscriber.extension == pf_phone_number).all()
    if len(pf_subscriber) > 1:
        logger.error("HLR has incorrect structure more then one subscribers with extension {0}".format(pf_phone_number))
        manager.shutdown()
        manager.join()
        sys.exit(1)

    if len(pf_subscriber) == 0:
        obj = Subscriber(created=datetime.datetime.fromtimestamp(time.time()),
                         updated=datetime.datetime.fromtimestamp(time.time()),
                         imsi=pf_imsi,
                         name="peoplefinder",
                         extension=pf_phone_number,
                         authorized=1,
                         lac=1,
                         )
        with transaction.manager:
            HLRDBSession.add(obj)
            logger.info("Add PF subscriber. imsi: {0}, extension: {1}".format(pf_imsi, pf_phone_number))

    if len(pf_subscriber) == 1:
        logger.info("PF subscriber with phone number {0} already created.".format(pf_phone_number))

    # Init processes =========================================================
    logger.info("Init gpsd listener")
    gpsd_listener = GPSDListenerProcess(comms_model)

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
    gpsd_listener.start()
    logger.info("GPSD listener STARTED with pid: {0}".format(
        gpsd_listener.pid))

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
