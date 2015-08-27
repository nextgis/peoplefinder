from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='configuration', renderer='configuration.mako')
def configuration(request):
    return configuration_get(request) if (request.method == 'GET') else configuration_post(request)


def configuration_get(request):
    return {
        'welcome': 'W_MESSAGE',
        'reply': 'REPLY',
        'imsiUpdate': 3000,
        'smsUpdate': 3000,
        'silentSms': 3000
    }


def configuration_post(request):
    return {
        'welcome': request.POST['welcome'],
        'reply': request.POST['reply'],
        'imsiUpdate': request.POST['imsiUpdate'],
        'smsUpdate': request.POST['smsUpdate'],
        'silentSms': request.POST['silentSms']
    }
