# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_enumfield import enum


class TestRunStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = -1


class TestRun(models.Model):
    id = models.AutoField(primary_key=True)
    test_run_uri = models.URLField()
    main_revision = models.CharField(max_length=10)
    secondary_revision = models.CharField(max_length=10)
    status = enum.EnumField(TestRunStatus, default=TestRunStatus.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "{0}(#{1}): {2}@{3}".format(
            self.__class__.__name__,
            self.id,
            self.test_run_uri,
            self.main_revision
        )

    def __unicode__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __str__ = __unicode__
