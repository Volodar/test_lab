import os
from ..clients.device import Device
from ..clients.subprocess_wrapper import SubprocessWrapper
from ..log import Log


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
        else:
            Log.info('OSX Client: app not exist with path: [{}]', self.path_to_app)

    def scan_devices(self):
        pass

    def launch(self, configuration, scenario):
        if not self.devices:
            return 0
        args = configuration.get_scenario_app_args(scenario)

        try:
            self._run(args + ' ' + self.apps_args)
        except RuntimeError:
            return -1
        return 0

    def _run(self, args):
        Log.info('Run application on OSX platform. Args: {}', args)
        args = args.split(' ')
        args.extend(['-test_lab:platform', 'osx'])
        args.extend(['-test_lab:name', 'osx'])
        args.extend(['-test_lab:id', 'osx'])
        args.extend(['-test_lab:server', self.server_url])
        commands = ['open', '-a', self.path_to_app, '--args']
        commands.extend(args)

        process = SubprocessWrapper(commands)
        code = process.call()
        if code != 0: # 253 - no connected devices
            raise RuntimeError('Cannot launch application on OSX. Error:' + process.err)
