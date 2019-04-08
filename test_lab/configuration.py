import json
import os


class Configuration(object):
    def __init__(self, path_co_json=None, json_dict=None):
        if path_co_json and os.path.isfile(path_co_json):
            self.json = json.load(open(path_co_json))
        elif json_dict:
            self.json = json_dict
        else:
            raise RuntimeError('Cannot load configuration json')

    def get(self, client, key, default=None):
        if client not in self.json['clients'] and default is None:
            raise RuntimeError('Cannot find parameter [clients]->[{}]->[{}] in configuration json'.format(client, key))
        if key not in self.json['clients'][client] and default is None:
            raise RuntimeError('Cannot find parameter [clients]->[{}]->[{}] in configuration json'.format(client, key))
        return self.json['clients'][client].get(key, default)

    def get_scenario_config_value(self, scenario, key):
        for test_config in self.json['scenarios']:
            if test_config['name'] == scenario and key in test_config:
                return test_config[key]
        return None

    def get_scenario_app_args(self, scenario):
        return str(self.get_scenario_config_value(scenario, 'app_args'))

    def get_scenario_timeout(self, scenario):
        return self.get_scenario_config_value(scenario, 'timeout')
