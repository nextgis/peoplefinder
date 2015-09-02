# -*- coding: utf-8 -*
import xmlrpclib
import socket

from pyramid.view import view_config

@view_config(route_name='clear_data', request_method='GET', renderer='json')
def clear_data(request):
    result = {}
    try:
        request.xmlrpc.start_new_session()
        result['status'] = 'cleared'
    except (socket.error, xmlrpclib.Error) as e:
        result['status'] = 'failed'
        result['reason'] = e.strerror
    return result
