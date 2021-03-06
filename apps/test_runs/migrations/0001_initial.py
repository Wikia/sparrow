# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('test_run_uri', models.URLField()),
                ('main_revision', models.CharField(max_length=10)),
                ('secondary_revision', models.CharField(max_length=10)),
                ('status', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
