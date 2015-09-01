# -*- coding: utf-8 -*-
import psutil
import subprocess
import threading

from pyramid.view import view_config
from pkg_resources import resource_filename
from psutil import (
    STATUS_SLEEPING,
    STATUS_RUNNING,
    STATUS_ZOMBIE,
    NoSuchProcess,
)

from .pid import PID

pid = PID(resource_filename('peoplefinder', '.pid.file'))

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
    job_status = download_tiles_status(request).get('status')
    if job_status == JOB_STATUS[1]:
        bounds = request.POST.get('bounds').split(',')
        zoom = request.POST.get('zoom')

        minlon, minlat, maxlon, maxlat = bounds
        minzoom, maxzoom = zoom.split(':') if zoom is not None else (10, 18)

        cmd = ['downloadosmtiles',
               '--quiet',
               '--longitude=%s:%s' % (minlon, maxlon),
               '--latitude=%s:%s' % (minlat, maxlat),
               '--zoom=%s:%s' % (minzoom, maxzoom),
               '--destdir=%s' % (request.tile_dir,)]

        proc = subprocess.Popen(cmd)
        pid.value = proc.pid

        t = threading.Thread(target=proc.communicate)
        t.start()

        status = START_STATUS[0]
    
    elif job_status == JOB_STATUS[0]:
        status = START_STATUS[1]

    return dict(status=status, pid=pid.value)


@view_config(route_name='download_tiles_status', request_method='GET', renderer='json')
def download_tiles_status(request):
    status = JOB_STATUS[1]
    if pid.value is not None:
        try:
            proc = psutil.Process(pid.value)
            proc_status = proc.status()
            if proc_status in (STATUS_SLEEPING, STATUS_RUNNING):
                status = JOB_STATUS[0]
            elif proc_status in (STATUS_ZOMBIE,):
                status = JOB_STATUS[1]
        except NoSuchProcess:
            status = JOB_STATUS[1]

    return dict(status=status, pid=pid.value)


@view_config(route_name='download_tiles_stop', request_method='GET', renderer='json')
def download_tiles_stop(request):
    job_status = download_tiles_status(request).get('status')

    if job_status == JOB_STATUS[1]:
        status = STOP_STATUS[1]

    elif job_status == JOB_STATUS[0]:
        proc = psutil.Process(pid.value)
        proc.kill()

        status = STOP_STATUS[0]

    return dict(status=status, pid=pid.value)
