from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='configuration', renderer='configuration.mako')
def configuration(request):
    return {}