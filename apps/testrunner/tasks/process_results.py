# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy
import requests
import ujson
from celery.utils.log import get_task_logger
from metrics import Collection

from testrunner import app as celery_app
from testrunner.metric_generators import PhantomasMetricGenerator, ProfilerMetricGenerator, RequestsMetricGenerator, \
    SeleniumMetricGenerator

logger = get_task_logger(__name__)


class ProcessResponses(celery_app.Task):
    @staticmethod
    def _calculate_stats(values):
        if len(values) == 0:
            return {
                'count': 0,
                '5th_percentile': 0.0,
                '50th_percentile': 0.0,
                '90th_percentile': 0.0,
                '95th_percentile': 0.0,
                'std': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'lowest': 0.0,
                'highest': 0.0,
            }

        return {
            'count': int(len(values)),
            '5th_percentile': float(numpy.percentile(values, 5)),
            '50th_percentile': float(numpy.percentile(values, 50)),
            '90th_percentile': float(numpy.percentile(values, 90)),
            '95th_percentile': float(numpy.percentile(values, 95)),
            'std': float(numpy.std(values)),
            'mean': float(numpy.mean(values)),
            'median': float(numpy.median(values)),
            'lowest': float(numpy.min(values)),
            'highest': float(numpy.max(values)),
        }

    @staticmethod
    def post_results(uri, test_run_uri, task_uri, results):
        logger.info('Saving results')
        payload = {
            'results': results,
            'task': task_uri,
            'test_run': test_run_uri,
        }

        response = requests.post(
            uri,
            data=ujson.dumps(payload),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json',
            }
        )
        logger.debug('Response (code: {0}): {1}'.format(response.status_code, response.content))
        response.raise_for_status()

    def run(self, data, test_run_uri, task_uri, result_uri):
        logger.info('Starting processing results...')

        generators = {
            'phantomas': [
                PhantomasMetricGenerator()
            ],
            'mw_profiler': [
                ProfilerMetricGenerator()
            ],
            'python.requests': [
                RequestsMetricGenerator()
            ],
            'selenium': [
                SeleniumMetricGenerator()
            ]
        }

        metrics = Collection()
        for item in data:
            for generator in generators[item['generator']]:
                generator(metrics, item)

        results = metrics.serialize()

        self.post_results(result_uri, test_run_uri, task_uri, results)

        return results
