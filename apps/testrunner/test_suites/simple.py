# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson
from celery import group
from celery.utils.log import get_task_logger

from testrunner.tasks.deploy import Deploy
from testrunner.tasks.prepare_results import PrepareResults
from testrunner.tasks.http_get import HttpGet
from testrunner.tasks.http_get import MWProfilerGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses
from testrunner.tasks.selenium_get import SeleniumGet
from testrunner.tasks.base_task import BaseTask

logger = get_task_logger(__name__)


class SimpleTestSuite(object):
    DEFAULT_RETRIES_COUNT = 10

    def __init__(self, *args, **kwargs):
        self.DEPLOY_HOST = settings.DEPLOYTOOLS_MASTER
        self.TARGET_ENV = settings.TEST_TARGET_HOSTS[0]

    def run(self, **kwargs):
        if kwargs.get('retries') is None:
            kwargs['retries'] = self.DEFAULT_RETRIES_COUNT

        task_params = {
            'url': kwargs['url'],
            'retries': kwargs['retries'],
            'task_uri': kwargs['task_uri'],
            'test_run_uri': kwargs['test_run_uri'],
            'results_uri': kwargs['results_uri'],
            'raw_result_uri': kwargs['raw_result_uri'],
        }

        logger.info('Started execution of task #{} (x{})'.format(kwargs['task_uri'], kwargs['retries']))
        logger.debug('params = ' + ujson.dumps(kwargs))

        tasks = (
            Deploy().s(
                task_position=BaseTask.FIRST,
                task_uri=kwargs['task_uri'],
                deploy_host=self.DEPLOY_HOST,
                app='wikia',
                env=self.TARGET_ENV,
                repos={
                    'app': kwargs['app_commit'],
                    'config': kwargs['config_commit']
                }
            ) |
            PrepareResults().si(
                results_uri=kwargs['results_uri'],
                test_run_uri=kwargs['test_run_uri'],
                task_uri=kwargs['task_uri'],
            ) |
            HttpGet().s(**task_params) |
            MWProfilerGet().s(**task_params) |
            SeleniumGet().s(**task_params) |
            PhantomasGet().s(**task_params) |
            ProcessResponses().s(task_position=BaseTask.LAST, **task_params)
        )

        logger.info('Scheduled execution of task #{0}: {1}'.format(kwargs['task_uri'], tasks.id))

        result = tasks.delay()

        return result
