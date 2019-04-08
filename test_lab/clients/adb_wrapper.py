import re
import time

from test_lab.clients.subprocess_wrapper import SubprocessWrapper


class AdbWrapper(object):
    def __init__(self, subprocess_wrapper=SubprocessWrapper):
        self.connected_to_ip = None
        self.subprocess_wrapper = subprocess_wrapper

    def kill_server(self):
        self.subprocess_wrapper('adb kill-server').call()
        self.connected_to_ip = None

    def connect(self, ip):
        if ip == self.connected_to_ip:
            return

        self.kill_server()
        self.subprocess_wrapper('adb tcpip 5555').call()
        process = self.subprocess_wrapper('adb connect ' + ip)
        code = process.call()
        if code != 0:
            raise RuntimeError('Cannot connect adb to IP: ' + ip)

        time.sleep(1)
        self.connected_to_ip = ip
        return process.out.startswith('connected to ' + ip)

    def devices(self):
        self.kill_server()

        process = self.subprocess_wrapper('adb devices')
        process.call()

        devices = []
        lines = process.out.split('\n')
        lines = [line.strip() for line in lines]
        if 'List of devices attached' not in lines:
            raise RuntimeError('Don`t has connected Android devices')

        line_index = lines.index('List of devices attached') + 1
        while line_index < len(lines):
            matches = re.findall(r'(\w+)\s+device', lines[line_index])
            if matches:
                devices.append(matches[0])

            line_index += 1
        return devices

    def get_usb_device_name(self, identifier):
        process = self.subprocess_wrapper('adb -s {} shell getprop ro.config.CID'.format(identifier))
        if process.call() != 0:
            raise RuntimeError('Cannot get property from device: ' + identifier)
        return process.out.strip()

    def get_remove_device_identifier(self):
        process = self.subprocess_wrapper('adb shell getprop ro.boot.serialno')
        if process.call() != 0:
            raise RuntimeError('Cannot get property from remote device')
        return process.out.strip()

    def install_apk(self, ip, device, path_to_apk):
        command = ' install -r -t {}'.format(path_to_apk)
        if ip is not None:
            self.connect(ip)
            command = 'adb' + command
        else:
            command = 'adb -s {}'.format(device) + command
        process = self.subprocess_wrapper(command)
        if process.call() != 0:
            raise RuntimeError('Cannot install apk to device')

    def uninstall(self, ip, device, package):
        command = ' uninstall {}'.format(package)
        if ip is not None:
            self.connect(ip)
            command = 'adb' + command
        else:
            command = 'adb -s {}'.format(device) + command
        process = self.subprocess_wrapper(command)
        if process.call() != 0:
            raise RuntimeError('Cannot uninstall app from device')

    def start_app(self, ip, device, package, activity, app_args):
        command = ' shell am start -n {}/{} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER'.format(
                    package,
                    activity)

        if ip is not None:
            self.connect(ip)
            command = 'adb' + command
        else:
            command = 'adb -s {}'.format(device) + command

        if app_args is not None:
            command += ' -e ' + app_args

        process = self.subprocess_wrapper(command)
        if process.call() != 0:
            raise RuntimeError('Cannot launch app on device')