# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
import ujson


class JSONField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, value):
        try:
            obj = ujson.loads(value)
        except ValueError:
            raise serializers.ValidationError("Invalid JSON <{0}>".format(value))

        return obj

    def to_representation(self, value):
        return ujson.dumps(value)