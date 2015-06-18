# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CompareRequest(models.Model):
    id = models.AutoField(primary_key=True)

    repo = models.CharField(max_length=100)
    pull_request_num = models.IntegerField()

    base_ref = models.CharField(max_length=250)
    base_sha = models.CharField(max_length=40)
    base_test_run = models.ForeignKey('test_runs.TestRun', related_name='base_in_compare_requests')

    head_ref = models.CharField(max_length=250)
    head_sha = models.CharField(max_length=40)
    head_test_run = models.ForeignKey('test_runs.TestRun', related_name='head_in_compare_requests')

    created = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "{0} #{1}".format(self.__class__.__name__, self.id)

    __unicode__ = __repr__

    __str__ = __repr__
