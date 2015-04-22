# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import TestResult


class TestResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestResult
