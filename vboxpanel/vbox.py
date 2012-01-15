"""
Interface with VirtualBox OSE.

Spawns VBoxManage in a subprocess.  Hacky.  It would be cleaner to use libvirt.
"""

import os
import pwd
import re
import socket
import subprocess


class VirtualBox(object):

    VBoxManage = 'VBoxManage'

    def get_username(self):
        return pwd.getpwuid(os.getuid()).pw_name

    def get_hostname(self):
        return socket.getfqdn()

    def list_vms(self):
        vms = []
        rx = re.compile('^"([^"]+)" *{([^}]+)}')
        for line in self.run(self.VBoxManage, '-q', 'list', 'vms').splitlines():
            m = rx.match(line)
            if m is not None:
                vms.append(VirtualMachine(m.group(1), m.group(2), self))
        return vms

    def run(self, *argv):
        with subprocess.Popen(argv, stdout=subprocess.PIPE).stdout as f:
            return f.read()


class VirtualMachine(object):

    def __init__(self, name, vm_id, vbox):
        self.name = name
        self.vm_id = vm_id
        self.vbox = vbox

