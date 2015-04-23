# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets

from .serializers import TasksSerializer
from .models import Tasks


class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
