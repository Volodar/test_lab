import subprocess


class OsxClient(object):
    def __init__(self, configuration):
        self.path_to_app = configuration.get('osx', 'path_to_app')
        self.apps_args = configuration.get('osx', 'app_args')
        self.devices = ['osx']

    def scan_devices(self):
        pass

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)
        self._run(self.path_to_app, args + ' ' + self.apps_args)

    def _run(self, path, args):
        print('Run application on OSX platform')
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
