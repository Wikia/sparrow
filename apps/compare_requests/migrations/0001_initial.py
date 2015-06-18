# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_runs', '0002_auto_20150525_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompareRequest',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('repo', models.CharField(max_length=100)),
                ('pull_request_num', models.IntegerField()),
                ('base_ref', models.CharField(max_length=250)),
                ('base_sha', models.CharField(max_length=40)),
                ('head_ref', models.CharField(max_length=250)),
                ('head_sha', models.CharField(max_length=40)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('base_test_run', models.ForeignKey(related_name='base_in_compare_requests', to='test_runs.TestRun')),
                ('head_test_run', models.ForeignKey(related_name='head_in_compare_requests', to='test_runs.TestRun')),
            ],
        ),
    ]
