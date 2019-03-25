from collections import OrderedDict


class Storage(object):

    def __init__(self):
        self.results = OrderedDict()

    def add_result(self, client_address, info, result):
        if client_address not in self.results:
            self.results[client_address] = OrderedDict()
        self.results[client_address][info] = result
