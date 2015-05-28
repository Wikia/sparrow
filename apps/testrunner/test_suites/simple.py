# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson
from celery import group
from celery import chord
from celery.utils.log import get_task_logger

from testrunner.tasks.deploy import Deploy
from testrunner.tasks.http_get import HttpGet
from testrunner.tasks.http_get import MWProfilerGet
from testrunner.tasks.process_results import ProcessResponses

logger = get_task_logger(__name__)


class SimpleTestSuite(object):
    def __init__(self, *args, **kwargs):
        test_runner_config = settings.SPARROW_TEST_RUNNER
        self.DEPLOY_HOST = test_runner_config['deploy_host']['hostname']
        self.TARGET_ENV = test_runner_config['target_hosts'][0]['hostname']

    def run(self, task_id, retries, **kwargs):
        from pudb import set_trace; set_trace()
        logger.info('Started execution of task #{} (x{})'.format(task_id, retries))
        logger.debug('params = ' + ujson.dumps(kwargs))

        tasks = (
            Deploy().s(
                deploy_host=self.DEPLOY_HOST,
                app='wikia',
                env=self.TARGET_ENV,
                repos={
                    'app': kwargs['app_commit'],
                    'config': kwargs['config_commit']
                }
            ) |
                # group(
                #      HttpGet().si(url=kwargs['url']) for _ in range(retries)
                # ),
                # |
                # group(
                #     MWProfilerGet().si(url=kwargs['url']) for _ in range()
                # ) |
            HttpGet().si(url=kwargs['url'], retries=retries) |
            MWProfilerGet().si(url=kwargs['url'], retries=retries) |
            ProcessResponses().s()
        )

        result = tasks.delay()

        logger.info('Finished execution of task #{}'.format(task_id))

        return result.get()
