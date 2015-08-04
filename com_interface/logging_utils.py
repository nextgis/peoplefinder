# -*- coding: utf-8 -*-
import sys
import logging


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter_simple = logging.Formatter('%(levelname)s\t- ' +
                                         '%(asctime)s - ' +
                                         '%(name)s - ' +
                                         '%(message)s')

    clh = logging.StreamHandler(sys.stdout)
    clh.setLevel(level)
    clh.setFormatter(formatter_simple)

    logger.addHandler(clh)

    return logger
