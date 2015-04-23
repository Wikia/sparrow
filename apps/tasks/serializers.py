# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from .models import Tasks


class TasksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tasks
