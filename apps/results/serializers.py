# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import TestResult
from common.field_serializers import JSONField


class TestResultSerializer(serializers.HyperlinkedModelSerializer):
    results = JSONField(required=False)

    class Meta:
        model = TestResult
        fields = ('id', 'test_run', 'task', 'created', 'results', 'url')
