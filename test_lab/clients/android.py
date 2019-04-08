import os
from test_lab.clients.adb_wrapper import AdbWrapper
from test_lab.clients.device import Device


def get_root():
    project_root = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    project_root = os.path.abspath(project_root + '/../..')
    return project_root


class AndroidClient(object):

    def __init__(self, configuration, adb=None):
        self.package = ''
        self.uninstall_app = True
        self.path_to_app = None
        self.device_limit = -1
        self.devices = []
        self.adb = AdbWrapper() if adb is None else adb

        self.activity = configuration.get('android', 'activity')
        self.package = configuration.get('android', 'package')
        self.path_to_app = configuration.get('android', 'path_to_apk')
        self.path_to_app = os.path.abspath(self.path_to_app.format(root=get_root()))
        self.uninstall_app = configuration.get('android', 'uninstall_required', self.uninstall_app)
        self.device_limit = configuration.get('android', 'device_limit', self.device_limit)

        self.scan_devices()
        self.scan_remote_devices(configuration)

        print 'Available devices'
        for device in self.devices:
            print '  Name: {}, ID: {}, IP: {}'.format(device.name, device.identifier, device.ip)

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)

        for device in self.devices:
            if self.uninstall_app:
                self._uninstall_apk(device)
            self._install_apk(device, self.path_to_app)
            self._run_appplication(device, args)

    def scan_devices(self):
        print('Scan devices:')
        self.adb.kill_server()
        usb_devices = self.adb.devices()
        for identifier in usb_devices:
            device = Device()
            device.identifier = identifier
            device.name = self.adb.get_usb_device_name(identifier)
            self.devices.append(device)

    def scan_remote_devices(self, configuration):
        print('Scan remote devices')

        remote_devices = configuration.get('android', 'remote_devices', [])

        for device_json in remote_devices:
            ip = device_json['ip']
            if self.adb.connect(ip):
                device = Device()
                device.ip = ip
                device.name = device_json.get('name')
                device.identifier = self.adb.get_remove_device_identifier()
                self.devices.append(device)

        self.adb.kill_server()

    def _install_apk(self, device, path_to_apk):
        print('Install apk to device ' + device.get_human_name())
        self.adb.install_apk(device.ip, device.identifier, path_to_apk)

    def _uninstall_apk(self, device):
        print('Uninstall apk on device ' + device.get_human_name())
        self.adb.uninstall(device.ip, device.identifier, self.package)

    def _run_appplication(self, device, app_args=None):
        print('Run application on device ' + device.get_human_name())
        app_args = app_args.split(' ')
        app_args.extend(['-test_lab:platform', 'android'])
        app_args.extend(['-test_lab:name', device.name])
        app_args.extend(['-test_lab:id', device.identifier])
        app_args = ' '.join(args)
        self.adb.start_app(device.ip, device.identifier, self.package, self.activity, app_args)


def tests():
    from test_lab.configuration import Configuration

    config = Configuration('../../configuration.json')

    client = AndroidClient(config)
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()
