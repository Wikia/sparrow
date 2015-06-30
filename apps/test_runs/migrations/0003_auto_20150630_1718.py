# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('test_runs', '0002_auto_20150525_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='testrun',
            name='retries',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='main_revision',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')]),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='secondary_revision',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')]),
        ),
    ]
