import time
import datetime
import multiprocessing
import gps

import logging_utils


class GPSDListenerProcess(multiprocessing.Process):
    def __init__(self,
                 comms_model,
                 test_mode=False):
        self.__comms_model = comms_model
        super(GPSDListenerProcess, self).__init__(name="GPSDListener")

        self.__time_to_shutdown = multiprocessing.Event()

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def run(self):
        self.logger = logging_utils.get_logger("GPSDListenerProcess")

        while not self.__time_to_shutdown.is_set():
            try:
                self.logger.info("Try to create connection with gpsd")
                self.__session = gps.gps()
                self.__session.stream(gps.WATCH_ENABLE)
                self.logger.info("Connection with gpsd is established!")
            except:
                self.logger.error("To establish connection with gpsd failed!")
                time.sleep(0.1)
                continue

            for report in self.__session:
                if self.__time_to_shutdown.is_set():
                    break

                if report.get(u'class') == u'TPV':
                    lat = report.get(u'lat')
                    lon = report.get(u'lon')

                    time_str = report.get('time')
                    if time_str is None:
                        self.logger.error("GPS coordinate does not have timestamps: {0}".format(report))
                        continue

                    time_timestamp = None
                    try:
                        time_timestamp = time.mktime(datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
                    except ValueError as err:
                        self.logger.error("Cann't deformed time in gpsd message: {0}".format(err.message))
                        continue

                    self.__comms_model.add_gps_meas(time_timestamp, lat, lon)

            if not self.__time_to_shutdown.is_set():
                self.logger.error("Connection with gpsd lost!")
