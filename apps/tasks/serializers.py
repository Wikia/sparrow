# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Task
from results.models import TestResult


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'test_run', 'created', 'status', 'results', 'url')
