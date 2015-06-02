import ujson

import requests
import six
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import logging

logger = get_task_logger(__name__)

# How many time repeat one test
_TEST_RUN_RETRIES = 10


class AutoDiscoverFailed(ImproperlyConfigured):
    pass


class TaskRepo(object):
    """
    Encapsulates HTTP tasks API
    """

    API_SERVER = None
    TASKS_API_URL = None
    RESULTS_API_URL = None
    RAW_RESULTS_API_URL = None

    def __init__(self):
        # Auto Discover API URIs
        self.API_SERVER = settings.SPARROW_TEST_RUNNER['api_server']
        api_descr = {}

        try:
            req = requests.get(self.API_SERVER)
            req.raise_for_status()

            api_descr = req.json()

            self.TASKS_API_URL = api_descr['tasks']
            self.RESULTS_API_URL = api_descr['results']
            self.RAW_RESULTS_API_URL = api_descr['raw_results']
        except Exception as ex:
            six.raise_from(AutoDiscoverFailed('Cannot find API URIs: {0}'.format(api_descr)), ex)

    def acquire(self):
        url = '{}fetch/'.format(self.TASKS_API_URL)
        logger.debug('HTTP request (GET): {}'.format(url))
        response = requests.get(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code, response.content))
        if response.ok:
            response_data = response.json()
            task_data = {
                'id': response_data['id'],
                'task_url': response_data['url'],
                'details_url': response_data['test_run']
            }
            return Task(self, task_data)

    def _fetch_details(self, task):
        url = task['details_url']
        logger.debug('HTTP request (GET): {}'.format(url))
        response = requests.get(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code, response.content))
        response.raise_for_status()
        response_data = response.json()
        details_data = {
            'app_commit': response_data['main_revision'],
            'config_commit': response_data['secondary_revision'],
            'url': response_data['test_run_uri']
        }
        task.update(details_data)

    def release(self, task):
        url = task['task_url'] + 'lock/'
        logger.debug('HTTP request (DELETE): {}'.format(url))
        response = requests.delete(url)
        logger.debug('HTTP response {}: {}'.format(response.status_code, response.content))
        response.raise_for_status()

    def submit_result(self, task, result, raw_result):
        payload = {
            'results': ujson.dumps(result),
            'task': task['task_url'],
            'test_run': task['details_url'],
        }
        logger.debug('HTTP result request (POST): {} with params: {}'.format(self.RESULTS_API_URL, payload))
        response = requests.post(self.RESULTS_API_URL, data=payload)
        logger.debug('HTTP result response {}: {}'.format(response.status_code, response.content))
        response.raise_for_status()
        result_url = response.json()
        result_url = result_url['url']

        for key, value in six.iteritems(raw_result):
            payload = {
                'type': key,
                'data': ujson.dumps(value),
                'result': result_url,
            }
            logger.debug('HTTP raw result {} request (POST): {}'.format(key, self.RAW_RESULTS_API_URL))
            response = requests.post(self.RAW_RESULTS_API_URL, data=payload)
            logger.debug('HTTP raw result response {}: <full dump skipped>'.format(response.status_code))
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

    def load_data(self):
        self.repo._fetch_details(self)

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

    def save_result(self, result, raw_result):
        self.repo.submit_result(self, result, raw_result)
