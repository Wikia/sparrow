# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class TestResult(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey('tests.Test', related_name='results')
