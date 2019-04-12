from __future__ import print_function
import os
from device import Device
from subprocess_wrapper import SubprocessWrapper


class OsxClient(object):
    def __init__(self, configuration):
        self.server_url = ''
        self.path_to_app = configuration.get('osx', 'path_to_app')
        self.apps_args = ''
        self.devices = []
        if os.path.isfile(self.path_to_app) or os.path.isdir(self.path_to_app):
            self.apps_args = configuration.get('osx', 'app_args', '')
            device = Device()
            self.devices.append(device)

    def scan_devices(self):
        pass

    def launch(self, configuration, scenario):
        if not self.devices:
            return
        args = configuration.get_scenario_app_args(scenario)
        self._run(args + ' ' + self.apps_args)

    def _run(self, args):
        print('Run application on OSX platform')
        args = args.split(' ')
        args.extend(['-test_lab:platform', 'osx'])
        args.extend(['-test_lab:name', 'osx'])
        args.extend(['-test_lab:id', 'osx'])
        args.extend(['-test_lab:server', self.server_url])
        args = ' '.join(args)
        command = 'open -a {path} --args {args}'.format(
            path=self.path_to_app,
            args=args)

        process = SubprocessWrapper(command)
        code = process.call()
        if code != 0: # 253 - no connected devices
            raise RuntimeError('Cannot launch application on OSX. Error:' + process.err)
