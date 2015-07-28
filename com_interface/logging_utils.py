# -*- coding: utf-8 -*-
import sys
import logging
import traceback
import threading
import multiprocessing


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter_verbose = logging.Formatter('%(levelname)s - ' +
                                          '%(name)s - ' +
                                          '%(asctime)s ' +
                                          '%(module)s ' +
                                          '%(process)d ' +
                                          '%(thread)d ' +
                                          '%(message)s')

    formatter_simple = logging.Formatter('%(levelname)s - ' +
                                         '%(name)s - ' +
                                         '%(message)s')

    clh = CustomLogHandler('comms_interface.log')
    clh.setLevel(level)
    # clh.setVerboseFormatter(formatter_verbose)
    clh.setSimpleFormatter(formatter_simple)

    logger.addHandler(clh)

    return logger


# ============================================================================
# Define Log Handler
# ============================================================================
class CustomLogHandler(logging.Handler):
    """multiprocessing log handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    """
    def __init__(self, fname):
        logging.Handler.__init__(self)

        # self._file_handler = logging.FileHandler(fname)
        self._stream_handler = logging.StreamHandler()

        self.queue = multiprocessing.Queue(-1)

        thrd = threading.Thread(target=self.receive)
        thrd.daemon = True
        thrd.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        # self._file_handler.setFormatter(fmt)
        self._stream_handler.setFormatter(fmt)

    def setVerboseFormatter(self, fmt):
        # self._file_handler.setFormatter(fmt)
        self._stream_handler.setFormatter(fmt)

    def setSimpleFormatter(self, fmt):
        self._stream_handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                # self._file_handler.emit(record)
                self._stream_handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None
        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._file_handler.close()
        self._stream_handler.close()
        logging.Handler.close(self)
