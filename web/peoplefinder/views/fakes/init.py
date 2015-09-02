from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return configuration_get(request)


@view_config(route_name='configuration', renderer='configuration.mako')
def configuration(request):
    return configuration_get(request) if (request.method == 'GET') else configuration_post(request)


def configuration_get(request):
    return {
        'wellcome_message': 'W_MESSAGE',
        'reply_message': 'REPLY',
        'imsiUpdate': 3000,
        'smsUpdate': 3000,
        'silentSms': 3000
    }


def configuration_post(request):
    return {
        'wellcome_message': request.POST['welcome'],
        'reply_message': request.POST['reply'],
        'imsiUpdate': request.POST['imsiUpdate'],
        'smsUpdate': request.POST['smsUpdate'],
        'silentSms': request.POST['silentSms']
    }
