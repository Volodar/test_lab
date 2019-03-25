from test_lab import TestLab, TestLabClientType
import urlparse


def convert_url_parameters_to_dict(query):
    result = dict()
    pairs = query.split('&')
    for pair in pairs:
        name, value = pair.split('=')
        result[name] = value
    return result


def handler_request(storage, client_address, payload):
    url = payload
    parsed = urlparse.urlparse(url)
    params = convert_url_parameters_to_dict(parsed.query)

    storage.add_result(client_address, params.get('message', ''), params.get('code', '0'))


def condition_finish(storage):
    return len(storage.results) >= 1


def run_test(test):
    lab = TestLab('192.168.0.105', 8045, handler_request, condition_finish)

    lab.add_client(TestLabClientType.Python, path='client.py')
    # lab.add_client(TestLabClientType.Android,
    #                package='com.forfunstudio.dungeonheroes.dev',
    #                activity='org.cocos2dx.cpp.AppActivity',
    #                app_args=['-e', '-scenario', test])
    # lab.add_client(TestLabClientType.OSX,
    #                path='/work/dungeon/client/build/bin/dungeon',
    #                app_args=['-scenario', test,
    #                          '-project_root', '/work/dungeon',
    #                          ])

    lab.run()
    print '\n\nResults:'
    print lab.storage.results
    print '\n\n'


if __name__ == '__main__':
    run_test('window_choose_hero_in_battle')
    # run_test('window_hero')
    # run_test('all_levels')
