# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re

from celery.utils.log import get_task_logger

from testrunner.api_client import ApiClient
from base_task import BaseTask


logger = get_task_logger(__name__)


class PrepareResults(BaseTask):
    def run(self, results_uri, test_run_uri, task_uri, **params):
        self.position = params.get('task_position', self.MIDDLE)
        self.on_start(task_uri)

        result = ApiClient.post(results_uri, {
            'test_run': test_run_uri,
            'task': task_uri,
        })

        return result['url']
