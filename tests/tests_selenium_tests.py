# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import mock

from rest_framework.test import APITestCase
from testrunner.actions.run_selenium_test import RunSeleniumTest


class TestResultTestCase(APITestCase):

    def __navigation_timing_api_side_effect(self, *args, **kwargs):
        if args[0] == 'return new Date().getTime()':
            return 0
        if args[0] == 'return document.readyState':
            return 'complete'
        if args[0] == 'return window.performance.timing.loadEventEnd':
            return 7
        elif args[0] == 'return window.performance.timing':
            return dict(
                navigationStart=1,
                responseStart=2,
                responseEnd=3,
                domInteractive=4,
                domComplete=5,
                domContentLoadedEventEnd=6,
                loadEventEnd=7
            )
        else:
            raise Exception('Invalid __navigation_timing_api_side_effect invocation')

    def test_selenium_tests(self):
        url = 'http://muppet.wikia.com'
        hostname = 'wikia.com'

        chrome_mock = mock.MagicMock()
        chrome_mock.execute_script.side_effect = self.__navigation_timing_api_side_effect
        with mock.patch('selenium.webdriver.Chrome', return_value=chrome_mock):
            with mock.patch('selenium.webdriver.support.wait.WebDriverWait'):
                chrome_mock.execute_script = self.__navigation_timing_api_side_effect

                run_selenium_test_action = RunSeleniumTest()
                run_selenium_test_action.run([
                    RunSeleniumTest.Test(name='enter_page', params={'url' : url}),
                    RunSeleniumTest.Test(name='perftest_oasis_anon_search_pageviews', params={'hostname' : hostname}),
                    RunSeleniumTest.Test(name='perftest_oasis_user_search_pageviews', params={'hostname' : hostname})
                ])
                self.assertEqual(len(run_selenium_test_action.result), 3)
                self.assertEqual(run_selenium_test_action.result[0]['total_load_time'], 7)
                self.assertEqual(run_selenium_test_action.result[0]['steps'][0]['url'], 'http://muppet.wikia.com')
                self.assertEqual(run_selenium_test_action.result[0]['steps'][0]['backend_time'], 1)
                self.assertEqual(run_selenium_test_action.result[1]['total_load_time'], 7)
                self.assertEqual(run_selenium_test_action.result[2]['total_load_time'], 7)
