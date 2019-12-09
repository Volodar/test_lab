from test_lab import TestLab
from test_lab.log import *


def main():
    Log.LEVEL = DEBUG
    lab = TestLab('configuration.json')
    lab.run()


if __name__ == '__main__':
    main()
