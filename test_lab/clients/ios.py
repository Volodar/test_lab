import re
import os
import signal

from .android import get_root
from .device import Device
from .subprocess_wrapper import SubprocessWrapper
from ..log import Log


# Used tool: https://github.com/ios-control/ios-deploy
# TODO: add to README.md


class IosClient(object):

    def __init__(self, configuration):
        self.server_url = ''
        self.package = ''
        self.uninstall_app = True
        self.path_to_app = None
        self.device_limit = -1
        self.devices = []
        self.root = os.path.dirname(os.path.abspath(__file__))

        self.package = configuration.get('ios', 'package')
        self.path_to_app = configuration.get('ios', 'path_to_ipa')
        self.uninstall_app = configuration.get('ios', 'uninstall_required', self.uninstall_app)
        self.device_limit = configuration.get('ios', 'device_limit', self.device_limit)

        if not self.path_to_app:
            return
        if not os.path.isfile(self.path_to_app) and not os.path.isdir(self.path_to_app):
            Log.info('iOS Client: app not exist with path: [{}]', self.path_to_app)
            return

        self.path_to_app = os.path.abspath(self.path_to_app.format(root=get_root()))
        try:
            self.scan_devices()
            self.scan_remote_devices(configuration)
        except RuntimeError:
            pid = os.getpid()
            os.kill(pid, signal.SIGKILL)

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)

        if self.uninstall_app:
            self.uninstall()
        return self.install_and_run(self.path_to_app, args)

    def scan_devices(self):
        Log.info('Scan devices...')

        process = SubprocessWrapper('{root}/ios-deploy -c --timeout 2'.format(root=self.root))
        code = process.call()
        if code != 0 and code != 253:  # 253 - no connected devices
            raise RuntimeError('Error on scan devices: ' + process.err)

        lines = process.out.split('\n')
        for line in lines:
            match = re.findall(r"Found ([\w-]+).+a\.k\.a\. '(.+)'", line)
            if match and match[0]:
                device = Device()
                device.identifier = match[0][0]
                device.name = match[0][1]
                self.devices.append(device)
            if 0 < self.device_limit <= len(self.devices):
                break

        Log.info('Available iOS devices:')
        for device in self.devices:
            Log.info('  Name: {}, ID: {}, IP: {}', device.name, device.identifier, device.ip)

    def scan_remote_devices(self, configuration):
        pass

    def uninstall(self):
        for device in self.devices:
            self._uninstall_app(device)

    def install_and_run(self, path, args):
        result = 0
        for device in self.devices:
            try:
                self._install_and_run(device, path, args)
            except RuntimeError:
                result -= 1
        return result

    def _uninstall_app(self, device):
        Log.debug('Uninstall app on device {}...', device.identifier)
        command = '{root}/ios-deploy --uninstall_only --bundle_id {bundle} -i {device}'.format(root=self.root,
                                                                                               device=device.identifier,
                                                                                               bundle=self.package)
        process = SubprocessWrapper(command)
        code = process.call()
        if code != 0:
            raise RuntimeError('Cannot uninstall app on device ' + device.identifier)

    def _install_and_run(self, device, path, args):
        Log.info('Run application on iOS Device: {}. Args: {} ', device.get_human_name(), args)
        Log.info('Install app to device...')
        args = args.split(' ')

        device.name = device.name.replace(' ', '_')

        args.extend(['-test_lab:platform', 'ios'])
        args.extend(['-test_lab:name', device.name])
        args.extend(['-test_lab:id', device.identifier])
        args.extend(['-test_lab:server', self.server_url])

        commands = [
            '{root}/ios-deploy'.format(root=self.root),
            '--justlaunch',
            '--debug',
            '--bundle', path,
            '-i', device.identifier,
            '--no-wifi'
        ]
        commands.extend(['--args', ' '.join(args)])
        process = SubprocessWrapper(commands)
        code = process.call()
        if code != 0:
            Log.error('Error on install app to ios Device: {} [{}]', device.identifier, device.name)
            Log.error('Out:')
            Log.error('    \n'.join(process.out.split('\n')))
            Log.error('Error:')
            Log.error('    \n'.join(process.err.split('\n')))
            raise RuntimeError('Cannot install app to device: {}', device.identifier)


def tests():
    from ..configuration import Configuration

    config = Configuration('../../configuration.json')

    client = IosClient(config)
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()
