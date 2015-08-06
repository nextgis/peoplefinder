from pyramid.config import Configurator
from sqlalchemy import engine_from_config

import xmlrpclib

from model.models import (
    DBSession,
    Base,
)

from model.hlr import (
    HLRDBSession,
)


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.pf.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    engine = engine_from_config(settings, 'sqlalchemy.hlr.')
    HLRDBSession.configure(bind=engine)

    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('get_imsi_list', '/imsi/list')
    config.add_route('get_imsi_messages', 'imsi/{imsi}/messages')
    config.add_route('get_imsi_circles', 'imsi/{imsi}/circles')

    proxy = xmlrpclib.ServerProxy('http://localhost:8123')

    # get_peoplefinder_number = lambda request: '10001' # TODO: Get from xmlrpc
    try:
        get_peoplefinder_number = proxy.get_peoplefinder_number()
    except xmlrpclib.Error as e:
        print "ERROR", e

    config.add_request_method(get_peoplefinder_number, 'peoplefinder_number', reify=True)

    config.scan()
    return config.make_wsgi_app()
