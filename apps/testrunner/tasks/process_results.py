# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy
import requests
from celery.utils.log import get_task_logger

from metrics import Collection
from testrunner import app as celery_app
from testrunner.metric_generators import PhantomasMetricGenerator, ProfilerMetricGenerator, RequestsMetricGenerator, \
    SeleniumMetricGenerator
from testrunner.api_client import ApiClient

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

    def run(self, result_uri, raw_result_uri, test_run_uri, task_uri, results_uri, **params):
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
        result = ApiClient.get(result_uri)

        for raw_result_uri in result['raw_results']:
            raw_result = ApiClient.get(raw_result_uri)

            for item in raw_result['data']:
                for generator in generators[raw_result['generator']]:
                    generator(metrics, raw_result)

        ApiClient.put(result_uri, {
            'test_run': test_run_uri,
            'task': task_uri,
            'results': metrics.serialize(),
        })
