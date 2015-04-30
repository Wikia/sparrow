import functools
import json
import time

import requests

from .logger import logger
from .runner import SimpleTest




def exception_guard(message, value_on_error):
    @functools.wraps(exception_guard)
    def decorator(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                logger.warning(message, exc_info=True)
            return value_on_error

        return wrapper

    return decorator


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

    def save_reslut(self, result):
        self.repo.submit_result(self, result)


class TaskQueueConsumer(object):
    def __init__(self, repo=None):
        self.repo = repo or TaskRepo()

    def run(self):
        logger.info('Starting TaskQueueConsumer')
        while True:
            task = self.acquire_task()
            if task is not None:
                time.sleep(10)
                continue

            logger.info('Acquired task #{} for execution'.format(task.id))

            task_result = self.run_task(task)

            if task_result:
                self.save_result(task, task_result)
                logger.info('Completed task execution successfully.')
            else:
                logger.warning('Failed executing task #{}. Releasing the task.'.format(task.id))
                self.release_task(task)

    @exception_guard('Error while acquiring task', value_on_error=None)
    def acquire_task(self):
        return self.repo.acquire()

    @exception_guard('Error while saving result', value_on_error=None)
    def save_result(self, task, result):
        task.save_result(result)

    @exception_guard('Error while releasing task', value_on_error=None)
    def release_task(self, task):
        task.release()

    @exception_guard('Error while running task', value_on_error=None)
    def run_task(self, task):
        simple_test = SimpleTest(**task)
        simple_test.run()
        if simple_test.ok:
            return simple_test.result
        else:
            return None
