# -*- coding: utf-8 -*-

from pyramid.view import view_config
import random

JOB_STATUS = (
    'downloading',
    'ready',
)

START_STATUS = (
    'started',
    'already started',
)

STOP_STATUS = (
    'stopped',
    'not started',
)


@view_config(route_name='download_tiles_start', request_method='POST', renderer='json')
def download_tiles_start(request):
    return {}


@view_config(route_name='download_tiles_status', request_method='GET', renderer='json')
def download_tiles_status(request):
    return {
        'status': random.choice(['downloading', 'ready'])
    }


@view_config(route_name='download_tiles_stop', request_method='GET', renderer='json')
def download_tiles_stop(request):
    return {}
