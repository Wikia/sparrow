# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django_enumfield import enum


class TaskStatus(enum.Enum):
    PENDING = 0
    IN_PROGRESS = 1
    DONE = 2
    ERROR = -1


class Tasks(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey('tests.Test', related_name='tasks')
    created = models.DateField(auto_now_add=True)
    status = enum.EnumField(TaskStatus, default=TaskStatus.PENDING)

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__
