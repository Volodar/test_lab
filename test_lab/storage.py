from collections import OrderedDict


class TestCaseRecord(object):
    def __init__(self):
        self.client_id = ''
        self.client_name = ''
        self.client_platform = ''
        self.result_code = 0


class TestCase(object):
    def __init__(self, name):
        self.name = name
        self.results = []


class Storage(object):

    def __init__(self):
        self.results = []

    def add_result(self, test_case_name, result_code, client_id, client_name, client_platform):
        if test_case_name not in self.results:
            self.results[test_case_name] = TestCase(test_case_name)
        
        test_case = self.results[test_case_name]
        record = TestCaseRecord()
        record.result_code = result_code
        record.client_id = client_id
        record.client_name = client_name
        record.client_platform = client_platform
        
        test_case.results.append(record)
        
    def get_records_count(self, test_case_name):
        for test_case in reversed(self.results):
            if test_case.name == test_case_name:
                return len(test_case.results)
        return 0
