# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskSerializer
from .models import Task, TaskStatus


class TaskViewSet(viewsets.ModelViewSet):
    """Task resource."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @detail_route(['GET'])
    def fetch(self, request, pk=None):
        """ This method will fetch given task and set it's status from PENDING to IN_PROGRESS.

        It's purpose is to acquire task for process and set it as being processed so no other
        task runners can fetch the same tasks multiple times multiple. Method will fail if the
        given task is in status other than PENDING.

        Args:
            request (Request): Request data
            pk (int): ID of the task to fetch

        Returns:
            Response: up-to-date task representation
        """
        task = get_object_or_404(self.queryset, pk=pk)

        if task.status != TaskStatus.PENDING:
            return Response(
                {'status': 'Task not in PENDING status'},
                status=status.HTTP_412_PRECONDITION_FAILED
            )

        task.status = TaskStatus.IN_PROGRESS
        task.save()
        serializer = self.serializer_class(task, context={'request': request})

        return Response(serializer.data)
