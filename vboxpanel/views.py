from pyramid.view import view_config

from vboxpanel.vbox import VirtualBox


vbox = VirtualBox()


@view_config(route_name='home', renderer='vm_list.mako')
def vm_list(request):
    return {'username': vbox.get_username(),
            'hostname': vbox.get_hostname(),
            'vms': vbox.list_vms()}

