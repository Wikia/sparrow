# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import CompareRequest


class CompareRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompareRequest
        fields = ('id', 'repo', 'pull_request_num', 'base_ref', 'base_sha', 'base_test_run', 'head_ref', 'head_sha',
                  'head_test_run')


class CompareRequestCreateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompareRequest
        fields = ('repo', 'pull_request_num')
