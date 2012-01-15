import unittest

from pyramid import testing

from . import main
from . import views
from . import vbox


class VboxTests(unittest.TestCase):

    def test_run(self):
        v = vbox.VirtualBox()
        self.assertEquals(v.run('echo', 'hello', 'world'), "hello world\n")

    def test_list(self):
        v = vbox.VirtualBox()
        def run(*args):
            self.assertEquals(args, ('VBoxManage', '-q', 'list', 'vms'))
            return '"vm1" {uuid1}\n"vm2" {uuid2}'
        v.run = run
        vms = v.list_vms()
        self.assertEquals(len(vms), 2)
        self.assertEquals(vms[0].name, 'vm1')
        self.assertEquals(vms[0].vm_id, 'uuid1')
        self.assertEquals(vms[0].vbox, v)


class AppTests(unittest.TestCase):

    def test_main(self):
        main({})


class DummyVirtualBox(object):

    def list_vms(self):
        return [vbox.VirtualMachine(name, '{%s}' % name.encode('hex'), self)
                for name in 'ie6box ie7box ie8box'.split()]


class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.orig_vbox = views.vbox
        views.vbox = DummyVirtualBox()

    def tearDown(self):
        views.vbox = self.orig_vbox
        testing.tearDown()

    def test_vm_list(self):
        info = views.vm_list(self.request)
        self.assertEqual(info['username'], 'buildbot')
        self.assertEqual(info['hostname'], 'localhost')
        self.assertEqual(len(info['vms']), 3)

