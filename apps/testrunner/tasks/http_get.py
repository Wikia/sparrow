# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger
import requests
import time
from common.utils import collect_results

from testrunner import app as celery_app
from testrunner.api_client import ApiClient


logger = get_task_logger(__name__)


class HttpGet(celery_app.Task):
    def get_current_time(self):
        return time.time()

    def __parse_content(self, response_content):
        return ''

    def run(self, result_uri, url, retries=1, query_params=None, **params):
        def run_test():
            logger.info('HTTP GET request: {} with params={}'.format(url, query_params))
            start_time = self.get_current_time()
            response = requests.get(url, params=query_params)
            elapsed_time = self.get_current_time() - start_time
            if not response.ok:
                logger.debug('HTTP status {}: {}'.format(response.status_code, response.content))
            response.raise_for_status()
            return {
                'content': self.__parse_content(response.text),
                'headers': dict(response.headers),
                'time': elapsed_time
            }

        results = collect_results(run_test, retries)

        logger.info('Sending results from HttpGet for url: {0}'.format(url))

        # posting raw results
        ApiClient.post(params['raw_result_uri'], {
            'result': result_uri,
            'generator': params.get('generator', 'python.requests'),
            'context': params.get('context', {'url': url, 'origin': 'python.requests', }),
            'data': results,
        })

        return result_uri


class MWProfilerGet(HttpGet):
    def run(self, result_uri, url, retries=1, query_params=None, **params):
        if query_params is None:
            query_params = {}

        query_params['forceprofile'] = 1
        params['context'] = {'url': url, 'origin': 'mw_profiler'}
        params['generator'] = 'mw_profiler'

        return HttpGet.run(self, result_uri, url, retries, query_params, **params)

    def __parse_content(self, response_content):
        try:
            start_pos = response_content.rindex('<!--')
            end_pos = response_content.rindex('-->')
        except ValueError:
            logger.warn('Cannot find backend performance metrics')
            return None

        return response_content[start_pos + 4:end_pos]
