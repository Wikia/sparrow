import ujson
import time

import requests
import sys

from .logger import logger
from .runner import SimpleTest


class TaskRepo(object):
    """
    Encapsulates HTTP tasks API
    """
    # todo: get rid of hardcoded URL here
    URL = 'http://localhost:8000/task'

    def acquire(self):
        url = '{}/acquire'.format(self.URL)
        response = requests.get(url)
        if response.ok:
            task_data = response.json()
            return Task(self, task_data)

    def release(self, task):
        url = '{}/{}/lock'.format(self.URL, task.id)
        response = requests.delete(url)
        response.raise_for_status()

    def submit_result(self, task, result):
        url = '{}/{}/result'.format(self.URL, task.id)
        response = requests.post(url, json=ujson.dumps(result))
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
            task = self.acquire_task()

            if task is not None:
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
            self.release_task(task)
        except:
            logger.error('Releasing task #{} failed, it will remain stuck.'.format(task.id))

        # raise saved exception if any
        if exc_info:
            raise exc_info[0], exc_info[1], exc_info[2]

        return True

    def process_task(self, task):
        logger.info('Processing task #{}...'.format(task.id))
        simple_test = SimpleTest(**task)
        simple_test.run()
        if simple_test.ok:
            self.save_result(task, simple_test.result)
        else:
            logger.warning('Test execution did not complete successfully')

    def acquire_task(self):
        logger.debug('Fetching task from queue...')
        return self.repo.acquire()

    def save_result(self, task, result):
        logger.debug('Saving result for task #{}...'.format(task.id))
        task.save_result(result)
        logger.info('Saved result for task #{}'.format(task.id))

    def release_task(self, task):
        logger.debug('Releasing task #{}...'.format(task.id))
        task.release()
        logger.info('Released task #{}'.format(task.id))
