# -*- coding: utf-8 -*-
import os

from paste.deploy import loadapp

if 'PASTE_CONFIG' in os.environ:
    app = loadapp('config:' + os.environ['PASTE_CONFIG'])


def application(environ, start_response):
    if os.environ.get('WSGI_FILE_WRAPPER', 'yes').lower() in ('no', 'false'):
        environ.pop('wsgi.file_wrapper', None)

    return app(environ, start_response)
