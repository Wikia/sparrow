# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger
import requests

from testrunner import app as celery_app


logger = get_task_logger(__name__)


class HttpGet(celery_app.Task):
    def run(self, url, retries=1, query_params=None):
        result = []

        for turn in range(1, retries + 1):
            logger.info('HTTP request #{0} (GET): {1} with params={2}'.format(turn, url, query_params))
            response = requests.get(url, params=query_params)
            if response.ok:
                logger.debug(
                    'HTTP response #{0} {1}: <full dump skipped> ({2} bytes)'.format(
                        turn, response.status_code, len(response.content)
                    )
                )
            else:
                logger.debug('HTTP response #{0} {1}: {2}'.format(turn, response.status_code, response.content))

            result.append({
                'content': response.text,
                'headers': dict(response.headers),
            })

        return {
            'generator': 'python.requests',
            'context': {
                'url': url,
                'origin': 'python.requests'
            },
            'data': result
        }


class MWProfilerGet(HttpGet):
    __PROFILER_REGEXP = re.compile(r'^\s*([\d\.]+\%)\s+([\d\.]+)\s+(\d+)\s+\-\s+([^\s].*[^\s])\s*$')
    __MEMCACHE_REGEXP = re.compile(r'MWMemcached::get.*!(HIT|MISS|DUPE)')
    __QUERY_REGEXP = re.compile(r'^\s*query(?:-m)?:\s*(.*)\s*$')

    def run(self, url, retries=1, query_params=None):
        if query_params is None:
            query_params = {}

        query_params['forceprofile'] = 1

        get_result = HttpGet.run(self, url, retries, query_params)

        return {
            'generator': 'mw_profiler',
            'context': get_result['context'],
            'data': [
                dict(single_result.items() + [('profiler_data', self.extract_profiler_data(single_result['content']))])
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
