# -*- coding: utf-8 -*-
import telnetlib

import logging_utils


class VTYClient(object):
    def __init__(self, host="localhost", port=4242, timeout=5):
        self.logger = logging_utils.get_logger("VTYClient")
        self.__readtimeout_secs = timeout

        try:
            self.tn = telnetlib.Telnet(host, port, self.__readtimeout_secs)
        except:
            raise ValueError("Cann't create telnet object")

        try:
            self.tn.read_until("OpenBSC>", self.__readtimeout_secs)
        except:
            raise ValueError("Cann't read welcome message")

        # self.logger.info("Conneect to VTYClient")
        # self.logger.debug("Conneect to VTYClient: {0}".format(welcome_msg))

    def conf_meas_feed(self):
        try:
            self.tn.write("enable\n")

            self.tn.read_until("OpenBSC#", self.__readtimeout_secs)
            self.tn.write("configure terminal\n")

            self.tn.read_until("OpenBSC(config)#", self.__readtimeout_secs)
            self.tn.write("mncc-int\n")

            self.tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.tn.write("meas-feed destination 127.0.0.1 8888\n")

            self.tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.tn.write("write file\n")

            self.tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
        except EOFError as err:
            self.logger.error("Cann't configurate measurement feed: {0}".format(err))
        #     raise err
        # except:
        #     raise

    def send_silent_sms(self, imsi):
        cmd = 'subscriber imsi {0} silent-sms sender imsi {0} send "silent hello"\n'.format(imsi)
        self.logger.debug("Try send silent-sms: {0}".format(cmd))

        try:
            self.tn.write(cmd)
            output = self.tn.read_until("OpenBSC>", self.__readtimeout_secs)

            self.logger.debug("Send silent sms output: {0}".format(output))
        except EOFError as err:
            self.logger.error("Cann't send silent sms: {0}".format(err))
        #     raise err
        # except:
        #     raise

    def send_sms(self, imsi, text):
        # self.logger.debug("Called send_sms func")
        cmd = 'subscriber imsi {0} sms sender extension 10001 send "{1}"\n'.format(imsi, text)
        # self.logger.debug("Try send sms: {0}".format(cmd))

        try:
            self.tn.write(cmd)
            output = self.tn.read_until("OpenBSC>", self.__readtimeout_secs)

            self.logger.debug("Send sms output: {0}".format(output))
        except EOFError as err:
            self.logger.error("Cann't send sms: {0}".format(err))
        #     raise err
        # except:
        #     raise
