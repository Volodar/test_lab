import time
import urlparse
from threading import Thread
from threading import Lock
from server import HttpServer
from configuration import Configuration
from scenario import Scenario
from clients.android import AndroidClient
from clients.ios import IosClient
from clients.osx import OsxClient


class TestLab(object):
    def __init__(self, path_or_json):
        RequestHandler.TEST_LAB = self
        self.configuration = Configuration(path_or_json)

        self.server = None
        self.server_url = self.configuration.json.get('server_url', 'http://127.0.0.1:8010')
        self.server_url = self.server_url.encode('utf-8')
        if ':' in self.server_url:
            index = self.server_url.rfind(':')
            self.server_port = int(self.server_url[index+1:])
            self.server_url = self.server_url[:index]
        else:
            self.server_port = 80
        self.server_thread = None
        self.monitor_thread = None

        self.tests = {}
        self.scenarios = []
        for scenario in self.configuration.json['scenarios']:
            self.scenarios.append(Scenario(scenario))
            self.tests[self.scenarios[-1].name] = []

        self.clients = []
        self.clients_count = 0
        self._create_clients()
        self._terminate = False
        self.mutex = Lock()

    def run(self):
        self._run_server()
        for scenario in self.scenarios:
            self._run_monitor(scenario)
            self._run_scenario(scenario)
            self.monitor_thread.join()
        self._stop_server()
        self._print_results()

    def _run_server(self):
        print('Run server')

        def worker():
            self.server.serve_forever()

        self.server = HttpServer.start(url=self.server_url, port=self.server_port,
                                       request_handler_class=RequestHandler)
        self.server_thread = Thread(target=worker)
        self.server_thread.start()

    def _run_monitor(self, scenario):
        print 'Run monitor'

        def worker():
            start_time = time.time()
            while time.time() <= start_time + scenario.timeout:
                time.sleep(1)
                with self.mutex:
                    if self._terminate:
                        break
                    print 'Results: {}, Clients: {}'.format(len(self.tests[scenario.name]), self.clients_count)
                    if len(self.tests[scenario.name]) == self.clients_count:
                        break

        self.monitor_thread = Thread(target=worker)
        self.monitor_thread.start()

    def _run_scenario(self, scenario):
        for client in self.clients:
            client.launch(self.configuration, scenario.name)

    def _stop_server(self):
        print 'Stop server'
        if self.server:
            self.server.shutdown()
            self.server_thread.join()
            self.server = None

    def _create_clients(self):
        for platform, json in self.configuration.json['clients'].items():
            clients = {
                'android': AndroidClient,
                'ios': IosClient,
                'osx': OsxClient,
            }
            if platform not in clients:
                continue
            client = clients[platform](self.configuration)
            self.clients.append(client)
            self.clients_count += len(client.devices)

    def _print_results(self):
        print('\n\nTests result:\n')
        success = True
        for scenario, data in self.tests.items():
            print('  Test: ', scenario)
            for result in self.tests[scenario]:
                print('    Platform: [TODO], Device: [TODO], Result: {}'.format(result))
                success = success and (result == 0)
        print('\nSumary: ' + ('Success' if success else 'Failed'))

    def add_result(self, code, scenario):
        self.tests[scenario].append(code)


class RequestHandler:
    TEST_LAB = None

    def __init__(self, server):
        self.response = None
        self.server = server

    def handle(self, client_address, payload):
        try:
            parsed = urlparse.urlparse(payload)
            params = urlparse.parse_qs(parsed.query)
            print 'Got Payload: ', payload
            if parsed.path == '/result' and 'code' in params or 'scenario' in params:
                with RequestHandler.TEST_LAB.mutex:
                    RequestHandler.TEST_LAB.add_result(int(params['code'][0]), params['scenario'][0])
        except RuntimeError:
            self.server.send('error')
        else:
            self.server.send('ok')
