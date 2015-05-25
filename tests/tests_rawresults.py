# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestRawResultTestCase(APITestCase):
    def setUp(self):
        self.results = mommy.make('results.TestResult')
        self.rawresult_to_delete = mommy.make('results.TestRawResult')

    def test_create_result(self):
        url = reverse('testrawresult-list')

        payload = {
            'result': reverse('testresult-detail', args=[self.results.id, ]),
        }

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg='Create failed: {0}'.format(response.data))

    def test_read_result(self):
        url = reverse('testrawresult-detail', args=[self.rawresult_to_delete.id, ])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Read failed: {0}'.format(response.data))

    def test_update_result(self):
        url = reverse('testrawresult-detail', args=[self.rawresult_to_delete.id, ])
        payload = {'data': "Some test data.\nMode test data"}

        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Update failed: {0}'.format(response.data))
        self.assertEqual(response.data['data'], payload['data'])

    def test_delete_result(self):
        url = reverse('testrawresult-detail', args=[self.rawresult_to_delete.id, ])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg='Delete failed: {0}'.format(response.data))
