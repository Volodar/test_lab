import unittest
from test_lab.clients.adb_wrapper import AdbWrapper


class AndroidDeviceDummy(object):
    def __init__(self):
        self.applications = []
        self.identifier = 'id_dummy'
        self.ip = '192.168.0.1'


class AdbServer(object):
    STATUS = 'kill'
    PORT = 0
    IP = None
    APPLICATIONS = []
    STARTED_APPS = []
    REMOTE_DEVICES = ['192.168.0.2']

    def __init__(self):
        pass

    @staticmethod
    def clear():
        AdbServer.STATUS = 'kill'
        AdbServer.PORT = 0
        AdbServer.IP = None
        AdbServer.APPLICATIONS = []
        AdbServer.STARTED_APPS = []


class SubprocessDummy(object):
    ADB = None

    def __init__(self, arguments):
        if isinstance(arguments, str):
            arguments = arguments.split(' ')

        assert isinstance(arguments, list)
        assert len(arguments) > 0

        self.arguments = arguments
        self.out = ''
        self.err = ''
        self.code = 0

    def call(self):
        self.dummy_call()
        return self.code

    def dummy_call(self):
        commands = self.arguments

        if commands[0] == 'adb':
            adb_command = commands[1]
            if adb_command == '-s':
                new_commands = commands[:1]
                new_commands.extend(commands[3:])
                commands = new_commands
                adb_command = commands[1]

            if adb_command == 'shell':
                adb_command = commands[2]
            if adb_command == 'am':
                adb_command = commands[3]

            AdbServer.STATUS = 'run'

            if adb_command == 'kill-server':
                AdbServer.STATUS = 'kill'
                AdbServer.IP = None
                AdbServer.PORT = 0
                self.out = ''
                self.err = ''
                self.code = 0
            elif adb_command == 'tcpip':
                AdbServer.STATUS = 'run'
                AdbServer.PORT = int(commands[2])
                self.out = ''
                self.err = ''
                self.code = 0
            elif adb_command == 'connect':
                ip = commands[2]
                if ip in AdbServer.REMOTE_DEVICES:
                    AdbServer.IP = ip
                    self.out = ''
                    self.err = ''
                    self.code = 0
                else:
                    self.out = ''
                    self.err = 'Cannot connect to device'
                    self.code = 1
            elif adb_command == 'devices':
                self.out = 'List of devices attached\r\ntest_device device\n'
                self.err = ''
                self.code = 0
            elif adb_command == 'getprop':
                if commands[3] == 'ro.product.model':
                    self.out = 'test_name'
                elif commands[3] == 'ro.boot.serialno':
                    self.out = 'test_device'
                self.err = ''
                self.code = 0
            elif adb_command == 'install':

                replace = '-r' in commands
                allow_test = '-t' in commands

                if not allow_test:
                    self.out = ''
                    self.err = 'CANNOT INSTALL TEST APK'
                    self.code = 1
                    return

                if replace:
                    commands.remove('-r')
                if allow_test:
                    commands.remove('-t')
                app = commands[2]

                if not replace and app in AdbServer.APPLICATIONS:
                    self.out = ''
                    self.err = 'CANNOT INSTALL APK'
                    self.code = 1
                    return
                if app not in AdbServer.APPLICATIONS:
                    AdbServer.APPLICATIONS.append(app)
                self.out = ''
                self.err = 'Success'
                self.code = 0
            elif adb_command == 'uninstall':
                app = commands[2]

                if app not in AdbServer.APPLICATIONS:
                    self.err = ''
                    self.out = 'CANNOT UNINSTALL APK'
                    self.code = 0
                else:
                    AdbServer.APPLICATIONS.remove(app)
                    self.out = 'Success'
                    self.err = ''
                    self.code = 0
            elif adb_command == 'start':
                app = commands[commands.index('-n') + 1]
                package, activity = app.split('/')
                if package in AdbServer.APPLICATIONS and activity == 'test_activity':
                    AdbServer.STARTED_APPS.append(package)
                    self.out = 'Success'
                    self.err = ''
                    self.code = 0
                else:
                    self.out = ''
                    self.err = 'Error'
                    self.code = 1
            else:
                print '\nCommand:'
                print adb_command


class TestAdb(unittest.TestCase):

    def test_kill_server(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.kill_server()

        self.assertEqual(AdbServer.STATUS, 'kill')

    def test_connect(self):
        AdbServer.clear()
        ip = '192.168.0.2'
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.connect(ip)

        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.PORT, 5555)
        self.assertEqual(AdbServer.STATUS, 'run')

    def test_devices(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        devices = wrapper.devices()

        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(devices, ['test_device'])

    def test_get_usb_device_name(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        devices = wrapper.devices()
        name = wrapper.get_usb_device_name('test_device')

        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(name, 'test_name')

    def test_get_remove_device_identifier(self):
        AdbServer.clear()
        ip = '192.168.0.2'
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.connect(ip)
        identifier = wrapper.get_remove_device_identifier()

        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(identifier, 'test_device')

    def test_install_apk_to_local_device(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        device = wrapper.devices()[0]
        wrapper.install_apk(None, device, 'test_apk')

        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, ['test_apk'])

    def test_install_apk_to_remote_device(self):
        AdbServer.clear()
        ip = '192.168.0.2'
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.connect(ip)
        identifier = wrapper.get_remove_device_identifier()
        wrapper.install_apk(ip, identifier, 'test_apk')

        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, ['test_apk'])

    def test_uninstall_from_local_device(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        device = wrapper.devices()[0]

        wrapper.uninstall(None, device, 'test_apk')
        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, [])

        wrapper.install_apk(None, device, 'test_apk')
        self.assertEqual(AdbServer.APPLICATIONS, ['test_apk'])

        wrapper.uninstall(None, device, 'test_apk')
        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, [])

    def test_uninstall_from_remote_device(self):
        AdbServer.clear()
        ip = '192.168.0.2'
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.connect(ip)
        identifier = wrapper.get_remove_device_identifier()

        wrapper.uninstall(ip, identifier, 'test_apk')
        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, [])

        wrapper.install_apk(ip, identifier, 'test_apk')
        self.assertEqual(AdbServer.APPLICATIONS, ['test_apk'])

        wrapper.uninstall(ip, identifier, 'test_apk')
        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.STATUS, 'run')
        self.assertEqual(AdbServer.APPLICATIONS, [])

    def test_start_app_on_local_device(self):
        AdbServer.clear()
        wrapper = AdbWrapper(SubprocessDummy)
        device = wrapper.devices()[0]
        wrapper.install_apk(None, device, 'test_apk')

        wrapper.start_app(None, device, 'test_apk', 'test_activity', 'arg0 arg1')
        self.assertEqual(AdbServer.IP, None)
        self.assertEqual(AdbServer.STARTED_APPS, ['test_apk'])

    def test_start_app_on_remote_device(self):
        AdbServer.clear()
        ip = '192.168.0.2'
        wrapper = AdbWrapper(SubprocessDummy)
        wrapper.connect(ip)
        identifier = wrapper.get_remove_device_identifier()
        wrapper.install_apk(ip, identifier, 'test_apk')

        wrapper.start_app(ip, identifier, 'test_apk', 'test_activity', 'arg0 arg1')
        self.assertEqual(AdbServer.IP, ip)
        self.assertEqual(AdbServer.STARTED_APPS, ['test_apk'])



if __name__ == '__main__':
    unittest.main()
