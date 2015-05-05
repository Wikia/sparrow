import time
import ujson

import requests
import sys

from .logger import logger
from .test_suites import SimpleTestSuite


class TaskRepo(object):
    """
    Encapsulates HTTP tasks API
    """
    # todo: get rid of hardcoded URL here
    URL = 'http://localhost:8000/api/v1/tasks'

    def acquire(self):
        url = '{}/fetch'.format(self.URL)
        logger.debug('HTTP request (GET): {}'.format(url))
        response = requests.get(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code,response.content))
        if response.ok:
            response_data = response.json()
            task_data = {
                'id': response_data['url'],
                'task_url': response_data['url'],
                'details_url': response_data['test_run']
            }
            return Task(self, task_data)

    def get_details(self, url):
        logger.debug('HTTP request (GET): {}'.format(url))
        response = requests.get(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code,response.content))
        response.raise_for_status()
        if response.ok:
            response_data = response.json()
            details_data = {
                'app_commit': response_data['main_revision'],
                'config_commit': response_data['secondary_revision'],
                'url': response_data['test_run_uri']
            }
            return details_data


    def release(self, task):
        url = task['task_url'] + 'lock'
        logger.debug('HTTP request (DELETE): {}'.format(url))
        response = requests.delete(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code,response.content))
        response.raise_for_status()

    def submit_result(self, task, result):
        url = task['task_url'] + 'result'
        logger.debug('HTTP request (POST): {}'.format(url))
        response = requests.post(url, json=ujson.dumps(result))
        logger.debug('HTTP response {}: {}'.format(response.status_code,response.content))
        response.raise_for_status()


class Task(dict):
    """
    Represents a single task fetched from the repository
    """
    def __init__(self, repo, *args, **kwargs):
        self._repo = repo
        super(Task, self).__init__(*args, **kwargs)
        if 'id' not in self:
            raise KeyError('Task data does not specify ID')

    def load_details(self):
        details_data = self.repo.get_details(self['details_url'])
        self.update(details_data)

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        if self._repo is not None:
            raise ValueError('Task #{} already has a repo parent.')
        self._repo = value

    @property
    def id(self):
        return self['id']

    def release(self):
        self.repo.release(self)

    def save_result(self, result):
        self.repo.submit_result(self, result)


class TaskQueueWorker(object):
    """
    Daemon worker which fetches tasks from the queue, executes them and sends back result data
    """

    def __init__(self, repo=None):
        self.repo = repo or TaskRepo()

    def run(self):
        logger.info('Started task processor, entering main loop...')
        while True:
            work_done = True
            try:
                work_done = self.run_one()
            except KeyboardInterrupt:
                raise
            except:
                logger.warning('Task execution interrupted. Next check in 10 seconds.', exc_info=True)

            if not work_done: # = was totally idle
                time.sleep(10)

    def run_one(self):
        task = None
        exc_info = None
        try:
            logger.debug('Fetching task from queue...')
            task = self.repo.acquire()

            if task is not None:
                task.load_details()
                self.process_task(task)
            else:
                logger.debug('No queued task found. Next check in 10 seconds.')
                return False
        except:
            # In case of any error make sure to release current task but try not to
            # mess with the original exception so the caller can report it.
            # @see http://www.ianbicking.org/blog/2007/09/re-raising-exceptions.html
            exc_info = sys.exc_info()

        try:
            if task is not None:
                logger.debug('Releasing task #{}...'.format(task.id))
                task.release()
                logger.info('Released task #{}'.format(task.id))
        except:
            logger.error('Releasing task #{} failed, it will remain stuck.'.format(task.id))

        # raise saved exception if any
        if exc_info:
            raise exc_info[0], exc_info[1], exc_info[2]

        return True

    def process_task(self, task):
        logger.info('Processing task #{}...'.format(task.id))
        simple_test = SimpleTestSuite(**task)
        simple_test.run()
        if simple_test.ok:
            logger.debug('Saving result for task #{}...'.format(task.id))
            task.save_result(simple_test.result)
            logger.info('Saved result for task #{}'.format(task.id))
        else:
            logger.warning('Test execution did not complete successfully')
