import subprocess
import re


class AndroidClient(object):

    def __init__(self, configuration):
        self.package = ''
        self.uninstall_app = True
        self.path_to_app = None
        self.device_limit = -1
        self.devices = []

        self.activity = configuration.get('android', 'activity')
        self.package = configuration.get('android', 'package')
        self.path_to_app = configuration.get('android', 'path_to_apk')
        self.uninstall_app = configuration.get('android', 'uninstall_required', self.uninstall_app)
        self.device_limit = configuration.get('android', 'device_limit', self.device_limit)

    def launch(self, configuration, scenario):
        args = configuration.get_scenario_app_args(scenario)

        if self.uninstall_app:
            self.uninstall()
        self.install(self.path_to_app)
        self.run(self.activity, args)

    def scan_devices(self):
        print('Scan devices:')
        process = subprocess.Popen(['adb', 'devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('Error on scan devices: ' + error)
        print(output)
        if error:
            print(error)
        lines = output.split('\n')
        line_index = lines.index('List of devices attached')
        if line_index == '-1':
            raise RuntimeError('Don`t has connected Android devices ')
        line_index += 1
        while line_index < len(lines):
            device = re.findall(r'(\w+)\s+device', lines[line_index])
            if device:
                self.devices.append(device[0])
            if 0 < self.device_limit <= len(self.devices):
                break
            line_index += 1

    def install(self, path_to_apk):
        for device in self.devices:
            self._install_apk(device, path_to_apk)

    def uninstall(self):
        for device in self.devices:
            self._uninstall_apk(device)

    def run(self, activity, args=None):
        for device in self.devices:
            self._run_appplication(device, activity, args)

    def _install_apk(self, device, path_to_apk):
        print('Install apk to device ' + device)
        command = 'adb -s {device} install -r -t {apk}'.format(device=device, apk=path_to_apk)
        process = subprocess.Popen(command.split(' '))
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot install akp to device ' + device)

    def _uninstall_apk(self, device):
        print('Uninstall apk on device ' + device)
        command = 'adb -s {device} uninstall {package}'.format(device=device, package=self.package)
        print command
        process = subprocess.Popen(command.split(' '))
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot uninstall apk on device ' + device)

    def _run_appplication(self, device, activity, app_args=None):
        print('Run application on device ' + device)
        command = 'adb -s {device} shell am start -n {package}/{activity} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER'.format(
            device=device,
            package=self.package,
            activity=activity)

        commands = command.split(' ')
        if app_args is not None:
            commands.append('-e')
            commands.extend(app_args.split(' '))
        print commands

        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(output)
        if error:
            print(error)
        if process.returncode != 0:
            raise RuntimeError('Cannot launch application on device ' + device)


def tests():
    from test_lab.configuration import Configuration

    config = Configuration('../../configuration.json')

    client = AndroidClient(config)
    client.scan_devices()
    client.launch(config, 'window_choose_hero_in_battle')


if __name__ == '__main__':
    tests()