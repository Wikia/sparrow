# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestResultTestCase(APITestCase):
    def setUp(self):
        self.test_run = mommy.make('test_runs.TestRun')

    def test_create_result(self):
        url = reverse('testresult-list')

        payload = {
            'test_run': reverse('testrun-detail', args=[self.test_run.id, ]),
        }

        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
