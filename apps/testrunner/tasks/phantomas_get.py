# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import phantomas
from celery.utils.log import get_task_logger
from django.conf import settings
from common.utils import collect_results

from testrunner import app as celery_app

logger = get_task_logger(__name__)


class PhantomasGet(celery_app.Task):
    CONSECUTIVE_FAILURES_LIMIT = 5

    def __init__(self, *args, **kwargs):
        self.__phantomas_path = settings.SPARROW_TEST_RUNNER['phantomas_path']

    def run(self, url, retries=1, query_params=None):
        logger.info('Starting getting data ({0} runs) with Phantomas for url: {1}'.format(retries, url))

        phantomas_runner = phantomas.Phantomas(
            url=url,
            runs=1,
            exec_path=self.__phantomas_path
        )

        def run_test():
            return phantomas_runner.run()

        all_runs = collect_results(run_test,retries)

        return {
            'generator': 'phantomas',
            'context': {
                'url': url,
                'origin': 'phantomas'
            },
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
            ]
        }
