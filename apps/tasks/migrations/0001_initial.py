# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0003_test_created'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tasks',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True)),
                ('status', models.IntegerField(default=0)),
                ('test', models.ForeignKey(related_name='tasks', to='tests.Test')),
            ],
        ),
    ]
