# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import requests

from . import Action

logger = logging.getLogger(__name__)


class HttpGet(Action):
    REQUIRED_PARAMS = (
        'url',
        'retries',
    )

    def __init__(self, *args, **kwargs):
        super(HttpGet, self).__init__(*args, **kwargs)

    def run(self):
        query_params = {}

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

            self.result[self._RESULT_NAME].append(response)

        if len(self.result[self._RESULT_NAME]):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED


class MWProfilerGet(HttpGet):
    def __init__(self, *args, **kwargs):
        super(MWProfilerGet, self).__init__(*args, **kwargs)

        self.params['params'] = {'forceprofile': 1}
