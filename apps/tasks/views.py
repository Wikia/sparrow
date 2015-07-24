# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException


from .serializers import TaskSerializer
from .models import Task


class PreconditionFailed(APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = _('Precondition failed.')


class TaskViewSet(viewsets.ModelViewSet):
    """Task resource."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @detail_route(methods=['post', ])
    def run(self, request, pk=None):
        task = self.get_object()

        task.run(
            results_uri=request.build_absolute_uri(reverse('testresult-list')),
            raw_result_uri=request.build_absolute_uri(reverse('testrawresult-list')),
            task_uri=request.build_absolute_uri(reverse('task-detail', args=[pk, ])),
            test_run_uri=request.build_absolute_uri(reverse('testrun-detail', args=[task.test_run_id, ])),
        )

        return Response(status=status.HTTP_202_ACCEPTED)
