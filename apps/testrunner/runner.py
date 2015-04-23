import json
import logging
import time

from django.conf import Settings
import requests

from .ssh import SSHConnection


logger = logging.getLogger(__name__)


class TaskRepo(object):
    # todo: add HTTP requests to fetch/save data
    URL = 'http://localhost:8000/task'

    def acquire(self):
        url = '{}/acquire'.format(self.URL)
        response = requests.get(url)
        if response.ok:
            task_data = response.json()
            return Task(self,task_data['id'],task_data)

    def release(self, task):
        url = '{}/{}/lock'.format(self.URL,task.id)
        response = requests.delete(url)
        response.raise_for_status()

    def submit_result(self, task, result):
        url = '{}/{}/result'.format(self.URL,task.id)
        response = requests.post(url,json=json.dumps(result))
        response.raise_for_status()


class Task(dict):
    def __init__(self, repo, id, *args, **kwargs):
        self.repo = repo
        self.id = id
        super(Task,self).__init__(*args,**kwargs)


class TestRunner(object):

    def __init__(self, repo=None):
        self.repo = repo or TaskRepo()

    def run_loop(self):
        while True:
            # fetch and lock the test for execution
            test = self.get_test()
            if not test:
                time.sleep(10)
                continue

            logger.debug('Acquired test #{} for execution'.format(test.id))
            result = None

            # if we got a test
            if test:
                result = self.run_test(test)

            # if test execution succeeded and we got result
            if test and result:
                self.repo.submit_result(test, result)
                logger.debug('Finished test execution successfully and stored results')
                test = None

            # if test was fetched but we didn't manage to execute it, release it
            if test:
                self.repo.release(test)

    def get_test(self):
        try:
            return self.repo.acquire()
        except:
            logger.error('Error while fetching the test to run', exc_info=True)

    def run_test(self, test):
        result = None
        try:
            env = self.set_up_env(test['app_commit'], test['config_commit'])
            response = self.do_request(env, test['url'])
            result = self.create_result(response)
        except:
            logger.error('Error while executing test', exc_info=True)

        return result

    def set_up_env(self, app_commit, config_commit):
        target_env = Settings.SPARROW_TEST_RUNNER['target_hosts'][0]
        target_env_hostname = target_env['hostname']

        # todo: implement
        ssh_connection = SSHConnection(**Settings.SPARROW_TEST_RUNNER['manager_host'])

        # run prep
        prep_cmd = 'dt {operation} -y -a {application} -e {environment} -r app@{app_commit} -r config@{config_commit}'.format(
            operation='prep', application='wikia', environment=target_env_hostname,
            app_commit=app_commit, config_commit=config_commit)
        ssh_connection.execute(prep_cmd)

        # run push
        push_cmd = 'dt {operation} -y -a {application} -e {environment}'.format(
            operation='push', application='wikia', environment=target_env_hostname,
            app_commit=app_commit, config_commit=config_commit)
        ssh_connection.execute(push_cmd)

        env = {
            'hostname': target_env_hostname
        }
        return env

    def do_request(self, env, url):

        response = requests.get(url)
        return response

    def create_result(self, response):
        response_time = response.headers['X-Backend-Response-Time']
        result = {
            'response_time': response_time
        }
        return result