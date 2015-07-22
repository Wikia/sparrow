# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger
import requests
import time
from common.utils import collect_results

from testrunner import app as celery_app


logger = get_task_logger(__name__)


class HttpGet(celery_app.Task):
    def get_current_time(self):
        return time.time()

    def run(self, url, retries=1, query_params=None):
        def run_test():
            logger.info('HTTP GET request: {} with params={}'.format(url, query_params))
            start_time = self.get_current_time()
            response = requests.get(url, params=query_params)
            elapsed_time = self.get_current_time() - start_time
            if not response.ok:
                logger.debug('HTTP status {}: {}'.format(response.status_code, response.content))
            response.raise_for_status()
            return {
                'content': response.text,
                'headers': dict(response.headers),
                'time': elapsed_time
            }

        results = collect_results(run_test,retries)

        return {
            'generator': 'python.requests',
            'context': {
                'url': url,
                'origin': 'python.requests'
            },
            'data': results
        }


class MWProfilerGet(HttpGet):
    def run(self, url, retries=1, query_params=None):
        if query_params is None:
            query_params = {}

        query_params['forceprofile'] = 1

        get_result = HttpGet.run(self, url, retries, query_params)

        return {
            'generator': 'mw_profiler',
            'context': get_result['context'],
            'data': [
                dict(single_result, **{'profiler_data': self.extract_profiler_data(single_result['content'])})
                for single_result in get_result['data']
            ]
        }

    def extract_profiler_data(self, response_content):
        try:
            start_pos = response_content.rindex('<!--')
            end_pos = response_content.rindex('-->')
        except ValueError:
            logger.warn('Cannot find backend performance metrics')
            return None

        return response_content[start_pos + 4:end_pos]
