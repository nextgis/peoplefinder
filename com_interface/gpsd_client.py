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
                keys = report.keys()
                if ('lat' in keys) and ('lon' in keys):
                    lat = report['lat']
                    lon = report['lon']
                    t = time.mktime(datetime.datetime.strptime(report['time'], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())

                    self.__comms_model.add_gps_meas(int(t), lat, lon)

            self.logger.error("Connection with gpsd lost!")
