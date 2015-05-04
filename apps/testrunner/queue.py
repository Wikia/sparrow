import json
import time

import requests
import sys

from .logger import logger
from .runner import SimpleTest


class TaskRepo(object):
    # todo: add HTTP requests to fetch/save data
    URL = 'http://localhost:8000/task'

    def acquire(self):
        url = '{}/acquire'.format(self.URL)
        response = requests.get(url)
        if response.ok:
            task_data = response.json()
            return Task(self, task_data['id'], task_data)

    def release(self, task):
        url = '{}/{}/lock'.format(self.URL, task.id)
        response = requests.delete(url)
        response.raise_for_status()

    def submit_result(self, task, result):
        url = '{}/{}/result'.format(self.URL, task.id)
        response = requests.post(url, json=json.dumps(result))
        response.raise_for_status()


class Task(dict):
    def __init__(self, repo, id, *args, **kwargs):
        self.repo = repo
        self.id = id
        super(Task, self).__init__(*args, **kwargs)

    def release(self):
        self.repo.release(self)

    def save_result(self, result):
        self.repo.submit_result(self, result)


class TaskQueueWorker(object):
    def __init__(self, repo=None):
        self.repo = repo or TaskRepo()

    def run(self):
        logger.info('Started task processor, entering main loop...')
        while True:
            try:
                self.run_one()
            except KeyboardInterrupt:
                raise
            except:
                logger.warning('Task execution interrupted. Next check in 10 seconds.', exc_info=True)
                time.sleep(10)

    def run_one(self):
        task = None
        try:
            task = self.acquire_task()

            if task is not None:
                self.process_task(task)
            else:
                logger.debug('No queued task found. Next check in 10 seconds.')
                time.sleep(10)
        except:
            # In case of any error make sure to release current task but try not to
            # mess with the original exception so the caller can report it.
            # @see http://www.ianbicking.org/blog/2007/09/re-raising-exceptions.html
            exc_info = sys.exc_info()
            logger.info('Task execution interrupted, trying to release current task...')
            try:
                if task is not None:
                    self.release_task(task)
            except:
                logger.error('Releasing task #{} failed, it will remain stuck.'.format(task.id))
            raise exc_info[0], exc_info[1], exc_info[2]

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
