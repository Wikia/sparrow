# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from .serializers import TaskSerializer
from .models import Task, TaskStatus


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
