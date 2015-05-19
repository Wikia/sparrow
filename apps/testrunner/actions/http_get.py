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

    def run(self):
        self.result['responses'] = []

        for retry in range(1, self.params['retries']+1):
            logger.info('HTTP request #{0} (GET): {1}'.format(retry, self.params['url']))
            response = requests.get(self.params['url'])
            if response.ok:
                logger.debug(
                    'HTTP #{0} response {1}: <full dump skipped> ({2} bytes)'.format(
                        retry, response.status_code, len(response.content)
                    )
                )
            else:
                logger.debug('HTTP #{0} response {1}: {2}'.format(retry, response.status_code, response.content))
                continue

            self.result['responses'].append(response)

        if len(self.result['responses']):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED
