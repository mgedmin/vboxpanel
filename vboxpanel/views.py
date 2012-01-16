from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from vboxpanel.vbox import VirtualBox


@view_config(route_name='home', renderer='vm_list.mako')
def vm_list(request):
    vbox = VirtualBox()
    return {'username': vbox.get_username(),
            'hostname': vbox.get_hostname(),
            'vms': vbox.list_vms()}


@view_config(route_name='screenshot')
def screenshot(request):
    vm_name = request.matchdict['name']
    vbox = VirtualBox()
    try:
        jpeg_data = vbox.vms[vm_name].get_screenshot()
    except KeyError:
        return HTTPNotFound()
    if jpeg_data is None:
        return HTTPNotFound()
    else:
        return Response(jpeg_data, content_type='image/jpeg')

