import subprocess
from ..log import Log


class SubprocessWrapper(object):
    def __init__(self, arguments):
        assert isinstance(arguments, list) or isinstance(arguments, str)

        if isinstance(arguments, str):
            arguments = arguments.split(' ')

        assert len(arguments) > 0

        self.arguments = arguments
        Log.debug(' '.join(arguments))
        self.process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out = ''
        self.err = ''
        self.code = 0

    def call(self):
        try:
            self.out, self.err = self.process.communicate(timeout=60)
            self.out = self.out.decode('utf-8') if self.out else ''
            self.err = self.err.decode('utf-8') if self.err else ''
            self.code = self.process.returncode
        except subprocess.TimeoutExpired:
            self.out, self.err = ('Timeout', 'Timeout')
            self.code = -1

        Log.debug(self.out)
        return self.code
