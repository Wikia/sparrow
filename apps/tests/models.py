# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_enumfield import enum


class TestStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = -1


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    test_uri = models.URLField()
    main_revision = models.CharField(max_length=10)
    secondary_revision = models.CharField(max_length=10)
    status = enum.EnumField(TestStatus, default=TestStatus.PENDING)
