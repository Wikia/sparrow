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
            num_runs = self.params['retries']
            phantomas_runner = phantomas.Phantomas(
                url=self.params['url'],
                runs=num_runs
            )
            phantomas_result = phantomas_runner.run()
            if num_runs == 1:
                all_runs = [phantomas_result]
            else:
                all_runs = phantomas_result.runs

            self.result[self._RESULT_NAME].extend([
                {
                    'generator': single_run.get_generator(),
                    'metrics': single_run.get_metrics(),
                    'offenders': {
                        metric: single_run.get_offenders(metric)
                        for metric in single_run.get_metrics()
                    }
                }
                for single_run in all_runs
            ])
        except:
            logger.error('phantomas execution failed', exc_info=True)

        if len(self.result[self._RESULT_NAME]):
            self.status = self.COMPLETED
        else:
            self.status = self.FAILED

