# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Test


class TestSerializer(serializers.HyperlinkedModelSerializer):
    results = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='testresult-detail'
    )

    class Meta:
        model = Test
