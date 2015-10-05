# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger
import requests
from common.utils import collect_results

from .base_task import BaseTask
from testrunner.api_client import ApiClient


logger = get_task_logger(__name__)


class HttpGet(BaseTask):
    def _parse_content(self, response_content):
        pass

    def _elapsed_time(self, response):
        return response.elapsed.microseconds

    def run(self, result_uri, url, retries=1, query_params=None, **params):
        self.position = params.get('task_position', self.MIDDLE)
        self.on_start(params['task_uri'])

        def run_test():
            logger.info('HTTP GET request: {} with params={}'.format(url, query_params))
            response = requests.get(url, params=query_params)
            if not response.ok:
                logger.debug('HTTP status {}: {}'.format(response.status_code, response.content))
            response.raise_for_status()
            return {
                'content': self._parse_content(response.text),
                'content_length': len(response.text),
                'headers': dict(response.headers),
                'time': self._elapsed_time(response),
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

    def _parse_content(self, response_content):
        try:
            start_pos = response_content.rindex('<!--')
            end_pos = response_content.rindex('-->')
        except ValueError:
            logger.warn('Cannot find backend performance metrics')
            return None

        return response_content[start_pos + 4:end_pos]
