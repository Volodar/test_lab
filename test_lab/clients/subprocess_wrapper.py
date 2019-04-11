from __future__ import print_function
import subprocess


class SubprocessWrapper(object):
    def __init__(self, command):
        self.command = command
        self.process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out = ''
        self.err = ''
        self.code = 0

    def call(self):
        print(self.command)
        self.out, self.err = self.process.communicate()
        self.code = self.process.returncode
        print(self.out)
        return self.code
