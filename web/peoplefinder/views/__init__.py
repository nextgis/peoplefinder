from pyramid.view import view_config

import socket
import xmlrpclib

from sqlalchemy.orm.exc import NoResultFound

from model.models import (
    DBSession,
    Settings,
)


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='configuration', renderer='configuration.mako')
def configuration(request):
    return configuration_get(request) if (request.method == 'GET') else configuration_post(request)


def configuration_get(request):
    query = DBSession.query(
        Settings.name,
        Settings.value
    )

    result = {}
    for setting in query.all():
        result[setting.name] = setting.value

    try:
        result.update(request.xmlrpc.get_parameters())
    except (socket.error, xmlrpclib.Error) as e:
        result['welcome'] = None
        result['reply'] = None

    return result


def configuration_post(request):
    for setting in ('imsiUpdate', 'smsUpdate', 'silentSms',):
        obj = DBSession.query(Settings).filter_by(name=setting).one()
        obj.value = request.POST.get(setting)
        DBSession.add(obj)

    try:
        request.xmlrpc.set_parameters({
            'wellcome_message': request.POST.get('welcome'),
            'reply_message': request.POST.get('reply')
        })
    except (socket.error, xmlrpclib.Error) as e:
        pass

    return configuration_get(request)
