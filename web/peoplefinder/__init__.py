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

    xmlrpc_url = 'http://%(xmlrpc.host)s:%(xmlrpc.port)s' % settings
    xmlrpc = lambda request: xmlrpclib.ServerProxy(xmlrpc_url)

    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('get_imsi_list', '/imsi/list')
    config.add_route('get_imsi_messages', 'imsi/{imsi}/messages')
    config.add_route('get_imsi_circles', 'imsi/{imsi}/circles')
    config.add_route('send_imsi_message', 'imsi/{imsi}/message')

    config.add_request_method(xmlrpc, 'xmlrpc', reify=True)

    config.scan()
    return config.make_wsgi_app()
