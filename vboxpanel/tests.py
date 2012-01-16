import unittest
import pwd
import os

from pyramid import testing

from . import main
from . import views
from . import vbox


class VboxTests(unittest.TestCase):

    def test_run(self):
        v = vbox.VirtualBox()
        self.assertEquals(v._run('echo', 'hello', 'world'), "hello world\n")

    def test_get_username(self):
        v = vbox.VirtualBox()
        username = v.get_username()
        self.assertEquals(pwd.getpwnam(username).pw_uid, os.getuid())

    def test_get_hostname(self):
        v = vbox.VirtualBox()
        self.assertTrue(isinstance(v.get_hostname(), str))

    def test_parse_vms(self):
        v = vbox.VirtualBox()
        vms = v._parse_vm_list('"vm1" {uuid1}\n"vm2" {uuid2}')
        self.assertEquals(len(vms), 2)
        self.assertEquals(vms[0].name, 'vm1')
        self.assertEquals(vms[0].vm_id, 'uuid1')
        self.assertEquals(vms[0].vbox, v)

    def test_list_vms(self):
        v = vbox.VirtualBox()
        def run(*args):
            self.assertEquals(args, ('VBoxManage', '-q', 'list', 'vms'))
            return '"vm1" {uuid1}\n"vm2" {uuid2}'
        v._run = run
        vms = v.list_vms()
        self.assertEquals(len(vms), 2)
        self.assertEquals(vms[0].name, 'vm1')
        self.assertEquals(vms[0].vm_id, 'uuid1')
        self.assertEquals(vms[0].vbox, v)

    def test_vms(self):
        v = vbox.VirtualBox()
        v.list_vms = DummyVirtualBox().list_vms
        self.assertEquals(sorted(v.vms), ['ie6box', 'ie7box', 'ie8box'])
        self.assertEquals(v.vms['ie6box'].name, 'ie6box')

    def test_list_running_vms(self):
        v = vbox.VirtualBox()
        def run(*args):
            self.assertEquals(args, ('VBoxManage', '-q', 'list', 'runningvms'))
            return '"vm1" {uuid1}\n"vm2" {uuid2}'
        v._run = run
        vms = v.list_running_vms()
        self.assertEquals(len(vms), 2)
        self.assertEquals(vms[0].name, 'vm1')
        self.assertEquals(vms[0].vm_id, 'uuid1')
        self.assertEquals(vms[0].vbox, v)

    def test_running_vm_names(self):
        v = vbox.VirtualBox()
        v.list_running_vms = DummyVirtualBox().list_running_vms
        self.assertEquals(v.running_vm_names, set(['ie6box']))

    def test_vm_running(self):
        dummy = DummyVirtualBox()
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', dummy)
        vm2 = vbox.VirtualMachine('ie7box', 'uuid2', dummy)
        self.assertTrue(vm1.running)
        self.assertFalse(vm2.running)

    def test_vm_vnc_port(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        vm1.extra_data = {}
        vm2 = vbox.VirtualMachine('ie7box', 'uuid2', DummyVirtualBox())
        vm2.extra_data = {'VBoxInternal/Devices/pcnet/0/LUN#0/Config/vnc/HostPort': '5900'}
        self.assertEqual(vm1.vnc_port, None)
        self.assertEqual(vm2.vnc_port, 5900)

    def test_vm_vnc_screen(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        vm1.vnc_port = None
        vm2 = vbox.VirtualMachine('ie7box', 'uuid2', DummyVirtualBox())
        vm2.vnc_port = 5900
        vm3 = vbox.VirtualMachine('ie8box', 'uuid3', DummyVirtualBox())
        vm3.vnc_port = 5903
        vm4 = vbox.VirtualMachine('ie9box', 'uuid4', DummyVirtualBox())
        vm4.vnc_port = 5899
        self.assertEqual(vm1.vnc_screen, None)
        self.assertEqual(vm2.vnc_screen, ':0')
        self.assertEqual(vm3.vnc_screen, ':3')
        self.assertEqual(vm4.vnc_screen, None)

    def test_vm_extra_data(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        def run(*args):
            self.assertEquals(args, ('VBoxManage', '-q', 'getextradata', 'ie6box', 'enumerate'))
            return 'Key: key1, Value: 42\nKey: key2, Value: 1,2,3,4\n'
        vm1.vbox._run = run
        self.assertEqual(vm1.extra_data, {'key1': '42', 'key2': '1,2,3,4'})

    def test_vm_get_screenshot_no_vnc(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        vm1.vnc_screen = None
        self.assertEqual(vm1.get_screenshot(), None)

    def test_vm_get_screenshot_failure(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        vm1.vnc_screen = ':5'
        def run(*args):
            self.assertEquals(args[:-1], ('vncsnapshot', '-quiet', ':5'))
            raise OSError('could not take a snapshot: this is a test')
        vm1.vbox._run = run
        self.assertEqual(vm1.get_screenshot(), None)

    def test_vm_get_screenshot_success(self):
        vm1 = vbox.VirtualMachine('ie6box', 'uuid1', DummyVirtualBox())
        vm1.vnc_screen = ':5'
        def run(*args):
            self.assertEquals(args[:-1], ('vncsnapshot', '-quiet', ':5'))
            with open(args[-1], 'wb') as f:
                f.write(':)')
            return ''
        vm1.vbox._run = run
        self.assertEqual(vm1.get_screenshot(), ':)')


class AppTests(unittest.TestCase):

    def test_main(self):
        main({})


class DummyVirtualBox(object):

    VBoxManage = 'VBoxManage'
    vncsnapshot = 'vncsnapshot'

    def get_username(self):
        return 'buildbot'

    def get_hostname(self):
        return 'localhost'

    def list_vms(self):
        return [DummyVirtualMachine(name, '{%s}' % name.encode('hex'), self)
                for name in 'ie6box ie7box ie8box'.split()]

    def list_running_vms(self):
        return [DummyVirtualMachine(name, '{%s}' % name.encode('hex'), self)
                for name in 'ie6box'.split()]

    running_vm_names = set(['ie6box'])

    @property
    def vms(self):
        return dict((vm.name, vm) for vm in self.list_vms())


class DummyVirtualMachine(object):

    def __init__(self, name, vm_id, vbox):
        self.name = name
        self.vm_id = vm_id
        self.vbox = vbox

    def get_screenshot(self):
        return {'ie6box': ':)'}.get(self.name)


class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.orig_vbox = views.VirtualBox
        views.VirtualBox = DummyVirtualBox

    def tearDown(self):
        views.VirtualBox = self.orig_vbox
        testing.tearDown()

    def test_vm_list(self):
        info = views.vm_list(self.request)
        self.assertEqual(info['username'], 'buildbot')
        self.assertEqual(info['hostname'], 'localhost')
        self.assertEqual(len(info['vms']), 3)

    def test_screenshot_bad_vm_name(self):
        self.request.matchdict['name'] = 'nosuchbox'
        response = views.screenshot(self.request)
        self.assertEqual(response.status_int, 404)

    def test_screenshot_vm_no_screenshot(self):
        self.request.matchdict['name'] = 'ie7box'
        response = views.screenshot(self.request)
        self.assertEqual(response.status_int, 404)

    def test_screenshot_vm_screenshot(self):
        self.request.matchdict['name'] = 'ie6box'
        response = views.screenshot(self.request)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'image/jpeg')
        self.assertEqual(response.body, ':)')

