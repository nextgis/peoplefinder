from pyramid.view import view_config


@view_config(route_name='get_imsi_list', renderer='json')
def get_imsi_list(request):
    result = [
        {'id': 1, 'imsi': '410041234567800', 'last_lur': 15},
        {'id': 2, 'imsi': '410041234567810', 'last_lur': 3},
        {'id': 3, 'imsi': '430041234567802', 'last_lur': 1},
        {'id': 4, 'imsi': '210041234234800', 'last_lur': 24},
        {'id': 5, 'imsi': '550041234567810', 'last_lur': 35},
        {'id': 6, 'imsi': '120041234567802', 'last_lur': 13},
        {'id': 7, 'imsi': '430041234234800', 'last_lur': 24}
    ]

    if 'jtSorting' in request.GET:
        sorting_params = request.GET['jtSorting'].split(' ')
        sorting_field = sorting_params[0]
        reverse = sorting_params[1] == 'DESC'
        result.sort(key=lambda x: x[sorting_field], reverse=reverse)

    return {
        'Result': 'OK',
        'Records': result
    }