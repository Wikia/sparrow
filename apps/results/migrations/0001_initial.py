# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('test_runs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('results', jsonfield.fields.JSONField(default={})),
                ('test_run', models.ForeignKey(to='test_runs.TestRun', related_name='results')),
            ],
        ),
    ]
