import subprocess
import re
import os


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

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)

        if self.uninstall_app:
            self.uninstall()
        self.install_and_run(self.path_to_app, args)

    def scan_devices(self):
        print('Scan devices:')

        command = '{root}/ios-deploy -c --timeout 1'.format(root=self.root)
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        if error:
            print(process.returncode, error)
        if process.returncode != 0 and process.returncode != 253:
            raise RuntimeError('Error on scan devices: ' + error)

        lines = output.split('\n')
        for line in lines:
            device = re.findall(r"Found ([\w-]+).+a\.k\.a\. '(.+)'", line)
            if device and device[0]:
                self.devices.append([device[0][0], device[0][1]])
            if 0 < self.device_limit <= len(self.devices):
                break
        print self.devices

    def uninstall(self):
        for device in self.devices:
            self._uninstall_app(device)

    def install_and_run(self, path, args=None):
        for device in self.devices:
            self._install_and_run(device, path, args)

    def _uninstall_app(self, device):
        print('Uninstall app on device ' + device[1])
        command = '{root}/ios-deploy --uninstall_only --bundle_id {package} -i {device}'.format(root=self.root,
                                                                                                device=device[0],
                                                                                                package=self.package)
        process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot uninstall app on device ' + device[1])

    def _install_and_run(self, device, path, args):
        print('Install app to device ' + device[1])
        command = '{root}/ios-deploy --justlaunch --debug --bundle {path} -i {device}'.format(root=self.root,
                                                                                                device=device[0],
                                                                                                path=path)
        commands = command.split(' ')
        if args is not None:
            commands.extend(['--args', '{}'.format(args if isinstance(args, str) else ' '.join(args))])
        print ' '.join(commands)
        null = open('/dev/null', 'w')
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   stdin=null)
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot install app to device ' + device[1])


def tests():
    from test_lab.configuration import Configuration

    config = Configuration('../../configuration.json')

    client = IosClient(config)
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()