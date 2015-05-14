# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from test_runs.models import TestRunStatus


class TestResultTestCase(APITestCase):
    def setUp(self):
        self.testrun_to_delete = mommy.make('test_runs.TestRun')
        self.task_to_delete = mommy.make('tasks.Task')
        self.result = mommy.make('results.TestResult')

    def test_create_testrun(self):
        url = reverse('testrun-list')

        payload = {
            'test_run_uri': 'http://www.google.com/',
            'main_revision': 'dev',
            'secondary_revision': '1234sdfg',
        }

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg='Create failed: {0}'.format(response.data))

        # check if Task was automatically created
        self.assertEqual(len(response.data['tasks']), 1, msg='Sub task missing: {0}'.format(response.data))

    def test_read_testrun(self):
        url = reverse('testrun-detail', args=[self.testrun_to_delete.id, ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Read failed: {0}'.format(response.data))

    def test_update_testrun(self):
        url = reverse('testrun-detail', args=[self.testrun_to_delete.id, ])
        payload = {'status': TestRunStatus.PENDING}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Update failed: {0}'.format(response.data))
        self.assertEqual(response.data['status'], payload['status'])

    def test_delete_result(self):
        url = reverse('testrun-detail', args=[self.testrun_to_delete.id, ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg='Delete failed: {0}'.format(response.data))
