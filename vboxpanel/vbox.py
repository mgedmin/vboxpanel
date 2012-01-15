"""
Interface with VirtualBox OSE.

Spawns VBoxManage in a subprocess.  Hacky.  It would be cleaner to use libvirt.
"""

import os
import pwd
import re
import socket
import subprocess

from pyramid.decorator import reify


class VirtualBox(object):

    VBoxManage = 'VBoxManage'

    def get_username(self):
        return pwd.getpwuid(os.getuid()).pw_name

    def get_hostname(self):
        return socket.getfqdn()

    def list_vms(self):
        return self._parse_vm_list(
            self._run(self.VBoxManage, '-q', 'list', 'vms'))

    def list_running_vms(self):
        return self._parse_vm_list(
            self._run(self.VBoxManage, '-q', 'list', 'runningvms'))

    @reify
    def running_vm_names(self):
        return set(vm.name for vm in self.list_running_vms())

    def _parse_vm_list(self, output):
        vms = []
        rx = re.compile('^"([^"]+)" *{([^}]+)}')
        for line in output.splitlines():
            m = rx.match(line)
            if m is not None:
                vms.append(VirtualMachine(m.group(1), m.group(2), self))
        return vms

    def _run(self, *argv):
        with subprocess.Popen(argv, stdout=subprocess.PIPE).stdout as f:
            return f.read()


class VirtualMachine(object):

    def __init__(self, name, vm_id, vbox):
        self.name = name
        self.vm_id = vm_id
        self.vbox = vbox

    @reify
    def running(self):
        return self.name in self.vbox.running_vm_names

    @reify
    def vnc_port(self):
        # This assumes
        #   1. A native VNC server was installed in the guest
        #   2. Somebody set up guest port mapping with the name 'vnc'
        return self.extra_data.get('VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/HostPort')

    @reify
    def extra_data(self):
        return self._parse_extra_data(self.vbox._run(
            self.vbox.VBoxManage, '-q', 'getextradata', self.name, 'enumerate'))

    def _parse_extra_data(self, output):
        extradata = {}
        rx = re.compile('^Key: ([^,]+), Value: (.*)')
        for line in output.splitlines():
            m = rx.match(line)
            if m is not None:
                extradata[m.group(1)] = m.group(2)
        return extradata

