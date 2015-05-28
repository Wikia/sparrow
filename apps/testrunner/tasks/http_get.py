# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests
from celery.task import Task


logger = logging.getLogger(__name__)


class HttpGet(Task):
    def run(self):
        query_params = {}
        result = []

        if 'params' in self.params:
            query_params = self.params['params']

        for retry in range(1, self.params['retries']+1):
            logger.info('HTTP request #{0} (GET): {1} with params={2}'.format(retry, self.params['url'], query_params))
            response = requests.get(self.params['url'], params=query_params)
            if response.ok:
                logger.debug(
                    'HTTP #{0} response {1}: <full dump skipped> ({2} bytes)'.format(
                        retry, response.status_code, len(response.content)
                    )
                )
            else:
                logger.debug('HTTP #{0} response {1}: {2}'.format(retry, response.status_code, response.content))
                continue

            result.append(response)

        return result


class MWProfilerGet(HttpGet):
    def run(self):
        self.params['forceprofile'] = 1

        return super(MWProfilerGet, self).run()
