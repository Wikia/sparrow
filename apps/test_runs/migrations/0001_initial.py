# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('test_run_uri', models.URLField()),
                ('main_revision', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')])),
                ('secondary_revision', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$', 'Revision must be alphanumeric')])),
                ('status', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
