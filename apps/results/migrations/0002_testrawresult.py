# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRawResult',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('source', models.CharField(max_length=100)),
                ('data', models.TextField(default='')),
                ('result', models.ForeignKey(to='results.TestResult', related_name='raw_results')),
            ],
        ),
    ]
