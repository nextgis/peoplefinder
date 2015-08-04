from pyramid.view import view_config
from sqlalchemy import func

import datetime

from model.models import (
    DBSession,
    Measure,
)


@view_config(route_name='get_imsi_list', renderer='json')
def get_imsi_list(request):
    result = []

    query = DBSession.query(
        Measure.id,
        Measure.imsi,
        func.max(Measure.timestamp).label("last")
    ).group_by(Measure.imsi).all()

    for measure in query:
        dtime = datetime.datetime.now() - measure.last
        result.append({
            'id': measure.id,
            'imsi': measure.imsi,
            'last_lur': dtime.total_seconds() // 60
        })

    if 'jtSorting' in request.GET:
        sorting_params = request.GET['jtSorting'].split(' ')
        sorting_field = sorting_params[0]
        reverse = sorting_params[1] == 'DESC'
        result.sort(key=lambda x: x[sorting_field], reverse=reverse)

    return {
        'Result': 'OK',
        'Records': result
    }


@view_config(route_name='get_imsi_messages', renderer='json')
def get_imsi_messages(request):
    imsi = request.matchdict['imsi']
    timestamp_begin = request.GET['timestamp_begin'] if 'timestamp_begin' in request.GET else None
    timestamp_end = request.GET['timestamp_end']

    types = ['from', 'to']

    result = {
        'imsi': imsi,
        'sms': []
    }

    import random
    import string

    if timestamp_begin:
        sms_count = random.randrange(0, 2)
    else:
        sms_count = random.randrange(1, 10)

    c = 0
    while c < sms_count:
        result['sms'].append({
            'type': random.choice(types),
            'text': "".join([random.choice(string.letters) for i in xrange(random.randrange(15, 40))])
        })
        c += 1

    return result