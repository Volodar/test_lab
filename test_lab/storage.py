
class TestCaseRecord(object):
    def __init__(self):
        self.client_id = ''
        self.client_name = ''
        self.client_platform = ''
        self.result_code = 0
        self.duration = 0


class TestCase(object):
    def __init__(self, name):
        self.name = name
        self.results = []


class Storage(object):

    def __init__(self):
        self.results = []

    def push_test_case(self, test_case_name):
        self.results.append(TestCase(test_case_name))

    def add_result(self, test_case_name, result_code, client_id, client_name, client_platform, seconds):
        test_case = self.get_test_case(test_case_name)
        record = TestCaseRecord()
        record.result_code = result_code
        record.client_id = client_id
        record.client_name = client_name
        record.client_platform = client_platform
        record.duration = seconds

        test_case.results.append(record)

    def get_test_case(self, name):
        for test_case in reversed(self.results):
            if test_case.name == name:
                return test_case
        return None

    def get_records_count(self, test_case_name):
        test_case = self.get_test_case(test_case_name)
        if test_case is None:
            return 0
        return len(test_case.results)
