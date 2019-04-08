import os
import subprocess


class OsxClient(object):
    def __init__(self, configuration):
        self.path_to_app = configuration.get('osx', 'path_to_app')
        self.apps_args = ''
        self.devices = []
        if os.path.isfile(self.path_to_app) or os.path.isdir(self.path_to_app):
            self.apps_args = configuration.get('osx', 'app_args', '')
            self.devices = ['osx']

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
        args = ' '.join(args)
        command = 'open -a {path} --args {args}'.format(
            path=self.path_to_app,
            args=args)

        commands = command.split(' ')
        print command
        print commands
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot launch application on OSX ')
