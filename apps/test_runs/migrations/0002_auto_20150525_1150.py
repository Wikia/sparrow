# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('test_runs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testrun',
            name='main_revision',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')], max_length=10),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='secondary_revision',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')], max_length=10),
        ),
    ]
