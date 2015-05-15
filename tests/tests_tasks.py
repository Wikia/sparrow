# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from model_mommy import mommy

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task
from tasks.models import TaskStatus


class TestResultTestCase(APITestCase):
    def setUp(self):
        self.test_run = mommy.make('test_runs.TestRun')
        self.task_to_delete = mommy.make('tasks.Task')
        self.result = mommy.make('results.TestResult')

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

    def test_fetch_task(self):
        url = reverse('task-fetch')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Fetch failed: {0}'.format(response.data))
        self.assertEqual(response.data['status'], TaskStatus.IN_PROGRESS)

        # now to remove the lock from fetched Task
        lock_url = reverse('task-lock', args=[response.data['id']])
        response = self.client.delete(lock_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg='Lock remove failed: {0}'.format(response.data))
        # we expect status to be set to ERROR since no results were generated for this Task
        self.assertEqual(response.data['status'], TaskStatus.ERROR)

        # now we create task with some results
        proper_task = mommy.make('tasks.Task')
        mommy.make('results.TestResult', task=proper_task)

        # now we need to fetch it
        url = reverse('task-fetch')
        while True:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                             msg='Cannot fetch proper task: {0}'.format(response.data))
            if response.data['id'] == proper_task.id:
                break

        lock_url = reverse('task-lock', args=[proper_task.id])
        response = self.client.delete(lock_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Lock remove failed for proper task: {0}'.format(response.data))
        # in this we expect status to be set to DONE - we do have Result associated with this Task
        self.assertEqual(response.data['status'], TaskStatus.DONE)

        # set all tasks from PENDING to ERROR to test if fetch returns 404
        for task in Task.objects.filter(status=TaskStatus.PENDING):
            task.status = TaskStatus.ERROR
            task.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         msg='Fetch none failed: {0}'.format(response.data))

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
