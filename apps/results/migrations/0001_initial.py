# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
        ('test_runs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('results', jsonfield.fields.JSONField(default={})),
                ('task', models.ForeignKey(related_name='results', to='tasks.Task')),
                ('test_run', models.ForeignKey(related_name='results', to='test_runs.TestRun')),
            ],
        ),
    ]
