# -*- coding: utf-8 -*-
import os
import argparse
import ConfigParser
import time
import datetime
import multiprocessing
from multiprocessing.managers import BaseManager
from sqlalchemy import create_engine
import transaction

from model import models
from model.models import DBSession
import logging_utils
from meas_json_client import MeasJsonListenerProcess
# import xmlrpc_server
# import osmo_nitb_utils


default_config_file = os.path.join(os.getcwd(), "config.ini")

wellcome_message = "You are connected to a mobile search and rescue team. \
                    Please SMS to 10001 to communicate. \
                    Your temporary phone number is %s"


# Write measurements to DB.
# Cache last measurement time for imsi.
class MeasurementsModel(object):
    def __init__(self, pf_db_url):
        self._last_measurements = {}

        # db_peewee_models.database.init(pf_db_url)
        engine = create_engine("sqlite:///{0}".format(pf_db_url), echo=True)
        DBSession.configure(bind=engine)

        self._fill_from_db()

        self.logger = logging_utils.get_logger("MeasurementsModel")

    def _fill_from_db(self):
        pass

    def add_measurement(self, meas):
        distance = self.__calculate_distance(long(meas['meas_rep']['L1_TA']))

        with transaction.manager:
            obj = models.Measure(imsi=meas['imsi'],
                                 timestamp=datetime.datetime.fromtimestamp(meas['time']),
                                 timing_advance=meas['meas_rep']['L1_TA'],
                                 distance=distance,
                                 phone_number="xxx xxx xx xx",
                                 gps_lat=0.0,
                                 gps_lon=0.0,
                                 )

            models.DBSession.add(obj)

        self._last_measurements[meas['imsi']] = meas['time']

    def __repr__(self):
        return repr(self._last_measurements.keys())

    def __len__(self):
        return len(self._last_measurements)

    def __contains__(self, imsi):
        return imsi in self._last_measurements

    def __unicode__(self):
        return unicode(repr(self._last_measurements.keys()))

    def __calculate_distance(self, ta, te=1.0):
        return 0.001 * ta * 535


# Read queue measurements.
# Add measurement in MeasurementsModel.
# Send welcome message for new imsi.
class MeasHandler(multiprocessing.Process):
    def __init__(self, queue_measurement, pf_db_url):
        self.queue_measurement = queue_measurement

        super(MeasHandler, self).__init__()

        self.__pf_db_url = pf_db_url
        self.__time_to_shutdown = multiprocessing.Event()
        # gc.disable()
        # gc.set_debug(gc.DEBUG_LEAK)

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def run(self):
        self.logger = logging_utils.get_logger("MeasHandler")
        # self._vty_client = osmo_nitb_utils.VTYClient("localhost", 4242, 2)
        self._mm = MeasurementsModel(self.__pf_db_url)

        try:
            while not self.__time_to_shutdown.is_set():
                meas = self.queue_measurement.get()
                if meas is not None:
                    self.process_measure(meas)
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.debug("Catch KeyboardInterrupt!")
        finally:
            self.logger.debug("Process STOPED!")

        # try:
        #     if self.tracking_queue_measurement.qsize() > 0:
        #         meas = self.tracking_queue_measurement.get()
        #         self.process_measure(meas)
        #     elif self.queue_measurement.qsize() > 0:
        #         meas = self.queue_measurement.get()
        #         self.process_measure(meas)
        #     else:
        #         time.sleep(0.1)
        # except (KeyboardInterrupt, SystemExit):
        #     raise
        # except EOFError:
        #     break
        # except:
        #     traceback.print_exc(file=sys.stderr)

    def process_measure(self, meas):
        self.logger.info("Process meas: IMSI {0}".format(meas['imsi']))

        imsi = meas['imsi']
        if imsi not in self._mm:
            self._mm.add_measurement(meas)
            self.logger.info("Detect new IMSI. Send welcome message.")
            # self._vty_client.send_SMS(imsi, wellcome_message)

        else:
            self._mm.add_measurement(meas)
            self.logger.info("IMSI already detected.")


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
    pf_db_url = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'storage', 'pf.sqlite')
    logger.info("pf.sqlite path: {0}".format(pf_db_url))

    # Init shared objects ====================================================
    manager = MeasurementQueueManager()
    manager.start()
    queue_measurement = manager.MeasurementQueue()

    # Init processes =========================================================
    logger.info("Init meas heandler writer")
    meas_handler = MeasHandler(queue_measurement, pf_db_url)
    # meas_handler.daemon = True

    logger.info("Init meas_json listener")
    meas_json_listener = MeasJsonListenerProcess(queue_measurement, args.test_mode)
    # meas_json_listener.daemon = True

    # logger.info("Init xml-rpc server")
    # requsets_server = xmlrpc_server.XMLRPCProcess()

    # Start processes ========================================================
    meas_handler.start()
    logger.info("Meas heandler writer STARTED with pid: {0}".format(
        meas_handler.pid))

    meas_json_listener.start()
    logger.info("meas_json listener STARTED with pid: {0}".format(
        meas_json_listener.pid))

    # requsets_server.start()
    # logger.info("XML-RPC server STARTED with pid: {0}".format(
    #     requsets_server.pid))

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

        # requsets_server.join()
        meas_json_listener.join()
        meas_handler.join()

        manager.join()
