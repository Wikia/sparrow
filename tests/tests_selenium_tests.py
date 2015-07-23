# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test.utils import override_settings
import mock

from rest_framework.test import APITestCase
from testrunner.tasks.selenium_get import SeleniumGet
from tests.mocks.chrome import ChromeMock


@override_settings(SELENIUM_USE_VIRTUAL_DISPLAY=False)
class TestResultTestCase(APITestCase):

    @mock.patch('testrunner.tasks.selenium_get.webdriver.Chrome', ChromeMock.create)
    @mock.patch('selenium.webdriver.support.wait.WebDriverWait', mock.MagicMock())
    @mock.patch('testrunner.tasks.selenium_get.Display', mock.MagicMock())
    def test_selenium_tests(self):
        url = 'http://muppet.wikia.com'
        hostname = 'wikia.com'

        selenium_get = SeleniumGet()
        result_list = selenium_get.run(url=url, retries=2, tests=[
            dict(test_func='enter_page',
                             test_name='enter_page', params={'url' : url}),
            dict(test_func='perftest_oasis_anon_search_pageviews',
                             test_name='perftest_oasis_anon_search_pageviews', params={'hostname' : hostname}),
            dict(test_func='perftest_oasis_user_search_pageviews',
                             test_name='perftest_oasis_user_search_pageviews', params={'hostname' : hostname})
        ])['data']

        self.assertEqual(len(result_list), 3)
        self.assertEqual(result_list['enter_page'][0]['result']['total_load_time'], 7)
        self.assertEqual(result_list['enter_page'][0]['result']['steps'][0]['url'], 'http://muppet.wikia.com')
        self.assertEqual(result_list['enter_page'][0]['result']['steps'][0]['backend_time'], 1)
        self.assertEqual(result_list['perftest_oasis_anon_search_pageviews'][0]['result']['total_load_time'], 7)
        self.assertEqual(result_list['perftest_oasis_user_search_pageviews'][0]['result']['total_load_time'], 7)
