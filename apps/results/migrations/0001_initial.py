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
            name='TestRawResult',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('source', models.CharField(max_length=100)),
                ('data', jsonfield.fields.JSONField(default={})),
            ],
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('results', jsonfield.fields.JSONField(default={})),
                ('task', models.ForeignKey(to='tasks.Task', related_name='results')),
                ('test_run', models.ForeignKey(to='test_runs.TestRun', related_name='results')),
            ],
        ),
        migrations.AddField(
            model_name='testrawresult',
            name='result',
            field=models.ForeignKey(to='results.TestResult', related_name='raw_results'),
        ),
    ]
