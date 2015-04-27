# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import jsonfield


class TestResult(models.Model):
    id = models.AutoField(primary_key=True)
    test_run = models.ForeignKey('test_runs.TestRun', related_name='results')
    created = models.DateTimeField(auto_now_add=True)
    results = jsonfield.JSONField(default={})

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__
