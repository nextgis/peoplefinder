from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from model.models import (
    DBSession,
    Base,
)


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    config.include('pyramid_mako')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('get_imsi_list', '/imsi/list')
    config.add_route('get_imsi_messages', 'imsi/{imsi}/messages')
    config.add_route('get_imsi_circles', 'imsi/{imsi}/circles')

    config.scan()
    return config.make_wsgi_app()
