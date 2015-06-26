# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .serializers import TestRunSerializer
from .models import TestRun
from .models import TestRunStatus
from tasks.models import Task


class TestRunViewSet(viewsets.ModelViewSet):
    queryset = TestRun.objects.all()
    serializer_class = TestRunSerializer
