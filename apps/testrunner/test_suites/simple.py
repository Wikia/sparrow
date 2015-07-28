# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson
from celery import group
import celery.states
from celery.utils.log import get_task_logger
from tasks.signals import celery_request_status_update

from testrunner.tasks.deploy import Deploy
from testrunner.tasks.http_get import HttpGet
from testrunner.tasks.http_get import MWProfilerGet
from testrunner.tasks.phantomas_get import PhantomasGet
from testrunner.tasks.process_results import ProcessResponses
from testrunner.tasks.selenium_get import SeleniumGet
from testrunner import app as celery_app

logger = get_task_logger(__name__)


class SimpleTestSuite(object):
    DEFAULT_RETRIES_COUNT = 10

    def __init__(self, *args, **kwargs):
        self.DEPLOY_HOST = settings.DEPLOYTOOLS_MASTER
        self.TARGET_ENV = settings.TEST_TARGET_HOSTS[0]

    def run(self, **kwargs):
        if kwargs.get('retries') is None:
            kwargs['retries'] = self.DEFAULT_RETRIES_COUNT

        logger.info('Started execution of task #{} (x{})'.format(kwargs['task_uri'], kwargs['retries']))
        logger.debug('params = ' + ujson.dumps(kwargs))

        mode = 'SINGLE'
        if mode == 'MULTIPLE':
            task = self.get_multiple_tasks(**kwargs)
        elif mode == 'SINGLE':
            task = self.get_single_task(**kwargs)

        logger.info('Scheduled execution of task #{0}: {1}'.format(kwargs['task_uri'], task.id))

        result = task.delay()

        return result

    def get_multiple_tasks(self, **kwargs):
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
            group(
                HttpGet().si(url=kwargs['url'], retries=retries),
                MWProfilerGet().si(url=kwargs['url'], retries=retries),
                SeleniumGet().si(url=kwargs['url'], retries=retries),
                PhantomasGet().si(url=kwargs['url'], retries=retries)
            ) |
            ProcessResponses().s(
                result_uri=kwargs['result_uri'],
                task_uri=kwargs['task_uri'],
                test_run_uri=kwargs['test_run_uri']
            )
        )

        return tasks

    def get_single_task(self, **kwargs):
        task = SimpleTestSuiteTask().s(**kwargs)

        return task


class SimpleTestSuiteTask(celery_app.Task):
    def run(self, task_id=None, *args, **kwargs):
        DEPLOY_HOST = settings.DEPLOYTOOLS_MASTER
        TARGET_ENV = settings.TEST_TARGET_HOSTS[0]

        celery_request_status_update.send(self.__class__, task_id=task_id, job_id=self.request.id,
                                                status=celery.states.STARTED)

        deploy_result = Deploy().run(
            deploy_host=DEPLOY_HOST,
            app='wikia',
            env=TARGET_ENV,
            repos={
                'app': kwargs['app_commit'],
                'config': kwargs['config_commit']
            }
        )

        url = kwargs['url']
        retries = kwargs['retries']
        http_get_result = HttpGet().run(url=url, retries=retries)
        mw_profiler_result = MWProfilerGet().run(url=url, retries=retries)
        selenium_result = SeleniumGet().run(url=url, retries=retries)
        phantomas_result = PhantomasGet().run(url=url, retries=retries)

        ProcessResponses().run(
            data=[
                http_get_result,
                mw_profiler_result,
                selenium_result,
                phantomas_result
            ],
            result_uri=kwargs['result_uri'],
            task_uri=kwargs['task_uri'],
            test_run_uri=kwargs['test_run_uri']
        )

    def on_success(self, retval, task_id, args, kwargs):
        result = self.AsyncResult(task_id)
        result.forget()
        celery_request_status_update.send(self.__class__, task_id=kwargs['task_id'], job_id=task_id,
                                                status=celery.states.SUCCESS)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        celery_request_status_update.send(self.__class__, task_id=kwargs['task_id'], job_id=task_id,
                                                status=celery.states.FAILURE)
