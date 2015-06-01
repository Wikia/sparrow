# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
import ujson

import logging
from testrunner.actions import Action
from testrunner.actions.deploy import Deploy
from testrunner.actions.http_get import HttpGet
from testrunner.actions.http_get import MWProfilerGet
from testrunner.actions.process_results import ProcessResponses
from testrunner.actions.run_selenium_test import RunSeleniumTest
from common import media_wiki_tools

logger = logging.getLogger(__name__)


class SimpleTestSuite(Action):
    def __init__(self, *args, **kwargs):
        super(SimpleTestSuite,self).__init__(*args,**kwargs)
        test_runner_config = settings.SPARROW_TEST_RUNNER
        self.DEPLOY_HOST = test_runner_config['deploy_host']['hostname']
        self.TARGET_ENV = test_runner_config['target_hosts'][0]['hostname']

    def run_selenium_tests(self, url):
        logger.info('Running selenium task...')
        hostname = media_wiki_tools.get_hostname_from_url(url)

        run_selenium_test_action = RunSeleniumTest()
        run_selenium_test_action.run([
            RunSeleniumTest.Test(name='enter_page', params={'url' : url}),
            RunSeleniumTest.Test(name='perftest_oasis_anon_search_pageviews', params={'hostname' : hostname}),
            RunSeleniumTest.Test(name='perftest_oasis_user_search_pageviews', params={'hostname' : hostname})
        ])

        if not run_selenium_test_action.ok:
            raise RuntimeError('Selenium tests failed')

        return run_selenium_test_action.result

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

        selenium_result = self.run_selenium_tests(self.params['url'])

        logger.info('Running MW Profiler task...')
        mw_profiler = MWProfilerGet(url=self.params['url'], retries=self.params['retries'])
        mw_profiler.run()

        if not http_get_task.ok:
            raise RuntimeError('Could not perform HTTP request to application')

        logger.info('Processing data...')
        results = dict(http_get_task.result)
        results.update(mw_profiler.result)
        results['selenium'] = selenium_result
        processor = ProcessResponses(results=results)
        processor.run()

        if not processor.ok:
            raise RuntimeError('There was an error during data processing')

        self.result = processor.result
        self.raw_result = processor.raw_result
        self.status = self.COMPLETED
        logger.info('Finished execution of task #{}'.format(task_id))
