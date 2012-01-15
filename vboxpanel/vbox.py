"""
Interface with VirtualBox OSE.

Spawns VBoxManage in a subprocess.  Hacky.  It would be cleaner to use libvirt.
"""

import contextlib
import logging
import os
import pwd
import re
import shutil
import socket
import subprocess
import tempfile

from pyramid.decorator import reify


log = logging.getLogger(__name__)


class VirtualBox(object):

    VBoxManage = 'VBoxManage'
    vncsnapshot = 'vncsnapshot'

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
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout


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
        port = self.extra_data.get('VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/HostPort')
        if port:
            return int(port)
        else:
            return None

    @reify
    def vnc_screen(self):
        if self.vnc_port and 5900 <= self.vnc_port: # what's the upper limit?
            return ':%d' % (self.vnc_port - 5900)
        else:
            return None

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

    def get_screenshot(self):
        if not self.vnc_screen:
            return None
        try:
            with temporary_directory(prefix='vboxpanel-vncsnapshot-') as d:
                filename = os.path.join(d, 'snapshot.jpg')
                self.vbox._run(self.vbox.vncsnapshot, '-quiet', self.vnc_screen,
                               filename)
                with open(filename, 'rb') as f:
                    return f.read()
        except OSError, e:
            log.error('Failed to get VNC snapshot: %s', e)
            return None


@contextlib.contextmanager
def temporary_directory(prefix='vboxpanel-', suffix=''):
    d = tempfile.mkdtemp(prefix=prefix, suffix=suffix)
    try:
        yield d
    finally:
        shutil.rmtree(d)

