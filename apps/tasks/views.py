# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
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

        task.run()

        return Response(status=status.HTTP_202_ACCEPTED)
