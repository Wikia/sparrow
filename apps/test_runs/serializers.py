# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import TestRun


class TestRunSerializer(serializers.HyperlinkedModelSerializer):
    results = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='testresult-detail'
    )
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='task-detail'
    )

    class Meta:
        model = TestRun
        fields = ('id','name', 'test_run_uri', 'main_revision', 'secondary_revision', 'retries',
                  'status', 'created', 'tasks', 'results', 'url')
