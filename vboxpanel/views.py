from pyramid.view import view_config

from vboxpanel.vbox import VirtualBox


@view_config(route_name='home', renderer='vm_list.mako')
def vm_list(request):
    vbox = VirtualBox()
    return {'username': vbox.get_username(),
            'hostname': vbox.get_hostname(),
            'vms': vbox.list_vms()}

