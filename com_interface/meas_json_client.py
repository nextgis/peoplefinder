import os
import subprocess
import multiprocessing
import json
import time
import traceback

import logging_utils


# Receive measurement information.
# Add measurement into queue.
class MeasJsonListenerProcess(multiprocessing.Process):
    def __init__(self,
                 queue_measurement,
                 test_mode=False):
        self.queue_measurement = queue_measurement
        super(MeasJsonListenerProcess, self).__init__(name="MeasJsonListenerProcess")

        self.__time_to_shutdown = multiprocessing.Event()
        self.__test_mode = test_mode
        self.__p = None

    def shutdown(self):
        self.logger.debug("Shutdown initiated")
        self.__time_to_shutdown.set()

    def run(self):
        self.logger = logging_utils.get_logger("MeasJsonListenerProcess")
        self.try_to_create_meas_json_process()
        self.start_loop()

    def try_to_create_meas_json_process(self):
        if self.__test_mode:
            cmd = ['python', '-u', os.path.join(os.path.dirname(__file__), u"emulators", u"emulator_meas_json.py")]
        else:
            cmd = ['stdbuf', '-oL', 'meas_json']

        try:
            self.logger.info("Try to create process: {0}".format(" ".join(cmd)))
            self.__p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.logger.info("Process created!")
        except:
            self.logger.error("Process creation failed!")
            self.__p = None

    def start_loop(self):
        while not self.__time_to_shutdown.is_set():
            if self.__p is None:
                self.try_to_create_meas_json_process()
                time.sleep(1)
                continue

            if self.__p.poll() is not None:
                self.logger.error("Process terminated!")
                self.try_to_create_meas_json_process()
                time.sleep(1)
                continue

            line = self.__p.stdout.readline()
            self.logger.debug("Received message:\n{0}".format(line))
            self.process_package(line)

    def process_package(self, data_str):
        try:
            data = json.loads(data_str)

            if 'imsi' not in data:
                self.logger.error("Parsing package error. " +
                                  "IMSI not found. \n" +
                                  "Data:{0}".format(data_str))
                return

            self.queue_measurement.put_measurement(data)

        except ValueError as err:
            self.logger.error("Parsing package error. " +
                              "ValueError: {0} \n".format(err.message) +
                              "Traceback: {0} \n".format(traceback.format_exc()) +
                              "Data:{0}".format(data_str))
        except TypeError as err:
            self.logger.error("Parsing package error. " +
                              "TypeError: {0} \n".format(err.message) +
                              "Traceback: {0} \n".format(traceback.format_exc()) +
                              "Data:{0}".format(data_str))
