# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestResultTestCase(APITestCase):
    def setUp(self):
        self.test_run = mommy.make('test_runs.TestRun')
        self.task = mommy.make('tasks.Task')
        self.result_to_delete = mommy.make('results.TestResult')

    def test_create_result(self):
        url = reverse('testresult-list')

        payload = {
            'test_run': reverse('testrun-detail', args=[self.test_run.id, ]),
            'task': reverse('task-detail', args=[self.task.id, ]),
        }

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg='Create failed: {0}'.format(response.data))

    def test_read_result(self):
        url = reverse('testresult-detail', args=[self.result_to_delete.id, ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Read failed: {0}'.format(response.data))

    def test_update_result(self):
        url = reverse('testresult-detail', args=[self.result_to_delete.id, ])
        payload = {'results': {'foo': 'bar', }}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Update failed: {0}'.format(response.data))
        self.assertEqual(response.data['results'], payload['results'])

    def test_delete_result(self):
        url = reverse('testresult-detail', args=[self.result_to_delete.id, ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg='Delete failed: {0}'.format(response.data))
