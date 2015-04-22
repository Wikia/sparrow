# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    test_uri = models.URLField()
    main_revision = models.CharField(max_length=10)
    secondary_revision = models.CharField(max_length=10)
