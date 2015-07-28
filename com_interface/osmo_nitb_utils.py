# -*- coding: utf-8 -*-
import telnetlib


class VTYClient(object):

    def __init__(self, host, port, timeout=0):
        self.tn = telnetlib.Telnet(host, port, timeout)

    def send_sms(self, imsi, text):
        cmd = 'subscriber imsi {0} sms send "{1}"'.format(imsi, text)
        self.tn.write(cmd)

    def foo(self):
        pass
