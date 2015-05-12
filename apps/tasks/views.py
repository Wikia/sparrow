# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import APIException


from .serializers import TaskSerializer
from .models import Task, TaskStatus


class PreconditionFailed(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = _('Precondition failed.')


class TaskViewSet(viewsets.ModelViewSet):
    """Task resource."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @list_route()
    def fetch(self, request):
        """ This method will fetch first task with status PENDING and set it's status to IN_PROGRESS.

        It's purpose is to acquire task for process and set it as being processed so no other
        task runners can fetch the same tasks multiple times multiple. This implement behaviour
        similar to queue.

        Args:
            request (Request): Request data

        Returns:
            Response: Details about the fetched task
        """
        task = self.queryset.filter(status=TaskStatus.PENDING).order_by('id').first()

        if task is None:
            raise NotFound('No pending tasks found')

        task.status = TaskStatus.IN_PROGRESS
        task.save()
        serializer = self.serializer_class(task, context={'request': request})

        return Response(serializer.data)

    @detail_route(methods=['delete'])
    def lock(self, request, pk=None):
        """ This method implements releasing lock on task in progress.

        Queue clients needs to be able to return tasks to queue (retry process) on non fatal errors. This method
        sets status to DONE or ERROR depending on the task result.

        Args:
            request (Request): Request data
            pk (int): Id of the task to remove lock from
        """
        task = self.get_object()

        if task.status != TaskStatus.IN_PROGRESS:
            raise PreconditionFailed('Task has not been fetched yet')

        if task.results.count() > 0:
            # assuming test has been executed successfully
            task.status = TaskStatus.DONE
        else:
            task.status = TaskStatus.ERROR
        task.save()

        serializer = self.serializer_class(task, context={'request': request})

        return Response(serializer.data)

    @detail_route(['post'])
    def result(self, request, pk):
        task = self.get_object()

        if task.status != TaskStatus.IN_PROGRESS:
            raise PreconditionFailed('Task is not being processed now')

        result, created = task.results.get_or_create(test_run=task.test_run)
        result.results = request.data
        result.save()

        task.status = TaskStatus.DONE
        task.save()

        serializer = self.serializer_class(task, context={'request': request})

        return Response(serializer.data)
