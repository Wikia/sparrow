import time

from .ssh import SSHConnection

class TestRunnerRepo(object):
    # todo: add HTTP requests to fetch/save data
    URL = 'http://localhost:5000/task'
    def get_and_book_test(self):
        # todo: implement
        pass

    def release_test(self, test):
        # todo: implement
        pass

    def save_test_result(self, test, result):
        # todo: implement
        pass


class TestRunner(object):
    MANAGE_HOST = ''
    TARGET_HOST = ''

    def __init__(self, repo=None):
        self.repo = repo or TestRunnerRepo()

    def run_loop(self):
        while True:
            test = None
            try:
                test = self.repo.get_and_book_test()
                if test is not None:
                    result = self.run_test(test)
                    self.repo.save_test_result(test,result)
                else:
                    time.sleep(10)
            except:
                if test is not None:
                    try:
                        self.repo.release_test(test)
                    except:
                        pass

    def run_test(self, test):
        self.set_up_env(test['app_commit'],test['config_commit'])
        response = self.do_request(test['url'])
        return self.create_result(response)

    def set_up_env(self, app_commit, config_commit):
        # todo: implement
        ssh_connection = SSHConnection(self.MANAGE_HOST)
        # run prep
        ssh_connection.execute('')
        # run push
        ssh_connection.execute('')

    def do_request(self, url):
        # todo: implement
        pass

    def create_result(self, response):
        # todo: implement
        pass