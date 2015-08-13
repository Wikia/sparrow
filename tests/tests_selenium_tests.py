# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
import mock
import re
import responses
from model_mommy import mommy

from results.models import TestRawResult
from rest_framework.test import APITestCase
from testrunner.tasks.selenium_get import SeleniumGet
from tests.mocks.chrome import ChromeMock
from tests.mocks.requests import post_response, patch_response


@override_settings(SELENIUM_USE_VIRTUAL_DISPLAY=False)
class TestResultTestCase(APITestCase):
    def setUp(self):
        self.result = mommy.make('results.TestResult')
        self.task = mommy.make('tasks.Task')

    @mock.patch('testrunner.tasks.selenium_get.webdriver.Chrome', ChromeMock.create)
    @mock.patch('selenium.webdriver.support.wait.WebDriverWait', mock.MagicMock())
    @mock.patch('testrunner.tasks.selenium_get.Display', mock.MagicMock())
    @responses.activate
    @post_response
    @patch_response
    def test_selenium_tests(self, post_callback, patch_callback):
        url = 'http://muppet.wikia.com'
        hostname = 'wikia.com'

        api_uri = re.compile(r'https?://testserver')

        # mocking API results calls
        responses.add_callback(responses.POST, api_uri, callback=post_callback,
                               content_type='application/json')

        responses.add_callback(responses.PATCH, api_uri, callback=patch_callback,
                               content_type='application/json')

        task_uri = 'http://testserver' + reverse('task-detail', args=[self.task.id, ])

        selenium_get = SeleniumGet()
        tests = [
            dict(test_func='enter_page', test_name='enter_page', params={'url': url}),
            dict(test_func='perftest_oasis_anon_search_pageviews', test_name='perftest_oasis_anon_search_pageviews',
                 params={'hostname': hostname}),
            dict(test_func='perftest_oasis_user_search_pageviews', test_name='perftest_oasis_user_search_pageviews',
                 params={'hostname': hostname})
        ]
        selenium_get.run(url=url, retries=2, raw_result_uri='http://testserver' + reverse('testrawresult-list'),
                         result_uri=reverse('testresult-detail', args=[self.result.id, ]), tests=tests, task_uri=task_uri)

        raw_result = TestRawResult.objects.last()
        result = raw_result.data

        self.assertEqual(len(result), 3)
        self.assertEqual(result['enter_page'][0]['result']['total_load_time'], 7)
        self.assertEqual(result['enter_page'][0]['result']['steps'][0]['url'], 'http://muppet.wikia.com')
        self.assertEqual(result['enter_page'][0]['result']['steps'][0]['backend_time'], 1)
        self.assertEqual(result['perftest_oasis_anon_search_pageviews'][0]['result']['total_load_time'], 7)
        self.assertEqual(result['perftest_oasis_user_search_pageviews'][0]['result']['total_load_time'], 7)
