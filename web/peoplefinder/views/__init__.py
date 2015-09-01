from pyramid.view import view_config

from model.models import (
    DBSession,
    Settings,
)


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return configuration_get(request)


@view_config(route_name='configuration', renderer='configuration.mako')
def configuration(request):
    return (configuration_get(request) if (request.method == 'GET')
        else configuration_post(request))


def configuration_get(request):
    query = DBSession.query(
        Settings.name,
        Settings.value
    )

    result = {}
    for setting in query.all():
        result[setting.name] = setting.value

    return result


def configuration_post(request):
    for setting in ('imsiUpdate', 'smsUpdate', 'silentSms',
                    'welcomeMessage', 'replyMessage'):
        obj = DBSession.query(Settings).filter_by(name=setting).one()
        obj.value = request.POST.get(setting)
        DBSession.add(obj)

    return configuration_get(request)
