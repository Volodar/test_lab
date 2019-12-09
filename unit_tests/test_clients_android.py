import unittest
from test_lab.clients.android import AndroidClient


class Test1(unittest.TestCase):
    def test_build_args_string_1(self):
        args = '-scenario name -use_inapp_mock yes'
        string = AndroidClient.get_args_string(args)
        self.assertEqual(string, '-e -scenario name -e -use_inapp_mock yes')
    def test_build_args_string_2(self):
        args = ''
        string = AndroidClient.get_args_string(args)
        self.assertEqual(string, '')
    def test_build_args_string_3(self):
        args = '-scenario name yes'
        string = AndroidClient.get_args_string(args)
        self.assertEqual(string, '-e -scenario name')


if __name__ == '__main__':
    unittest.main()
