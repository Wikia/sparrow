# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pprint

from model_mommy import mommy
import mock
import responses
import re

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from metrics.values import Stats

from tasks.models import TaskStatus
from tests.mocks.ssh import SSHConnectionMock, SSHConnectionMockBuilder
from tests.mocks.requests import post_response
from tests.mocks.phantomas import PhantomasMock
from tests.mocks.chrome import ChromeMock


CURRENT_TIME_MOCK = 1401041000

def time_time_mock(*args, **kwargs):
    global CURRENT_TIME_MOCK
    CURRENT_TIME_MOCK += 2
    return CURRENT_TIME_MOCK

def noop(*args, **kwargs):
    pass


@override_settings(CELERY_ALWAYS_EAGER=True)
@override_settings(API_SERVER_URL='http://testserver')
class TestResultTestCase(APITestCase):
    def setUp(self):
        self.test_run = mommy.make('test_runs.TestRun')
        self.task_to_delete = mommy.make('tasks.Task')
        self.result = mommy.make('results.TestResult')
        self.response_data = {}
        self.mw_content = """
            <html>
            Some stuff here
            <!-- Some comments here
            And more comments
            -->
            </html>
            <!--
            100.00% 1.869824      1 - -total
             90.10% 1.684765      1 - MediaWiki::main
             80.50% 1.505257      1 - MediaWiki::finalCleanup
             80.49% 1.504998      1 - OutputPage::output
             18.72% 0.350065    314 - DatabaseBase::query-master
             0.72% 0.013514     11 - DatabaseBase::query
             4.63% 0.086566    170 - MWMemcached::get
             0.35% 0.006459      1 - MWMemcached::get::NavigationModel:wikicities:en:message-global-navigation-hubs-menu-7-4-4-:1
             0.01% 0.000109      4 - MWMemcached::get::wikicities:WikiFactoryHub::getAllVerticals !DUPE
             0.01% 0.000125      1 - MWMemcached::get::muppet:newtalk:ip:94.42.104.162 !MISS
            -->
        """

    def test_create_task(self):
        url = reverse('task-list')

        payload = {
            'test_run': reverse('testrun-detail', args=[self.test_run.id, ]),
            'status': TaskStatus.PENDING,
            'results': [],
        }

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg='Create failed: {0}'.format(response.data))

    def test_read_task(self):
        url = reverse('task-detail', args=[self.task_to_delete.id, ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Read failed: {0}'.format(response.data))

    @mock.patch('testrunner.tasks.deploy.SSHConnection', SSHConnectionMockBuilder('1'))
    @mock.patch('testrunner.tasks.phantomas_get.phantomas.Phantomas', PhantomasMock)
    @mock.patch('testrunner.tasks.selenium_get.webdriver.Chrome', ChromeMock.create)
    @mock.patch('selenium.webdriver.support.wait.WebDriverWait', mock.MagicMock())
    @mock.patch('testrunner.test_suites.simple.SimpleTestSuiteTask.on_success', noop)
    @mock.patch('testrunner.tasks.http_get.HttpGet.get_current_time',time_time_mock)
    @responses.activate
    @post_response
    def test_run_task(self, post_callback):
        def extract_values_from_results(origin, id):
            series = [x for x in results
                      if x['context']['id'] == id
                      if x['context']['origin'] == origin]
            self.assertEqual(len(series), 1, '{}:{} gave {} value series (1 expected)'.format(origin, id, len(series)))
            return [x['value'] for x in series[0]['values']]

        def get_stats_from_requests(id, origin):
            values = extract_values_from_results(id, origin)
            return Stats(values)
        url = reverse('task-run', args=[self.task_to_delete.id, ])
        api_uri = re.compile(r'https?://testserver')

        # mocking MW responses
        responses.add(responses.GET, self.task_to_delete.test_run.test_run_uri,
                      body=self.mw_content, status=status.HTTP_200_OK,
                      adding_headers={'X-Backend-Response-Time': '123', })

        # mocking API results calls
        responses.add_callback(responses.POST, api_uri, callback=post_callback,
                               content_type='application/json')

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED,
                         msg='Run task failed: {0}'.format(response.data))

        results = self.response_data['results']

        response_times = get_stats_from_requests('requests', 'server.app.response_time')
        self.assertEqual(response_times.count, 10)
        self.assertEqual(response_times.min, 2.0)
        self.assertEqual(response_times.max, 2.0)

        memcached_dupes = get_stats_from_requests('mw_profiler', 'server.app.memcached.dupe_count')
        memcached_misses = get_stats_from_requests('mw_profiler', 'server.app.memcached.miss_count')
        queries_master = get_stats_from_requests('mw_profiler', 'server.app.database.queries.master_count')
        queries_slave = get_stats_from_requests('mw_profiler', 'server.app.database.queries.slave_count')
        queries_time = get_stats_from_requests('mw_profiler', 'server.app.database.queries.time')
        response_times = get_stats_from_requests('mw_profiler', 'server.app.response_time')
        self.assertEqual(memcached_dupes.count, 10)
        self.assertEqual(memcached_dupes.max, 4.0)
        self.assertEqual(memcached_misses.count, 10)
        self.assertEqual(memcached_misses.max, 1.0)
        self.assertEqual(queries_master.max, 314.0)
        self.assertEqual(queries_slave.max, 11.0)
        self.assertEqual(queries_time.max, 0.363579)
        self.assertEqual(response_times.max, 1.869824)

        js_size = get_stats_from_requests('phantomas', 'browser.assets.js.size')
        content_length = get_stats_from_requests('phantomas', 'raw.phantomas.contentLength')
        css_count = get_stats_from_requests('phantomas', 'browser.assets.css.count')
        body_size = get_stats_from_requests('phantomas', 'browser.assets.total_size')
        html_size = get_stats_from_requests('phantomas', 'browser.assets.html.size')
        other_count = get_stats_from_requests('phantomas', 'browser.assets.other.count')
        self.assertEqual(js_size.max, 927221.0)
        self.assertEqual(content_length.max, 1922742.0)
        self.assertEqual(css_count.max, 5.0)
        self.assertEqual(body_size.max, 1304562.0)
        self.assertEqual(html_size.max, 124541.0)
        self.assertEqual(other_count.max, 19.0)

    def test_update_result(self):
        url = reverse('task-detail', args=[self.task_to_delete.id, ])
        payload = {'status': TaskStatus.ERROR}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Update failed: {0}'.format(response.data))
        self.assertEqual(response.data['status'], payload['status'])

    def test_delete_result(self):
        url = reverse('task-detail', args=[self.task_to_delete.id, ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT,
                         msg='Delete failed: {0}'.format(response.data))
