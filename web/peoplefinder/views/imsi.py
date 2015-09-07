# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid.view import view_config
from sqlalchemy import func

import time
import xmlrpclib
import socket

from model.models import (
    DBSession,
    Measure,
)

from model.hlr import (
    HLRDBSession,
    Sms,
    Subscriber,
)


@view_config(route_name='get_imsi_list', request_method='GET', renderer='json')
def get_imsi_list(request):
    result = []
    messages = []

    query = DBSession.query(
        Measure.id,
        Measure.imsi,
        func.max(Measure.timestamp).label('last')
    ).group_by(Measure.imsi).all()

    for measure in query:
        dtime = datetime.now() - measure.last
        result.append({
            'id': measure.id,
            'imsi': measure.imsi,
            'last_lur': dtime.total_seconds() // 60
        })


    # Calculate message count for each IMSI
    imsi_list = map(lambda item: item['imsi'], result);
    query = HLRDBSession.query(
        Subscriber.imsi,
        func.count(Sms.id).label('sms_count')
    ).filter((
        (Sms.src_addr == Subscriber.extension) |
        (Sms.dest_addr == Subscriber.extension)) &
        (Sms.protocol_id != 64) &
        (Subscriber.imsi.in_(imsi_list))
    ).group_by(
        Subscriber.imsi
    ).all()

    for record in query:
        messages.append({
            'imsi': int(record.imsi),
            'count': record.sms_count
        })


    if 'jtSorting' in request.GET:
        sorting_params = request.GET['jtSorting'].split(' ')
        sorting_field = sorting_params[0]
        reverse = sorting_params[1] == 'DESC'
        result.sort(key=lambda x: x[sorting_field], reverse=reverse)

    try:
        gps_status = all(request.xmlrpc.get_current_gps())
        gps_status = 'yes' if gps_status else 'no'
    except (socket.error, xmlrpclib.Error) as e:
        gps_status = 'failed'


    return {
        'Result': 'OK',
        'Records': result,
        'Messages': messages,
        'GpsStatus': gps_status
    }


@view_config(route_name='get_imsi_messages', request_method='GET', renderer='json')
def get_imsi_messages(request):
    imsi = int(request.matchdict['imsi'])

    pfnum = request.xmlrpc.get_peoplefinder_number()
    pimsi = request.xmlrpc.get_peoplefinder_imsi()

    query = HLRDBSession.query(
        Sms.id,
        Sms.text,
        Sms.src_addr,
        Sms.dest_addr,
        Sms.created,
        Sms.sent
    ).filter(
        ((Sms.src_addr == Subscriber.extension) |
         (Sms.dest_addr == Subscriber.extension)) &
        (Subscriber.imsi == imsi) &
        (Sms.protocol_id != 64)
    ).order_by(Sms.created.asc())

    result = {
        'imsi': imsi,
        'sms': []
    }

    for obj in query.all():
        dest_subscriber_res = HLRDBSession.query(
            Subscriber.imsi
        ).filter(
            Subscriber.extension == obj.dest_addr
        ).all()

        dest = "xx"
        if len(dest_subscriber_res) > 0:
            dest_imsi = int(dest_subscriber_res[0].imsi)
            dest = "server" if dest_imsi == pimsi else str(dest_imsi)

        direction = 'to' if obj.src_addr == pfnum else 'from'
        sms = {
            'id': obj.id,
            'text': obj.text,
            'type': direction,
            'ts': time.strftime('%d %b %Y, %H:%M:%S', obj.created.timetuple()),
            'dest': dest,
        }

        if direction == 'to':
            sms['sent'] = True if obj.sent else False

        result['sms'].append(sms)

    return result


@view_config(route_name='get_imsi_circles', request_method='GET', renderer='json')
def get_imsi_circles(request):
    imsi = request.matchdict['imsi']
    ts_begin = request.GET.get('timestamp_begin')
    ts_end = request.GET.get('timestamp_end')

    query = DBSession.query(
        Measure.distance,
        Measure.gps_lat,
        Measure.gps_lon,
        Measure.timestamp
    ).filter(
        (Measure.imsi == imsi) &
        (Measure.gps_lat != None) &
        (Measure.gps_lon != None) &
        (Measure.timestamp <= datetime.fromtimestamp(float(ts_end) / 1000))
    ).order_by(Measure.timestamp.asc())

    if ts_begin is not None:
        query = query.filter(
            Measure.timestamp >= datetime.fromtimestamp(float(ts_begin) / 1000)
        )

    result = {
        'imsi': imsi,
        'circles': []
    }

    for circle in query.all():
        result['circles'].append({
            'center': [
                circle.gps_lat,
                circle.gps_lon
            ],
            'radius': circle.distance,
            'ts': time.mktime(circle.timestamp.timetuple())
        })

    return result


@view_config(route_name='send_imsi_message', request_method='POST', renderer='json')
def send_imsi_message(request):
    result = {}
    imsi = request.matchdict['imsi']
    text = request.body

    try:
        sent = request.xmlrpc.send_sms(imsi, text)
        result['status'] = 'sent' if sent else 'failed'
    except (socket.error, xmlrpclib.Error) as e:
        result['status'] = 'failed'
        result['reason'] = e.strerror
    return result


@view_config(route_name='start_tracking', request_method='GET', renderer='json')
def start_tracking(request):
    result = {}
    try:
        request.xmlrpc.start_tracking()
        result['status'] = 'started'
    except (socket.error, xmlrpclib.Error) as e:
        result['status'] = 'failed'
        result['reason'] = e.strerror
    return result


@view_config(route_name='stop_tracking', request_method='GET', renderer='json')
def stop_tracking(request):
    result = {}
    try:
        request.xmlrpc.stop_tracking()
        result['status'] = 'stopped'
    except (socket.error, xmlrpclib.Error) as e:
        result['status'] = 'failed'
        result['reason'] = e.strerror
    return result
