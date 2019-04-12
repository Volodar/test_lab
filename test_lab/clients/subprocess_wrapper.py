from __future__ import print_function
import subprocess


class SubprocessWrapper(object):
    def __init__(self, arguments):
        if not isinstance(arguments, str):
            print([arguments])
        assert isinstance(arguments, list) or isinstance(arguments, str)

        if isinstance(arguments, str):
            arguments = arguments.split(' ')

        assert len(arguments) > 0

        self.arguments = arguments
        print(arguments)
        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out = ''
        self.err = ''
        self.code = 0

    def call(self):
        self.out, self.err = self.process.communicate()
        self.code = self.process.returncode
        print(self.out)
        return self.code
