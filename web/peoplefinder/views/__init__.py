from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='settings', renderer='settings.mako')
def settings(request):
    return {}