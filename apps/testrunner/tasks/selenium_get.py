# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from contextlib import closing
import os

from celery.utils.log import get_task_logger
from pyvirtualdisplay.display import Display

from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from common.utils import collect_results
from testrunner import app as celery_app
from testrunner.test_suites.selenium_tests import selenium_tests
from testrunner.test_suites.selenium_tests.selenium_timer import SeleniumTimer
from common import media_wiki_tools

from django.conf import settings

logger = get_task_logger(__name__)


class quitting(object):
    def __init__(self, thing):
        self.thing = thing
    def __enter__(self):
        return self.thing
    def __exit__(self, *exc_info):
        self.thing.quit()


class SeleniumGet(celery_app.Task):
    @staticmethod
    def get_driver():
        caps = DesiredCapabilities.CHROME
        driver = webdriver.Chrome(executable_path=settings.CRHOMEDRIVER_PATH,
                                  service_args=["--verbose", "--log-path=chromelog.log"],
                                  desired_capabilities=caps)
        driver.implicitly_wait(1)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)

        return driver

    @staticmethod
    def get_test_list(url):
        hostname = media_wiki_tools.get_hostname_from_url(url)
        url_muppet = 'http://muppet.{0}/wiki/Kermit'.format(hostname)
        url_perftest = 'http://perftest.{0}/wiki/Medium_Article'.format(hostname)
        url_perftest_no_externals = 'http://perftest.{0}/wiki/Medium_Article?noexternals=1'.format(
            hostname)
        return [
            {'test_func': 'enter_page', 'test_name': 'load_provided_url',
             'params': {'url': url}},
            # {'test_func': 'enter_page', 'test_name': 'oasis_muppet_kermit',
            #  'params': {'url': url_muppet}},
            # {'test_func': 'enter_page', 'test_name': 'oasis_perftest_medium_article_no_ads',
            #  'params': {'url': url_perftest}},
            # {'test_func': 'enter_page', 'test_name': 'oasis_perftest_medium_article_no_externals',
            #  'params': {'url': url_perftest_no_externals}},
            # {'test_func': 'perftest_oasis_anon_search_pageviews', 'test_name': 'perftest_oasis_anon_search_pageviews',
            #  'params': {'hostname': hostname}},
            # {'test_func': 'perftest_oasis_user_search_pageviews', 'test_name': 'perftest_oasis_user_search_pageviews',
            #  'params': {'hostname': hostname}}
        ]

    def run(self, url, retries=1, tests=None):
        logger.info('Starting getting data ({0} runs) with selenium for url: {1}'.format(retries, url))

        results = {}
        if tests is None:
            tests = self.get_test_list(url)

        display = None
        try:
            if settings.SELENIUM_USE_VIRTUAL_DISPLAY:
                display = Display()
                display.start()

            def run_test():
                return self.run_test(test)

            for test in tests:
                test_results = zip(range(retries),collect_results(run_test,retries))
                results[test['test_name']] = [
                    {
                        'run': i + 1,
                        'result': test_result
                    }
                    for i, test_result in test_results
                ]

        finally:
            if display is not None:
                display.stop()


        return {
            'generator': 'selenium',
            'context': {
                'origin': 'selenium'
            },
            'data': results
        }

    def run_test(self, test):
        logger.info('Running selenium test: ' + test['test_name'])
        try:
            with quitting(self.get_driver()) as driver:
                timer = SeleniumTimer(driver)
                timer.start()

                test_func = getattr(selenium_tests, test['test_func'])
                test_func(driver, timer, test['params'])

                return timer.get_result()
        except:
            logger.error('Exception caught while running selenium test: ' + test['test_name'], exc_info=True)
