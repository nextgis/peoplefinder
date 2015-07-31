import os
import subprocess
import multiprocessing
import json
import time

import logging_utils


# Receive measurement information.
# Add measurement into queue.
class MeasJsonListenerProcess(multiprocessing.Process):
    def __init__(self,
                 queue_measurement,
                 test_mode=False):
        self.queue_measurement = queue_measurement
        super(MeasJsonListenerProcess, self).__init__()

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
            self.logger.error("Failed to create process")
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
            self.logger.debug("Received message:\n {0}".format(line))
            self.process_package(line)

    def process_package(self, data_str):
        try:
            data = json.loads(data_str)

            if 'imsi' not in data:
                self.logger.error("Parsing package error. " +
                                  "IMSI not found. \n" +
                                  "Data:{0}".format(data_str))
                return

            self.queue_measurement.put(data)

        except ValueError as err:
            self.logger.error("Parsing package error. " +
                              "ValueError: {0} \n" +
                              "Data: {1}".format(err, data_str))
        except TypeError as err:
            self.logger.error("Parsing package error. " +
                              "TypeError: {0} \n" +
                              "Data: {1}".format(err, data_str))

# # Listen udp port.
# # Receive measurement information.
# # Add measurement into queue.
# class MeasJsonListenerProcess(multiprocessing.Process):

#     recv_buffer_size = 81920
#     recv_datagram_size = 1024

#     def __init__(self,
#                  queue_measurement,
#                  tracking_imsi):
#         self.queue_measurement = queue_measurement
#         self.tracking_imsi = tracking_imsi
#         super(MeasJsonListenerProcess, self).__init__()

#         self.server_address = ("", 8888)

#         # gc.disable()
#         # gc.set_debug(gc.DEBUG_LEAK)

#     def run(self):
#         self.logger = logging_utils.get_logger("MeasJsonListenerProcess")

#         self.logger.info("MeasJsonListenerProcess run START")
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.logger.info("MeasJsonListenerProcess socket created")
#         try:
#             self.sock.bind(self.server_address)
#             self.logger.info("MeasJsonListenerProcess socket bind")
#             self.sock.setsockopt(socket.SOL_SOCKET,
#                                  socket.SO_RCVBUF,
#                                  self.recv_buffer_size)
#             self.logger.info("MeasJsonListenerProcess socket setsockopt")
#         except:
#             self.sock.close()
#             raise

#         self.server_address = self.sock.getsockname()

#         self.logger.info("MeasJsonListenerProcess socket getsockname")

#         while True:
#             try:
#                 self.logger.info("Wait message")
#                 data, addr = self.sock.recvfrom(self.recv_datagram_size)
#                 self.logger.info("Received message from {0}".format(addr))

#                 self.process_package(data)
#             except socket.error as err:
#                 self.logger.error("Receive message error: {0}".format(err))

#         self.sock.close()

#     def process_package(self, data_str):
#         try:
#             data = json.loads(data_str)

#             if 'imsi' not in data:
#                 self.logger.error("Parsing package error. " +
#                                   "IMSI not found. \n" +
#                                   "Data:{0}".format(data_str))
#                 return

#             imsi = self.tracking_imsi.get_obj().value

#             if imsi != u'no traking' and imsi == data['imsi']:
#                 self.queue_measurement.put(data, True)
#             else:
#                 self.queue_measurement.put(data)

#         except ValueError as err:
#             self.logger.error("Parsing package error. " +
#                               "ValueError: {0} \n" +
#                               "Data: {1}".format(err, data_str))
#         except TypeError as err:
#             self.logger.error("Parsing package error. " +
#                               "TypeError: {0} \n" +
#                               "Data: {1}".format(err, data_str))
