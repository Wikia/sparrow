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
