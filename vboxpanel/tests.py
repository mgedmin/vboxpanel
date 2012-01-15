import unittest

from pyramid import testing

from . import main
from . import views


class AppTests(unittest.TestCase):

    def test_main(self):
        app = main({})


class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()

    def tearDown(self):
        testing.tearDown()

    def test_vm_list(self):
        info = views.vm_list(self.request)
        self.assertEqual(info['username'], 'buildbot')
        self.assertEqual(info['hostname'], 'localhost')
        self.assertEqual(len(info['vms']), 3)

