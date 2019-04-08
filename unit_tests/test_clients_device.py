import unittest
from test_lab.clients.device import Device


class Test(unittest.TestCase):

    def test_create(self):
        device = Device()
        self.assertIsNone(device.identifier)
        self.assertIsNone(device.ip)
        self.assertIsNotNone(device.name)

    def test_is_remote(self):
        device = Device()
        device.ip = 'localhost'
        device.identifier = 'some_id'
        self.assertTrue(device.is_remote())
        self.assertFalse(device.is_usb())

    def test_is_usb(self):
        device = Device()
        device.identifier = 'some_id'
        self.assertTrue(device.is_usb())
        self.assertFalse(device.is_remote())

    def test_get_human_name(self):
        device = Device()
        device.identifier = 'some_id'
        self.assertIsInstance(device.get_human_name(), str)

        device = Device()
        device.ip = 'localhost'
        self.assertIsInstance(device.get_human_name(), str)

        device = Device()
        device.ip = 'localhost'
        device.identifier = 'some_id'
        self.assertIsInstance(device.get_human_name(), str)


if __name__ == '__main__':
    unittest.main()
