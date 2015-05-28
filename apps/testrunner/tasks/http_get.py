# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
import requests

from testrunner import app as celery_app
from common.utils import camel2snake


logger = get_task_logger(__name__)


class HttpGet(celery_app.Task):
    def run(self, url, retries=1, query_params=None):
        result = []

        for turn in range(retries):
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
                'content': str(response.content),
                'headers': dict(response.headers),
            })

        key = camel2snake(self.__class__.__name__)
        return {key: result, }

class MWProfilerGet(HttpGet):
    def run(self, url, retries=1, query_params=None):
        if query_params is None:
            query_params = {}

        query_params['forceprofile'] = 1

        return super(MWProfilerGet, self).run(url, retries, query_params)
