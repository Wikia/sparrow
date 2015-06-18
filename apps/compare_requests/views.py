# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from .serializers import CompareRequestSerializer
from .models import CompareRequest


class CompareRequestViewSet(viewsets.ModelViewSet):
    queryset = CompareRequest.objects.all()
    serializer_class = CompareRequestSerializer
