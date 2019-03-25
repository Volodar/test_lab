

class Scenario(object):
    def __init__(self, config):
        self.name = config.get('name')
        self.timeout = config.get('timeout', 300)
        self.app_args = config.get('args', None)
