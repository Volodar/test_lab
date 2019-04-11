from __future__ import print_function
import re
import os
from device import Device
from subprocess_wrapper import SubprocessWrapper


# Used tool: https://github.com/ios-control/ios-deploy
# TODO: add to README.md


class IosClient(object):
    
    def __init__(self, configuration):
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
        
        self.scan_devices()
        self.scan_remote_devices(configuration)
    
    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)
        
        if self.uninstall_app:
            self.uninstall()
        self.install_and_run(self.path_to_app, args)
    
    def scan_devices(self):
        print('Scan devices:')
        
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

        print('Available iOS devices')
        for device in self.devices:
            print('  Name: {}, ID: {}, IP: {}'.format(device.name, device.identifier, device.ip))
    
    def scan_remote_devices(self, configuration):
        pass
    
    def uninstall(self):
        for device in self.devices:
            self._uninstall_app(device)
    
    def install_and_run(self, path, args):
        for device in self.devices:
            self._install_and_run(device, path, args)
    
    def _uninstall_app(self, device):
        print('Uninstall app on device ' + device.identifier)
        command = '{root}/ios-deploy --uninstall_only --bundle_id {bundle} -i {device}'.format(root=self.root,
                                                                                               device=device.identifier,
                                                                                               bundle=self.package)
        process = SubprocessWrapper(command)
        code = process.call()
        if code != 0:
            raise RuntimeError('Cannot uninstall app on device ' + device.identifier)
    
    def _install_and_run(self, device, path, args):
        print('Install app to device ' + device.identifier)
        args = args.split(' ')
        args.extend(['-test_lab:platform', 'ios'])
        args.extend(['-test_lab:name', device.name])
        args.extend(['-test_lab:id', device.identifier])
        args = ' '.join(args)
        command = '{root}/ios-deploy --justlaunch --debug --bundle {path} -i {device} --no-wifi'.format(root=self.root,
                                                                                                        device=device.identifier,
                                                                                                        path=path)
        commands = command.split(' ')
        if args is not None:
            commands.extend(['--args', '{}'.format(args if isinstance(args, str) else ' '.join(args))])
        command = ' '.join(commands)
        
        process = SubprocessWrapper(command)
        code = process.call()
        if code != 0:
            raise RuntimeError('Cannot install app to device ' + device.identifier)


def tests():
    from test_lab.configuration import Configuration
    
    config = Configuration('../../configuration.json')
    
    client = IosClient(config)
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()
