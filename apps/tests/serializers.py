# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Test


class TestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Test
