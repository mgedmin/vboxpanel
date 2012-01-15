from pyramid.view import view_config


@view_config(route_name='home', renderer='vm_list.mako')
def vm_list(request):
    return {'username': 'buildbot',
            'hostname': 'localhost',
            'vms': ['ie6box', 'ie7box', 'ie8box']}

