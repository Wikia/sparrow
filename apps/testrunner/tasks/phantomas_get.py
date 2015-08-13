# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import phantomas
from celery.utils.log import get_task_logger
from django.conf import settings
from common.utils import collect_results

from base_task import BaseTask
from testrunner.api_client import ApiClient

logger = get_task_logger(__name__)


class PhantomasGet(BaseTask):
    CONSECUTIVE_FAILURES_LIMIT = 5

    def __init__(self, *args, **kwargs):
        self.__phantomas_path = settings.PHANTOMAS_PATH

    def run(self, result_uri, url, retries=1, query_params=None, **params):
        logger.info('Starting getting data ({0} runs) with Phantomas for url: {1}'.format(retries, url))

        self.position = params.get('task_position', self.MIDDLE)
        self.on_start(params['task_uri'])

        phantomas_runner = phantomas.Phantomas(
            url=url,
            runs=1,
            exec_path=self.__phantomas_path
        )

        def run_test():
            return phantomas_runner.run()

        all_runs = collect_results(run_test, retries)

        logger.info('Sending results from Phantomas for url: {0}'.format(url))

        # posting raw results
        ApiClient.post(params['raw_result_uri'], {
            'result': result_uri,
            'generator': 'phantomas',
            'context': {'url': url, 'origin': 'phantomas', },
            'data': [
                {
                    'generator': single_run.get_generator(),
                    'metrics': single_run.get_metrics(),
                    'offenders': {
                        metric: single_run.get_offenders(metric)
                        for metric in single_run.get_metrics()
                    }
                }
                for single_run in all_runs
            ],
        })

        return result_uri
