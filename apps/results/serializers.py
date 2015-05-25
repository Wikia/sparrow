# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import TestResult
from .models import TestRawResult
from common.field_serializers import JSONField


class TestResultSerializer(serializers.HyperlinkedModelSerializer):
    results = JSONField(required=False)
    raw_results = serializers.HyperlinkedIdentityField(many=True, read_only=True, required=False, view_name='testrawresult-detail')

    class Meta:
        model = TestResult
        fields = ('id', 'test_run', 'task', 'created', 'results', 'raw_results', 'url')

class TestRawResultSerializer(serializers.HyperlinkedModelSerializer):
    data = JSONField(required=False)

    class Meta:
        model = TestRawResult
        fields = ('id', 'result', 'data', 'url')
