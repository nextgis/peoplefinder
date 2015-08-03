# -*- coding: utf-8 -*-
import telnetlib
import ConfigParser


class VTYClient(object):
    def __init__(self, configuration):
        self.__tn = None

        try:
            self.__host = configuration.get('osmo_nitb', 'vty_host')
            self.__port = configuration.getint('osmo_nitb', 'vty_port')
            self.__readtimeout_secs = configuration.getint('osmo_nitb', 'vty_timeout')

        except ConfigParser.Error as err:
            raise ValueError('Configuration error: {0}'.format(err.message))

    def try_connect(self):
        try:
            self.__tn = telnetlib.Telnet(self.__host, self.__port, self.__readtimeout_secs)
        except:
            self.__tn = None
            return False

        try:
            self.__tn.read_until("OpenBSC>", self.__readtimeout_secs)
        except:
            self.__tn.close()
            self.__tn = None
            return False

        return True

    def is_active(self):
        return self.__tn is not None

    def conf_meas_feed(self):
        if self.__tn is None:
            return False

        try:
            self.__tn.write("enable\n")

            self.__tn.read_until("OpenBSC#", self.__readtimeout_secs)
            self.__tn.write("configure terminal\n")

            self.__tn.read_until("OpenBSC(config)#", self.__readtimeout_secs)
            self.__tn.write("mncc-int\n")

            self.__tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.__tn.write("meas-feed destination 127.0.0.1 8888\n")

            self.__tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)
            self.__tn.write("write file\n")

            self.__tn.read_until("OpenBSC(config-mncc-int)#", self.__readtimeout_secs)

            return True
        except:
            self.__tn = None
            return False

    def send_silent_sms(self, imsi):
        if self.__tn is None:
            return False

        cmd = 'subscriber imsi {0}  silent-sms sender extension 10001 send "silent hello"\n'.format(imsi)

        try:
            self.__tn.write(cmd)
            self.__tn.read_until("OpenBSC>", self.__readtimeout_secs)

            return True

        except:
            self.__tn = None
            return False

    def send_sms(self, imsi, text):
        if self.__tn is None:
            return False

        cmd = 'subscriber imsi {0} sms sender extension 10001 send "{1}"\n'.format(imsi, text)
        try:
            self.__tn.write(cmd)
            self.__tn.read_until("OpenBSC>", self.__readtimeout_secs)

            return True

        except:
            self.__tn = None
            return False
