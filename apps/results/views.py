# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from .serializers import TestResultSerializer
from .serializers import TestRawResultSerializer
from .models import TestResult
from .models import TestRawResult


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer

class TestRawResultViewSet(viewsets.ModelViewSet):
    queryset = TestRawResult.objects.all()
    serializer_class = TestRawResultSerializer
