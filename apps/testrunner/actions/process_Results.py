# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import statistics
import logging

from . import Action

logger = logging.getLogger(__name__)


class ProcessResponses(Action):
    REQUIRED_PARAMS = (
        'responses',
    )

    def run(self):
        logger.info('Starting processing {0} results'.format(len(self.params['responses'])))

        metrics = [float(response.headers['X-Backend-Response-Time']) for response in self.params['responses']]
        self.result['response_time'] = {
            'mean': statistics.mean(metrics),
            'median': statistics.median(metrics),
            'lowest': min(metrics),
            'highest': max(metrics),
        }

        self.status = self.COMPLETED
