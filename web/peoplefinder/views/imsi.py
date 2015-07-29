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
