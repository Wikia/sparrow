# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger

from testrunner.api_client import ApiClient
from testrunner import app as celery_app


logger = get_task_logger(__name__)


class PrepareResults(celery_app.Task):
    def run(self, results_uri, test_run_uri, task_uri):
        result = ApiClient.post(results_uri, {
            'test_run': test_run_uri,
            'task': task_uri,
        })

        return result['url']
