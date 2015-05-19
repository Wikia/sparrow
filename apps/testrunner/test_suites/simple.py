# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson

import logging
from testrunner.actions import Action
from testrunner.actions.deploy import Deploy
from testrunner.actions.http_get import HttpGet
from testrunner.actions.process_results import ProcessResponses

logger = logging.getLogger(__name__)


class SimpleTestSuite(Action):
    def __init__(self, *args, **kwargs):
        super(SimpleTestSuite,self).__init__(*args,**kwargs)
        test_runner_config = settings.SPARROW_TEST_RUNNER
        self.DEPLOY_HOST = test_runner_config['deploy_host']['hostname']
        self.TARGET_ENV = test_runner_config['target_hosts'][0]['hostname']

    def run(self):
        task_id = self.params['id']
        logger.info('Started execution of task #{}'.format(task_id))
        logger.debug('params = ' + ujson.dumps(self.params))

        logger.info('Running deploy task...')
        deploy_task = Deploy(
            deploy_host=self.DEPLOY_HOST,
            app='wikia',
            env=self.TARGET_ENV,
            repos={
                'app': self.params['app_commit'],
                'config': self.params['config_commit']
            })
        deploy_task.run()

        if not deploy_task.ok:
            raise RuntimeError('Could not deploy application')

        logger.info('Running http get task...')
        http_get_task = HttpGet(url=self.params['url'], retries=self.params['retries'])
        http_get_task.run()

        if not http_get_task.ok:
            raise RuntimeError('Could not perform HTTP request to application')

        logger.info('Processing data...')
        processor = ProcessResponses(responses=http_get_task.result['responses'])
        processor.run()

        if not processor.ok:
            raise RuntimeError('There was an error during data processing')

        self.result['response_time'] = processor.result['response_time']
        self.status = self.COMPLETED
        logger.info('Finished execution of task #{}'.format(task_id))
