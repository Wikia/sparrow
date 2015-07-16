# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import jsonfield


class TestResultManager(models.Manager):
    """ Custom model manager for TestResult model.

        To optimize SQL queries when fetching TestResults we set
        most database-heavy fields to be fetched separatelly when
        they are acctually needed. This speed ups the responses
        dramatically.
    """

    def get_queryset(self):
        return super(TestResultManager, self).get_queryset().defer('results')


class TestResult(models.Model):
    # Custom object manager to allow using deferred fields
    objects = TestResultManager()

    id = models.AutoField(primary_key=True)
    test_run = models.ForeignKey('test_runs.TestRun', related_name='results')
    task = models.ForeignKey('tasks.Task', related_name='results')
    created = models.DateTimeField(auto_now_add=True)
    results = jsonfield.JSONField(default={})

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__


class TestRawResult(models.Model):
    id = models.AutoField(primary_key=True)
    result = models.ForeignKey(TestResult, related_name='raw_results')
    source = models.CharField(max_length=100)
    data = jsonfield.JSONField(default={})
