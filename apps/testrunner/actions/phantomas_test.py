# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import phantomas

from . import Action
from phantomas.results import Runs


logger = logging.getLogger(__name__)


class PhantomasTest(Action):
    REQUIRED_PARAMS = (
        'url',
    )

    def __init__(self, *args, **kwargs):
        super(PhantomasTest, self).__init__(*args, **kwargs)

    def run(self):
        try:
            phantomas_runner = phantomas.Phantomas(
                url=self.params['url'],
                runs=self.params['retries']
            )
            phantomas_result = phantomas_runner.run()
            if hasattr(phantomas_result,'_runs'):
                all_runs = phantomas_result._runs
            else:
                all_runs = [phantomas_result]
            self.result[self._RESULT_NAME].extend([
                {
                    'generator': single_run._generator,
                    'metrics': single_run._metrics,
                    'offenders': single_run._offenders
                }
                for single_run in all_runs
            ])
        except:
            logger.error('phantomas execution failed', exc_info=True)

        if len(self.result[self._RESULT_NAME]):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED

