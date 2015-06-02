# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy
import mock
import responses
import re

from django.core.urlresolvers import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import TaskStatus
from tests.mocks.ssh import SSHConnectionMock
from tests.mocks.requests import post_response
from tests.mocks.phantomas import PhantomasMock


@override_settings(CELERY_ALWAYS_EAGER=True)
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

    @mock.patch('testrunner.tasks.deploy.SSHConnection', SSHConnectionMock)
    @mock.patch('testrunner.tasks.phantomas_get.phantomas.Phantomas', PhantomasMock)
    @responses.activate
    @post_response
    def test_run_task(self, post_callback):
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

        self.assertEqual(self.response_data['results']['response_time']['count'], 10)
        self.assertEqual(self.response_data['results']['response_time']['highest'], 123.0)
        self.assertEqual(self.response_data['results']['response_time']['lowest'], 123.0)

        self.assertEqual(self.response_data['results']['backend_metrics']['memc_dupes']['count'], 10)
        self.assertEqual(self.response_data['results']['backend_metrics']['memc_dupes']['highest'], 4.0)
        self.assertEqual(self.response_data['results']['backend_metrics']['memc_misses']['count'], 10)
        self.assertEqual(self.response_data['results']['backend_metrics']['memc_misses']['highest'], 1.0)
        self.assertEqual(self.response_data['results']['backend_metrics']['query_master']['highest'], 314.0)
        self.assertEqual(self.response_data['results']['backend_metrics']['query_slave']['highest'], 11.0)
        self.assertEqual(self.response_data['results']['backend_metrics']['query_time']['highest'], 0.363579)
        self.assertEqual(self.response_data['results']['backend_metrics']['server_time']['highest'], 1.869824)

        self.assertEqual(self.response_data['results']['phantomas_metrics']['js_size']['highest'], 927221.0)
        self.assertEqual(self.response_data['results']['phantomas_metrics']['content_length']['highest'], 1922742.0)
        self.assertEqual(self.response_data['results']['phantomas_metrics']['css_count']['highest'], 5.0)
        self.assertEqual(self.response_data['results']['phantomas_metrics']['body_size']['highest'], 1304562.0)
        self.assertEqual(self.response_data['results']['phantomas_metrics']['html_size']['highest'], 124541.0)
        self.assertEqual(self.response_data['results']['phantomas_metrics']['other_count']['highest'], 19.0)

    def test_update_result(self):
        url = reverse('task-detail', args=[self.task_to_delete.id, ])
        payload = {'status': TaskStatus.ERROR}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Update failed: {0}'.format(response.data))
        self.assertEqual(response.data['status'], payload['status'])

    def test_delete_result(self):
        url = reverse('task-detail', args=[self.task_to_delete.id, ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg='Delete failed: {0}'.format(response.data))
