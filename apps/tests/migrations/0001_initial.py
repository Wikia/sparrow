# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('test_uri', models.URLField()),
                ('main_revision', models.CharField(max_length=10)),
                ('secondary_revision', models.CharField(max_length=10)),
            ],
        ),
    ]
