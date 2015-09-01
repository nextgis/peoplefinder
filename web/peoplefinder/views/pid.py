# -*- coding: utf-8 -*-
import os.path

class PID(object):
    def __init__(self, path):
        self.path = path

    def get_value(self):
        with open(self.path) as pid_file:
            try:
                value = int(pid_file.readline())
            except ValueError:
                return None
        return value


    def set_value(self, value):
        with open(self.path, 'w') as pid_file:
            pid_file.write('%s' % value)


    value = property(get_value, set_value)
