# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Task
from results.models import TestResult


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    results = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=TestResult.objects.all(),
        view_name='testresult-detail'
    )

    class Meta:
        model = Task
