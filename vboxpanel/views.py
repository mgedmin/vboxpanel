from pyramid.view import view_config

from vboxpanel.vbox import VirtualBox


vbox = VirtualBox()


@view_config(route_name='home', renderer='vm_list.mako')
def vm_list(request):
    return {'username': 'buildbot',
            'hostname': 'localhost',
            'vms': vbox.list_vms()}

