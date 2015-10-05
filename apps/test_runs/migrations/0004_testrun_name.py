# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_runs', '0003_auto_20150630_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='testrun',
            name='name',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
    ]
