import os
import signal

from ..clients.adb_wrapper import AdbWrapper
from ..clients.device import Device
from ..log import Log


def get_root():
    project_root = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    project_root = os.path.abspath(project_root + '/../..')
    return project_root


class AndroidClient(object):

    def __init__(self, configuration, adb=None):
        self.server_url = ''
        self.package = ''
        self.uninstall_app = True
        self.install_required = True
        self.path_to_app = None
        self.device_limit = -1
        self.devices = []
        self.adb = AdbWrapper() if adb is None else adb

        self.activity = configuration.get('android', 'activity')
        self.package = configuration.get('android', 'package')
        self.path_to_app = configuration.get('android', 'path_to_apk')
        self.uninstall_app = configuration.get('android', 'uninstall_required', self.uninstall_app)
        self.device_limit = configuration.get('android', 'device_limit', self.device_limit)

        if not self.path_to_app:
            return
        if not os.path.isfile(self.path_to_app) and not os.path.isdir(self.path_to_app):
            Log.info('Android Client: app not exist with path: [{}]', self.path_to_app)
            return

        self.path_to_app = os.path.abspath(self.path_to_app.format(root=get_root()))
        try:
            self.scan_devices()
            self.scan_remote_devices(configuration)
        except RuntimeError:
            pid = os.getpid()
            os.kill(pid, signal.SIGKILL)

        Log.info('Available Android devices')
        for device in self.devices:
            Log.info('  Name: {}, ID: {}, IP: {}', device.name, device.identifier, device.ip)

    @staticmethod
    def get_args_string(args):
        args = args.split(' ')
        result = ''
        i = 0
        while i < len(args) - 1:
            result += '-e {} {} '.format(args[i], args[i+1])
            i += 2
        if result:
            result = result[0:-1]
        return result

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)
        args = ' ' + AndroidClient.get_args_string(args)

        result = 0
        for device in self.devices:
            try:
                if self.uninstall_app or not device.app_installed:
                    self._uninstall_apk(device)
                    self.install_required = True

                if self.install_required:
                    self._install_apk(device, self.path_to_app)
                    device.app_installed = True
                    self.install_required = False
                self._run_appplication(device, args)
            except RuntimeError as error:
                Log.error(str(error))
                result -= 1
                result = max(0, result)
        return result

    def scan_devices(self):
        Log.info('Scan devices:')
        self.adb.kill_server()
        usb_devices = self.adb.devices()
        for identifier in usb_devices:
            device = Device()
            device.identifier = identifier
            device.name = self.adb.get_usb_device_name(identifier)
            self.devices.append(device)

    def scan_remote_devices(self, configuration):
        Log.info('Scan remote devices...')

        remote_devices = configuration.get('android', 'remote_devices', [])

        for device_json in remote_devices:
            ip = device_json['ip'].encode('utf-8')
            if self.adb.connect(ip):
                device = Device()
                device.ip = ip
                device.name = device_json.get('name')
                device.identifier = self.adb.get_remove_device_identifier()
                self.devices.append(device)

        self.adb.kill_server()

    def _install_apk(self, device, path_to_apk):
        Log.info('Install apk to device {}...', device.get_human_name())
        self.adb.install_apk(device.ip, device.identifier, path_to_apk)

    def _uninstall_apk(self, device):
        Log.info('Uninstall apk on device {}...', device.get_human_name())
        self.adb.uninstall(device.ip, device.identifier, self.package)

    def _run_appplication(self, device, app_args=None):
        Log.info('Run application on Android Device: {}. Args: {} ', device.get_human_name(), app_args)
        device_name = device.name
        device_name = device_name.replace(' ', '_')
        app_args = app_args.split(' ')
        app_args.extend(['-e', '-test_lab:platform', 'android'])
        app_args.extend(['-e', '-test_lab:name', device_name])
        app_args.extend(['-e', '-test_lab:id', device.identifier])
        app_args.extend(['-e', '-test_lab:server', self.server_url])
        app_args = ' '.join(app_args)
        self.adb.start_app(device.ip, device.identifier, self.package, self.activity, app_args)


def tests():
    from ..configuration import Configuration

    config = Configuration('../../configuration.json')

    client = AndroidClient(config)
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()
